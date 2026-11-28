"""Rule 3.5: no import cycles between directories, and none between files."""

from __future__ import annotations

import posixpath
from collections import defaultdict, deque

from cq_measure.codebase import is_testish, parts_of
from cq_measure.structure.dependencies.graph import strongly_connected


def sibling_pair(source_dir: str, target_dir: str) -> tuple[str, str] | None:
    """Lift an edge between two directories to the two sibling directories under their common parent."""
    source_parts, target_parts = parts_of(source_dir), parts_of(target_dir)
    shared = 0
    while shared < min(len(source_parts), len(target_parts)) and source_parts[shared] == target_parts[shared]:
        shared += 1
    if shared in (len(source_parts), len(target_parts)):
        return None
    return "/".join(source_parts[: shared + 1]), "/".join(target_parts[: shared + 1])


def shortest_cycle(graph: dict, component: list) -> list:
    """Return a shortest cycle through the first node of a strongly connected component."""
    start = component[0]
    members = set(component)
    previous = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for successor in sorted(graph.get(node, ())):
            if successor == start:
                return _path_to(previous, node) + [start]
            if successor in members and successor not in previous:
                previous[successor] = node
                queue.append(successor)
    return component + [start]


def _path_to(previous: dict, node) -> list:
    path = []
    while node is not None:
        path.append(node)
        node = previous[node]
    return path[::-1]


def _report(emit, graph: dict, describe) -> None:
    for component in strongly_connected(graph):
        if len(component) < 2:
            continue
        cycle = shortest_cycle(graph, component)
        emit.flag(graph[cycle[0]][cycle[1]], describe(cycle))


def runtime_edges(workspace):
    """Yield (importer, target, record) for imports that are not type-only and not made by tests."""
    for path, targets in sorted(workspace.graph.edges.items()):
        if is_testish(path):
            continue
        for target, record in sorted(targets.items()):
            if not record.type_only:
                yield path, target, record


def check_import_cycle(workspace, emit) -> None:
    graph: dict = defaultdict(dict)
    for path, target, record in runtime_edges(workspace):
        pair = sibling_pair(posixpath.dirname(path), posixpath.dirname(target))
        if pair:
            graph[pair[0]].setdefault(pair[1], (path, record.line))
    _report(emit, graph, lambda cycle: (
        f"Directories import each other: {' -> '.join(cycle)}. "
        "Move the shared concept into its own package, or reverse one dependency with an interface."
    ))


def check_file_cycle(workspace, emit) -> None:
    graph: dict = defaultdict(dict)
    for path, target, record in runtime_edges(workspace):
        if posixpath.dirname(path) == posixpath.dirname(target):
            graph[path].setdefault(target, (path, record.line))
    _report(emit, graph, lambda cycle: (
        f"Files import each other: {' -> '.join(posixpath.basename(node) for node in cycle)}. "
        "Move the shared part into its own file."
    ))
