# CLI reference

Use `aacert --help` or `aacert <command> --help` for help from the installed
version.

| Command | Purpose |
| --- | --- |
| `aacert version` | Show version information. |
| `aacert status` | Show active provider, patch status, and account details. |
| `aacert setup --ca <provider>` | Configure provider email/credentials; add `--enable` to enable immediately. |
| `aacert set-ca <provider>` | Switch the active provider. |
| `aacert set-eab <provider> --kid <KID> --hmac <HMAC>` | Update EAB credentials. |
| `aacert enable` | Enable custom CA overrides. |
| `aacert disable` | Disable overrides and return aaPanel to native Let's Encrypt. |
| `aacert test [provider]` | Test connectivity to a provider's ACME directory. |
| `aacert install` | Install the aaPanel hook patch. |
| `aacert uninstall` | Remove the patch and restore aaPanel. |
| `aacert doctor` | Audit aaPanel ACME account and order state. |
| `aacert doctor --clean-pending` | Back up and remove stale pending orders. |

Provider IDs: `letsencrypt`, `zerossl`, `google`, and `ssl_com`.

## Examples

```bash
aacert status
aacert test
aacert test ssl_com
aacert setup --ca ssl_com --email your-email@example.com
aacert set-ca letsencrypt
aacert doctor
```

See the [provider guide](providers.md) for EAB, account, and billing details.
