# Contributing

## Change a rule

1. Edit the rule in `guidelines/`. Do not edit `AGENTS.md` or the index in `skills/rules/SKILL.md`, because the generator writes them.
2. If the rule has a measure, change `src/cq_measure/defaults.json` to match, and change the check in `src/cq_measure/`.
3. Run the generator: `python3 scripts/build_index.py`.
4. Run all checks (the same checks as CI):

```
python3 scripts/build_index.py --check
python3 -m unittest discover -s scripts -p "*_test.py"
PYTHONPATH=src python3 -m unittest discover -s src -p "*_test.py" -t src
node --test src/cq_measure/metrics/measure-typescript.test.cjs
PYTHONPATH=src python3 -m cq_measure .
```

The TypeScript measures need a `typescript` package of version 5 or 6. Install it outside the repository, and set `CQ_TYPESCRIPT` to its path for the last three commands:

```
npm install --prefix /tmp/cq-typescript typescript@6
export CQ_TYPESCRIPT=/tmp/cq-typescript/node_modules/typescript
```

Without it, the Node.js tests and one Python test are skipped, and `cq-measure` uses the approximation.

## Add a rule

- Add it at the end of its section. Rule numbers are stable, because reviews and commit messages cite them. Do not renumber existing rules.
- Write the statement as an instruction of 12 words or fewer.
- Give it a **Measure** line: one or more check IDs with their limits, or `judged (self-check)`.
- Give the reason in two to four sentences. Add a bad and a good example only if they make the rule clearer.
- If the rule is judged, add a question for it to the table in `skills/self-check/SKILL.md`.

## Writing style

The rules are written in [ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/). The style is clear for readers who are not native English speakers, and it gives models fewer ways to misread an instruction:

- Write instructions in the imperative, with a maximum of 20 words for each sentence.
- Use "must" and "can". Do not use "should", "may", or "might".
- Put a condition before its instruction: "If the value is required, fail."
- Use one word for one concept.

## The tool obeys its own rules

`cq-measure` must report no `fail` findings on this repository. Put each unit test next to its module as `<module>_test.py`.
