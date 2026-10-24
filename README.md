# aacert

> **Multi-CA ACME Manager for aaPanel**  
> Seamlessly switch between **ZeroSSL**, **Google Public CA**, **SSL.com**, and **Let's Encrypt** in aaPanel without modifying core SSL cron jobs or breaking panel updates.

---

## 🚀 Features

- **Multi-CA Support**:
  - **ZeroSSL** (90-day certificates via EAB)
  - **Google Public CA** (90-day certificates via Google Trust Services EAB)
  - **SSL.com** (90-day certificates)
  - **Let's Encrypt** (Default, fallback)
- **Zero-Disruption Architecture**:
  - Non-destructive 4-line micro-patch in aaPanel's `acme_v2.py`.
  - Safely falls back to native Let's Encrypt behavior if disabled or uninstalled.
  - Namespaces account keys (`acme_account_key_<ca>`) so your existing Let's Encrypt account keys are never overwritten.
  - Asynchronous order finalization polling built-in for CAs requiring processing time (e.g. ZeroSSL & Google PKI).
- **Plug & Play CLI**:
  - Accessible directly via the `aacert` terminal command.
  - Switch providers with a single command.
  - Automated DNS verification & renewal through aaPanel's native UI remains 100% operational.
- **Tested & Verified**:
  - Fully compatible with **aaPanel Linux 8.0.7+** running Python 3.12 pyenv.

---

## 📦 Quick Installation

Run the one-line installer via `curl`:

```bash
curl -sSL https://raw.githubusercontent.com/dyzulk/aacert/main/setup.sh | bash
```

The script will:
1. Clone the repository into `~/.aacert/`.
2. Add the global executable link `/usr/local/bin/aacert` and shell aliases to `.bashrc` / `.zshrc`.
3. Safely patch aaPanel's ACME class without disrupting existing websites.

---

## 🛠️ Usage & Commands

### 1. Check Status
Check current active CA, patch status, and credentials:
```bash
aacert status
```

### 2. Configure a Provider

#### Option A: ZeroSSL (Recommended)
1. Get your free EAB credentials from [ZeroSSL Developer Console](https://app.zerossl.com/developer).
2. Configure and enable in one command:
```bash
aacert setup --ca zerossl \
  --email your-email@example.com \
  --kid "YOUR_EAB_KID" \
  --hmac "YOUR_EAB_HMAC_KEY" \
  --enable
```

#### Option B: Google Public CA
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

#### Option C: SSL.com
```bash
aacert setup --ca ssl_com --email your-email@example.com --enable
```

---

### 3. Quick Switching Between Providers
Once credentials are saved, you can easily toggle providers anytime:
```bash
# Switch to ZeroSSL
aacert set-ca zerossl

# Switch to Google Public CA
aacert set-ca google

# Switch back to Let's Encrypt
aacert set-ca letsencrypt
```

---

### 4. Enable or Disable Custom CA
```bash
# Enable custom CA overrides
aacert enable

# Disable custom CA (aaPanel reverts to default Let's Encrypt)
aacert disable
```

---

### 5. Test ACME Directory Connectivity
Verify your server can reach the ACME directory endpoint of the active CA:
```bash
aacert test
# Or test a specific provider:
aacert test zerossl
```

---

## 🌐 Requesting SSL in aaPanel

Once `aacert` is configured and enabled:
1. Open your **aaPanel Dashboard** -> **Website**.
2. Click **Conf** on your site -> **SSL**.
3. Choose **Let's Encrypt** tab (aacert dynamically intercepts this request under the hood).
4. Select your verification method (DNS Verification via Cloudflare API recommended, or File Verification).
5. Click **Apply**.
6. When issued, inspect the certificate lock icon in your browser: it will now display **ZeroSSL**, **Google Trust Services**, etc., instead of Let's Encrypt!

---

## 🔄 Uninstallation & Safe Rollback

If you ever wish to remove the patch and revert aaPanel back to factory state:
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

## 🔒 Security & Privacy

- All EAB credentials and configs remain strictly local to your server in `~/.aacert/config.json`.
- The micro-patch runs locally within Python at runtime; no external telemetry or third-party servers are queried.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
