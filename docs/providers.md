# Provider guide

Provider IDs are case-sensitive in examples and should be entered as shown.
For SSL.com, use `ssl_com`, not `ssl.com`.

| Provider | ID | EAB | Notes |
| --- | --- | --- | --- |
| ZeroSSL | `zerossl` | Required | Obtain EAB credentials from the [ZeroSSL Developer Console](https://app.zerossl.com/developer). |
| Google Public CA | `google` | Required | Generate EAB credentials with Google Cloud PKI. |
| SSL.com | `ssl_com` | Use the Account/ACME Key and HMAC credentials issued for your account | SSL.com's onboarding email provides these EAB credentials. Directory metadata may still report `externalAccountRequired: false`. |
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

### Temporary issuance pause

The aacert SSL.com provider is currently marked **under maintenance** because
the observed ACME authorization remained pending even while the DNS TXT value
was visible on both authoritative nameservers and a public resolver. The
provider remains registered, its credentials are preserved, and you can still
configure it or test directory connectivity; however, aacert will return a
clear maintenance message instead of submitting certificate issuance requests.
Choose another CA or aaPanel's native Let's Encrypt until this is cleared.

This gate is controlled by the `maintenance` and `maintenance_message` fields
for `ssl_com` in `config.json`. To re-enable issuance after verification, set
`maintenance` to `false`, remove or update the notice, and restart aaPanel.

The configured directory is [SSL.com DV RSA](https://acme.ssl.com/sslcom-dv-rsa).
Although its directory metadata reports `externalAccountRequired: false`,
SSL.com's account onboarding email provides an Account/ACME Key and HMAC Key
and instructs the customer to use them for ACME. Use those account-issued
credentials with aacert:

```bash
aacert setup --ca ssl_com \
  --email your-email@example.com \
  --kid "YOUR_SSL_COM_ACCOUNT_KEY" \
  --hmac "YOUR_SSL_COM_HMAC_KEY" \
  --enable
```

The metadata flag describes whether the ACME directory globally mandates EAB
for every new account. It does not override SSL.com's account-level onboarding
instructions. Do not paste EAB secrets into logs, screenshots, or public
repositories. SSL.com's [ACME client guide](https://www.ssl.com/how-to/acme-ssl-tls-automation-with-apache-and-nginx/)
also explains where to find ACME credentials in the customer portal.

Use the public SSL.com directory URL configured by aacert. If an email or
copied command shows a loopback address such as `127.0.0.1` as the ACME server,
verify it with SSL.com before using it; a loopback URL refers to the local
machine, not SSL.com's public ACME service.

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
aacert setup --ca ssl_com --email your-email@example.com \
  --kid "YOUR_SSL_COM_ACCOUNT_KEY" --hmac "YOUR_SSL_COM_HMAC_KEY" --enable
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
