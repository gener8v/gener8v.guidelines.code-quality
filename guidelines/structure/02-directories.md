# 2. Directories

The directory tree is the first map of a codebase that a reader sees. A good tree is grouped by feature, named by category, shallow, and has no junk drawers. A reader can guess where a file is before they search for it.

### 2.1 Keep the repository root clean

**Measure:** `root-files` — warn above 15, fail above 25. `root-source` — fail.

The root holds only what tools expect to find there: manifests, lockfiles, tool configuration, and the standard documents (`README`, `LICENSE`, `CHANGELOG`, `CONTRIBUTING`, `AGENTS.md`). Source code goes into a source directory. The count excludes dotfiles. In a monorepo, the same rule applies to the root of each package (each directory with a manifest).

`root-source` finds a source module at the root. Configuration files that tools require at the root (`vite.config.ts`, `conftest.py`, `manage.py`, `setup.py`) are not findings.

### 2.2 Keep each directory small

**Measure:** `dir-files` — warn above 12, fail above 20. `dir-subdirs` — warn above 12, fail above 20.

`dir-files` counts the source files in one directory. Test files are not counted, because they sit next to their source files (rule 6.1). `dir-subdirs` counts the subdirectories. A directory over the limit holds more than one category. Split it into subdirectories that each name one category.

### 2.3 Keep the directory tree shallow

**Measure:** `dir-depth` — warn above 5, fail above 7.

The check counts directory levels below the nearest package root (the nearest directory with a manifest, or the repository root). A deep tree hides files and makes import paths long. Two levels of grouping (feature, then role) are almost always enough.

### 2.4 Never give a directory or a file a junk-drawer name

**Measure:** `vague-name` — fail.

A name such as `utils`, `helpers`, `common`, or `misc` is a junk drawer. It is not a category. It tells the reader nothing about the code, and it collects code that has no other home.

Each of these names is a finding. None of them is a correct name for a directory or a file:

`utils`, `util`, `helpers`, `helper`, `misc`, `common`, `stuff`, `general`, `other`, `temp`, `tmp`, `new`, `old`

A name that ends in `-old`, `-new`, `-copy`, or a number (`parser2`) is also a finding.

Name a directory for the feature that it holds (`billing`, `search`), or for a real category of code (`parsers`, `migrations`, `http`). A real category tells the reader what each file in it is.

A `.code-quality.json` file can add names to the list with `vague_names`. It cannot remove a name from the list.

Exception: in the route directory of a web framework (`app/`, `pages/`, `routes/`), a directory name is part of a URL and does not group code. There, `new`, `old`, `other`, and `general` are permitted. Example: `app/projects/new/page.tsx` serves the URL `/projects/new`.

Bad: `src/utils/format.ts`, `src/helpers/retry.py`.
Good: `src/currency/format.ts`, `src/http/retry.py`.

### 2.5 Group code by feature, then by role

**Measure:** `package-by-layer` — warn.

Put the code for one feature in one directory. Inside the feature, group by role if the feature is large. A change to one feature then touches one directory.

Bad (packaged by layer):

```
src/controllers/  src/services/  src/repositories/  src/models/
```

Good (packaged by feature):

```
src/billing/   src/accounts/   src/reporting/
```

The check finds a source directory where three or more of the subdirectories are role names (`controllers`, `services`, `models`, `repositories`, `handlers`, `views`).

### 2.6 Do not nest a directory only to hold one directory

**Measure:** `single-child-dir` — warn.

A directory that holds only one subdirectory and no files adds a level and no meaning. Move the content up. Source trees for Java and Kotlin are not findings, because their package paths need these levels.

### 2.7 Give scripts and generated code their own directory

**Measure:** `generated-placement` — warn. `script-placement` — warn.

Generated code goes into a directory named `generated`, `gen`, or `__generated__`. Then nobody edits it by hand and reviewers can skip it. `generated-placement` finds a file with a generated marker (`@generated`, `DO NOT EDIT`, `auto-generated`) in another directory.

Shell scripts go into `scripts/`, `bin/`, or `tools/`. `script-placement` finds a shell script in a source directory.

### 2.8 Use one case convention for directory names

**Measure:** `dir-name-case` — warn.

Directory names are lowercase. A directory that holds Python modules uses `snake_case`, because Python cannot import a name with a hyphen. Other directories use `kebab-case`. Tool directories (`__tests__`, `__fixtures__`, `__mocks__`, `__generated__`), dot directories, and framework route directories (`[id]`, `(group)`, `@slot`) are not findings.
