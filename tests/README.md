# Running Tests Locally

These instructions are for local development on an aaPanel host. Run the test
suite in an isolated virtual environment; do not install test dependencies into
the system Python or aaPanel's `/www/server/panel/pyenv` environment. This
prevents test tooling from changing Python packages used by aaPanel.

Run commands from the repository root:

```bash
# Use an available Python 3.10+ interpreter.
python3 --version
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install cryptography
python -m tests.run_tests
```

The complete suite currently uses `cryptography` to create test-only RSA keys.
The `tests.run_tests` module invocation keeps imports inside the repository
root and is the recommended way to run the suite.

If you prefer not to activate the virtual environment, run the same commands
with its Python executable directly from the repository root:

```bash
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install cryptography
./.venv/bin/python -m tests.run_tests
```

To run only the release-note tests:

```bash
PYTHONPATH=.github/scripts python -m unittest tests.unit.test_release_notes
```

The unit tests mock provider requests and do not require API keys. To exercise
the live Gemini, Groq, and local-fallback paths, install the release-note SDKs
into the same virtual environment and use the local test runner:

```bash
python -m pip install -r .github/scripts/requirements-release-notes.txt
python .github/scripts/test_release_notes.py --provider all
```

The runner reads `GEMINI_API_KEY` and `GROQ_API_KEY` from the environment or,
by default, from `tmp/secret.env`. Keep that file local and never commit or
print its contents. Live provider tests make external API requests and may be
subject to provider quotas.

## CI

GitHub Actions creates its own isolated runner environment and installs the
dependencies declared by each workflow. These local virtual-environment steps
are for aaPanel hosts and developer machines, not a replacement for CI setup.
