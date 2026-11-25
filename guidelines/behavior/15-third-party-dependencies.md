# 15. Third-party dependencies

Each dependency is code that you did not write, cannot review fully, and must update for as long as the project lives. Agents add packages freely, and sometimes they add packages that do not exist.

### 15.1 Prefer the standard library and the dependencies that you already have

**Measure:** judged (self-check).

Before you add a package, look for the function in the standard library and in the existing dependencies.

### 15.2 Get approval for each new dependency

**Measure:** judged (self-check).

Before you add a dependency, tell the user what it does that the existing code cannot do. Also give its maintenance state, its license, and its size. Add it only after the user agrees.

### 15.3 Make sure that the package is the real one

**Measure:** judged (self-check).

Find the exact package name in the registry before you install it. Make sure that it has the expected publisher, a history, and real use. Models invent plausible package names, and attackers register those names with harmful code.

### 15.4 Use the package manager of the project, and commit the lockfile

**Measure:** judged (self-check).

Add dependencies with the package manager that the project already uses. Do not edit a lockfile by hand. Do not add a second package manager.

### 15.5 Do not copy library code into the project

**Measure:** judged (self-check).

If you must copy code from a library, make sure that its license permits it. Then record the source, the version, and the license beside the copy.
