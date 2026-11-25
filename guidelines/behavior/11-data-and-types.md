# 11. Data and types

Most faults start with data that is not what the code expects. Make sure that data is correct at the edge of the system, then let the types carry that guarantee inward.

### 11.1 Validate input at the boundary

**Measure:** judged (self-check).

Parse and validate data where it enters the system: an HTTP request, a file, a queue message, an environment variable, a database row from a schema that you do not own, or the output of a model. Inside the system, trust the type. Do not validate the same value again in each function.

### 11.2 Make invalid states impossible to represent

**Measure:** judged (self-check).

Use enums and tagged unions instead of free strings and sets of booleans.

Bad:

```ts
type Load = { isLoading: boolean; isError: boolean; data?: Invoice[]; error?: string };
```

Good:

```ts
type Load =
  | { state: "loading" }
  | { state: "failed"; error: string }
  | { state: "loaded"; invoices: Invoice[] };
```

The bad form permits `isLoading` and `isError` at the same time. The good form does not.

### 11.3 Do not escape the type system

**Measure:** `type-escape` — warn.

Do not use `any`, `as any`, `@ts-ignore`, `# type: ignore`, or an unchecked cast to make a type error go away. The error usually shows a real fault. If a cast is necessary, write a comment that says why it is safe.

### 11.4 Name your constants

**Measure:** judged (self-check).

Do not put unexplained numbers or strings in logic. Write `MAX_UPLOAD_BYTES = 10 * 1024 * 1024`, not `10485760`. A named constant says what the value means, and it has one place to change.

### 11.5 Prefer immutable data

**Measure:** judged (self-check).

Do not change an argument that a caller gave you. Return a new value. Use `const`, `readonly`, frozen dataclasses, and tuples. Code that changes shared data is hard to test and hard to run in parallel.

### 11.6 Use the correct type for money, time, and identifiers

**Measure:** judged (self-check).

Store money as integer minor units or as a decimal type, never as a float. Store timestamps in UTC with the time zone attached. Treat identifiers as opaque strings, not as numbers for arithmetic.
