# The rules

There are 18 sections in two parts. Each rule has a number, a short statement, a **Measure** line, and the reason for the rule.

## Part A: Structure

These rules control where code goes and how large it gets. Most of them have a measure that `cq-measure` reports.

| Section | Rules |
|---|---|
| [1. Files](structure/01-files.md) | Size, one concept per file, names that match the concept, role suffixes, case conventions |
| [2. Directories](structure/02-directories.md) | A clean root, small directories, a shallow tree, no junk drawers, paths that start with a domain function |
| [3. Packages](structure/03-packages.md) | Entry points, no deep imports, dependency direction, no cycles, limited fan-out |
| [4. Functions and classes](structure/04-functions-and-classes.md) | Length, nesting, complexity, parameters, class size |
| [5. Interfaces and abstraction](structure/05-interfaces-and-abstraction.md) | When an interface or an abstraction pays for itself |
| [6. Test placement](structure/06-test-placement.md) | Unit tests next to the files that they test |
| [7. Duplication and dead code](structure/07-duplication-and-dead-code.md) | Copied blocks, orphan files, unused names, commented-out code |

## Part B: Behavior

These rules control how an agent works on a change. Most of them need judgment. The `self-check` skill turns them into review questions.

| Section | Rules |
|---|---|
| [8. Scope of a change](behavior/08-scope-of-a-change.md) | Change only what the task needs |
| [9. Read before you write](behavior/09-read-before-you-write.md) | Reuse, conventions, real APIs, causes before symptoms |
| [10. Names in code](behavior/10-names-in-code.md) | Clear names, domain words, units |
| [11. Data and types](behavior/11-data-and-types.md) | Validation at the boundary, types that forbid invalid states |
| [12. Errors](behavior/12-errors.md) | No swallowed errors, no hidden failures, fail closed |
| [13. Test discipline](behavior/13-test-discipline.md) | Honest tests that prove behavior |
| [14. Comments and documents](behavior/14-comments-and-docs.md) | Comments that explain why |
| [15. Third-party dependencies](behavior/15-third-party-dependencies.md) | Few, approved, real packages |
| [16. Security hygiene](behavior/16-security-hygiene.md) | The minimum for each change |
| [17. Performance](behavior/17-performance.md) | Limits, no queries in loops |
| [18. Before you say "done"](behavior/18-before-you-say-done.md) | Proof, not claims |

## How to read a rule

```
### 1.1 Keep each source file short

**Measure:** `file-lines` — warn above 300, fail above 500.
```

- **The number** (`1.1`) is the section and the position. Cite it in reviews and commit messages.
- **The statement** is the instruction.
- **The Measure line** names the `cq-measure` check and its limits. A rule marked *judged* has no automatic measure. A person or an agent reviews it.
- **The text** after the Measure line gives the reason and, where it helps, a bad and a good example.

A `fail` finding makes `cq-measure` exit with code 1. A `warn` finding does not. A repository can change each limit, or turn off a check, in `.code-quality.json` at its root.

## Sources

The rules are our own. These sources agree with them on what to measure:

- ISO/IEC 5055:2021, *Automated Source Code Quality Measures* ([CISQ](https://www.it-cisq.org/standards/code-quality-standards/)). It measures reliability, performance efficiency, security, and maintainability from the internal structure of the code. It lists high cyclomatic complexity, duplicated code, and excessive component size among the maintainability weaknesses.
- ISO/IEC 25010, the product quality model that ISO/IEC 5055 measures a part of.
- [IBM: What is code quality?](https://www.ibm.com/think/topics/code-quality) It recommends a style guide as context for an AI coding assistant, "or even as part of your AI agent's system prompt."
- [AWS: What is code quality?](https://aws.amazon.com/what-is/code-quality/)
