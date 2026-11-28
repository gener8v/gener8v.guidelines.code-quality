import unittest

from cq_measure.behavior.secret_literal import mask
from cq_measure.testing import findings_for

AWS = "AKIA" + "Q3EXAMPLF7ZZTOPQ"
GITHUB = "ghp_" + "a1B2" * 9
PEM = "-----BEGIN " + "RSA PRIVATE KEY-----"
OPENAI = "sk-" + "proj-" + "Ab3dE6gH9jK2mN5pQ8sT1v"


class SecretLiteralTest(unittest.TestCase):
    def test_token_formats_are_masked(self):
        text = f'aws = "{AWS}"\ngh = "{GITHUB}"\n{PEM}\nkey = "{OPENAI}"\n'
        found = findings_for({"config.py": text}, "secret-literal")
        self.assertEqual([f.line for f in found], [1, 2, 3, 4])
        self.assertTrue(all(f.severity == "fail" for f in found))
        self.assertNotIn(AWS, found[0].message)
        self.assertIn("AKIA****", found[0].message)

    def test_assignments_outside_tests(self):
        text = 'DB_PASSWORD = "hunter2Hunter"\napi_key: "zX9qLm22pQ"\n'
        self.assertEqual([f.line for f in findings_for({"settings.py": text}, "secret-literal")], [1, 2])
        self.assertEqual(findings_for({"settings_test.py": text}, "secret-literal"), [])

    def test_placeholders_and_names(self):
        text = (
            'password = "changeme123"\ntoken_url = "https://x.io/token"\nsecret = "${SECRET}"\n'
            'tokenType = "access_token"\naws = "AKIAIOSFODNN7EXAMPLE"\nkey = "sk-short"\n'
            'slack = "xoxb-123456789012-abcdefghijkl"\n'
        )
        self.assertEqual(findings_for({"settings.py": text}, "secret-literal"), [])
        self.assertEqual(mask("abcdefgh"), "abcd****")


if __name__ == "__main__":
    unittest.main()
