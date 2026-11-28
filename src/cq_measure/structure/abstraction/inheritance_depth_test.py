import unittest

from cq_measure.testing import findings_for


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
