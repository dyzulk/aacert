# Troubleshooting

## SSL.com ACME account registration is rejected

Review the full ACME error returned by aaPanel. SSL.com may require the customer
account to be activated and a billing profile to be completed. Follow any
instructions sent to the account email and check the [SSL.com customer portal](https://secure.ssl.com/).

The Digital Identity prompt for document signing and email is generally separate
from TLS DV domain validation. It is not normally needed for an ACME website
certificate, but comply with account-specific requirements shown by SSL.com if
issuance remains blocked.

The project's SSL.com directory metadata does not require EAB, while SSL.com's
ACME client guide describes Account/ACME Key and HMAC credentials. See the
[provider guide](providers.md) for this distinction; consult SSL.com if an
account-specific error indicates credentials are required.

## Check directory connectivity

```bash
aacert test
aacert test ssl_com
```

This tests access to the ACME directory; it does not verify account eligibility,
billing status, domain validation, or certificate pricing.

## Inspect aaPanel ACME state

```bash
aacert doctor
```

The command reports registered accounts and pending/valid orders. To back up
and clean stale pending orders:

```bash
aacert doctor --clean-pending
```

For installation rollback, see [Uninstallation](uninstallation.md).
