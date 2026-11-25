// Run with `node --test`. Set CQ_TYPESCRIPT to the path of a `typescript`
// package, or install `typescript` where Node.js can find it from here.
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { FileMeasurer, loadTypescript } = require("./measure-typescript.cjs");

function compiler() {
  try {
    return loadTypescript(process.cwd(), [], process.env.CQ_TYPESCRIPT || null);
  } catch {
    return null; // The tests skip when no compiler is installed.
  }
}

const ts = compiler();
const skip = ts ? false : "the typescript package is not installed";

function measure(text, file = "a.tsx") {
  return new FileMeasurer(ts, text, file).measure();
}

function byName(functions) {
  return Object.fromEntries(functions.map((fn) => [fn.name, fn]));
}

const ROUTE = `function route(req, res = {}) {
  if (req.a && req.b) {
    for (const x of req.items) {
      try {
        if (x) { send(x); } else if (x === 0) { skip(x ?? 0); } else { other(x?.y); }
      } catch (e) {
        res.fail(e ? 1 : 2);
      }
    }
  }
  const inner = () => { if (a || b) { return 1; } };
  switch (req.kind) { case 1: break; case 2: break; default: break; }
}
`;

test("measures lines, nesting, complexity, and parameters of a function", { skip }, () => {
  const { route, inner } = byName(measure(ROUTE).functions);
  assert.deepEqual(
    { lines: route.lines, nesting: route.nesting, complexity: route.complexity, params: route.params },
    { lines: 11, nesting: 4, complexity: 13, params: 2 },
  );
  assert.deepEqual({ complexity: inner.complexity, nesting: inner.nesting }, { complexity: 3, nesting: 1 });
});

test("counts a braceless block and keeps an else-if at the depth of its if", { skip }, () => {
  const source = "function f(xs) {\n  for (const x of xs)\n    if (x) g();\n    else if (h) k();\n}\n";
  assert.equal(measure(source).functions[0].nesting, 2);
});

test("does not count a nested function in the outer function", { skip }, () => {
  const { functions } = measure("const make = (a = 1) => () => (a ? 1 : 2);\n");
  assert.deepEqual(functions.map((fn) => [fn.name, fn.complexity]), [["make", 2], ["<anonymous>", 2]]);
});

test("names anonymous functions for the place that holds them", { skip }, () => {
  const source = [
    "describe('x', () => { it('y', () => {}); });",
    "describe.each([1])('z', () => {});",
    "items.map((x) => x);",
    "exports.total = function () { return 1; };",
    "const el = <a onClick={() => go()} />;",
    "const o = { load: async () => 1 };",
  ].join("\n");
  const names = measure(source).functions.map((fn) => fn.name);
  assert.deepEqual(names, [
    "describe callback", "it callback", "describe.each callback", "items.map callback", "total", "onClick", "load",
  ]);
});

test("leaves out `this`, overloads, and type signatures", { skip }, () => {
  const source = [
    "function on(this: Window, e: Event): void;",
    "function on(this: Window, e: Event) { return e; }",
    "type Handler = (a: number, b: number) => void;",
    "interface Port { send(a: string): void; cb: (x: number) => void }",
  ].join("\n");
  const { functions } = measure(source, "a.ts");
  assert.deepEqual(functions.map((fn) => [fn.name, fn.params]), [["on", 1]]);
});

test("describes classes and interfaces", { skip }, () => {
  const source = [
    "abstract class Repo extends base.Store implements Reader, Writer<T> {",
    "  constructor() { super(); }",
    "  get(key) { return key; }",
    "  handle = (e) => e;",
    "  name = 'repo';",
    "  abstract save(item): void;",
    "}",
    "interface Reader extends Base { read(): string; size: number }",
  ].join("\n");
  const [repo, reader] = measure(source, "a.ts").classes;
  assert.deepEqual(repo, {
    name: "Repo", line: 1, kind: "abstract", bases: ["Store"], implements: ["Reader", "Writer"],
    methods: ["constructor", "get", "handle", "save"],
  });
  assert.deepEqual(reader, { name: "Reader", line: 8, kind: "interface", bases: ["Base"], implements: [], methods: ["read"] });
});

test("refuses a typescript package without the compiler API, such as TypeScript 7", () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "cq-ts7-"));
  fs.mkdirSync(path.join(directory, "lib"));
  fs.writeFileSync(path.join(directory, "package.json"), JSON.stringify({ exports: { ".": "./lib/version.cjs" } }));
  fs.writeFileSync(path.join(directory, "lib", "version.cjs"), "module.exports = { version: '7.0.2' };");
  try {
    assert.throws(() => loadTypescript(directory, [], directory), /typescript 7\.0\.2 has no compiler API/);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("reports a clear error when typescript cannot be found", () => {
  assert.throws(() => loadTypescript(path.parse(process.cwd()).root, [], null), /not installed/);
});
