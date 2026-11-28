# 2. Directories

The directory tree is the first map of a codebase that a reader sees. In a good tree, each path starts with a domain function and narrows from there. The tree is shallow and has no junk drawers. A reader can guess where a file is before they search for it.

### 2.1 Keep the repository root clean

**Measure:** `root-files` — warn above 15, fail above 25. `root-source` — fail.

The root holds only what tools expect to find there: manifests, lockfiles, tool configuration, and the standard documents (`README`, `LICENSE`, `CHANGELOG`, `CONTRIBUTING`, `AGENTS.md`). Source code goes into a source directory. The count excludes dotfiles. In a monorepo, the same rule applies to the root of each package (each directory with a manifest).

`root-source` finds a source module at the root. Configuration files that tools require at the root (`vite.config.ts`, `conftest.py`, `manage.py`, `setup.py`) are not findings.

### 2.2 Keep each directory small

**Measure:** `dir-files` — warn above 12, fail above 20. `dir-subdirs` — warn above 12, fail above 20.

`dir-files` counts the source files in one directory. Test files are not counted, because they sit next to their source files (rule 6.1). `dir-subdirs` counts the subdirectories. A directory over the limit holds more than one category. Split it into subdirectories that each name one category.

### 2.3 Keep the directory tree shallow

**Measure:** `dir-depth` — warn above 5, fail above 7.

The check counts directory levels below the nearest package root (the nearest directory with a manifest, or the repository root). A deep tree hides files and makes import paths long. A domain function, one or two subdomains, and then a role are almost always enough: `accounting/disputes/routes/`.

### 2.4 Never give a directory or a file a junk-drawer name

**Measure:** `vague-name` — fail.

A name such as `utils`, `helpers`, `common`, or `misc` is a junk drawer. It is not a category. It tells the reader nothing about the code, and it collects code that has no other home.

Each of these names is a finding. None of them is a correct name for a directory or a file:

`utils`, `util`, `helpers`, `helper`, `misc`, `common`, `stuff`, `general`, `other`, `temp`, `tmp`, `new`, `old`

A name that ends in `-old`, `-new`, `-copy`, or a number (`parser2`) is also a finding.

Name a directory for the domain function that it holds, or for a part of that function: `accounting`, `accounting/disputes`. Rule 2.5 gives the full order of a path.

A `.code-quality.json` file can add names to the list with `vague_names`. It cannot remove a name from the list.

Exception: in the route directory of a web framework (`app/`, `pages/`, `routes/`), a directory name is part of a URL and does not group code. There, `new`, `old`, `other`, and `general` are permitted. Example: `app/projects/new/page.tsx` serves the URL `/projects/new`.

Bad: `src/utils/format.ts`, `src/helpers/retry.py`.
Good: `src/billing/invoices/format.ts`, `src/shipping/carriers/retry.py`.

### 2.5 Start each path with a domain function, then narrow it

**Measure:** `package-by-layer` — fail.

A directory path is a sequence from general to specific. It starts with a domain function: the part of the business that the code serves, such as `accounting`, `billing`, or `fleet`. Each level below it narrows the function: `accounting/disputes/`, `accounting/discrepancies/`. A reader who knows the business can find code from its path. A change to one function stays in one subtree.

A role or a layer is not a domain function. Put a role directory (`services`, `controllers`, `routes`, `models`, `components`) only inside a domain directory, at the end of the path. Shared technical code (`logging`, `auth`, `database`, `network`) also goes inside the domain that owns it, or into a domain that the business can name.

Bad (packaged by layer):

```
src/controllers/  src/services/  src/routes/  src/models/  src/logging/
```

Good (domain first, role last):

```
src/accounting/disputes/routes/
src/accounting/disputes/services/
src/accounting/discrepancies/
src/billing/
```

The guidance of the large ecosystems has this order:

- Microsoft puts the bounded context first and the layers below it: `Ordering.API`, `Ordering.Domain`, `Ordering.Infrastructure` ([DDD-oriented microservice](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice)). Its namespace pattern is `<Company>.<Product>.<Feature>.<Subnamespace>` ([Names of Namespaces](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-namespaces)).
- Spring Boot puts `customer` and `order` directly below the application package. The role is in the class name: `CustomerController`, `CustomerService` ([Structuring Your Code](https://docs.spring.io/spring-boot/reference/using/structuring-your-code.html)).
- Eric Evans: "Choose modules that tell the story of the system" ([DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)).
- Angular: "Avoid creating subdirectories based on the type of code" ([style guide](https://angular.dev/style-guide)).

A framework default that puts layers first is also a finding. Examples are Rails `app/models` and `app/controllers`, and a .NET solution with `Domain`, `Application`, `Infrastructure`, and `Web` projects. To keep such a default, turn the check off in `.code-quality.json`. Then the decision is visible.

The check finds a role, layer, tier, or technical name at the top of a path. The top is the first name below the package root and the directories that a build tool requires: `src`, `lib`, `app`, `internal`, `src/main/java`, and a chain of single subdirectories such as `com/acme/shop`. The list of names is in [`package_by_layer.py`](../../src/cq_measure/directories/package_by_layer.py). A `.code-quality.json` file can add names with `role_dirs`. It cannot remove names. The route directories of a web framework (`app/api/route.ts`) are URL segments, so they are not findings. Rules 2.7 and 6.3 control the directories for scripts, generated code, and tests.

### 2.6 Do not nest a directory only to hold one directory

**Measure:** `single-child-dir` — warn.

A directory that holds only one subdirectory and no files adds a level and no meaning. Move the content up. Source trees for Java and Kotlin are not findings, because their package paths need these levels.

### 2.7 Give scripts and generated code their own directory

**Measure:** `generated-placement` — warn. `script-placement` — warn.

Generated code goes into a directory named `generated`, `gen`, or `__generated__`. Then nobody edits it by hand and reviewers can skip it. `generated-placement` finds a file with a generated marker (`@generated`, `DO NOT EDIT`, `auto-generated`) in another directory.

Shell scripts go into `scripts/`, `bin/`, or `tools/`. `script-placement` finds a shell script in a source directory.

### 2.8 Use the case convention of the language for directory names

**Measure:** `dir-name-case` — warn.

The case of a directory name follows the language of the files in it, because the directory name is often part of a namespace or an import path:

| Files in the directory | Case | Example |
|---|---|---|
| C# | PascalCase, with dots between namespace parts. The directory matches the namespace (.NET rule IDE0130). | `Ordering.Domain` |
| Java, Kotlin, Go | One lowercase word, with no separators. Java package names and Go package names have no separators. | `customer`, `userstore` |
| Python, Rust | `snake_case`. Python cannot import a name with a hyphen. | `order_lines` |
| Ruby | `snake_case` or `kebab-case` | `order_lines` |
| Other languages, or no files | `kebab-case` | `order-lines` |

Sources: [IDE0130](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/ide0130), [Naming a Package](https://docs.oracle.com/javase/tutorial/java/package/namingpkgs.html), [Go package names](https://go.dev/blog/package-names). Tool directories (`__tests__`, `__fixtures__`, `__mocks__`, `__generated__`), dot directories, and framework route directories (`[id]`, `(group)`, `@slot`) are not findings.
