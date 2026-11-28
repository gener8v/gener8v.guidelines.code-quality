# 4. Functions and classes

A function is the smallest unit that a reader must understand in one piece. These limits keep each function small enough to read on one screen and to test with a few cases.

`cq-measure` measures these rules from the syntax tree. For Python, it uses the Python parser. For TypeScript and JavaScript, it uses the TypeScript compiler of the measured repository. If the repository does not have the `typescript` package, the measure for TypeScript and JavaScript is approximate, and the report says so. [`linters/eslint.config.mjs`](../../linters/eslint.config.mjs) and [`linters/ruff.toml`](../../linters/ruff.toml) set the same limits in ESLint and Ruff.

### 4.1 Keep functions short

**Measure:** `function-lines` — warn above 40, fail above 80.

The count is the non-blank lines of the function body. A function longer than 40 lines almost always does more than one job. Extract each step into a function with a name that says what the step does.

### 4.2 Keep nesting shallow

**Measure:** `nesting` — warn above 3, fail above 4.

The check counts nested blocks (`if`, `for`, `while`, `try`, `with`, `switch`) inside one function. Return early for the invalid cases, then write the main path at the lowest indent.

Bad:

```python
def ship(order):
    if order:
        if order.paid:
            if order.items:
                return dispatch(order)
    return None
```

Good:

```python
def ship(order):
    if not order or not order.paid or not order.items:
        return None
    return dispatch(order)
```

### 4.3 Keep each function simple

**Measure:** `complexity` — warn above 10, fail above 15.

The check measures cyclomatic complexity: one, plus one for each branch (`if`, loop, `case`, `catch`, `and`, `or`, ternary). In TypeScript and JavaScript, `??`, each optional chain (`?.`), and each default value are also branches, as in the ESLint `complexity` rule. Each branch is a path that a test must cover.

### 4.4 Limit the number of parameters

**Measure:** `params` — warn above 4, fail above 6.

`self` and `cls` are not counted. A long parameter list is hard to call correctly, and two arguments of the same type are easy to swap. Group related parameters into one named object.

### 4.5 Do not use a boolean parameter to switch behavior

**Measure:** `flag-param` — warn.

`render(true)` does not tell the reader what `true` does. Write two functions, or pass a named option. The check finds a Python parameter with a `bool` type or a `True` or `False` default.

Bad: `export_report(report, True)`
Good: `export_report_as_pdf(report)`

### 4.6 Keep classes small

**Measure:** `class-methods` — warn above 15, fail above 25.

A class with many methods holds many responsibilities. Split it along the groups of fields that the methods use.

### 4.7 Give each function one job

**Measure:** judged (self-check).

If you need the word "and" to say what a function does, split it. A function either decides or acts: it computes a value, or it does input and output. Keep the computation in pure functions and do the input and output at the edges.
