import ast
import unittest

from cq_measure.metrics.python_classes import base_name, python_classes

SOURCE = '''
from abc import ABC, abstractmethod
from typing import Protocol


class Store(ABC):
    @abstractmethod
    def get(self, key): ...


class Clock(Protocol):
    def now(self): ...


class Proxy(models.Model):
    def __init__(self, inner):
        self.inner = inner

    def get(self, key):
        return self.inner.get(key)

    async def put(self, key, value=None):
        return await self.inner.put(key, value=value)
'''


class PythonClassesTest(unittest.TestCase):
    def setUp(self):
        self.classes = {c.name: c for c in python_classes(ast.parse(SOURCE))}

    def test_kinds_and_bases(self):
        self.assertEqual(self.classes["Store"].kind, "abstract")
        self.assertEqual(self.classes["Clock"].kind, "protocol")
        self.assertEqual(self.classes["Proxy"].bases, ("Model",))
        self.assertTrue(self.classes["Store"].is_interface)

    def test_pass_through_field(self):
        self.assertEqual(self.classes["Proxy"].pass_through_field, "inner")
        self.assertIsNone(self.classes["Store"].pass_through_field)

    def test_base_name(self):
        self.assertEqual(base_name(ast.parse("Generic[T]").body[0].value), "Generic")


if __name__ == "__main__":
    unittest.main()
