// Measure the functions and classes of TypeScript and JavaScript files with the
// TypeScript compiler. cq-measure runs this file with Node.js. It reads
// {"root", "files", "typescript"} as JSON on stdin and writes JSON on stdout.
// Complexity counts what the ESLint `complexity` rule counts: branches, loops,
// cases, catches, logical operators, optional chains, and default values.
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ANONYMOUS = "<anonymous>";
const LOGICAL_OPERATORS = new Set(["&&", "||", "??", "&&=", "||=", "??="]);
const BRANCH_KINDS = [
  "IfStatement", "ConditionalExpression", "ForStatement", "ForInStatement", "ForOfStatement", "WhileStatement",
  "DoStatement", "CaseClause", "CatchClause",
];
const WRAPPERS = new Set([
  "ParenthesizedExpression", "AsExpression", "SatisfiesExpression", "TypeAssertionExpression", "NonNullExpression",
]);

// Load the compiler from `override`, or from the node_modules of the
// repository root or of the directories that hold the files.
function loadTypescript(root, files, override) {
  if (override) return require(override);
  const directories = [root, ...new Set(files.map((file) => path.dirname(path.join(root, file))))];
  for (const directory of directories.slice(0, 50)) {
    const location = resolveFrom(directory);
    if (location) return require(location);
  }
  throw new Error("the typescript package is not installed in the repository");
}

function resolveFrom(directory) {
  try {
    return require.resolve("typescript", { paths: [directory] });
  } catch {
    return null; // Not installed here is an expected answer; the caller tries the next directory.
  }
}

function scriptKind(ts, file) {
  const extension = path.extname(file).toLowerCase();
  if (extension === ".tsx") return ts.ScriptKind.TSX;
  if (extension === ".jsx") return ts.ScriptKind.JSX;
  if ([".js", ".mjs", ".cjs"].includes(extension)) return ts.ScriptKind.JS;
  return ts.ScriptKind.TS;
}

function isFunction(ts, node) {
  return ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node)
    || ts.isMethodDeclaration(node) || ts.isConstructorDeclaration(node) || ts.isGetAccessorDeclaration(node)
    || ts.isSetAccessorDeclaration(node);
}

function isClass(ts, node) {
  return ts.isClassDeclaration(node) || ts.isClassExpression(node);
}

function isAbstract(ts, node) {
  return (ts.getCombinedModifierFlags(node) & ts.ModifierFlags.Abstract) !== 0;
}

function lineOf(source, position) {
  return source.getLineAndCharacterOfPosition(position).line + 1;
}

// Measure the functions of one file, and collect its classes and interfaces.
class FileMeasurer {
  constructor(ts, text, file) {
    this.ts = ts;
    this.lines = text.split(/\r?\n/);
    this.source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, scriptKind(ts, file));
    this.functions = [];
    this.classes = [];
    this.branchKinds = new Set(BRANCH_KINDS.map((kind) => ts.SyntaxKind[kind]));
  }

  measure() {
    this.visit(this.source);
    return { functions: this.functions, classes: this.classes };
  }

  visit(node) {
    const ts = this.ts;
    if (isFunction(ts, node) && node.body) this.functions.push(this.describeFunction(node));
    if (isClass(ts, node) && node.name) this.classes.push(new ClassDescriber(ts, this.source).describeClass(node));
    if (ts.isInterfaceDeclaration(node)) this.classes.push(new ClassDescriber(ts, this.source).describeInterface(node));
    ts.forEachChild(node, (child) => this.visit(child));
  }

  lineOf(position) {
    return lineOf(this.source, position);
  }

  describeFunction(node) {
    const params = node.parameters.filter((param) => param.name.getText(this.source) !== "this");
    const block = node.body.kind === this.ts.SyntaxKind.Block;
    return {
      name: this.functionName(node),
      line: this.lineOf(node.getStart(this.source)),
      lines: this.bodyLines(node.body),
      nesting: block ? this.nesting(node.body, 0) : 0,
      complexity: 1 + node.parameters.reduce((sum, param) => sum + this.branches(param), 0) + this.branches(node.body),
      params: params.length,
    };
  }

  bodyLines(body) {
    const first = this.lineOf(body.getStart(this.source));
    const last = this.lineOf(body.end);
    if (first === last) return 1;
    const braced = body.kind === this.ts.SyntaxKind.Block || body.kind === this.ts.SyntaxKind.ParenthesizedExpression;
    const lines = braced ? this.lines.slice(first, last - 1) : this.lines.slice(first - 1, last);
    return lines.filter((line) => line.trim()).length;
  }

  functionName(node) {
    if (this.ts.isConstructorDeclaration(node)) return "constructor";
    if (node.name) return node.name.getText(this.source);
    return contextName(this.ts, node, this.source);
  }

  isScope(node) {
    return isFunction(this.ts, node) || isClass(this.ts, node);
  }

  // Count the branches in `node` and its children, but not in nested functions or classes.
  branches(node) {
    if (this.isScope(node)) return 0;
    let total = this.isBranch(node) ? 1 : 0;
    this.ts.forEachChild(node, (child) => {
      total += this.branches(child);
    });
    return total;
  }

  isBranch(node) {
    const ts = this.ts;
    if (this.branchKinds.has(node.kind) || node.questionDotToken) return true;
    if (ts.isBinaryExpression(node)) return LOGICAL_OPERATORS.has(ts.tokenToString(node.operatorToken.kind));
    return Boolean(node.initializer) && (ts.isParameter(node) || ts.isBindingElement(node));
  }

  nesting(node, depth) {
    let deepest = depth;
    this.ts.forEachChild(node, (child) => {
      if (this.isScope(child)) return;
      const inner = this.blockDepth(node, child, depth);
      deepest = Math.max(deepest, this.nesting(child, inner), inner);
    });
    return deepest;
  }

  // Return the depth of `child` inside `parent`: one deeper for the body of a
  // block statement. An `else if` stays at the depth of its `if`.
  blockDepth(parent, child, depth) {
    const ts = this.ts;
    if (ts.isIfStatement(parent)) {
      const sameDepth = child === parent.expression || (child === parent.elseStatement && ts.isIfStatement(child));
      return sameDepth ? depth : depth + 1;
    }
    if (ts.isTryStatement(parent)) return depth + 1;
    return child === this.deeperChild(parent) ? depth + 1 : depth;
  }

  // The body of a loop, a `with`, or a `switch`.
  deeperChild(parent) {
    const ts = this.ts;
    if (ts.isIterationStatement(parent, false) || ts.isWithStatement(parent)) return parent.statement;
    return ts.isSwitchStatement(parent) ? parent.caseBlock : null;
  }
}

