# 13. Test discipline

A test is proof that the code does what someone says that it does. Agents are under pressure to make the tests pass, and the easiest way to do that is to change the test. These rules keep the proof honest. Rules 6.1 to 6.5 cover where tests are.

### 13.1 Add a test for each new behavior

**Measure:** judged (self-check). Rule 6.4 measures files with no test.

A behavior with no test is a behavior that the next change can break without a warning.

### 13.2 For a bug fix, first write a test that fails

**Measure:** judged (self-check).

Write the test that shows the bug. Run it and see it fail. Then fix the code and see the test pass. A test that you never saw fail can pass for the wrong reason.

### 13.3 Never weaken a test to make it pass

**Measure:** judged (self-check).

Do not delete a test, skip it, loosen an assertion, change an expected value, or increase a timeout to get a green result. If you think that the test is wrong, stop. Tell the user why, and get their agreement before you change it.

### 13.4 Test behavior, not implementation

**Measure:** judged (self-check).

Assert on outputs and on effects that a caller can see, through the public interface. Do not assert on private methods, internal state, or the order of internal calls. A test that knows the implementation breaks at each refactor and proves nothing about behavior.

### 13.5 Replace only the boundaries with fakes

**Measure:** judged (self-check).

Fake the network, the clock, the file system, and third-party services. Do not mock the code under test or its collaborators inside the same package. A test that only asserts that a mock was called proves that the mock works.

### 13.6 Make each test deterministic

**Measure:** judged (self-check).

No `sleep`, no real clock, no random values without a fixed seed, no network, no dependency on the order of tests, and no shared state between tests. A test that fails one time in fifty teaches the team to ignore failures.

### 13.7 Name each test for the behavior that it proves

**Measure:** judged (self-check).

`rejects_an_expired_token`, not `test_auth_2`. When the test fails, its name tells the reader what is broken.

### 13.8 Test the edges

**Measure:** judged (self-check).

Test the empty case, one item, many items, the values at each limit, invalid input, and the error path. Faults collect at the edges, and the main path is the one that already works.
