# Changelog — googleVisionPDFtextout.py

> Surface: googleVisionPDFtextout.py. New dated entries go at the top; retain existing entries.

## 2026-10-15 — Export the same PDF from a fresh directory

Derive the output prefix from the explicit PDF URI, create json_out after successful parsing, preserve dotted filenames/Unicode, numeric page ordering, and the blank-page marker. Remove unused Vision construction and commented CSV/database alternatives; provider errors and empty results fail before replacing an existing local export.

**Evidence:** Offline checks exercise a new directory, unordered batches, blank pages, six concurrent isolated exports, ten repeated exports, and degraded/error inputs. Cloud OCR and atomic local writes remain unverified or unsupported, as documented.

**Commit:** this change; use `git log --follow -- googleVisionPDFtextout.py` to resolve its commit. **Author:** Codex.

**Touches:** [docs/readme.md](../docs/readme.md), [scripts/batch-extract.md](../scripts/batch-extract.md), [dependencies/requirements.md](../dependencies/requirements.md), [tests/workflow.md](../tests/workflow.md).
