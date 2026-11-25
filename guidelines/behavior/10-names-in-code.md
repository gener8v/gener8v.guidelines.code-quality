# 10. Names in code

A name is the shortest piece of documentation and the one that a reader sees most often. Rules 1.3 to 1.5 and 2.4 cover the names of files and directories. These rules cover the names of variables, functions, types, and fields.

### 10.1 Name a thing for what it is or what it does

**Measure:** judged (self-check).

`invoiceTotal`, `retryDelayMs`, `isExpired`, `sendReminder`. Not `data`, `info`, `result2`, `temp`, `obj`, `handle`, or `process`. If you cannot find a clear name, the thing probably does more than one job.

### 10.2 Use the words of the business domain

**Measure:** judged (self-check).

If the business says "policy holder", the code says `policyHolder`, not `customer` or `user`. Then the people who own the rules and the people who own the code use the same words.

### 10.3 Give each concept one name

**Measure:** judged (self-check).

Do not call the same thing `account` in one file and `profile` in another. Do not use one name for two different things. A reader who sees two names assumes that there are two concepts.

### 10.4 Put units and formats in names

**Measure:** judged (self-check).

`timeoutMs`, `priceCents`, `createdAtUtc`, `sizeBytes`, `ratePercent`. A number without a unit causes errors that no type checker finds.

### 10.5 Name a boolean as a statement that is true or false

**Measure:** judged (self-check).

`isActive`, `hasAccess`, `canRetry`. Not `flag`, `status`, or `check`. A reader can then read `if (canRetry)` as a sentence.

### 10.6 Do not abbreviate

**Measure:** judged (self-check).

Write `customer`, not `cust`. Write `message`, not `msg`. Abbreviations that the whole industry uses (`id`, `url`, `http`, `db`) are permitted. One saved keystroke costs every future reader a guess.
