# 16. Security hygiene

These rules are the minimum for each change. They do not replace a security review. For a full review, use the [OWASP Top 10](https://owasp.org/Top10/), and the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) for code that calls a model.

### 16.1 Never put a secret in code, tests, logs, or commits

**Measure:** `secret-literal` — fail.

Read secrets from the environment or from a secret manager. If a secret gets into a commit, it is exposed. Rotate it. Removing it from the history does not make it safe again.

### 16.2 Use parameters for queries and commands

**Measure:** judged (self-check).

Do not build SQL, shell commands, or HTML from strings that contain input. Use parameterized queries, argument lists, and templates that escape their values.

Bad: `db.query("SELECT * FROM users WHERE email = '" + email + "'")`
Good: `db.query("SELECT * FROM users WHERE email = $1", [email])`

### 16.3 Do not run input as code

**Measure:** judged (self-check).

Do not use `eval`, `exec`, `pickle.loads`, unsafe YAML loaders, or dynamic `require` and `import` on data that a user or an external system can control.

### 16.4 Check authorization on the server for each request

**Measure:** judged (self-check).

Make sure that this user can do this operation on this object. Do not trust the client to hide what a user cannot do. An identifier in a URL is input, not proof of ownership.

### 16.5 Log events, not sensitive data

**Measure:** judged (self-check).

Do not write passwords, tokens, full card numbers, or personal data to logs. Log an identifier that lets an operator find the record.

### 16.6 Treat the output of a model as untrusted input

**Measure:** judged (self-check).

Validate the output of a language model before you act on it, as you validate any user input (rule 11.1). Do not let model output choose a file path, a query, a command, or a URL without a check against a list of permitted values.
