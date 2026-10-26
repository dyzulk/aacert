<div align="center">

# aacert

**Multi-CA ACME Manager for aaPanel**

Issue and renew certificates through ZeroSSL, Google Public CA, SSL.com, or
aaPanel's native Let's Encrypt integration.

[![Stars](https://img.shields.io/github/stars/dyzulk/aacert?style=for-the-badge&logo=github&label=STARS&color=yellow)](https://github.com/dyzulk/aacert/stargazers)
[![Downloads](https://img.shields.io/github/downloads/dyzulk/aacert/total?style=for-the-badge&color=2ea44f&label=DOWNLOADS)](https://github.com/dyzulk/aacert/releases)
[![Release](https://img.shields.io/github/v/tag/dyzulk/aacert?style=for-the-badge&color=0969da&label=RELEASE&sort=semver)](https://github.com/dyzulk/aacert/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-0D1117?style=for-the-badge)](LICENSE)

</div>

---

## Overview

- Keeps aaPanel's native certificate workflow and DNS integrations.
- Separates ACME accounts by provider to protect existing Let's Encrypt data.
- Supports ZeroSSL and Google Public CA asynchronous order processing.
- Installs a small hook in aaPanel and can be disabled or uninstalled.

**Requirements:** aaPanel Linux 8.0.7+ and Python 3.10+ (tested with aaPanel's
Python 3.12 environment).

## Install

```bash
curl -sSL https://cdn.jsdelivr.net/gh/dyzulk/aacert@main/setup.sh | bash
```

See [Installation](docs/installation.md) for alternatives and what the installer
changes.

## Quick start

```bash
aacert status
aacert setup --ca zerossl --email you@example.com --kid "EAB_KID" --hmac "EAB_HMAC" --enable
```

Provider setup, requirements, and provider-specific caveats are documented in
[Provider guide](docs/providers.md). For the full command list, see
[CLI reference](docs/cli-reference.md).

## Documentation

- [Installation and prerequisites](docs/installation.md)
- [Provider setup and comparison](docs/providers.md)
- [CLI commands](docs/cli-reference.md)
- [Issuing certificates through aaPanel](docs/issuing-certificates.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Rollback and uninstallation](docs/uninstallation.md)
- [Security architecture](docs/security.md)

## License

MIT. See [LICENSE](LICENSE).
