# 17. Performance

Most code is fast enough. The code that is not fast enough is usually slow for a small number of known reasons. Prevent those reasons, and measure before you optimize anything else.

### 17.1 Measure before you optimize

**Measure:** judged (self-check).

Do not make code more complex for speed without a measurement that shows the problem. Write the measurement in the change description.

### 17.2 Set a limit on everything that can grow

**Measure:** judged (self-check).

Paginate queries. Limit the size of requests and uploads. Put a maximum on batch sizes. Give each cache an eviction rule. A result set with no limit works in the demo and fails in production.

### 17.3 Do not query in a loop

**Measure:** judged (self-check).

Get the records for a list in one query, not one query per item. The "N+1" pattern is the most frequent cause of a slow page.

### 17.4 Look at the complexity when the input has no limit

**Measure:** judged (self-check).

Do not loop over one large input inside a loop over another. Use a map or a set for the lookup.

### 17.5 Do not block an asynchronous runtime

**Measure:** judged (self-check).

Do not call synchronous file, network, or CPU-heavy work inside asynchronous code. One blocked call stops every other request on the same event loop.
