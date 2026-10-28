"""Offline contract checks; not app, auth, job execution or viewer evidence."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


class ShellContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE / 'integration.schema.json').is_file(),
                        'shell integration contract is missing')
        self.schema = json.loads((HERE / 'integration.schema.json').read_text(encoding='utf-8'))
        self.validator = Draft202012Validator(self.schema)
        self.examples = json.loads((HERE / 'examples.json').read_text(encoding='utf-8'))

    def reject(self, value):
        self.assertFalse(self.validator.is_valid(value), value)

    def test_schema_and_all_examples(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual({'viewer', 'job', 'library'}, {v['kind'] for v in self.examples})
        for value in self.examples:
            self.validator.validate(value)

    def test_guest_cannot_reference_private_scene(self):
        value = copy.deepcopy(self.examples[0])
        value['scene']['access'] = 'private'
        self.reject(value)

    def test_job_ready_requires_result_and_failed_requires_error(self):
        value = copy.deepcopy(self.examples[1])
        value['status'] = 'ready'
        self.reject(value)
        value['result'] = copy.deepcopy(self.examples[0]['scene'])
        self.validator.validate(value)
        value['status'] = 'failed'
        self.reject(value)
        value['result'] = None
        value['error'] = {'code': 'DEPENDENCY_UNAVAILABLE', 'message': 'Try later.'}
        self.validator.validate(value)

    def test_nonready_cannot_publish_result(self):
        for status in ['queued', 'running', 'failed', 'cancelled']:
            value = copy.deepcopy(self.examples[1])
            value['status'] = status
            value['result'] = copy.deepcopy(self.examples[0]['scene'])
            self.reject(value)

    def test_unknown_version_extra_fields_and_unsafe_ids(self):
        for field, bad in [('contract_version', '2.0.0'), ('token', 'not-a-real-secret')]:
            value = copy.deepcopy(self.examples[0])
            value[field] = bad
            self.reject(value)
        for bad in ['../private', 'https://example.invalid/scene', 'a?token=x', 'a\\b']:
            value = copy.deepcopy(self.examples[0])
            value['scene']['scene_id'] = bad
            self.reject(value)

    def test_library_only_public_entries(self):
        value = copy.deepcopy(self.examples[2])
        value['scene']['access'] = 'private'
        self.reject(value)

    def test_fixture_mount_is_real_synthetic_bundle_and_read_only(self):
        mounts = json.loads((HERE / 'fixture-mounts.json').read_text(encoding='utf-8'))
        self.assertEqual('1.0.0', mounts['contract_version'])
        self.assertEqual(1, len(mounts['mounts']))
        mount = mounts['mounts'][0]
        self.assertEqual('synthetic', mount['evidence'])
        self.assertTrue(mount['read_only'])
        scene_file = (ROOT / mount['repository_manifest']).resolve()
        self.assertTrue(scene_file.is_relative_to(ROOT / 'test-data' / 'synthetic'))
        scene = json.loads(scene_file.read_text(encoding='utf-8'))
        self.assertEqual('1.0.0', scene['schema_version'])
        self.assertTrue(scene['synthetic'])
        self.assertEqual(self.examples[0]['scene']['scene_id'], scene['id'])
        self.assertEqual(mount['scene_id'], scene['id'])


if __name__ == '__main__':
    unittest.main()
