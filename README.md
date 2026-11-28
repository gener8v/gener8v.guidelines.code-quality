# gener8v code-quality rules for agents

Coding agents write code faster than people can review it. This repository gives an agent the rules for where code goes, how large it gets, and how to work on a change, and it gives the agent a tool that measures those rules.

- **[The rules](guidelines/README.md):** 18 sections in two parts, each rule with a number, a measure, and the reason.
- **[`AGENTS.md`](AGENTS.md):** the index of all rules in one file, to copy into a repository.
- **`cq-measure`:** a command-line tool that measures a repository against the rules. It has no dependencies, and it exits with code 1 on a `fail` finding so that CI can use it.
- **A Claude Code plugin:** two skills. `rules` applies before the agent writes code, and `self-check` applies before the agent says "done".

## What the rules cover

**Part A: Structure.** Most of these rules have a measure.

| Section | Examples of measures (warn / fail) |
|---|---|
| 1. Files | File length (300 / 500 lines), one concept per file, the file name matches the class, one role suffix per role, one case convention per language |
| 2. Directories | Root files (15 / 25), source files per directory (12 / 20), depth (5 / 7), no `utils` or `helpers`, paths that start with a domain function |
| 3. Packages | No deep imports, relative climbs (2 / 3), dependencies point inward, no import cycles, fan-out (12 / 20) |
| 4. Functions and classes | Function length (40 / 80), nesting (3 / 4), complexity (10 / 15), parameters (4 / 6), methods per class (15 / 25) |
| 5. Interfaces and abstraction | Interfaces with one implementation, interface size (7 / 12), pass-through layers, inheritance depth (2 / 3) |
| 6. Test placement | Unit tests next to the tested file, test files named for their subject, files with no test |
| 7. Duplication and dead code | Copied blocks, orphan files, unused names, commented-out code |

**Part B: Behavior.** Most of these rules need judgment: scope of a change, read before you write, names in code, data and types, errors, test discipline, comments, third-party dependencies, security hygiene, performance, and the proof before "done". Five of them have a measure: type escapes, swallowed errors, TODOs without an issue, secrets in code, and debug output.

## Use with any agent

Copy [`AGENTS.md`](AGENTS.md) into the root of your repository. Codex, Cursor, Copilot, Gemini CLI, and other agents that read `AGENTS.md` load it. For Claude Code, add it to `CLAUDE.md`, or install the plugin.

Measure a repository with no installation (Python 3.10 or later):

```
uvx --from git+https://github.com/gener8v/gener8v.guidelines.code-quality cq-measure .
```

Useful options:

| Option | Effect |
|---|---|
| `--changed-since origin/main` | Measures the whole repository, and reports only findings in the changed files |
| `--format json` | Gives JSON for an agent or a script |
| `--fail-on warn` | Exits with code 1 on a `warn` finding too |
| `--only file-lines,import-cycle` | Runs only the named checks |
| `--list-checks` | Lists each check with its rule and limits |

### TypeScript and JavaScript

`cq-measure` measures TypeScript and JavaScript functions and classes with the TypeScript compiler. It uses the `typescript` package that the measured repository has installed, and it needs Node.js. The complexity is the same value that the ESLint `complexity` rule gives.

The package must be TypeScript 5 or 6. TypeScript 7 has no compiler API that `cq-measure` can use. For a repository on TypeScript 7, install `typescript@6` in a different directory and set `CQ_TYPESCRIPT` to its path.

If Node.js or the `typescript` package is not available, `cq-measure` approximates these measures, and the last line of its report says so. To use a different `typescript` package, set `CQ_TYPESCRIPT` to its path. To use the approximation, set `CQ_TYPESCRIPT=off`.

## Use with Claude Code

```
/plugin marketplace add gener8v/gener8v.guidelines.code-quality
/plugin install code-quality@gener8v-code-quality
```

| Skill | When it loads |
|---|---|
| `code-quality:rules` | Before the agent writes, edits, refactors, or fixes code. It gives the rules index and the questions for where new code goes. |
| `code-quality:self-check` | Before the agent says that a task is done. It runs `cq-measure` on the changed files, reviews the judged rules against the diff, corrects findings in the agent's own lines, and reports the rest with rule numbers. |

## Change the limits for a repository

Put a `.code-quality.json` file at the root of the repository that you measure. It merges over the defaults in [`src/cq_measure/configuration/defaults.json`](src/cq_measure/configuration/defaults.json):

```json
{
  "checks": {
    "file-lines": { "warn": 400, "fail": 600 },
    "orphan-file": { "enabled": false }
  },
  "ignore": ["legacy/**"],
  "layers": { "inner": ["domain"], "outer": ["infrastructure", "api"] }
}
```

To accept one finding, add a comment with a reason: `cq-ignore file-lines: generated parser table`. On a line, the comment applies to that line. On one of the first five lines of a file, it applies to the whole file.

## Linter configuration

[`linters/eslint.config.mjs`](linters/eslint.config.mjs) and [`linters/ruff.toml`](linters/ruff.toml) set the limits of section 4 in ESLint and Ruff, for feedback in the editor.

## Repository layout

```
guidelines/structure/   Part A, sections 1 to 7 (source of truth)
guidelines/behavior/    Part B, sections 8 to 18 (source of truth)
src/cq_measure/         the measuring tool, with each test next to its module
skills/                 the Claude Code skills: rules, self-check
linters/                ESLint and Ruff configuration for section 4
scripts/build_index.py  writes AGENTS.md and the skill index from guidelines/
```

The measuring tool has one directory for each area of the rules: `files/`, `directories/`, `dependencies/`, `functions/`, `classes/`, `interfaces/`, `test_placement/`, `duplication/`, and `behavior/`. Each holds one module for each check, named for the check. `codebase/` reads the measured repository: its files, languages, and syntax. `configuration/` and `reporting/` hold the settings and the report. `testing/` holds the test fixtures.

`scripts/build_index.py --check` runs in CI. It fails when a rule, its check, and its limits in `defaults.json` do not agree, or when `AGENTS.md` is out of date. The repository is measured by its own tool in CI.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. Read [LICENSE](LICENSE).
