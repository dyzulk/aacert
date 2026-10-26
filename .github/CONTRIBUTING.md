# Contributing to aacert

Thank you for your interest in improving aacert. Contributions should be focused, clearly explained, and consistent with the project's existing behavior and documentation.

## Before You Start

- For bugs and feature proposals, search existing issues and Discussions before opening a new one.
- Use Discussions for questions and early-stage ideas. Open an issue for a reproducible defect or a well-defined feature request.
- For significant changes, describe the proposed scope in an issue or Discussion before implementation.

## Development

1. Fork the repository and create a branch for your change.
2. Keep changes focused and avoid including unrelated formatting or generated files.
3. Add or update tests for behavior changes.
4. Run the test suite:

   ```bash
   python3 tests/run_tests.py
   ```

5. Update the relevant documentation when user-visible behavior, configuration, installation, or supported requirements change.

The project targets Python 3.10 and later. Avoid introducing dependencies unless they are necessary and documented.

## Pull Requests

Include the following in your pull request:

- A concise summary of the problem and the solution.
- Relevant issue or Discussion links, when applicable.
- Test commands run and their results.
- Documentation updates for user-facing changes.

Do not include credentials, private keys, EAB values, or other sensitive data in commits, logs, screenshots, or test fixtures.

## Commit Messages

Use a concise message that describes the change. Do not add a `Co-authored-by` trailer.
