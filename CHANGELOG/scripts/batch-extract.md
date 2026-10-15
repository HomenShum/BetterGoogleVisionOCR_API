# Changelog — googleVisionBatchExtract.py

> Surface: googleVisionBatchExtract.py. New dated entries go at the top; retain existing entries.

## 2026-10-15 — Submit the PDF the caller selects

Require one Cloud Storage PDF URI instead of selecting a built-in personal example, and stop replacing the caller's authentication settings. Help and invalid inputs exit before loading Google clients; batch size 10 and the 420-second operation timeout remain.

**Evidence:** The offline SDK records the exact input/output URIs, batch size, timeout, and unchanged authentication sentinel. A simulated operation timeout exits unsuccessfully.

**Commit:** this change; use `git log --follow -- googleVisionBatchExtract.py` to resolve its commit. **Author:** Codex.

**Touches:** [docs/readme.md](../docs/readme.md), [scripts/pdf-textout.md](../scripts/pdf-textout.md), [dependencies/requirements.md](../dependencies/requirements.md), [tests/workflow.md](../tests/workflow.md).
