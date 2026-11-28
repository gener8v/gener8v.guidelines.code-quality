import unittest

from cq_measure.testing import findings_for

PROXY = """class Proxy:
    def __init__(self, inner):
        self.inner = inner

    def get(self, key):
        return self.inner.get(key)

    def put(self, key, value):
        return self.inner.put(key, value)

    def drop(self, key):
        return self.inner.drop(key)
"""


class PassThroughTest(unittest.TestCase):
    def test_forwarding_class(self):
        self.assertEqual([f.line for f in findings_for({"a.py": PROXY}, "pass-through")], [1])

    def test_class_with_behavior(self):
        source = PROXY.replace("return self.inner.drop(key)", "return self.inner.drop(key.lower())")
        self.assertEqual(findings_for({"a.py": source}, "pass-through"), [])


if __name__ == "__main__":
    unittest.main()
