# Contributing

Open an issue before a behavioral change so the intended source-preservation and layout invariants stay clear.

For a pull request:

1. Do not add user photographs, generated outputs, credentials, machine paths, or assets without verified redistribution rights.
2. Keep long prompt text canonical in `references/prompt-template.md` rather than duplicating it.
3. Run `python scripts/validate_repository.py` and `python -m unittest discover -s tests -v`.
4. Describe observable behavior changes and any limitation the tests do not cover.

Contributors must have the right to submit their code and assets. Contribution licensing follows the repository's `LICENSE` when one exists; if no license is present, contact the maintainer before submitting reusable work.
