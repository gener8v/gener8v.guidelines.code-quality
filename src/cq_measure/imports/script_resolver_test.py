import unittest

from cq_measure.imports.script_resolver import ScriptResolver
from cq_measure.imports.tsconfig import AliasConfig

KNOWN = {"src/app.ts", "src/billing/index.ts", "src/billing/rounding.ts", "src/ui/button.tsx", "src/lib/x.ts"}


class ScriptResolverTest(unittest.TestCase):
    def setUp(self):
        aliases = {"": AliasConfig(None, {"@/*": ["src/*"]})}
        self.resolver = ScriptResolver(KNOWN, aliases)

    def test_relative_with_extension_swap_and_index(self):
        self.assertEqual(self.resolver.resolve("src/app.ts", "./billing"), "src/billing/index.ts")
        self.assertEqual(self.resolver.resolve("src/app.ts", "./billing/rounding.js"), "src/billing/rounding.ts")
        self.assertEqual(self.resolver.resolve("src/app.ts", "./ui/button"), "src/ui/button.tsx")

    def test_alias_and_package(self):
        self.assertEqual(self.resolver.resolve("src/ui/button.tsx", "@/lib/x"), "src/lib/x.ts")
        self.assertIsNone(self.resolver.resolve("src/app.ts", "react"))
        self.assertIsNone(self.resolver.resolve("src/app.ts", "../../outside"))


if __name__ == "__main__":
    unittest.main()
