"""Package the remapped production JAR under a stable release asset name."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
libs = ROOT / 'build/libs'
jars = [p for p in libs.glob('*.jar') if not p.name.endswith(('-sources.jar', '-dev.jar'))]
if len(jars) != 1:
    raise SystemExit(f'Expected exactly one production JAR, found {len(jars)}: {jars}')
with zipfile.ZipFile(jars[0]) as jar:
    if jar.testzip() is not None:
        raise SystemExit('Corrupt production JAR')
    manifest = json.loads(jar.read('fabric.mod.json'))
    if manifest['id'] != 'bocchi' or manifest['depends']['minecraft'] != '1.21.1':
        raise SystemExit('Unexpected mod or Minecraft version')
output = ROOT / 'release-assets'
output.mkdir(exist_ok=True)
shutil.copyfile(jars[0], output / 'btr-world.jar')
sources = libs / f"btr-world-{manifest['version']}-sources.jar"
if not sources.is_file():
    raise SystemExit(f'Missing matching sources JAR: {sources.name}')
shutil.copyfile(sources, output / 'btr-world-sources.jar')
shutil.copyfile(ROOT / 'README.md', output / 'README.md')
checksums = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
                    for p in sorted(output.iterdir()) if p.name != 'SHA256SUMS.txt')
(output / 'SHA256SUMS.txt').write_text(checksums)
print(f"Release assets ready: {manifest['version']} -> btr-world.jar")
