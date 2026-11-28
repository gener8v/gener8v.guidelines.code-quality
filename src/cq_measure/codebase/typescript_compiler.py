"""Measure TypeScript and JavaScript exactly with the TypeScript compiler.

`measure-typescript.cjs` runs once in Node.js and parses every file with the
`typescript` package of the measured repository. When Node.js or the package
is not available, the result holds the reason, and the caller uses the
approximate measure instead.

Set the environment variable `CQ_TYPESCRIPT` to the path of a `typescript`
package to use that compiler, or to `off` to use the approximate measure.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT = Path(__file__).with_name("measure-typescript.cjs")
TIMEOUT_SECONDS = 600


@dataclass(frozen=True)
class CompilerResult:
    """The compiler measures per file path, or the reason that there are none.

    Each measure is the plain dictionary that `measure-typescript.cjs` writes.
    The functions and classes domains turn them into their own types.
    """

    version: str | None = None
    reason: str = ""
    functions: dict[str, list[dict]] = field(default_factory=dict)
    classes: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def status(self) -> dict:
        """Say how the TypeScript and JavaScript files were measured, for the report."""
        if self.version:
            return {"measured_by": "compiler", "version": self.version}
        return {"measured_by": "approximation", "reason": self.reason}


def measure_with_compiler(root: Path, paths: list[str]) -> CompilerResult:
    """Measure the files (relative to `root`) with the compiler, or return why that was not possible."""
    override = os.environ.get("CQ_TYPESCRIPT", "").strip()
    if override.lower() == "off":
        return CompilerResult(reason="CQ_TYPESCRIPT is off")
    node = shutil.which("node")
    if node is None:
        return CompilerResult(reason="Node.js is not installed")
    request = json.dumps({"root": str(root), "files": paths, "typescript": override or None})
    try:
        completed = subprocess.run(
            [node, str(SCRIPT)], input=request, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return CompilerResult(reason=f"Node.js did not complete: {error}")
    return parse_reply(completed.stdout, completed.stderr)


def parse_reply(stdout: str, stderr: str) -> CompilerResult:
    """Turn the JSON reply of `measure-typescript.cjs` into measures."""
    try:
        reply = json.loads(stdout)
    except json.JSONDecodeError:
        lines = stderr.strip().splitlines()
        return CompilerResult(reason=f"the compiler stopped: {lines[-1] if lines else 'no output'}")
    if "error" in reply:
        return CompilerResult(reason=reply["error"])
    files = reply["files"]
    return CompilerResult(
        version=reply["version"],
        functions={path: measured["functions"] for path, measured in files.items()},
        classes={path: measured["classes"] for path, measured in files.items()},
    )
