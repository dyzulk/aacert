<div align="center">

# aacert

**Multi-CA ACME Manager for aaPanel**  
*Seamlessly issue & automate certificates from ZeroSSL, Google Public CA, SSL.com, and Let's Encrypt.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![aaPanel](https://img.shields.io/badge/aaPanel-8.0.7%2B-20B2AA?style=for-the-badge&logo=gnubash&logoColor=white)](https://aapanel.com)
[![Downloads](https://img.shields.io/github/downloads/dyzulk/aacert/total?style=for-the-badge&color=2ea44f)](https://github.com/dyzulk/aacert/releases)
[![Release](https://img.shields.io/github/v/release/dyzulk/aacert?style=for-the-badge&color=0969da)](https://github.com/dyzulk/aacert/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-0D1117?style=for-the-badge)](LICENSE)

<br/>

<a href="https://skillicons.dev">
  <img src="https://skillicons.dev/icons?i=python,bash,linux,github&theme=dark" alt="Supported Tech Stack" />
</a>

<br/>
<br/>

---

_Zero disruption to existing cron jobs &bull; RFC 8555 EAB binding &bull; Async certificate signing polling_

</div>

---

## Features

- **Multi-CA Support**:
  - **ZeroSSL** (90-day certificates via EAB credentials)
  - **Google Public CA** (90-day certificates via Google Trust Services EAB)
  - **SSL.com** (90-day certificates)
  - **Let's Encrypt** (Default aaPanel fallback)
- **Zero-Disruption Architecture**:
  - Non-destructive 4-line micro-patch in aaPanel's `acme_v2.py`.
  - Safely falls back to native Let's Encrypt behavior if disabled or uninstalled.
  - Namespaces account keys (`acme_account_key_<ca>`) so existing Let's Encrypt keys are never overwritten.
  - Asynchronous order finalization polling built-in for CAs requiring processing time (e.g. ZeroSSL & Google PKI).
- **Plug & Play CLI**:
  - Accessible directly via the `aacert` terminal command or alias.
  - Switch providers with a single command.
  - Automated DNS verification & renewal through aaPanel's native UI remains 100% operational.
- **Tested & Verified**:
  - Fully compatible with **aaPanel Linux 8.0.7+** running Python 3.12 pyenv.

---

## Installation

Install via `curl` with a single command:

```bash
# Recommended (Fast CDN via jsDelivr)
curl -sSL https://cdn.jsdelivr.net/gh/dyzulk/aacert@main/setup.sh | bash

# Alternative (GitHub Raw)
curl -sSL https://raw.githubusercontent.com/dyzulk/aacert/main/setup.sh | bash
```

The script will:
1. Download the release tarball asset into `~/.aacert/` (tracked on GitHub release counter).
2. Create the global executable symlink `/usr/local/bin/aacert`.
3. Detect active shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.profile`) and register the `aacert` alias.
4. Safely apply the micro-patch into aaPanel without disrupting active websites.

---

## CLI Usage

### Check Status
Check active CA provider, patch status, and credentials:
```bash
aacert status
```

### Configure a Provider

#### ZeroSSL (Recommended)
1. Get free EAB credentials from the [ZeroSSL Developer Console](https://app.zerossl.com/developer).
2. Configure and enable in one command:
```bash
aacert setup --ca zerossl \
  --email your-email@example.com \
  --kid "YOUR_EAB_KID" \
  --hmac "YOUR_EAB_HMAC_KEY" \
  --enable
```

#### Google Public CA
1. Obtain EAB Key ID & HMAC from Google Cloud PKI:
   ```bash
   gcloud publicca external-account-keys create
   ```
2. Configure in aacert:
```bash
aacert setup --ca google \
  --email your-email@example.com \
  --kid "YOUR_GOOGLE_KID" \
  --hmac "YOUR_GOOGLE_HMAC" \
  --enable
```

#### SSL.com
```bash
aacert setup --ca ssl_com --email your-email@example.com --enable
```

---

### Switching Providers
Once credentials are saved, toggle providers anytime:
```bash
# Switch to ZeroSSL
aacert set-ca zerossl

# Switch to Google Public CA
aacert set-ca google

# Switch back to Let's Encrypt
aacert set-ca letsencrypt
```

---

### Enable or Disable Custom CA
```bash
# Enable custom CA overrides
aacert enable

# Disable custom CA (aaPanel reverts to default Let's Encrypt)
aacert disable
```

---

### Test Directory Connectivity
Verify your server can reach the ACME directory endpoint of the active CA:
```bash
aacert test
# Or test a specific provider:
aacert test zerossl
```

---

## Workflow: Issuing SSL via Dashboard

Once `aacert` is configured and enabled:
1. Open your **aaPanel Dashboard** -> **Website**.
2. Click **Conf** on your site -> **SSL**.
3. Choose **Let's Encrypt** tab (aacert dynamically intercepts this request under the hood).
4. Select verification method (DNS Verification via Cloudflare API recommended, or File Verification).
5. Click **Apply**.
6. When issued, inspect the certificate in your browser: it will now display **ZeroSSL**, **Google Trust Services**, etc.

---

## Rollback & Uninstallation

To remove the patch and revert aaPanel back to factory state:
```bash
aacert uninstall
```
Or run directly:
```bash
bash ~/.aacert/uninstall.sh
```

To remove all configuration files:
```bash
rm -rf ~/.aacert /usr/local/bin/aacert
```

---

## Security Architecture

- All EAB credentials and configs remain strictly local to your server in `~/.aacert/config.json`.
- The micro-patch runs locally within Python at runtime; no external telemetry or third-party servers are queried.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
