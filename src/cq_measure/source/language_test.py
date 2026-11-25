import unittest

from cq_measure.source.language import family_of, is_declaration, language_of, stem_of


class LanguageTest(unittest.TestCase):
    def test_language_and_family(self):
        self.assertEqual(language_of("a/b.tsx"), "tsx")
        self.assertEqual(language_of("README.md"), None)
        self.assertEqual(family_of("jsx"), "script")
        self.assertEqual(family_of("kotlin"), "jvm")
        self.assertEqual(family_of("python"), "python")

    def test_declarations_and_stems(self):
        self.assertTrue(is_declaration("env.d.ts"))
        self.assertFalse(is_declaration("env.ts"))
        self.assertEqual(stem_of("src/env.d.ts"), "env")
        self.assertEqual(stem_of("src/user.service.ts"), "user.service")


if __name__ == "__main__":
    unittest.main()
