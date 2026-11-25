# 18. Before you say "done"

"Done" is a claim that another person will act on. They merge it, deploy it, and build on it. Agents say "done" when the code is written, not when it is proven. These rules make "done" mean proven.

### 18.1 Run the checks of the project

**Measure:** judged (self-check).

Run the formatter, the linter, the type checker, the tests, and `cq-measure`: the same checks that CI runs. Correct each finding in the code that you changed.

### 18.2 Report exactly what you ran and what happened

**Measure:** judged (self-check).

Name each command and give its result. If you did not run a check, say so and give the reason. Never write "this should work" or "the tests pass" about something that you did not run.

### 18.3 Read your own diff

**Measure:** judged (self-check).

Before you finish, read the full diff as a reviewer will. Look for debug output, unrelated edits, stray files, secrets, and comments that tell the story of the change.

### 18.4 Remove debug output

**Measure:** `debug-output` — warn.

Remove `print`, `console.log`, `debugger`, and `breakpoint()` that you added to find a fault. Use the logger of the project for output that must stay.

### 18.5 Say what is not finished

**Measure:** judged (self-check).

If part of the work is incomplete, stubbed, not tested, or only works for the main path, say so plainly at the top of your summary. A known gap that you report is a task. A known gap that you hide is a fault.

### 18.6 Use the code that you changed

**Measure:** judged (self-check).

Tests are not enough for a change to a UI, a CLI, or an API. Start the application and use the changed path one time, as a user does.
