# 12. Errors

An error that nobody sees is worse than a crash. A crash stops. A hidden error writes bad data for weeks. Agents hide errors to make a task "work": an empty `catch`, a default value, a broad fallback. These rules stop that.

### 12.1 Never swallow an error

**Measure:** `swallowed-error` — fail. Test files: warn.

Do not write an empty `catch`, an `except: pass`, or a `.catch(() => {})`. When you catch an error, handle it, or add context and raise it again.

In a test file, an empty `catch` is a warning, not a failure. A test can ignore an error on purpose, for example when the cleanup after a test removes a file that is possibly not there. An empty `catch` in a test can also hide a test failure. Thus, examine each one. If it is intentional, mark it with `cq-ignore swallowed-error: <reason>`.

Bad:

```python
try:
    charge(card, amount)
except Exception:
    pass
```

Good:

```python
try:
    charge(card, amount)
except CardDeclined as declined:
    raise PaymentFailed(f"charge of {amount} cents declined") from declined
```

### 12.2 Catch only the errors that you can handle

**Measure:** judged (self-check).

Catch a specific error type at the place that can do something about it. Do not wrap a whole function in a broad `catch`. An error that you cannot handle goes up to a layer that can.

### 12.3 Do not hide a failure behind a default value

**Measure:** judged (self-check).

`config.get("limits") or {}`, `?? []`, and "return `null` on error" make a failure look like empty data. If the value is required, fail with a clear error. Use a default only when "missing" is a correct, expected state.

### 12.4 Fail closed

**Measure:** judged (self-check).

If an authorization check, a validation, or a limit cannot run, deny the operation. Never fall back to "allowed".

### 12.5 Give each error its context

**Measure:** judged (self-check).

An error message says what operation failed, on which input, and why. Do not include secrets or personal data. Keep the original error as the cause (`raise … from …`, `new Error(msg, { cause })`).

### 12.6 Handle or log an error once

**Measure:** judged (self-check).

Do not log an error and raise it again at each layer. Then one fault makes five log entries. The layer that handles the error logs it.

### 12.7 Set a timeout on each call over the network

**Measure:** judged (self-check).

A call without a timeout can wait forever and hold a connection, a thread, or a lock. Limit retries, use backoff, and retry only operations that are safe to repeat.

### 12.8 Release what you acquire

**Measure:** judged (self-check).

Close files, connections, cursors, and locks with `with`, `using`, `try … finally`, or `defer`. A resource leak is invisible until the system stops under load.
