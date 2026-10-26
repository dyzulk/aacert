# Project Guidelines

## Communication

- Use professional, clear English in repository content and project communication.
- Never use emojis in responses, code, comments, documentation, commit messages, pull requests, issues, discussions, or generated release notes.

## Git Commits

- Do not add any `Co-authored-by` trailer to a commit message, including a Copilot co-author trailer.
- Keep commit messages concise and describe the change clearly.

## Project Context

- aacert is a Python-based multi-CA ACME manager designed for aaPanel.
- Preserve aaPanel's native certificate workflow and provider-specific account data.
- Do not expose or include credentials, private keys, EAB values, or other secrets in source code, logs, examples, or generated output.

## Validation

- Run the relevant tests for code changes with `python3 tests/run_tests.py`.
- Update user-facing documentation when behavior or setup requirements change.
- Follow existing project patterns and keep changes focused on the requested work.
