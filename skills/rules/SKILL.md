---
name: rules
description: "The gener8v code-quality rules for writing and changing code: file size and file naming, directory and package structure, root files, dependency direction and import cycles, function and class size, interfaces and abstraction, test placement next to the tested file, duplication and dead code, scope of a change, errors, test discipline, comments, third-party dependencies, security hygiene, performance and the proof before 'done'. Use before you write, edit, refactor or fix code in any language, or when asked where a file or a test belongs, how to name or split a module, or whether an interface or abstraction is justified. Not for checking finished work (self-check)."
---

# Code-quality rules

Obey these rules each time that you write or change code. Part A (structure) controls where code goes and how large it gets. Part B (behavior) controls how you work on a change.

## How to use the rules

1. Before you edit, read the index at the end of this file.
2. For each section that your change touches, read the full section file. The paths are relative to the directory of this skill.
3. If the instructions of the repository disagree with a rule, obey the repository. Examples are `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the linter configuration, and `.code-quality.json`. Tell the user about the disagreement.
4. When a rule stops you or changes what you do, cite its number, for example "rule 6.1".
5. If a rule needs work outside the task, report it. Do not do the work (rule 8.1). Example: an existing directory that is over the limit.
6. Before you say that the work is done, use the `self-check` skill.

## Where new code goes

Use these questions in this sequence when you add a file:

1. Which feature does the code belong to? Put it in the directory of that feature (rule 2.5). If no feature directory fits, make one with a feature name. Never use a junk-drawer name such as `utils`, `helpers`, `common`, or `misc`. These names are not categories (rule 2.4).
2. Does a file for this concept exist? Add to it while it stays under the size limit (rule 1.1) and holds one concept (rule 1.2).
3. If you make a new file, name it for its concept in the case convention of the language (rules 1.3 and 1.5). Add the role suffix that the repository uses for its role (rule 1.4).
4. Put its unit test next to it, named for it (rules 6.1 and 6.2).
5. Import other packages only through their entry point (rule 3.2). Keep imports pointing inward (rule 3.4).

## Rules index

<!-- rules:start -->
## Part A: Structure

### 1. Files ([full text](../../guidelines/structure/01-files.md))

- **1.1** Keep each source file short. *`file-lines` warn > 300, fail > 500*
- **1.2** Put one concept in each file. *`one-concept` warn*
- **1.3** Name the file for its primary concept. *`name-matches-export` warn*
- **1.4** Name files by category with one role suffix per role. *`role-suffix` warn*
- **1.5** Use one case convention for file names in each language. *`file-name-case` warn*

### 2. Directories ([full text](../../guidelines/structure/02-directories.md))

- **2.1** Keep the repository root clean. *`root-files` warn > 15, fail > 25; `root-source` fail*
- **2.2** Keep each directory small. *`dir-files` warn > 12, fail > 20; `dir-subdirs` warn > 12, fail > 20*
- **2.3** Keep the directory tree shallow. *`dir-depth` warn > 5, fail > 7*
- **2.4** Never give a directory or a file a junk-drawer name. *`vague-name` fail*
- **2.5** Group code by feature, then by role. *`package-by-layer` warn*
- **2.6** Do not nest a directory only to hold one directory. *`single-child-dir` warn*
- **2.7** Give scripts and generated code their own directory. *`generated-placement` warn; `script-placement` warn*
- **2.8** Use one case convention for directory names. *`dir-name-case` warn*

### 3. Packages and the dependencies between them ([full text](../../guidelines/structure/03-packages.md))

- **3.1** Give each package one public entry point. *judged*
- **3.2** Do not import the internals of another package. *`deep-import` fail*
- **3.3** Do not climb more than two levels in a relative import. *`relative-climb` warn > 2, fail > 3*
- **3.4** Keep dependencies pointing inward. *`layer-direction` fail*
- **3.5** Do not make import cycles. *`import-cycle` fail; `file-cycle` warn*
- **3.6** Limit the number of internal imports in one file. *`fan-out` warn > 12, fail > 20*
- **3.7** Name a package for the feature or concept that it holds. *judged*

### 4. Functions and classes ([full text](../../guidelines/structure/04-functions-and-classes.md))

- **4.1** Keep functions short. *`function-lines` warn > 40, fail > 80*
- **4.2** Keep nesting shallow. *`nesting` warn > 3, fail > 4*
- **4.3** Keep each function simple. *`complexity` warn > 10, fail > 15*
- **4.4** Limit the number of parameters. *`params` warn > 4, fail > 6*
- **4.5** Do not use a boolean parameter to switch behavior. *`flag-param` warn*
- **4.6** Keep classes small. *`class-methods` warn > 15, fail > 25*
- **4.7** Give each function one job. *judged*

### 5. Interfaces and abstraction ([full text](../../guidelines/structure/05-interfaces-and-abstraction.md))

- **5.1** Define an interface only where it has two implementations. *`single-implementation` warn*
- **5.2** Depend on the interface across a boundary. *judged*
- **5.3** Keep interfaces small. *`interface-size` warn > 7, fail > 12*
- **5.4** Wait for the third use before you abstract. *judged*
- **5.5** Do not add layers that only pass calls through. *`pass-through` warn*
- **5.6** Prefer composition to inheritance. *`inheritance-depth` warn > 2, fail > 3*
- **5.7** Do not mark names as interfaces or implementations. *`impl-naming` warn*

### 6. Test placement ([full text](../../guidelines/structure/06-test-placement.md))

- **6.1** Put each unit test next to the file that it tests. *`test-colocation` fail*
- **6.2** Name a test file for the file that it tests. *`test-name` warn*
- **6.3** Keep only cross-cutting tests in a top-level test directory. *judged*
- **6.4** Give each source file that holds logic a test. *`untested-file` warn*
- **6.5** Keep test data next to the tests that use it. *judged*

### 7. Duplication and dead code ([full text](../../guidelines/structure/07-duplication-and-dead-code.md))

- **7.1** Do not copy blocks of code. *`duplicate-block` warn*
- **7.2** Delete files that nothing uses. *`orphan-file` warn*
- **7.3** Delete unused functions, classes, and exports. *`unused-symbol` warn*
- **7.4** Do not leave commented-out code. *`commented-code` warn*

## Part B: Behavior

### 8. Scope of a change ([full text](../../guidelines/behavior/08-scope-of-a-change.md))

- **8.1** Change only the code that the task needs. *judged*
- **8.2** Do not reformat lines that you do not change. *judged*
- **8.3** Keep public interfaces stable. *judged*
- **8.4** Stop and ask before the scope grows. *judged*
- **8.5** Give each change one purpose. *judged*

### 9. Read before you write ([full text](../../guidelines/behavior/09-read-before-you-write.md))

- **9.1** Read the code around the change before you edit it. *judged*
- **9.2** Reuse what the codebase already has. *judged*
- **9.3** Follow the conventions of the codebase. *judged*
- **9.4** Use only APIs that exist in the version that the project uses. *judged*
- **9.5** Find the cause before you fix the symptom. *judged*

### 10. Names in code ([full text](../../guidelines/behavior/10-names-in-code.md))

- **10.1** Name a thing for what it is or what it does. *judged*
- **10.2** Use the words of the business domain. *judged*
- **10.3** Give each concept one name. *judged*
- **10.4** Put units and formats in names. *judged*
- **10.5** Name a boolean as a statement that is true or false. *judged*
- **10.6** Do not abbreviate. *judged*

### 11. Data and types ([full text](../../guidelines/behavior/11-data-and-types.md))

- **11.1** Validate input at the boundary. *judged*
- **11.2** Make invalid states impossible to represent. *judged*
- **11.3** Do not escape the type system. *`type-escape` warn*
- **11.4** Name your constants. *judged*
- **11.5** Prefer immutable data. *judged*
- **11.6** Use the correct type for money, time, and identifiers. *judged*

### 12. Errors ([full text](../../guidelines/behavior/12-errors.md))

- **12.1** Never swallow an error. *`swallowed-error` fail (warn in test files)*
- **12.2** Catch only the errors that you can handle. *judged*
- **12.3** Do not hide a failure behind a default value. *judged*
- **12.4** Fail closed. *judged*
- **12.5** Give each error its context. *judged*
- **12.6** Handle or log an error once. *judged*
- **12.7** Set a timeout on each call over the network. *judged*
- **12.8** Release what you acquire. *judged*

### 13. Test discipline ([full text](../../guidelines/behavior/13-test-discipline.md))

- **13.1** Add a test for each new behavior. *judged*
- **13.2** For a bug fix, first write a test that fails. *judged*
- **13.3** Never weaken a test to make it pass. *judged*
- **13.4** Test behavior, not implementation. *judged*
- **13.5** Replace only the boundaries with fakes. *judged*
- **13.6** Make each test deterministic. *judged*
- **13.7** Name each test for the behavior that it proves. *judged*
- **13.8** Test the edges. *judged*

### 14. Comments and documents ([full text](../../guidelines/behavior/14-comments-and-docs.md))

- **14.1** Write comments that explain why. *judged*
- **14.2** Do not tell the story of the change in comments. *judged*
- **14.3** Keep comments true. *judged*
- **14.4** Link each TODO to an issue. *`todo-without-issue` warn*
- **14.5** Update the documents that the change makes wrong. *judged*
- **14.6** Do not write chat text into code. *judged*

### 15. Third-party dependencies ([full text](../../guidelines/behavior/15-third-party-dependencies.md))

- **15.1** Prefer the standard library and the dependencies that you already have. *judged*
- **15.2** Get approval for each new dependency. *judged*
- **15.3** Make sure that the package is the real one. *judged*
- **15.4** Use the package manager of the project, and commit the lockfile. *judged*
- **15.5** Do not copy library code into the project. *judged*

### 16. Security hygiene ([full text](../../guidelines/behavior/16-security-hygiene.md))

- **16.1** Never put a secret in code, tests, logs, or commits. *`secret-literal` fail*
- **16.2** Use parameters for queries and commands. *judged*
- **16.3** Do not run input as code. *judged*
- **16.4** Check authorization on the server for each request. *judged*
- **16.5** Log events, not sensitive data. *judged*
- **16.6** Treat the output of a model as untrusted input. *judged*

### 17. Performance ([full text](../../guidelines/behavior/17-performance.md))

- **17.1** Measure before you optimize. *judged*
- **17.2** Set a limit on everything that can grow. *judged*
- **17.3** Do not query in a loop. *judged*
- **17.4** Look at the complexity when the input has no limit. *judged*
- **17.5** Do not block an asynchronous runtime. *judged*

### 18. Before you say "done" ([full text](../../guidelines/behavior/18-before-you-say-done.md))

- **18.1** Run the checks of the project. *judged*
- **18.2** Report exactly what you ran and what happened. *judged*
- **18.3** Read your own diff. *judged*
- **18.4** Remove debug output. *`debug-output` warn*
- **18.5** Say what is not finished. *judged*
- **18.6** Use the code that you changed. *judged*
<!-- rules:end -->
