"""Rule 2.5: a path starts with a domain function. Role and layer names sit only below a domain.

The check finds a role or technical-layer directory at the top of the tree.
"The top" is the first name below the mechanism directories that a build tool
or a language requires: a package root, `src`, `lib`, `app`, `internal`,
`src/main/java`, a chain of directories that hold no code and one
subdirectory each (`com/acme/shop`), and the one Python package in `src`.
"""

from __future__ import annotations

import posixpath

from cq_measure.codebase import (
    CODE_LANGUAGES,
    ROUTE_DIRS,
    has_hidden_part,
    in_script_dir,
    is_framework_file,
    is_generated,
    is_testish,
    language_of,
    nearest_root,
    parts_of,
)

# Role, layer, tier, and technical-capability names. None of them is a domain
# function. A repository can add names with `role_dirs`, but cannot remove these.
ROLE_NAMES = frozenset(
    """
    controllers controller services service models model repositories repository repos handlers handler
    views view viewmodels routes router routers components hooks middleware middlewares types interfaces
    schemas entities dto dtos stores adapters providers validators serializers resolvers mappers parsers
    migrations commands queries jobs workers usecases use_cases use-cases
    domain application infrastructure infra presentation persistence core web ui api frontend backend
    server client
    shared platform data database db logging auth network http cache messaging clients gateways
    """.split()
)
# Directories that a build tool, a language, or a convention requires. They are not names of the design.
CONTAINER_NAMES = frozenset({"src", "lib", "app", "pkg", "internal", "main", "java", "kotlin", "scala", "features", "packages", "apps", "libs"})
# Go puts one directory per program below `cmd/`. Those names are program names.
PROGRAM_DIRS = frozenset({"cmd"})


def check_package_by_layer(workspace, emit) -> None:
    roles = ROLE_NAMES | {name.lower() for name in emit.option("role_dirs", [])}
    for path in sorted(code_directories(workspace)):
        name = posixpath.basename(path)
        if name.lower() not in roles or not at_top(workspace, path) or serves_urls(workspace, path):
            continue
        example = posixpath.join(posixpath.dirname(path), "<domain>", name)
        emit.flag(
            (path, None),
            f"`{name}` is a role or a layer at the top of the tree. Start the path with a domain function, "
            f"and put `{name}/` inside it: `{example}/`.",
        )


def code_directories(workspace) -> set[str]:
    """Return every directory that holds source code, outside tests, scripts, and generated code."""
    found: set[str] = set()
    for source in workspace.sources:
        if source.language not in CODE_LANGUAGES or _excluded(source):
            continue
        directory = source.directory
        while directory and directory not in found:
            found.add(directory)
            directory = posixpath.dirname(directory)
    return found


def _excluded(source) -> bool:
    return has_hidden_part(source.path) or is_testish(source.path) or in_script_dir(source.path) or is_generated(source)


def at_top(workspace, path: str) -> bool:
    """Return True when every directory above `path`, up to its package root, is a mechanism directory."""
    parent = posixpath.dirname(path)
    if any(part in PROGRAM_DIRS for part in parts_of(parent)):
        return False
    root = nearest_root(parent, workspace.package_roots)
    current = root
    for name in parts_of(parent[len(root):].lstrip("/")):
        current = posixpath.join(current, name) if current else name
        if name.lower() not in CONTAINER_NAMES and not _wrapper(workspace, current):
            return False
    return True


def _wrapper(workspace, path: str) -> bool:
    """Return True for a directory that only wraps the design.

    That is the one subdirectory of its parent, when it holds no code (`com` in
    `java/com/acme`), or when it is the Python package of a `src` layout.
    """
    parent = workspace.directories.get(posixpath.dirname(path))
    directory = workspace.directories.get(path)
    if parent is None or directory is None or len(parent.subdirs) != 1:
        return False
    if posixpath.basename(parent.path) == "src" and "__init__.py" in directory.files:
        return True
    return not any(language_of(name) in CODE_LANGUAGES for name in directory.files)


def serves_urls(workspace, path: str) -> bool:
    """Return True for a directory in the route tree of a web framework: its name is a URL segment.

    The path must be at or below `app/`, `pages/`, or `routes/`, and hold a route file such as `page.tsx`.
    """
    if not any(part in ROUTE_DIRS for part in parts_of(path)):
        return False
    prefix = path + "/"
    return any(source.path.startswith(prefix) and is_framework_file(source.path) for source in workspace.sources)
