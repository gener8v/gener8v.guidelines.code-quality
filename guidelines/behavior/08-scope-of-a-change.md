# 8. Scope of a change

A change does what the task asks and nothing more. A small change is easy to review, easy to test, and easy to revert. Agents widen changes without being asked: they rename, reformat, and "improve" code that the task did not touch. These rules stop that.

### 8.1 Change only the code that the task needs

**Measure:** judged (self-check).

Do not refactor, rename, reformat, or "improve" code outside the task. If you find a problem outside the task, report it. Do not fix it in the same change. Unrelated edits hide the real change from the reviewer and add risk that nobody asked for.

### 8.2 Do not reformat lines that you do not change

**Measure:** judged (self-check).

A one-line fix must not come with a 400-line formatting diff. If the project enforces a formatter, run it on the files that you changed. Do not reformat other files. Do not change the formatter configuration as part of an unrelated task.

### 8.3 Keep public interfaces stable

**Measure:** judged (self-check).

Do not change a public function signature, an API response, a CLI flag, a configuration key, an event shape, or a database column unless the task asks for it. If the task needs the change, update every caller in the same change and list them.

### 8.4 Stop and ask before the scope grows

**Measure:** judged (self-check).

If the task needs more than you expected, stop and tell the user before you continue. Examples are a migration, a new dependency, a change to a shared module, or a change to a public interface. Give the reason and the size of the extra work.

### 8.5 Give each change one purpose

**Measure:** judged (self-check).

Do not mix a refactor and a change of behavior in one commit. First, do the refactor with no change of behavior, and make sure that the tests still pass. Then make the behavior change. A reviewer can then read each commit for one question.
