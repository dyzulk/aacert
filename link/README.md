# Server Symlinks

This directory is intended for symbolic links to server paths (such as `/www/server/`) for convenient access during development and testing.

All symbolic links created in this directory are ignored by Git, except this README file.

## Prerequisites

Ensure you are located at the repository root directory:

```bash
cd "$(git rev-parse --show-toplevel)"
```

## Creating the Symlink

Create a symbolic link pointing from `/www/server` to `link/server`:

```bash
ln -s /www/server link/server
```

## Verifying the Symlink

Verify that the symbolic link points to the target directory:

```bash
ls -la link/
```

Inspect the contents of the linked server directory:

```bash
ls -la link/server/
```

## Removing the Symlink

To safely remove the shortcut without affecting the actual server files, use `unlink`:

```bash
unlink link/server
```

Or use `rm`:

```bash
rm link/server
```

Note: Never include a trailing slash when removing a symlink (avoid `rm -rf link/server/`), as shells may treat it as a directory and delete files inside the original target folder.
