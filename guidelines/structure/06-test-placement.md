# 6. Test placement

A test next to its subject is easy to find, easy to keep current, and moves with the file when the file moves. A missing test is visible in the directory listing. These rules are about where tests are. Rules 13.1 to 13.8 are about what tests do.

### 6.1 Put each unit test next to the file that it tests

**Measure:** `test-colocation` — fail.

| Language | Source | Test |
|---|---|---|
| TypeScript, JavaScript | `invoice.ts` | `invoice.test.ts` (or `.spec.ts`) in the same directory |
| Python | `invoice.py` | `invoice_test.py` or `test_invoice.py` in the same directory |
| Go | `invoice.go` | `invoice_test.go` in the same directory |
| Java, Kotlin | `src/main/java/…/Invoice.java` | `src/test/java/…/InvoiceTest.java`, the same package path |

The check finds a unit test whose subject is in a different directory: for example, `tests/billing/test_invoice.py` for `src/billing/invoice.py`. Java and Kotlin use the mirror path that their build tools require. Rule 6.3 gives the exceptions.

### 6.2 Name a test file for the file that it tests

**Measure:** `test-name` — warn.

The check finds a test file with no source file of the matching name in the same directory. `invoice_test.py` tests `invoice.py`. A test file named `test_misc.py` or `helpers.test.ts` tests nothing in particular, and nobody knows when to run it.

### 6.3 Keep only cross-cutting tests in a top-level test directory

**Measure:** judged (self-check).

End-to-end, integration, contract, smoke, load, and performance tests use many files together, so they have no single subject. Put them in a top-level directory with a category name: `tests/e2e/`, `tests/integration/`. The checks for rules 6.1 and 6.2 ignore directories with these names. A repository can add names in `.code-quality.json`.

### 6.4 Give each source file that holds logic a test

**Measure:** `untested-file` — warn.

The check finds a source file with functions or classes and no test next to it. Files that only declare (types, constants, `index` and `__init__` files, configuration, generated code) are not findings.

### 6.5 Keep test data next to the tests that use it

**Measure:** judged (self-check).

Put fixtures that one test file uses in a `testdata/` or `__fixtures__/` directory next to that test. Keep fixtures small and readable. Make each fixture show the case that the test proves. Do not copy production data into fixtures.
