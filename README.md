<div align="center">

# aacert

**Multi-CA ACME Manager for aaPanel**  
*Seamlessly issue & automate certificates from ZeroSSL, Google Public CA, SSL.com, and Let's Encrypt.*

[![Stars](https://img.shields.io/github/stars/dyzulk/aacert?style=for-the-badge&logo=github&label=STARS&color=yellow)](https://github.com/dyzulk/aacert/stargazers)
[![Downloads](https://img.shields.io/github/downloads/dyzulk/aacert/total?style=for-the-badge&color=2ea44f&label=DOWNLOADS)](https://github.com/dyzulk/aacert/releases)
[![Release](https://img.shields.io/github/v/tag/dyzulk/aacert?style=for-the-badge&color=0969da&label=RELEASE&sort=semver)](https://github.com/dyzulk/aacert/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-0D1117?style=for-the-badge)](LICENSE)

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![aaPanel](https://img.shields.io/badge/aaPanel-8.0.7%2B-20B2AA?style=for-the-badge&logo=gnubash&logoColor=white)](https://aapanel.com)

<br/>

<a href="https://skillicons.dev">
  <img src="https://skillicons.dev/icons?i=python,bash,linux,github&theme=dark" alt="Supported Tech Stack" />
</a>

<br/>
<br/>

<p>If aacert is useful to you, please consider <a href="https://github.com/dyzulk/aacert/stargazers">giving it a star ⭐</a> — it helps others discover the project.</p>

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

**Recommended (Fast CDN via jsDelivr):**
```bash
curl -sSL https://cdn.jsdelivr.net/gh/dyzulk/aacert@main/setup.sh | bash
```

**Alternative (GitHub Raw):**
```bash
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

> [!TIP]
> **Restarting aaPanel after configuration changes:**
> Whenever you switch providers (`set-ca`), update credentials (`setup`), or toggle status (`enable` / `disable`), restart the aaPanel service so that background worker tasks (`BT-Panel` and `BT-Tasks`) reload the updated configuration into memory immediately:
> ```bash
> bt 1
> # Or:
> bt restart
> ```
> *(Or via panel CLI: `systemctl restart bt`)*

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

### 1. Automatic Cleanup (Recommended)

Run the uninstallation command and remove user configuration files in one step:

```bash
aacert uninstall && rm -rf ~/.aacert
```

If the `aacert` alias or command is no longer available in your current terminal session, run the uninstaller script directly:

```bash
bash ~/.aacert/uninstall.sh && rm -rf ~/.aacert
```

> [!NOTE]
> **Active Terminal Session:**
> The uninstaller automatically removes aliases from shell profile files (`~/.bashrc`, `~/.zshrc`, etc.). To clear the alias from your current active terminal session immediately without opening a new window, run:
> ```bash
> unalias aacert 2>/dev/null || true
> ```

---

### 2. Manual Step-by-Step Cleanup

If you need to manually remove patches and restore aaPanel without using the script:

```bash
# Step 1: Remove symlinks from aaPanel and global bin
rm -f /www/server/panel/class/acme_provider_hook.py
rm -f /www/server/panel/class/eab_helper.py
rm -f /usr/local/bin/aacert

# Step 2: Remove aacert shell aliases across profiles
for rc in ~/.bashrc ~/.zshrc ~/.bash_profile ~/.profile; do
  [ -f "$rc" ] && sed -i '/# aacert - Multi-CA ACME Manager for aaPanel/d;/alias aacert=/d' "$rc"
done

# Step 3: Restore original factory acme_v2.py
if [ -f "/www/server/panel/class/acme_v2.py.bak_orig" ]; then
  cp /www/server/panel/class/acme_v2.py.bak_orig /www/server/panel/class/acme_v2.py
  rm -f /www/server/panel/class/acme_v2.py.bak_orig
fi

# Step 4: Remove configuration and module files
rm -rf ~/.aacert

# Step 5: Restart aaPanel service
bt 1
```

---

### 3. Verifying Factory Integrity

To verify that aaPanel has returned to its clean original state:

1. Check that `acme_v2.py` no longer contains the hook:
   ```bash
   grep "AACERT_HOOK" /www/server/panel/class/acme_v2.py || echo "Original factory state verified (no hooks present)"
   ```

2. Test that aaPanel's internal Python environment initializes cleanly:
   ```bash
   /www/server/panel/pyenv/bin/python3 -c "import acme_v2; obj = acme_v2.acme_v2(); print('aaPanel ACME engine running in native factory mode.')"
   ```

---

## Security Architecture

- All EAB credentials and configs remain strictly local to your server in `~/.aacert/config.json`.
- The micro-patch runs locally within Python at runtime; no external telemetry or third-party servers are queried.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
