# Contributing to EyeGuard

Thanks for your interest in improving EyeGuard! 🎉

## Getting started

1. Fork the repo and clone your fork.
2. Create a virtual environment and install dev dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements-dev.txt
   pip install -e .
   ```
3. Create a branch for your change: `git checkout -b feature/my-improvement`.

## Development workflow

- **Format code:** `black eyeguard tests`
- **Lint:** `ruff check eyeguard tests`
- **Run tests:** `pytest --cov=eyeguard`

All of the above run automatically in CI on every pull request.

## Making changes

- Keep pull requests focused on a single change.
- Add or update tests for any behavior change (the test suite does **not**
  require a physical webcam — see `tests/test_detector.py` for the pattern
  of feeding synthetic frames/arrays instead).
- Update `README.md` if you change user-facing behavior or configuration.
- Follow [Conventional Commits](https://www.conventionalcommits.org/) style
  for commit messages where possible (e.g. `fix: correct distance formula`).

## Reporting bugs / requesting features

Please open an issue using the appropriate template under `.github/ISSUE_TEMPLATE/`
and include:
- Your OS, Python version, and webcam (if relevant)
- Steps to reproduce
- Expected vs. actual behavior

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Please be
respectful and constructive.
