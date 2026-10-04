import importlib.util,json,os,tempfile,unittest,zipfile,hashlib,urllib.error
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('publisher',Path(__file__).resolve().parents[1]/'scripts/publish_modrinth.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class UploadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'release').mkdir();self.artifacts=self.root/'release-assets';self.artifacts.mkdir()
  with zipfile.ZipFile(self.artifacts/'btr-world.jar','w') as z:z.writestr('fabric.mod.json',json.dumps({'id':'bocchi','version':'0.4.0','depends':{'minecraft':'1.21.1'}}))
  with zipfile.ZipFile(self.artifacts/'btr-world-sources.jar','w') as z:z.writestr('test.java','source')
  (self.root/'release/modrinth.json').write_text(json.dumps({'name':'BTR World','version_type':'beta','status':'unlisted','environment':'server_only_client_optional','game_versions':['1.21.1'],'loaders':['fabric'],'dependencies':[{'slug':'polymer','dependency_type':'required'}]}));(self.root/'release/CHANGELOG.md').write_text('Changes')
  self.files=p.inspect_files(self.artifacts)[1]
 def tearDown(self):self.tmp.cleanup()
 def match(self):return {'id':'existing','version_number':'0.4.0','files':[{'hashes':{'sha512':hashlib.sha512(f.read_bytes()).hexdigest()}} for _,f,_ in self.files]}
 def run_main(self,mock):
  with patch.object(p,'ROOT',self.root),patch.dict(os.environ,{'MODRINTH_PROJECT_ID':'project','MODRINTH_TOKEN':'test-secret'}),patch('sys.argv',['publish','--artifacts',str(self.artifacts)]),patch.object(p,'request',mock):p.main()
 def test_dry_run_has_no_network(self):
  with patch.object(p,'ROOT',self.root),patch('sys.argv',['publish','--dry-run','--artifacts',str(self.artifacts)]),patch.object(p,'request',side_effect=AssertionError('Network')):p.main()
 def test_duplicate_with_matching_hashes_skips_post(self):
  calls=[]
  def api(path,*args):
   calls.append(path);return {'id':'project','status':'unlisted'} if path=='/project/project' else [self.match()]
  self.run_main(api);self.assertEqual(calls,['/project/project','/project/project/version'])
 def test_version_collision_rejected(self):
  with self.assertRaises(ValueError):p.existing_match([{'id':'other','version_number':'0.4.0','files':[]}],'0.4.0',self.files)
 def test_upload_multipart_metadata_and_exact_bytes(self):
  def api(path,token='',method='GET',body=None,content_type=None):
   if path=='/project/project':return {'id':'project','status':'unlisted'}
   if path=='/project/project/version':return []
   if path=='/project/polymer':return {'id':'polymer-id'}
   self.assertEqual((path,method),('/version','POST'));self.assertNotIn(b'test-secret',body)
   self.assertIn(b'"dependency_type": "required"',body);self.assertIn(b'"primary_file": "mod"',body)
   for _,file,_ in self.files:self.assertIn(file.read_bytes(),body)
   self.assertTrue(content_type.startswith('multipart/form-data; boundary='));return {'id':'created'}
  self.run_main(api)
 def test_public_target_is_not_submitted(self):
  def api(path,*args):self.assertEqual(path,'/project/project');return {'id':'project','status':'approved'}
  with self.assertRaises(ValueError):self.run_main(api)
 def test_lost_response_does_not_duplicate_upload(self):
  calls=0
  def api(path,token='',method='GET',body=None,content_type=None):
   nonlocal calls
   if path=='/project/project':return {'id':'project','status':'unlisted'}
   if path=='/project/project/version':calls+=1;return [] if calls==1 else [self.match()]
   if path=='/project/polymer':return {'id':'polymer-id'}
   self.assertEqual(method,'POST');raise urllib.error.URLError('lost response')
  self.run_main(api);self.assertEqual(calls,2)
if __name__=='__main__':unittest.main()
