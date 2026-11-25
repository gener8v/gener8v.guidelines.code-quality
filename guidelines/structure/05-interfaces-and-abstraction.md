# 5. Interfaces and abstraction

An interface is a promise at a boundary. An abstraction is a name for a pattern that occurs more than once. Each one has a cost: the reader must follow one more step to find the code that runs. Add one only when it pays for that cost.

Agents add abstraction too early more often than too late. These rules work against that.

### 5.1 Define an interface only where it has two implementations

**Measure:** `single-implementation` — warn.

An interface with one implementation is a second name for one class. It doubles the places that a change must touch. Define an interface when two implementations exist, or when a boundary needs a seam: a port to a database, a network service, a clock, or a file system that tests replace with a fake. A fake in a test counts as the second implementation.

The check finds an interface, abstract class, ABC, or Protocol that one class in the repository implements, tests included.

### 5.2 Depend on the interface across a boundary

**Measure:** judged (self-check).

When domain code needs infrastructure (a database, a payment provider), the domain defines the interface that it needs. The infrastructure implements it. The domain imports only the interface. This keeps the dependency pointing inward (rule 3.4), and it gives the tests a seam.

### 5.3 Keep interfaces small

**Measure:** `interface-size` — warn above 7, fail above 12.

The check counts the methods of one interface, abstract class, ABC, or Protocol. A caller must not depend on methods that it does not use. Split a large interface by caller.

### 5.4 Wait for the third use before you abstract

**Measure:** judged (self-check).

Do not write a base class, a factory, a strategy, a plugin system, or a configuration option for a case that does not exist yet. Two similar pieces of code can stay separate. When the third one arrives, the real shape of the abstraction is clear. Code that looks the same but follows different business rules stays separate.

### 5.5 Do not add layers that only pass calls through

**Measure:** `pass-through` — warn.

A class where every method only calls the same method on another object adds a step and no behavior. Remove it and call the target directly. The check finds a Python class with three or more methods where each method only returns a call to a field with the same arguments.

### 5.6 Prefer composition to inheritance

**Measure:** `inheritance-depth` — warn above 2, fail above 3.

The check counts the levels of inheritance inside the repository. Framework base classes count as one level. A deep chain spreads one behavior across many files, and a change to a parent can break every child. Give an object the parts that it needs instead.

### 5.7 Do not mark names as interfaces or implementations

**Measure:** `impl-naming` — warn.

`IInvoiceStore` and `InvoiceStoreImpl` show an interface with one implementation (rule 5.1). Name the interface for the role (`InvoiceStore`), and name each implementation for how it works (`PostgresInvoiceStore`, `InMemoryInvoiceStore`).
