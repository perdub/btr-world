import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('release', Path(__file__).resolve().parents[1] / 'scripts/modrinth_release.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.files = [Path(self.tmp.name) / 'btr-world.jar', Path(self.tmp.name) / 'btr-world-sources.jar']
        for f in self.files:
            f.write_bytes(f.name.encode())
        self.v = {'id': 'version', 'project_id': 'project', 'version_number': '1.0.0', 'status': 'listed',
                  'game_versions': ['1.21.1'], 'loaders': ['fabric'],
                  'files': [{'filename': f.name, 'hashes': {'sha512': hashlib.sha512(f.read_bytes()).hexdigest()},
                             'primary': i == 0, 'file_type': 'sources-jar' if i else None} for i, f in enumerate(self.files)]}
    def tearDown(self):
        self.tmp.cleanup()
    def test_project_draft_allowed(self):
        p.validate_project_visibility({'status': 'draft'})
    def test_project_unlisted_allowed(self):
        p.validate_project_visibility({'status': 'unlisted'})
    def test_processing_with_private_target_allowed(self):
        p.validate_project_visibility({'status': 'processing', 'requested_status': 'unlisted'})
        p.validate_project_visibility({'status': 'processing', 'requested_status': 'draft'})
    def test_processing_without_private_target_rejected(self):
        for requested in (None, 'approved', 'private'):
            with self.subTest(requested_status=requested), self.assertRaisesRegex(ValueError, 'requested_status'):
                p.validate_project_visibility({'status': 'processing', 'requested_status': requested})
    def test_public_project_rejected(self):
        with self.assertRaisesRegex(ValueError, 'expected draft or unlisted'):
            p.validate_project_visibility({'status': 'approved'})
    def test_correct_readback(self):
        p.check_version(self.v, {'id': 'project'}, '1.0.0', self.files)
    def test_wrong_project_rejected(self):
        with self.assertRaises(ValueError):
            p.check_version(self.v, {'id': 'other'}, '1.0.0', self.files)
    def test_different_files_rejected(self):
        self.files[0].write_bytes(b'changed')
        with self.assertRaises(ValueError):
            p.check_version(self.v, {'id': 'project'}, '1.0.0', self.files)
    def test_hidden_version_rejected(self):
        self.v['status'] = 'unlisted'
        with self.assertRaises(ValueError):
            p.check_version(self.v, {'id': 'project'}, '1.0.0', self.files)
    def test_wrong_primary_rejected(self):
        self.v['files'][0]['primary'] = False
        with self.assertRaises(ValueError):
            p.check_version(self.v, {'id': 'project'}, '1.0.0', self.files)
    def test_missing_sources_type_rejected(self):
        self.v['files'][1]['file_type'] = None
        with self.assertRaises(ValueError):
            p.check_version(self.v, {'id': 'project'}, '1.0.0', self.files)

if __name__ == '__main__':
    unittest.main()
