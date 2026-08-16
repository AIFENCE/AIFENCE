# Contributing

## Change BizIQ behavior

Edit canonical files under `source/`. On a fresh clone/environment, install the declared validator dependencies first:

```bash
npm run setup:python
```

Then run:

```bash
npm run build
npm test
```

Commit the source changes and regenerated `build/` together.

## Change interoperability/runtime behavior

Edit `tooling/runtime-template/`, `tooling/templates/`, or the tooling scripts. Rebuild and test before committing.

## Never

- hand-edit `build/` as the source of a fix;
- commit `dist/` release ZIPs;
- duplicate BizIQ control logic inside individual platform adapters;
- change stable control IDs without following BizIQ source governance.
