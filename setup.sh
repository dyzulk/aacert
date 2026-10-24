#!/usr/bin/env bash
# ====================================================================
# aacert - One-liner Online Installer for aaPanel
# Usage:
#   curl -sSL https://raw.githubusercontent.com/dyzulk/aacert/main/setup.sh | bash
# ====================================================================
set -e

INSTALL_DIR="${HOME}/.aacert"
BIN_LINK="/usr/local/bin/aacert"

echo "=========================================================="
echo "           aacert - Multi-CA ACME Manager for aaPanel     "
echo "=========================================================="

# Check root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run this installer as root or with sudo."
    exit 1
fi

# Check prerequisites
for cmd in curl tar python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "[*] Installing prerequisite: $cmd..."
        if command -v apt-get &>/dev/null; then
            apt-get update -qq && apt-get install -y -qq "$cmd"
        elif command -v yum &>/dev/null; then
            yum install -y -q "$cmd"
        fi
    fi
done

# Check aaPanel existence
if [ ! -d "/www/server/panel" ]; then
    echo "[!] Error: aaPanel directory (/www/server/panel) was not found."
    echo "    aacert is designed specifically for aaPanel."
    exit 1
fi

# Backup existing config.json if present
BACKUP_CFG=""
if [ -f "${INSTALL_DIR}/config.json" ]; then
    BACKUP_CFG=$(mktemp)
    cp "${INSTALL_DIR}/config.json" "$BACKUP_CFG"
fi

# Repository release parameters
GITHUB_OWNER="dyzulk"
GITHUB_REPO="aacert"
ASSET_NAME="aacert.tar.gz"
TARBALL_URL="https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases/latest/download/${ASSET_NAME}"

echo "[*] Downloading latest release asset (${ASSET_NAME})..."
TMP_ARCHIVE=$(mktemp /tmp/aacert-XXXXXX.tar.gz)
curl -f -sSL -L "${TARBALL_URL}" -o "${TMP_ARCHIVE}"

# Clean existing installation directory and unpack
rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
tar -xzf "${TMP_ARCHIVE}" --strip-components=1 -C "${INSTALL_DIR}"
rm -f "${TMP_ARCHIVE}"

# Restore configuration if backed up
if [ -n "$BACKUP_CFG" ] && [ -f "$BACKUP_CFG" ]; then
    cp "$BACKUP_CFG" "${INSTALL_DIR}/config.json"
    rm -f "$BACKUP_CFG"
    echo "[✓] Preserved existing aacert configuration."
fi

# Set executable permissions
chmod +x "${INSTALL_DIR}/manage.py" "${INSTALL_DIR}/install.sh" "${INSTALL_DIR}/uninstall.sh"

# Create /usr/local/bin symlink
if [ -d "/usr/local/bin" ]; then
    ln -sf "${INSTALL_DIR}/manage.py" "${BIN_LINK}"
    echo "[✓] Created global command: ${BIN_LINK}"
fi

# Register alias based on active shell profile
detect_and_register_alias() {
    local target_rc=""
    local current_shell
    current_shell="$(basename "${SHELL:-bash}")"

    case "$current_shell" in
        zsh)
            target_rc="${HOME}/.zshrc"
            ;;
        bash)
            if [ -f "${HOME}/.bashrc" ]; then
                target_rc="${HOME}/.bashrc"
            elif [ -f "${HOME}/.bash_profile" ]; then
                target_rc="${HOME}/.bash_profile"
            fi
            ;;
        *)
            if [ -f "${HOME}/.profile" ]; then
                target_rc="${HOME}/.profile"
            fi
            ;;
    esac

    if [ -z "$target_rc" ] || [ ! -f "$target_rc" ]; then
        for candidate in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.bash_profile" "${HOME}/.profile"; do
            if [ -f "$candidate" ]; then
                target_rc="$candidate"
                break
            fi
        done
    fi

    if [ -n "$target_rc" ] && [ -f "$target_rc" ]; then
        if ! grep -q "alias aacert=" "$target_rc"; then
            echo "" >> "$target_rc"
            echo "# aacert - Multi-CA ACME Manager for aaPanel" >> "$target_rc"
            echo "alias aacert=\"python3 ${INSTALL_DIR}/manage.py\"" >> "$target_rc"
            echo "[✓] Detected shell '$current_shell': registered alias in ${target_rc}"
        else
            echo "[✓] Alias already configured in ${target_rc}"
        fi
    fi
}

detect_and_register_alias

# Run the patch installer
bash "${INSTALL_DIR}/install.sh"

echo ""
echo "=========================================================="
echo "  aacert installed successfully!"
echo "=========================================================="
echo "Usage Examples:"
echo "  aacert status"
echo "  aacert setup --ca zerossl --email you@example.com --kid <EAB_KID> --hmac <EAB_HMAC> --enable"
echo "  aacert setup --ca google --email you@example.com --kid <EAB_KID> --hmac <EAB_HMAC> --enable"
echo "  aacert set-ca letsencrypt"
echo "  aacert disable"
echo "=========================================================="
