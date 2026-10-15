# Change history by surface

These lanes begin with the 2026-10-15 first-run repair. Earlier changes remain in Git; no historical behavior was reconstructed.

- [Developer first run](docs/readme.md)
- [OCR submission command](scripts/batch-extract.md)
- [Page JSON export command](scripts/pdf-textout.md)
- [Runtime dependencies](dependencies/requirements.md)
- [Offline workflow regression check](tests/workflow.md)

Follow [the entry format](TEMPLATE.md) when changing a surface. The new .gitignore keeps local environments, credentials, bytecode, and exports out of routine submissions; it does not remove existing files.

- [Offline verification workflow](ci/verification.md)
