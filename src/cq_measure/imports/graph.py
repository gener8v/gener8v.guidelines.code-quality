"""The import graph between the source files of a repository."""

from __future__ import annotations

from collections import defaultdict

from cq_measure.imports.import_record import ImportRecord
from cq_measure.imports.python_imports import python_imports
from cq_measure.imports.python_resolver import PythonResolver
from cq_measure.imports.script_imports import climb_of, script_imports
from cq_measure.imports.script_resolver import ScriptResolver
from cq_measure.imports.tsconfig import load_alias_configs
from cq_measure.source.language import SCRIPT_LANGUAGES


class ModuleGraph:
    """Import records per file, and the edges between source files of the repository."""

    def __init__(self, records: dict[str, list[ImportRecord]], sources: set[str]):
        self.records = records
        self.edges: dict[str, dict[str, ImportRecord]] = {}
        self.importers: dict[str, set[str]] = defaultdict(set)
        for path, file_records in records.items():
            targets: dict[str, ImportRecord] = {}
            for record in file_records:
                if record.target in sources and record.target != path:
                    _keep_strongest(targets, record)
            self.edges[path] = targets
            for target in targets:
                self.importers[target].add(path)


def _keep_strongest(targets: dict[str, ImportRecord], record: ImportRecord) -> None:
    current = targets.get(record.target)
    if current is None or (current.type_only and not record.type_only):
        targets[record.target] = record


def build_graph(workspace) -> ModuleGraph:
    """Extract and resolve the imports of every Python, TypeScript, and JavaScript file."""
    known = set(workspace.by_path)
    python = PythonResolver(known, workspace.package_roots)
    aliases = load_alias_configs(lambda path: workspace.by_path[path].text if path in known else None, known)
    script = ScriptResolver(known, aliases)
    records = {}
    for source in workspace.sources:
        if source.language == "python":
            records[source.path] = _python_records(workspace, source, python)
        elif source.language in SCRIPT_LANGUAGES:
            records[source.path] = _script_records(workspace, source, script)
    return ModuleGraph(records, {source.path for source in workspace.sources})


def _python_records(workspace, source, resolver: PythonResolver) -> list[ImportRecord]:
    tree = workspace.python_tree(source)
    if tree is None:
        return []
    records = []
    for statement in python_imports(tree):
        records.extend(resolver.resolve(source.path, statement))
    return records


def _script_records(workspace, source, resolver: ScriptResolver) -> list[ImportRecord]:
    records = []
    for found in script_imports(workspace.scan(source)):
        target = resolver.resolve(source.path, found.specifier)
        climb = climb_of(found.specifier) if found.specifier.startswith(".") else 0
        records.append(ImportRecord(found.line, found.specifier, climb, found.type_only, (), target))
    return records


def strongly_connected(graph: dict) -> list[list]:
    """Return the strongly connected components of `graph` (node -> successors), Tarjan's method."""
    tarjan = _Tarjan(graph)
    for start in sorted(graph):
        if start not in tarjan.index_of:
            tarjan.visit(start)
    return tarjan.components


class _Tarjan:
    def __init__(self, graph: dict):
        self.graph = graph
        self.index_of: dict = {}
        self.low: dict = {}
        self.on_stack: set = set()
        self.stack: list = []
        self.components: list[list] = []

    def visit(self, start) -> None:
        work = [self._enter(start)]
        while work:
            node, successors = work[-1]
            pushed = self._step(node, successors)
            if pushed is not None:
                work.append(pushed)
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                self.low[parent] = min(self.low[parent], self.low[node])
            if self.low[node] == self.index_of[node]:
                self.components.append(self._pop_component(node))

    def _enter(self, node) -> tuple:
        self.index_of[node] = self.low[node] = len(self.index_of)
        self.stack.append(node)
        self.on_stack.add(node)
        return node, iter(sorted(self.graph.get(node, ())))

    def _step(self, node, successors):
        for successor in successors:
            if successor not in self.index_of:
                return self._enter(successor)
            if successor in self.on_stack:
                self.low[node] = min(self.low[node], self.index_of[successor])
        return None

    def _pop_component(self, root) -> list:
        component = []
        while True:
            node = self.stack.pop()
            self.on_stack.discard(node)
            component.append(node)
            if node == root:
                return sorted(component)
