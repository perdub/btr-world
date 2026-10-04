"""Upload built files to an existing Modrinth project. Token stays in the environment.
Dry-run performs no HTTP calls. Reruns verify SHA512 rather than duplicate releases.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,urllib.request,urllib.error,urllib.parse,uuid,zipfile
ROOT=Path(__file__).resolve().parents[1]
API='https://api.modrinth.com/v2'

def request(path,token='',method='GET',body=None,content_type=None):
 repo=os.environ.get('GITHUB_REPOSITORY','')
 headers={'User-Agent':'BTRWorldRelease/0.4.0'+(' (https://github.com/'+repo+')' if repo else '')}
 if token:headers['Authorization']=token
 if content_type:headers['Content-Type']=content_type
 req=urllib.request.Request(API+path,data=body,headers=headers,method=method)
 try:
  with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as error:
  raise RuntimeError(f'Modrinth {method} failed: HTTP {error.code}; check token permissions, project and metadata.') from None

def inspect_files(directory):
 jar=directory/'btr-world.jar';sources=directory/'btr-world-sources.jar'
 for file in [jar,sources]:
  if not file.is_file():raise ValueError(f'Missing release artifact: {file.name}')
 with zipfile.ZipFile(jar) as z:
  manifest=json.loads(z.read('fabric.mod.json'))
  if manifest['id']!='bocchi' or manifest['depends']['minecraft']!='1.21.1':raise ValueError('Wrong mod/Minecraft version')
 return manifest['version'],[('mod',jar,None),('sources',sources,'sources-jar')]

def metadata(config,project,version,dependencies,changelog):
 return {'name':config['name']+' '+version,'version_number':version,'project_id':project,
  'changelog':changelog,'version_type':config['version_type'],'status':config['status'],
  'environment':config['environment'],'game_versions':config['game_versions'],'loaders':config['loaders'],
  'featured':False,'dependencies':dependencies,'file_parts':['mod','sources'],'primary_file':'mod',
  'file_types':{'sources':'sources-jar'}}

def multipart(data,files):
 boundary='btr-'+uuid.uuid4().hex;parts=[]
 def part(header,content):parts.extend([('--'+boundary+'\r\n'+header+'\r\n\r\n').encode(),content,b'\r\n'])
 part('Content-Disposition: form-data; name="data"\r\nContent-Type: application/json',json.dumps(data).encode())
 for field,path,_ in files:
  part(f'Content-Disposition: form-data; name="{field}"; filename="{path.name}"\r\nContent-Type: application/java-archive',path.read_bytes())
 parts.append(('--'+boundary+'--\r\n').encode());return b''.join(parts),'multipart/form-data; boundary='+boundary

def existing_match(versions,version,files):
 matches=[v for v in versions if v['version_number']==version]
 if not matches:return None
 hashes={hashlib.sha512(p.read_bytes()).hexdigest() for _,p,_ in files}
 for match in matches:
  uploaded={f.get('hashes',{}).get('sha512') for f in match.get('files',[])}
  if hashes.issubset(uploaded):return match
 raise ValueError('Version number already exists with different files; bump mod_version instead of overwriting.')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');parser.add_argument('--artifacts',type=Path,default=ROOT/'release-assets');args=parser.parse_args()
 config=json.loads((ROOT/'release/modrinth.json').read_text());version,files=inspect_files(args.artifacts)
 project=os.environ.get('MODRINTH_PROJECT_ID','');token=os.environ.get('MODRINTH_TOKEN','')
 changelog=(ROOT/'release/CHANGELOG.md').read_text()
 if args.dry_run:
  deps=[{'project_id':d['slug'],'dependency_type':d['dependency_type']} for d in config['dependencies']]
  print(json.dumps(metadata(config,project or '<set MODRINTH_PROJECT_ID>',version,deps,changelog),ensure_ascii=False,indent=2));print('Dry-run: no network calls, no uploads.');return
 if not project or not token:raise ValueError('Set MODRINTH_PROJECT_ID and MODRINTH_TOKEN; never put the token in a file or command argument.')
 info=request('/project/'+urllib.parse.quote(project,safe=''),token)
 # This project was predominantly generated with AI; do not silently submit it as public.
 if info.get('status') not in ['unlisted','draft'] or config['status']!='unlisted':
  raise ValueError('Current release target must be draft/unlisted under Modrinth AI rules. Review release/PUBLISHING.md.')
 project=info['id'];path='/project/'+project+'/version'
 found=existing_match(request(path,token),version,files)
 if found:print('Matching version already exists: '+found['id']);return
 dependencies=[]
 for dep in config['dependencies']:
  dep_info=request('/project/'+urllib.parse.quote(dep['slug'],safe=''))
  dependencies.append({'project_id':dep_info['id'],'dependency_type':dep['dependency_type']})
 data=metadata(config,project,version,dependencies,changelog);body,content_type=multipart(data,files)
 try:result=request('/version',token,'POST',body,content_type)
 except (RuntimeError,urllib.error.URLError,TimeoutError):
  # A lost response may occur after the server accepted an upload. Check before retrying.
  found=existing_match(request(path,token),version,files)
  if found:print('Upload confirmed after interrupted response: '+found['id']);return
  raise
 print('Uploaded Modrinth version '+result['id'])
if __name__=='__main__':
 try:main()
 except (ValueError,RuntimeError,urllib.error.URLError,TimeoutError) as error:
  print(str(error),file=sys.stderr);sys.exit(1)
