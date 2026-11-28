# cq-ignore one-concept: Check, Rule, and Section are one data model for the rule files.
"""Build AGENTS.md and the rules index of the Claude Code skill from guidelines/.

The rule files in guidelines/ are the source of truth. This script:

- reads every section and rule, with its Measure line;
- makes sure that rule numbers, check IDs, severities, and thresholds agree
  with src/cq_measure/configuration/defaults.json;
- writes AGENTS.md and the index block in skills/rules/SKILL.md.

Run it with --check in CI. Then it changes nothing, and it exits 1 when a
generated file is out of date or the guidelines and the defaults disagree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDELINES = REPO_ROOT / "guidelines"
PARTS = (("structure", "Part A: Structure"), ("behavior", "Part B: Behavior"))
DEFAULTS = REPO_ROOT / "src" / "cq_measure" / "configuration" / "defaults.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
SKILL_MD = REPO_ROOT / "skills" / "rules" / "SKILL.md"
BLOB_URL = "https://github.com/gener8v/gener8v.guidelines.code-quality/blob/main/"
START, END = "<!-- rules:start -->", "<!-- rules:end -->"

SECTION_RE = re.compile(r"^# (\d+)\. (.+)$")
RULE_RE = re.compile(r"^### (\d+)\.(\d+) (.+)$")
MEASURE_RE = re.compile(r"^\*\*Measure:\*\* (.+)$")
CHECK_RE = re.compile(r"`([a-z][a-z-]+)` — (warn|fail)(?: above (\d+), fail above (\d+))?")
TEST_RE = re.compile(r"Test files: warn above (\d+), fail above (\d+)")
TEST_SEVERITY_RE = re.compile(r"Test files: (warn|fail)\.")


@dataclass
class Check:
    check_id: str
    severity: str
    warn: int | None = None
    fail: int | None = None
    test_warn: int | None = None
    test_fail: int | None = None
    test_severity: str | None = None


@dataclass
class Rule:
    number: str
    title: str
    measure: str = ""
    checks: list[Check] = field(default_factory=list)


@dataclass
class Section:
    number: int
    title: str
    path: Path
    rules: list[Rule] = field(default_factory=list)


def parse_measure(text: str) -> list[Check]:
    checks = []
    for match in CHECK_RE.finditer(text):
        check_id, severity, warn, fail = match.groups()
        check = Check(check_id, severity)
        if warn is not None:
            check.severity, check.warn, check.fail = "threshold", int(warn), int(fail)
        checks.append(check)
    test = TEST_RE.search(text)
    if test and checks:
        checks[0].test_warn, checks[0].test_fail = int(test.group(1)), int(test.group(2))
    test_severity = TEST_SEVERITY_RE.search(text)
    if test_severity and checks:
        checks[0].test_severity = test_severity.group(1)
    return checks


def read_line(section: Section, line: str, path: Path, errors: list[str]) -> None:
    rule = RULE_RE.match(line)
    if rule:
        section_no, rule_no, title = rule.groups()
        expected = len(section.rules) + 1
        if int(section_no) != section.number or int(rule_no) != expected:
            errors.append(f"{path.name}: rule {section_no}.{rule_no} must be {section.number}.{expected}")
        section.rules.append(Rule(f"{section_no}.{rule_no}", title))
        return
    measure = MEASURE_RE.match(line)
    if measure and section.rules:
        section.rules[-1].measure = measure.group(1)
        section.rules[-1].checks = parse_measure(measure.group(1))


def parse_section(path: Path, errors: list[str]) -> Section | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = SECTION_RE.match(lines[0]) if lines else None
    if not heading:
        errors.append(f"{path.name}: the first line must be '# N. Title'")
        return None
    section = Section(int(heading.group(1)), heading.group(2), path)
    for line in lines[1:]:
        read_line(section, line, path, errors)
    for rule in section.rules:
        if not rule.measure:
            errors.append(f"{path.name}: rule {rule.number} has no **Measure:** line")
    return section


def load_sections(errors: list[str]) -> list[tuple[str, list[Section]]]:
    parts, expected = [], 1
    for directory, label in PARTS:
        sections = []
        for path in sorted((GUIDELINES / directory).glob("*.md")):
            section = parse_section(path, errors)
            if section is None:
                continue
            if section.number != expected:
                errors.append(f"{path.name}: section {section.number} must be {expected}")
            expected = section.number + 1
            sections.append(section)
        parts.append((label, sections))
    return parts


def compare_check(rule: Rule, check: Check, spec: dict, errors: list[str]) -> None:
    where = f"rule {rule.number} `{check.check_id}`"
    if spec.get("rule") != rule.number:
        errors.append(f"{where}: defaults.json maps it to rule {spec.get('rule')}")
    if check.severity == "threshold":
        pairs = (("warn", check.warn), ("fail", check.fail),
                 ("test_warn", check.test_warn), ("test_fail", check.test_fail))
        for key, value in pairs:
            if value is not None and spec.get(key) != value:
                errors.append(f"{where}: {key} is {value} in the guideline, {spec.get(key)} in defaults.json")
    elif spec.get("severity") != check.severity:
        errors.append(f"{where}: severity is {check.severity} in the guideline, {spec.get('severity')} in defaults.json")
    if spec.get("test_severity") != check.test_severity:
        errors.append(f"{where}: test-file severity is {check.test_severity} in the guideline, {spec.get('test_severity')} in defaults.json")


def all_rules(parts: list[tuple[str, list[Section]]]):
    for _, sections in parts:
        for section in sections:
            yield from section.rules


def compare_defaults(parts: list[tuple[str, list[Section]]], defaults: dict, errors: list[str]) -> None:
    specs = defaults.get("checks", {})
    seen = set()
    for rule in all_rules(parts):
        for check in rule.checks:
            if check.check_id in seen:
                errors.append(f"`{check.check_id}` is named by more than one rule")
            seen.add(check.check_id)
            if check.check_id not in specs:
                errors.append(f"rule {rule.number}: `{check.check_id}` is not in defaults.json")
                continue
            compare_check(rule, check, specs[check.check_id], errors)
    for check_id, spec in specs.items():
        if spec.get("rule") is not None and check_id not in seen:
            errors.append(f"defaults.json: `{check_id}` (rule {spec['rule']}) is not named in any guideline")


def describe_measure(rule: Rule) -> str:
    if not rule.checks:
        return "judged"
    texts = []
    for check in rule.checks:
        if check.severity == "threshold":
            text = f"`{check.check_id}` warn > {check.warn}, fail > {check.fail}"
        else:
            text = f"`{check.check_id}` {check.severity}"
        if check.test_severity:
            text += f" ({check.test_severity} in test files)"
        texts.append(text)
    return "; ".join(texts)


def render_index(parts: list[tuple[str, list[Section]]], link) -> str:
    out = []
    for label, sections in parts:
        out.append(f"## {label}\n")
        for section in sections:
            out.append(f"### {section.number}. {section.title} ([full text]({link(section.path)}))\n")
            for rule in section.rules:
                out.append(f"- **{rule.number}** {rule.title}. *{describe_measure(rule)}*")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


AGENTS_HEADER = """# Code-quality rules for coding agents

