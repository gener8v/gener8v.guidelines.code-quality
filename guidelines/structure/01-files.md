# 1. Files

A file is the unit that a reader opens, a reviewer reads, and a search returns. A good file is short, holds one concept, and has a name that says what is in it.

### 1.1 Keep each source file short

**Measure:** `file-lines` — warn above 300, fail above 500. Test files: warn above 500, fail above 800.

The count is non-blank lines. A long file almost always holds more than one concept, and a reader cannot keep it in mind. When a file gets near the limit, split it along its concepts. Do not split it at an arbitrary line.

### 1.2 Put one concept in each file

**Measure:** `one-concept` — warn.

The check counts public top-level classes (Python), and exported classes or React components (TypeScript and JavaScript). More than one is a finding. Small private helpers that serve the one concept can stay in the file.

Bad: `models.py` with `Invoice`, `Customer`, `Payment`, and `Refund`.
Good: `invoice.py`, `customer.py`, `payment.py`, `refund.py` in a `billing/` directory.

### 1.3 Name the file for its primary concept

**Measure:** `name-matches-export` — warn.

When a file holds one class or one component, the file name matches it. The check ignores case and separators, so `invoice_service.py` matches `InvoiceService`, and `invoice-list.tsx` matches `InvoiceList`. A reader who knows the class name can find the file without a search.

### 1.4 Name files by category with one role suffix per role

**Measure:** `role-suffix` — warn.

When a file has a role (repository, service, controller, handler, schema, store, hook), put the role at the end of the name. Use one spelling and one separator for each role in the whole repository.

Bad: `user.service.ts`, `orderService.ts`, `payment-svc.ts`.
Good: `user.service.ts`, `order.service.ts`, `payment.service.ts`.

The check finds a role that appears with more than one separator style or with an abbreviation (`svc`, `repo`, `ctrl`).

### 1.5 Use one case convention for file names in each language

**Measure:** `file-name-case` — warn.

The defaults follow the convention of each language:

| Language | File names |
|---|---|
| Python, Go, Rust, Ruby | `snake_case` |
| TypeScript, JavaScript | `kebab-case` |
| TSX, JSX | `kebab-case` or `PascalCase`, one of the two for the whole repository |
| Java, Kotlin, C#, Swift | `PascalCase` |

The check ignores the role and test parts of a name (`.service`, `.test`, `test_`), and standard names such as `README.md`, `Dockerfile`, `__init__.py`, and `index.ts`. A repository can change the convention in `.code-quality.json`.
