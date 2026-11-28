import unittest

from cq_measure.structure.classes.class_info import ClassInfo


class ClassInfoTest(unittest.TestCase):
    def test_interface_kinds(self):
        self.assertTrue(ClassInfo("A", 1, kind="protocol").is_interface)
        self.assertFalse(ClassInfo("B", 1).is_interface)


if __name__ == "__main__":
    unittest.main()
