#!/usr/bin/env bash
# ====================================================================
# aacert - Safe Uninstaller for aaPanel
# https://github.com/dyzulk/aacert
# ====================================================================
set -e

PANEL_CLASS_DIR="/www/server/panel/class"
PANEL_PLUGIN_DIR="/www/server/panel/plugin"
TARGET_FILE="${PANEL_CLASS_DIR}/acme_v2.py"
BACKUP_FILE="${PANEL_CLASS_DIR}/acme_v2.py.bak_orig"

echo "=== [aacert] Uninstalling aacert from aaPanel ==="

# 1. Remove isolated plugin symlink, residual files, and global binary
rm -rf "${PANEL_PLUGIN_DIR}/aacert"
rm -f "${PANEL_CLASS_DIR}/acme_provider_hook.py"
rm -f "${PANEL_CLASS_DIR}/eab_helper.py"
rm -rf "${PANEL_CLASS_DIR}/aacert_core"
rm -f "/usr/local/bin/aacert"
echo "[✓] Removed ${PANEL_PLUGIN_DIR}/aacert and /usr/local/bin/aacert."

# Remove alias from any shell profile files
for rc in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.bash_profile" "${HOME}/.profile"; do
    if [ -f "$rc" ]; then
        sed -i '/# aacert - Multi-CA ACME Manager for aaPanel/d' "$rc" 2>/dev/null || true
        sed -i '/alias aacert=/d' "$rc" 2>/dev/null || true
    fi
done
echo "[✓] Aliases removed from shell profiles."

# 2. Revert acme_v2.py
if [ -f "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" "$TARGET_FILE"
    echo "[✓] Restored original acme_v2.py from factory backup."
else
    python3 - << 'EOF'
target = "/www/server/panel/class/acme_v2.py"
with open(target, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skipping = False
for line in lines:
    if "[AACERT_HOOK_START]" in line or "[ACME_MANAGER_HOOK_START]" in line:
        skipping = True
        continue
    if "[AACERT_HOOK_END]" in line or "[ACME_MANAGER_HOOK_END]" in line:
        skipping = False
        continue
    if not skipping:
        new_lines.append(line)

with open(target, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("[✓] Hook stripped cleanly from acme_v2.py")
EOF
fi

# 3. Test verification
if [ -f "/www/server/panel/pyenv/bin/python3" ]; then
    /www/server/panel/pyenv/bin/python3 -c "
import sys
sys.path.append('/www/server/panel/class')
import acme_v2
obj = acme_v2.acme_v2()
print('[✓] aaPanel acme_v2 running in original factory mode.')
"
fi

echo "=== [aacert] Uninstallation Complete ==="
echo "Note: ~/.aacert configuration folder remains intact. To remove entirely run: rm -rf ~/.aacert"
