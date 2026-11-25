---
name: self-check
description: "Measure and review a code change against the gener8v code-quality rules before you call it done: run cq-measure on the repository, keep the findings in the changed files, review the judged rules against the diff, correct the findings inside the task's scope, and report each result with its rule number. Also audits a whole repository's structure on request. Use before you report a coding task as done, before a commit or a pull request, or when asked to 'check this against the quality rules', 'measure the repo' or 'audit the structure'. Not for a gener8v pipeline ticket review (gener8v:quality-review)."
---

# Self-check

Measure the change, review what the tool cannot measure, correct what is yours to correct, and report the rest. The rules are in the `rules` skill and in `../../guidelines/` relative to the directory of this skill.

## 1. Find the change

1. Find the base branch: `git symbolic-ref --short refs/remotes/origin/HEAD`, with the `origin/` prefix removed. If there is no remote, use `main`.
2. List the changed files: `git diff --name-only <base>...HEAD` and `git status --porcelain`.
3. If the user asked for an audit of the whole repository, skip this step and measure everything.

## 2. Run the measuring tool

The plugin root is two directories above the directory of this skill. Run from the root of the repository that you measure:

```
PYTHONPATH="<plugin-root>/src" python3 -m cq_measure . --changed-since <base> --format json
```

- For an audit of the whole repository, remove `--changed-since <base>`.
- If `python3` is older than 3.10, run `uvx --from git+https://github.com/gener8v/gener8v.guidelines.code-quality cq-measure .` with the same options.
- `--changed-since` measures the whole repository, because import cycles and orphan files need the full graph. It reports only the findings in the changed files.
- If `summary.typescript.measured_by` is `approximation`, the function measures of TypeScript and JavaScript are approximate. Give the reason in your report.

Also run the checks of the project: formatter, linter, type checker, and tests (rule 18.1).

## 3. Review the judged rules

Read the full diff. For each changed hunk, answer these questions. Each question names its rules.

| Question | Rules |
|---|---|
| Does the diff change only what the task needs, with no reformatting and no change to public interfaces? | 8.1–8.5 |
| Did a function, type, or component that does this job exist already? | 9.2, 7.1 |
| Does each new call exist in the installed version of its library? | 9.4 |
| Is there a new interface, base class, factory, or option with one user? | 5.1, 5.4 |
| Does domain code depend on an interface, not on infrastructure? | 3.4, 5.2 |
| Do the names say what each thing is, with units, in the words of the domain? | 10.1–10.6 |
| Is input validated where it enters, and is each failure visible? | 11.1, 12.1–12.5 |
| Do the tests prove behavior, and did you weaken a test? | 13.1–13.8 |
| Do the comments explain why, with no story of the edit? | 14.1–14.6 |
| Is there a new dependency without the user's approval? | 15.1–15.5 |
| Are queries parameterized and authorization checked on the server? | 16.2–16.6 |
| Is there a query in a loop, or a result with no limit? | 17.2–17.4 |

## 4. Correct or report

- **A finding in lines that you changed:** correct it. Then run the tool again.
- **A finding in code that you did not change:** report it. Do not correct it (rule 8.1).
- **A structural finding that needs files to move:** for example a directory over its limit, a cycle between packages, or tests in a separate tree. Report it with a proposed plan. Do not move files without the user's approval (rule 8.4).
- **A finding that you think is wrong:** do not suppress it without a reason. If the user agrees, add `cq-ignore <check-id>: <reason>` on the line, or on one of the first five lines for the whole file.

## 5. Report

Report the results in this format:

```
Measured: cq-measure (base origin/main): 0 fail, 3 warn in changed files
Project checks: npm test, passed (212 tests). npm run lint, passed. tsc --noEmit, passed.

| Rule | Where | Finding | Action |
|------|-------|---------|--------|
| 1.1  | src/billing/invoice.ts | 341 lines; warn above 300 | Corrected: split out invoice-totals.ts |
| 6.1  | tests/billing/test_refund.py | Test is not next to src/billing/refund.py | Reported: existing layout |
| 13.3 | src/accounts/login.test.ts | — | No test weakened |
```

Name each command that you did not run, and give the reason (rule 18.2). Put each open gap at the top (rule 18.5).

For an audit of the whole repository, group the findings by section. Give the counts for each check and the ten worst files. Then propose an ordered plan. Make no edits until the user approves the plan.
