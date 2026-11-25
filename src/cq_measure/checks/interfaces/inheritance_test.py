import unittest

from cq_measure.fixture_repository import findings_for

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


class InheritanceDepthTest(unittest.TestCase):
    def test_chain_depth(self):
        source = "class A(Model):\n    pass\n\n\nclass B(A):\n    pass\n\n\nclass C(B):\n    pass\n\n\nclass D(C):\n    pass\n"
        found = findings_for({"a.py": source}, "inheritance-depth")
        self.assertEqual([(f.line, f.severity) for f in found], [(9, "warn"), (13, "fail")])

    def test_shallow(self):
        source = "class A(ABC):\n    pass\n\n\nclass B(A, Generic[T]):\n    pass\n"
        self.assertEqual(findings_for({"a.py": source}, "inheritance-depth"), [])


if __name__ == "__main__":
    unittest.main()
