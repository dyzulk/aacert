# Provider guide

Provider IDs are case-sensitive in examples and should be entered as shown.
For SSL.com, use `ssl_com`, not `ssl.com`.

| Provider | ID | EAB | Notes |
| --- | --- | --- | --- |
| ZeroSSL | `zerossl` | Required | Obtain EAB credentials from the [ZeroSSL Developer Console](https://app.zerossl.com/developer). |
| Google Public CA | `google` | Required | Generate EAB credentials with Google Cloud PKI. |
| SSL.com | `ssl_com` | Not required by this project's configured RSA directory metadata | See the SSL.com notes below; SSL.com's own client guide also documents ACME credentials. |
| Let's Encrypt | `letsencrypt` | No | aaPanel's native default provider. |

## ZeroSSL

Get free EAB credentials from the [ZeroSSL Developer Console](https://app.zerossl.com/developer), then configure:

```bash
aacert setup --ca zerossl \
  --email your-email@example.com \
  --kid "YOUR_EAB_KID" \
  --hmac "YOUR_EAB_HMAC_KEY" \
  --enable
```

## Google Public CA

Create EAB credentials using Google Cloud PKI:

```bash
gcloud publicca external-account-keys create
```

Use the resulting credentials:

```bash
aacert setup --ca google \
  --email your-email@example.com \
  --kid "YOUR_GOOGLE_KID" \
  --hmac "YOUR_GOOGLE_HMAC" \
  --enable
```

## SSL.com

The configured directory is [SSL.com DV RSA](https://acme.ssl.com/sslcom-dv-rsa).
Its ACME directory metadata reports `externalAccountRequired: false`, which is
why this provider does not require EAB in aacert's current configuration.
However, SSL.com's [ACME client guide](https://www.ssl.com/how-to/acme-ssl-tls-automation-with-apache-and-nginx/)
also documents Account/ACME Key and HMAC credentials. If registration is
rejected or SSL.com requires ACME credentials for your account, check its
account's API credentials page and contact SSL.com support before assuming the
provider can register without them.

SSL.com may require a customer web account to be activated and its billing
profile completed before ACME account registration or certificate issuance.
Follow account-specific notices and instructions sent to the registered email.

The portal may show an option to enable a free Digital Identity for document
signing and email. This is generally separate from domain validation for TLS DV
website certificates and is not normally needed for an ACME website order.
Follow any account-specific issuance requirements if the order remains blocked.

SSL.com offers a [Free DV certificate](https://www.ssl.com/products/website-security/tls-ssl/single-domain/free-dv/),
but choosing `ssl_com` in aacert does not itself guarantee a $0 order. Confirm
that the selected product/order in the SSL.com portal is Free DV and displays
$0 before proceeding. The Free DV product is single-domain; check SSL.com's
product terms for current coverage and pricing.

```bash
aacert setup --ca ssl_com --email your-email@example.com --enable
```

## Switch provider

After configuration, switch the active provider with:

```bash
aacert set-ca zerossl
aacert set-ca google
aacert set-ca ssl_com
aacert set-ca letsencrypt
```

Restart aaPanel after changing provider or credentials so background workers
reload the configuration. See [Issuing certificates](issuing-certificates.md).
