import unittest

from cq_measure.structure.dependencies.imports.tsconfig import (
    AliasConfig,
    load_alias_configs,
    strip_json_comments,
)

BASE = """{
  // comment
  "compilerOptions": { "baseUrl": ".", "paths": { "@/*": ["./src/*"], }, },
}"""
APP = '{ "extends": "../tsconfig.base.json", "compilerOptions": { "paths": { "~ui": ["./ui/index.ts"] } } }'


class TsconfigTest(unittest.TestCase):
    def test_strip_comments_keeps_strings(self):
        self.assertEqual(strip_json_comments('{"a": "//x", /* c */ "b": [1,],}'), '{"a": "//x",  "b": [1]}')

    def test_loads_paths_with_extends(self):
        texts = {"web/tsconfig.base.json": BASE, "web/app/tsconfig.json": APP}
        configs = load_alias_configs(texts.get, list(texts))
        app = configs["web/app"]
        self.assertEqual(app.paths["~ui"], ["web/app/ui/index.ts"])
        self.assertEqual(app.paths["@/*"], ["web/src/*"])
        self.assertEqual(configs["web"].base_url, "web")

    def test_candidates(self):
        config = AliasConfig("src", {"@/*": ["src/*"], "exact": ["lib/e"]})
        self.assertEqual(config.candidates("@/a/b"), ["src/a/b", "src/@/a/b"])
        self.assertEqual(config.candidates("exact")[0], "lib/e")


if __name__ == "__main__":
    unittest.main()
