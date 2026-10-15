# Offline verification workflow history

## 2026-10-15 — Check the OCR command contract on pull requests

A developer needs the next change to retain the repaired first run. This repository previously had no committed GitHub Actions workflow. Add normal dependency installation, compatibility and import checks, source compilation, help, and the existing eleven-method offline workflow suite on Ubuntu 24.04 with Python 3.11. Google credentials and live OCR calls are not part of this job.

Checkout and Python setup use immutable commit pins verified against their official v7 tags. The job has read-only repository permissions, no persisted checkout credentials and a ten-minute timeout. This records configured checks; an actual CI result must be read at the exact revision. It does not certify OCR quality, cloud permissions, malicious/large cloud payloads or all supported platforms.
