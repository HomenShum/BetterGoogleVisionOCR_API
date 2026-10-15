# Changelog — requirements.txt

> Surface: requirements.txt. New dated entries go at the top; retain existing entries.

## 2026-10-15 — Install the two clients actually used

Replace 11 unrelated legacy packages with the Google Vision 3.16.0 and Storage 3.17.1 clients. All five original tracked files were read and no active code used the removed packages; the optional SQLAlchemy example was only commented code. Rewrite the old UTF-16 requirements file as normal UTF-8 text.

**Evidence:** The original clean pip install passed, followed by a ModuleNotFoundError for google. Direct release versions and Python >=3.10 requirements were read from current PyPI metadata; repaired clean install/import results are recorded in the handoff receipt.

**Commit:** this change; use `git log --follow -- requirements.txt` to resolve its commit. **Author:** Codex.

**Touches:** [docs/readme.md](../docs/readme.md), [scripts/batch-extract.md](../scripts/batch-extract.md), [scripts/pdf-textout.md](../scripts/pdf-textout.md), [tests/workflow.md](../tests/workflow.md).
