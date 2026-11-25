# 7. Duplication and dead code

Copied code drifts: a fix goes into one copy and not the other. Dead code costs reading time and looks like it matters. Agents make both, because writing new code is easier for them than finding and changing old code.

### 7.1 Do not copy blocks of code

**Measure:** `duplicate-block` — warn.

The check finds 8 or more consecutive lines that are the same in two places after whitespace is removed. Blank lines, imports, and lines with only brackets do not count. Before you write a function, search for one that does the same job (rule 9.2). If two copies follow the same rule, extract the rule into one function. If they follow different rules that only look the same today, keep them separate.

### 7.2 Delete files that nothing uses

**Measure:** `orphan-file` — warn.

The check finds a source file that no other file imports, and that is not an entry point, a test, a script, or configuration. Entry points include `main`, `__main__.py`, `index` files, `bin` targets in `package.json`, Python files with an `if __name__ == "__main__"` block, and framework route directories (`app/`, `pages/`, `routes/`). A repository can add entry points in `.code-quality.json`.

### 7.3 Delete unused functions, classes, and exports

**Measure:** `unused-symbol` — warn.

The check finds an exported or top-level name that no other file in the repository mentions. Libraries that publish names for other repositories can list those names in `.code-quality.json`. Git keeps the history. You do not need to keep old code "just in case".

### 7.4 Do not leave commented-out code

**Measure:** `commented-code` — warn.

The check finds three or more consecutive comment lines that look like code. Commented-out code is never run, never tested, and never correct for long. Delete it.