// Describe a class or an interface: its bases, and the names of its methods.
class ClassDescriber {
  constructor(ts, source) {
    this.ts = ts;
    this.source = source;
  }

  describeClass(node) {
    const ts = this.ts;
    return {
      name: node.name.text,
      line: lineOf(this.source, node.getStart(this.source)),
      kind: isAbstract(ts, node) ? "abstract" : "class",
      bases: heritage(ts, node, ts.SyntaxKind.ExtendsKeyword).slice(0, 1),
      implements: heritage(ts, node, ts.SyntaxKind.ImplementsKeyword),
      methods: node.members.filter((member) => this.isMethod(member)).map((member) => this.memberName(member)),
    };
  }

  isMethod(member) {
    const ts = this.ts;
    if (ts.isPropertyDeclaration(member)) {
      const value = member.initializer && unwrap(ts, member.initializer);
      return Boolean(value) && (ts.isArrowFunction(value) || ts.isFunctionExpression(value));
    }
    return isFunction(ts, member) && (Boolean(member.body) || isAbstract(ts, member));
  }

  memberName(member) {
    return this.ts.isConstructorDeclaration(member) ? "constructor" : member.name.getText(this.source);
  }

  describeInterface(node) {
    const ts = this.ts;
    return {
      name: node.name.text,
      line: lineOf(this.source, node.getStart(this.source)),
      kind: "interface",
      bases: heritage(ts, node, ts.SyntaxKind.ExtendsKeyword),
      implements: [],
      methods: node.members.filter((member) => ts.isMethodSignature(member)).map((member) => member.name.getText(this.source)),
    };
  }
}

function unwrap(ts, node) {
  let current = node;
  while (WRAPPERS.has(ts.SyntaxKind[current.kind])) current = current.expression;
  return current;
}

// Name an anonymous function for the place that holds it, the same way as the
// approximate measure: `total`, `onClick`, or `items.map callback`.
function contextName(ts, node, source) {
  let child = node;
  let parent = node.parent;
  while (parent && WRAPPERS.has(ts.SyntaxKind[parent.kind])) {
    child = parent;
    parent = parent.parent;
  }
  if (!parent) return ANONYMOUS;
  return declaredName(ts, parent, child, source) || usedName(ts, parent, child, source) || ANONYMOUS;
}

// `const total = () => ...`, `{ total: () => ... }`, a class field, or a JSX attribute.
function declaredName(ts, parent, child, source) {
  if (ts.isJsxExpression(parent)) {
    return parent.parent && ts.isJsxAttribute(parent.parent) ? parent.parent.name.getText(source) : null;
  }
  const declares = ts.isVariableDeclaration(parent) || ts.isPropertyAssignment(parent) || ts.isPropertyDeclaration(parent);
  return declares && parent.initializer === child ? parent.name.getText(source) : null;
}

// `exports.total = () => ...`, or a callback argument such as `items.map(...)`.
function usedName(ts, parent, child, source) {
  if (ts.isBinaryExpression(parent) && parent.right === child) {
    return parent.operatorToken.kind === ts.SyntaxKind.EqualsToken ? lastName(ts, parent.left) : null;
  }
  if (ts.isCallExpression(parent) && parent.arguments.includes(child)) return calleeName(ts, parent.expression, source);
  return null;
}

function lastName(ts, node) {
  if (ts.isIdentifier(node)) return node.text;
  if (ts.isPropertyAccessExpression(node)) return node.name.text;
  return null;
}

function calleeName(ts, callee, source) {
  const target = ts.isCallExpression(callee) ? callee.expression : callee;
  const chain = /^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*$/;
  const text = target.getText(source);
  return chain.test(text) ? `${text} callback` : null;
}

function heritage(ts, node, keyword) {
  const clause = (node.heritageClauses || []).find((candidate) => candidate.token === keyword);
  if (!clause) return [];
  return clause.types.map((type) => lastName(ts, type.expression)).filter(Boolean);
}

function measureAll(request) {
  const ts = loadTypescript(request.root, request.files, request.typescript);
  const files = {};
  for (const file of request.files) {
    const text = fs.readFileSync(path.join(request.root, file), "utf8");
    files[file] = new FileMeasurer(ts, text, file).measure();
  }
  return { version: ts.version, files };
}

function main() {
  const request = JSON.parse(fs.readFileSync(0, "utf8"));
  let result;
  try {
    result = measureAll(request);
  } catch (error) {
    result = { error: error.message };
  }
  process.stdout.write(JSON.stringify(result));
}

if (require.main === module) main();

module.exports = { FileMeasurer, loadTypescript, measureAll };
