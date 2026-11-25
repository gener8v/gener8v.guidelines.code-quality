# 14. Comments and documents

The code tells the reader what it does. A comment tells the reader why it does it. Agents write the opposite: comments that repeat the code, or that tell the story of the edit. Rule 7.4 covers commented-out code.

### 14.1 Write comments that explain why

**Measure:** judged (self-check).

Use a comment for the reason, the limit, or the hazard that the code cannot show. Examples: a rule from a regulation, a known fault in a library, or a decision that looks wrong but is correct.

Bad: `// increment the counter`
Good: `// The vendor API counts from 1, not 0.`

### 14.2 Do not tell the story of the change in comments

**Measure:** judged (self-check).

Do not write `// changed to use the new client`, `// fixed the bug`, `// new implementation`, or `// as requested`. The commit message holds the history of a change. The comment describes the code as it is.

### 14.3 Keep comments true

**Measure:** judged (self-check).

When you change code, update or delete each comment that the change makes wrong. A wrong comment is worse than no comment, because the reader trusts it.

### 14.4 Link each TODO to an issue

**Measure:** `todo-without-issue` — warn.

Write `TODO(#123): …` or put a link to the issue. A TODO without an issue has no owner and no date, and nobody does it.

### 14.5 Update the documents that the change makes wrong

**Measure:** judged (self-check).

If the change affects the README, the API reference, the configuration reference, the setup steps, or the changelog, update them in the same change.

### 14.6 Do not write chat text into code

**Measure:** judged (self-check).

No apologies, no "Here is the updated function", no notes to the user, and no emoji in log messages. Source files are for the people who maintain the code, not for the conversation that produced it.
