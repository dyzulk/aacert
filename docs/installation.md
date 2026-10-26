# Installation

## Requirements

- aaPanel Linux 8.0.7 or later.
- Python 3.10 or later. The project has been tested with aaPanel's Python 3.12
  environment.
- Root or equivalent privileges to patch aaPanel and create the command symlink.

## Install

Recommended (jsDelivr CDN):

```bash
curl -sSL https://cdn.jsdelivr.net/gh/dyzulk/aacert@main/setup.sh | bash
```

Alternative (GitHub Raw):

```bash
curl -sSL https://raw.githubusercontent.com/dyzulk/aacert/main/setup.sh | bash
```

The installer downloads the release into `~/.aacert/`, creates
`/usr/local/bin/aacert`, adds a shell alias where applicable, and applies the
aaPanel hook patch. Review the install script before running it if you want to
inspect the changes first.

After installation, check the current state:

```bash
aacert status
```

Continue with the [provider setup guide](providers.md).
