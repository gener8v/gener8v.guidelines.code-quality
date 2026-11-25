# 9. Read before you write

An agent can write a plausible function faster than it can find the one that already exists. As a result, codebases fill with second copies, invented APIs, and fixes for symptoms. Read first.

### 9.1 Read the code around the change before you edit it

**Measure:** judged (self-check).

Read the file, its callers, and its tests. Know what the code does now before you change what it does. A change made without its context usually breaks a caller that you did not read.

### 9.2 Reuse what the codebase already has

**Measure:** judged (self-check). Rule 7.1 measures copied blocks.

Before you write a function, a type, or a component, search for one that does the same job. Search by behavior, not only by name. Two helpers that do the same job drift apart, and the next bug gets fixed in one of them only.

### 9.3 Follow the conventions of the codebase

**Measure:** judged (self-check).

Match the existing style for names, file layout, error handling, logging, and tests. Consistency is worth more than your preference. If a convention is harmful, report it. Do not start a second convention beside it.

### 9.4 Use only APIs that exist in the version that the project uses

**Measure:** judged (self-check).

Make sure that each function, method, flag, and option exists in the installed version. Read the version in the lockfile. Then read the library source or the documentation for that version. Do not write a call from memory. A call that does not exist fails at run time, and sometimes only on the path that nobody tested.

### 9.5 Find the cause before you fix the symptom

**Measure:** judged (self-check).

Reproduce the fault. Find why it occurs. Fix the cause. A fix that only suppresses the symptom moves the fault somewhere else.

Bad: add `?.` at each place where a value was `undefined`.
Good: find why the value is `undefined`, and correct the code that produced it.