<!-- Generated by scripts/build_index.py from guidelines/. Do not edit by hand. -->

These rules come from [gener8v.guidelines.code-quality](https://github.com/gener8v/gener8v.guidelines.code-quality). Copy this file into a repository as `AGENTS.md`, or add its content to `CLAUDE.md`. Each line links to the full rule, with its reason and examples.

How to apply the rules:

1. Obey each rule when you write, change, or review code.
2. If the instructions of the repository disagree with a rule, obey the repository. Tell the user about the disagreement.
3. Before you write code in a section, read the full text of that section.
4. When a rule changes what you do, cite its number, for example "rule 6.1".
5. Before you say that the work is done, run `cq-measure` and correct its findings in the code that you changed.

Run the measuring tool with no installation:

```
uvx --from git+https://github.com/gener8v/gener8v.guidelines.code-quality cq-measure .
```

The text after each rule shows how it is measured. A check ID with `warn` and `fail` limits is measured by `cq-measure`. A rule marked *judged* needs a review by a person or an agent.

"""


def build_outputs(parts: list[tuple[str, list[Section]]]) -> dict[Path, str]:
    agents = AGENTS_HEADER + render_index(parts, lambda p: BLOB_URL + p.relative_to(REPO_ROOT).as_posix())
    skill_index = render_index(parts, lambda p: "../../" + p.relative_to(REPO_ROOT).as_posix())
    skill = SKILL_MD.read_text(encoding="utf-8")
    head, rest = skill.split(START, 1)
    _, tail = rest.split(END, 1)
    return {AGENTS_MD: agents, SKILL_MD: f"{head}{START}\n{skill_index}{END}{tail}"}


def write_outputs(parts: list[tuple[str, list[Section]]], *, dry_run: bool) -> list[str]:
    stale = []
    for path, content in build_outputs(parts).items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == content:
            continue
        stale.append(path.relative_to(REPO_ROOT).as_posix())
        if not dry_run:
            path.write_text(content, encoding="utf-8")
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="change nothing; exit 1 if out of date")
    args = parser.parse_args(argv)
    errors: list[str] = []
    parts = load_sections(errors)
    compare_defaults(parts, json.loads(DEFAULTS.read_text(encoding="utf-8")), errors)
    stale = write_outputs(parts, dry_run=args.check)
    if args.check and stale:
        errors.append(f"out of date: {', '.join(stale)}. Run python3 scripts/build_index.py")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    rules = sum(1 for _ in all_rules(parts))
    print(f"{rules} rules in {sum(len(s) for _, s in parts)} sections")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
