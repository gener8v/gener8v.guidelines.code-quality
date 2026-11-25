import unittest

from cq_measure.fixture_repository import findings_for


class VagueNameTest(unittest.TestCase):
    def test_junk_drawers_and_versions(self):
        files = {"src/utils/format.ts": "", "src/helpers.py": "", "src/parser2.py": "", "src/report-old/a.ts": ""}
        found = findings_for(files, "vague-name")
        self.assertEqual(sorted(f.path for f in found), ["src/helpers.py", "src/parser2.py", "src/report-old", "src/utils"])
        self.assertTrue(all(f.severity == "fail" for f in found))

    def test_every_built_in_name_is_a_finding(self):
        names = "utils util helpers helper misc common stuff general other temp tmp new old".split()
        found = findings_for({f"src/{name}/a.ts": "" for name in names}, "vague-name")
        self.assertEqual(sorted(f.path for f in found), sorted(f"src/{name}" for name in names))

    def test_configuration_adds_names_but_cannot_remove_them(self):
        files = {"src/utils/a.ts": "", "src/shared/a.ts": ""}
        found = findings_for(files, "vague-name", {"vague_names": ["shared"]})
        self.assertEqual(sorted(f.path for f in found), ["src/shared", "src/utils"])
        self.assertEqual([f.path for f in findings_for(files, "vague-name", {"vague_names": []})], ["src/utils"])

    def test_specific_names_and_route_segments(self):
        files = {"src/currency/format.ts": "", "src/oauth2.py": "", "app/projects/new/page.tsx": "", "src/v2/api.py": ""}
        self.assertEqual(findings_for(files, "vague-name"), [])


class DirNameCaseTest(unittest.TestCase):
    def test_bad_directory_names(self):
        files = {"src/BillingStuff/a.ts": "", "src/my-pkg/a.py": "", "src/user_profile/a.ts": ""}
        found = findings_for(files, "dir-name-case")
        self.assertEqual(sorted(f.path for f in found), ["src/BillingStuff", "src/my-pkg", "src/user_profile"])

    def test_allowed_names(self):
        files = {"src/my_pkg/a.py": "", "src/user-profile/a.ts": "", "src/__tests__/a.test.ts": "", "app/[id]/page.tsx": "", "app/(auth)/x.tsx": ""}
        self.assertEqual(findings_for(files, "dir-name-case"), [])


if __name__ == "__main__":
    unittest.main()
