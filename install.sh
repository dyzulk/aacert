#!/usr/bin/env bash
# ====================================================================
# aacert - Patch Installer for aaPanel
# https://github.com/dyzulk/aacert
# ====================================================================
set -e

# Detect installation source directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PANEL_CLASS_DIR="/www/server/panel/class"
PANEL_PLUGIN_DIR="/www/server/panel/plugin"
TARGET_FILE="${PANEL_CLASS_DIR}/acme_v2.py"
BACKUP_FILE="${PANEL_CLASS_DIR}/acme_v2.py.bak_orig"

echo "=== [aacert] Installing aaPanel Hook Patch ==="

if [ ! -d "$PANEL_CLASS_DIR" ] || [ ! -f "$TARGET_FILE" ]; then
    echo "[!] Error: aaPanel does not seem to be installed at /www/server/panel"
    exit 1
fi

# Clean up any legacy files from /www/server/panel/class
rm -f "${PANEL_CLASS_DIR}/acme_provider_hook.py"
rm -f "${PANEL_CLASS_DIR}/eab_helper.py"
rm -rf "${PANEL_CLASS_DIR}/aacert_core"

# 1. Symlink isolated package into aaPanel plugin directory
mkdir -p "$PANEL_PLUGIN_DIR"
ln -sfn "${SCRIPT_DIR}" "${PANEL_PLUGIN_DIR}/aacert"
echo "[✓] Isolated aacert module linked to ${PANEL_PLUGIN_DIR}/aacert"

# 2. Inject safe micro-patch into acme_v2.py if not already present
if grep -q "\[ACME_MANAGER_HOOK_START\]" "$TARGET_FILE" || grep -q "\[AACERT_HOOK_START\]" "$TARGET_FILE"; then
    echo "[*] Updating existing hook patch in acme_v2.py..."
    python3 - << 'EOF'
import sys

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

hook_code = [
    "        # [AACERT_HOOK_START]\n",
    "        try:\n",
    "            import sys\n",
    "            _aacert_plugin = '/www/server/panel/plugin/aacert'\n",
    "            if _aacert_plugin not in sys.path:\n",
    "                sys.path.insert(0, _aacert_plugin)\n",
    "            import acme_provider_hook\n",
    "            acme_provider_hook.apply_hook(self)\n",
    "        except Exception:\n",
    "            pass\n",
    "        # [AACERT_HOOK_END]\n"
]

inserted = False
final_lines = []
for line in new_lines:
    final_lines.append(line)
    if not inserted and "self._task_obj = None" in line:
        final_lines.extend(hook_code)
        inserted = True

with open(target, "w", encoding="utf-8") as f:
    f.writelines(final_lines)
EOF
    echo "[✓] Hook patch updated with plugin directory isolation."
else
    # Create clean backup if not exists
    if [ ! -f "$BACKUP_FILE" ]; then
        cp "$TARGET_FILE" "$BACKUP_FILE"
        echo "[✓] Original backup created at: ${BACKUP_FILE}"
    fi

    # Inject patch after 'self._task_obj = None'
    python3 - << 'EOF'
import sys

target = "/www/server/panel/class/acme_v2.py"
with open(target, "r", encoding="utf-8") as f:
    lines = f.readlines()

hook_code = [
    "        # [AACERT_HOOK_START]\n",
    "        try:\n",
    "            import sys\n",
    "            _aacert_plugin = '/www/server/panel/plugin/aacert'\n",
    "            if _aacert_plugin not in sys.path:\n",
    "                sys.path.insert(0, _aacert_plugin)\n",
    "            import acme_provider_hook\n",
    "            acme_provider_hook.apply_hook(self)\n",
    "        except Exception:\n",
    "            pass\n",
    "        # [AACERT_HOOK_END]\n"
]

inserted = False
new_lines = []
for line in lines:
    new_lines.append(line)
    if not inserted and "self._task_obj = None" in line:
        new_lines.extend(hook_code)
        inserted = True

if not inserted:
    print("[!] Could not locate anchor 'self._task_obj = None' in acme_v2.py")
    sys.exit(1)

with open(target, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("[✓] Safe micro-patch injected into acme_v2.py")
EOF
fi

# 3. Create global symlink in /usr/local/bin
chmod +x "${SCRIPT_DIR}/aacert"
if [ -d "/usr/local/bin" ]; then
    ln -sf "${SCRIPT_DIR}/aacert" "/usr/local/bin/aacert"
    echo "[✓] Global command linked: /usr/local/bin/aacert"
fi

# 4. Smart shell profile detection & alias registration
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
            # Fallback for sh, dash, ksh, etc.
            if [ -f "${HOME}/.profile" ]; then
                target_rc="${HOME}/.profile"
            fi
            ;;
    esac

    # If detected target doesn't exist, check standard candidates
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
            echo "alias aacert=\"${SCRIPT_DIR}/aacert\"" >> "$target_rc"
            echo "[✓] Detected shell '$current_shell': registered alias in ${target_rc}"
        else
            echo "[✓] Alias already configured in ${target_rc}"
        fi
    fi
}

detect_and_register_alias

# 5. Test import inside aaPanel's python environment
if [ -f "/www/server/panel/pyenv/bin/python3" ]; then
    /www/server/panel/pyenv/bin/python3 -c "
import sys
sys.path.append('/www/server/panel/class')
import acme_v2
obj = acme_v2.acme_v2()
print('[✓] aaPanel acme_v2 initialized cleanly with isolated plugin hook!')
"
fi

echo "=== [aacert] Installation Finished Successfully ==="
