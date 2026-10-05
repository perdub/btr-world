"""Read-only preflight/readback for cloudnode-pro/modrinth-publish.
This script never uploads files or changes project/version visibility.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.modrinth.com/v2'


def get(path, token):
    req = urllib.request.Request(API + path, headers={
        'Authorization': token, 'User-Agent': 'BTRWorldReleaseVerification/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise ValueError(f'Modrinth GET {path.split("?")[0]}: HTTP {error.code}; check read scopes and project access.') from None


def inspect(directory):
    files = [directory / 'btr-world.jar', directory / 'btr-world-sources.jar']
    for file in files:
        if not file.is_file():
            raise ValueError(f'Missing {file.name}')
    with zipfile.ZipFile(files[0]) as jar:
        mod = json.loads(jar.read('fabric.mod.json'))
    if mod['id'] != 'bocchi' or mod['depends']['minecraft'] != '1.21.1':
        raise ValueError('Wrong mod or Minecraft version')
    return mod['version'], files


def versions(project, token):
    # The ordinary project version list can hide unlisted releases.
    ids = project.get('versions', [])
    result = []
    for start in range(0, len(ids), 50):
        query = urllib.parse.urlencode({'ids': json.dumps(ids[start:start + 50])})
        result.extend(get('/versions?' + query, token))
    return result


def match(records, number, project_id, files):
    candidates = [v for v in records if v['version_number'] == number]
    if not candidates:
        return None
    for v in candidates:
        if v['project_id'] != project_id:
            raise ValueError('API returned a version belonging to a different project')
        expected = {f.name: hashlib.sha512(f.read_bytes()).hexdigest() for f in files}
        uploaded = {f['filename']: f.get('hashes', {}).get('sha512') for f in v['files']}
        if all(uploaded.get(name) == digest for name, digest in expected.items()):
            return v
    raise ValueError('Version number exists with different files; bump mod_version')


def validate_project_visibility(project):
    """Distinguish actual visibility from a pending request to stay private."""
    status = project.get('status')
    if status in ('draft', 'unlisted'):
        return
    # Modrinth uses `processing` while reviewing a requested project transition.
    # It is safe for this plan only when the pending target is still non-public.
    requested = project.get('requested_status')
    if status == 'processing' and requested in ('draft', 'unlisted'):
        return
    if status == 'processing':
        raise ValueError(f"Project is processing with requested_status={requested!r}; expected draft or unlisted. Refusing upload.")
    raise ValueError(f'Project status is {status!r}; expected draft or unlisted. Refusing upload.')


def check_version(v, project, number, files):
    if not match([v], number, project['id'], files):
        raise ValueError('Version number does not match the built JAR')
    if v['status'] != 'listed':
        raise ValueError(f'Version {v["id"]} has status {v["status"]}, expected listed. Project visibility is independent.')
    primary = [f for f in v['files'] if f.get('primary')]
    sources = [f for f in v['files'] if f['filename'] == 'btr-world-sources.jar']
    if len(primary) != 1 or primary[0]['filename'] != 'btr-world.jar':
        raise ValueError('Wrong primary file')
    if not sources or sources[0].get('file_type') != 'sources-jar':
        raise ValueError('Sources JAR is missing its file type')
    if v['game_versions'] != ['1.21.1'] or v['loaders'] != ['fabric']:
        raise ValueError('Wrong game versions or loaders')


def output(key, value):
    destination = os.environ.get('GITHUB_OUTPUT')
    if destination:
        delimiter = 'btr_' + uuid.uuid4().hex
        with open(destination, 'a', encoding='utf-8') as file:
            file.write(f'{key}<<{delimiter}\n{value}\n{delimiter}\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'verify', 'inspect'])
    parser.add_argument('--version-id', help='Existing version to inspect; no files are uploaded')
    parser.add_argument('--artifacts', type=Path, default=ROOT / 'release-assets')
    args = parser.parse_args()
    token = os.environ.get('MODRINTH_TOKEN', '')
    identifier = os.environ.get('MODRINTH_PROJECT_ID', '')
    if not token or not identifier:
        raise ValueError('Set MODRINTH_PROJECT_ID and MODRINTH_TOKEN in Actions')
    project = get('/project/' + urllib.parse.quote(identifier, safe=''), token)
    print(f'Project: {project["title"]}; ID={project["id"]}; slug={project.get("slug")}; status={project["status"]}; requested_status={project.get('requested_status')!r}')
    if args.mode == 'inspect':
        if not args.version_id:
            raise ValueError('inspect requires --version-id')
        v = get('/version/' + urllib.parse.quote(args.version_id, safe=''), token)
        if v['project_id'] != project['id']:
            raise ValueError('Version belongs to a different project')
        print(json.dumps({k: v[k] for k in ['id', 'project_id', 'version_number', 'status', 'files']}, indent=2))
        return
    validate_project_visibility(project)
    number, files = inspect(args.artifacts)
    found = match(versions(project, token), number, project['id'], files)
    if args.mode == 'prepare':
        config = json.loads((ROOT / 'release/modrinth.json').read_text())
        if config['status'] != 'listed':
            raise ValueError('Release version status must be listed; project remains draft/unlisted')
        if found:
            check_version(get('/version/' + found['id'], token), project, number, files)
        dependencies = [{'project_id': get('/project/' + d['slug'], token)['id'],
                         'dependency_type': d['dependency_type']} for d in config['dependencies']]
        for key, value in {'project': project['id'], 'version': number,
                           'name': config['name'] + ' ' + number,
                           'exists': str(bool(found)).lower(),
                           'dependencies': json.dumps(dependencies),
                           'changelog': (ROOT / 'release/CHANGELOG.md').read_text()}.items():
            output(key, value)
        print('Existing matching version verified; upload skipped.' if found else 'Ready for Modrinth Publish action.')
        return
    if not found:
        raise ValueError('Upload NOT confirmed: API does not list the built version on this project')
    v = get('/version/' + found['id'], token)
    check_version(v, project, number, files)
    print(f'Confirmed by GET: version={v["id"]}; project={v["project_id"]}; status={v["status"]}; SHA512 of both JARs matches.')
    url = f'https://modrinth.com/mod/{project.get("slug") or project["id"]}/version/{v["id"]}'
    summary = f'### Modrinth upload verified\n\nProject: {project["title"]} (`{project["id"]}`, {project["status"]})\n\nVersion: `{number}` (`{v["id"]}`, {v["status"]})\n\n{url}\n\nBoth JARs verified by SHA512. Draft projects still require review before sharing.\n'
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as file:
            file.write(summary)
    print(url)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, urllib.error.URLError, TimeoutError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
