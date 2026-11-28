// ESLint flat config that sets the limits of the gener8v code-quality rules.
// cq-measure gives the same complexity as ESLint. ESLint's max-lines-per-function counts the whole
// function, and cq-measure counts only the body, so ESLint reports a function about two lines sooner.
// ESLint's max-depth counts one level less for the blocks after an `else if` chain.
//
//   Rule 1.1  file-lines      max-lines               fail above 500 (warn above 300)
//   Rule 4.1  function-lines  max-lines-per-function  fail above 80  (warn above 40)
//   Rule 4.2  nesting         max-depth               fail above 4   (warn above 3)
//   Rule 4.3  complexity      complexity              fail above 15  (warn above 10)
//   Rule 4.4  params          max-params              fail above 6   (warn above 4)
//
// ESLint gives one level per rule. These are the fail levels, as errors. For the
// warn levels, use the commented block instead (or add it as a second config
// object with "warn"). Test files may have up to 800 lines (warn above 500).

export default [
  {
    files: ["**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"],
    rules: {
      "max-lines": ["error", { max: 500, skipBlankLines: true, skipComments: false }],
      "max-lines-per-function": ["error", { max: 80, skipBlankLines: true, skipComments: false, IIFEs: true }],
      "max-depth": ["error", 4],
      complexity: ["error", 15],
      "max-params": ["error", 6],

      // Warn levels:
      // "max-lines": ["warn", { max: 300, skipBlankLines: true, skipComments: false }],
      // "max-lines-per-function": ["warn", { max: 40, skipBlankLines: true, skipComments: false, IIFEs: true }],
      // "max-depth": ["warn", 3],
      // complexity: ["warn", 10],
      // "max-params": ["warn", 4],
    },
  },
  {
    files: ["**/*.{test,spec}.{js,jsx,mjs,cjs,ts,tsx,mts,cts}", "**/__tests__/**"],
    rules: {
      "max-lines": ["error", { max: 800, skipBlankLines: true, skipComments: false }],
      // "max-lines": ["warn", { max: 500, skipBlankLines: true, skipComments: false }],
    },
  },
];
