# Changelog — tests/test_workflow.py

> Surface: tests/test_workflow.py. New dated entries go at the top; retain existing entries.

## 2026-10-15 — Keep a no-charge workflow regression check

Add standard-library subprocess tests with fake Google SDKs and blocked sockets. They check the real script entrypoints and file artifacts rather than replacing the application logic; each child receives only a bounded OS environment and explicit fake authentication.

**Evidence:** The test file is byte-identical to the external driver frozen before code edits. Eleven methods cover happy paths, invalid/missing input, degraded cloud responses, six concurrent isolated outputs, and ten sequential repetitions.

**Commit:** this change; use `git log --follow -- tests/test_workflow.py` to resolve its commit. **Author:** Codex.

**Touches:** [docs/readme.md](../docs/readme.md), [scripts/batch-extract.md](../scripts/batch-extract.md), [scripts/pdf-textout.md](../scripts/pdf-textout.md), [dependencies/requirements.md](../dependencies/requirements.md).
