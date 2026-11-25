import json
import unittest

from cq_measure.config import ConfigError, deep_merge, load_config, load_defaults
from cq_measure.fixture_repository import fixture_repo


class ConfigTest(unittest.TestCase):
    def test_every_check_has_a_rule_and_a_grade(self):
        for check_id, spec in load_defaults()["checks"].items():
            self.assertIn("rule", spec, check_id)
            self.assertTrue("severity" in spec or ("warn" in spec and "fail" in spec), check_id)

    def test_merges_repository_config(self):
        override = {"checks": {"file-lines": {"warn": 100}, "nesting": {"enabled": False}}, "public_symbols": ["api"]}
        with fixture_repo({".code-quality.json": json.dumps(override)}) as root:
            config = load_config(root)
        self.assertEqual(config["checks"]["file-lines"], {"rule": "1.1", "warn": 100, "fail": 500, "test_warn": 500, "test_fail": 800})
        self.assertFalse(config["checks"]["nesting"]["enabled"])
        self.assertEqual(config["public_symbols"], ["api"])

    def test_rejects_bad_json_and_unknown_ids(self):
        for text in ("{", '{"checks": {"no-such-check": {}}}', '{"colour": 1}', "[]"):
            with fixture_repo({".code-quality.json": text}) as root:
                with self.assertRaises(ConfigError):
                    load_config(root)

    def test_deep_merge_replaces_lists(self):
        self.assertEqual(deep_merge({"a": {"b": 1, "c": [1]}}, {"a": {"c": [2]}}), {"a": {"b": 1, "c": [2]}})


if __name__ == "__main__":
    unittest.main()
