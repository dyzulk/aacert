# Troubleshooting

## SSL.com ACME account registration is rejected

The bundled SSL.com provider may be marked under maintenance while an
authorization issue is investigated. In that mode aacert retains the provider
and its credentials but stops issuance with an explicit notice. Use another
provider or native Let's Encrypt until SSL.com issuance is re-enabled.

Review the full ACME error returned by aaPanel. SSL.com may require the customer
account to be activated and a billing profile to be completed. Follow any
instructions sent to the account email and check the [SSL.com customer portal](https://secure.ssl.com/).

The Digital Identity prompt for document signing and email is generally separate
from TLS DV domain validation. It is not normally needed for an ACME website
certificate, but comply with account-specific requirements shown by SSL.com if
issuance remains blocked.

The directory metadata's `externalAccountRequired: false` flag does not negate
SSL.com's account-specific onboarding instructions. If SSL.com emailed an
Account/ACME Key and HMAC Key, configure both using `aacert setup --ca ssl_com`
before retrying. See the [provider guide](providers.md).

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
