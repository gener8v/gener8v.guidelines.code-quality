# 3. Packages and the dependencies between them

A package is a directory that other code uses as one unit. Its boundary is the place where you can change the inside without a change to the outside. These rules keep the boundaries real: each package has one public entry, the dependencies point one way, and nothing makes a cycle.

### 3.1 Give each package one public entry point

**Measure:** judged (self-check). Rule 3.2 measures the effect.

Export the public names of a package from one file: `index.ts` in TypeScript and JavaScript, `__init__.py` in Python. Other packages import from that file only. Everything that the entry point does not export is internal, and you can change it freely.

### 3.2 Do not import the internals of another package

**Measure:** `deep-import` — fail.

TypeScript and JavaScript: the check finds an import of a file inside a directory that has an `index` file, from code outside that directory, when the import does not go through the `index` file. Python: the check finds an import of a module or name with a leading underscore from outside its package.

Bad: `import { roundCents } from "../billing/internal/rounding";`
Good: `import { roundCents } from "../billing";`

### 3.3 Do not climb more than two levels in a relative import

**Measure:** `relative-climb` — warn above 2, fail above 3.

`../../../shared/thing` couples a file to the shape of the tree, and it breaks when either file moves. A long climb usually means that the import crosses a package boundary. Use the package entry point, or a path alias that the project already configures. In Python, `from ... import` (three dots) is a climb of two levels.

### 3.4 Keep dependencies pointing inward

**Measure:** `layer-direction` — fail.

Domain code holds the business rules. It does not import the database, the HTTP framework, the UI, or a vendor SDK. Infrastructure imports the domain, never the reverse. Then you can test the rules without infrastructure, and replace infrastructure without a change to the rules.

The default layers are:

| Layer | Directory names |
|---|---|
| Inner | `domain`, `core`, `model`, `models`, `entities` |
| Outer | `infrastructure`, `infra`, `adapters`, `db`, `persistence`, `api`, `http`, `web`, `ui`, `cli` |

A file below an inner directory must not import a file below an outer directory. A repository can set its own layers in `.code-quality.json`.

### 3.5 Do not make import cycles

**Measure:** `import-cycle` — fail. `file-cycle` — warn.

`import-cycle` finds a cycle between directories: `billing` imports `accounts`, and `accounts` imports `billing`. Two packages in a cycle are one package with two names. You cannot understand, test, or release one without the other. Break the cycle: move the shared concept into its own package, or reverse one dependency with an interface (rule 5.2).

`file-cycle` finds a cycle between files in the same directory.

### 3.6 Limit the number of internal imports in one file

**Measure:** `fan-out` — warn above 12, fail above 20.

The check counts the distinct files in the repository that one file imports. A file that imports many others knows too much and changes whenever any of them change. It usually does more than one job (rule 4.7).

### 3.7 Name a package for the feature or concept that it holds

**Measure:** judged (self-check).

`billing`, `search`, `notifications`. Not `core2`, `stuff`, or `services`. Use the words of the business domain. Use one form, singular or plural, for all package names in the repository.
