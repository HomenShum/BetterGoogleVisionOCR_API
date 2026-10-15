# Changelog — README.md

> Surface: README.md. New dated entries go at the top; retain existing entries.

## 2026-10-15 — Give the next developer an executable first run

Replace source-editing instructions and the embedded Google sample with two explicit commands for the same PDF, safe authentication guidance, navigable source/test links, and readiness limits. Preserve the historical examples in Git rather than keeping duplicate executable-looking instructions.

**Evidence:** The identical offline workflow driver changed from 18 failures and 2 errors across 11 test methods to 11 passing methods. The original install succeeded but the Google SDK import failed; repaired-install evidence is recorded in the handoff receipt.

**Commit:** this change; use `git log --follow -- README.md` to resolve its commit. **Author:** Codex.

**Touches:** [scripts/batch-extract.md](../scripts/batch-extract.md), [scripts/pdf-textout.md](../scripts/pdf-textout.md), [dependencies/requirements.md](../dependencies/requirements.md), [tests/workflow.md](../tests/workflow.md).
