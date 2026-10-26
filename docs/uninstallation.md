# Rollback and uninstallation

## Recommended

Run the uninstaller, then remove the local aacert installation and configuration
if you no longer need them:

```bash
aacert uninstall
rm -rf ~/.aacert
```

If the `aacert` command is unavailable:

```bash
bash ~/.aacert/uninstall.sh
rm -rf ~/.aacert
```

The uninstaller removes aliases from shell profile files. To clear the alias
from the current shell immediately:

```bash
unalias aacert 2>/dev/null || true
```

## Manual cleanup

Use this only if the uninstaller cannot restore aaPanel:

```bash
rm -f /www/server/panel/class/acme_provider_hook.py
rm -f /www/server/panel/class/eab_helper.py
rm -f /usr/local/bin/aacert

for rc in ~/.bashrc ~/.zshrc ~/.bash_profile ~/.profile; do
  [ -f "$rc" ] && sed -i '/# aacert - Multi-CA ACME Manager for aaPanel/d;/alias aacert=/d' "$rc"
done

if [ -f "/www/server/panel/class/acme_v2.py.bak_orig" ]; then
  cp /www/server/panel/class/acme_v2.py.bak_orig /www/server/panel/class/acme_v2.py
  rm -f /www/server/panel/class/acme_v2.py.bak_orig
fi

rm -rf ~/.aacert
bt restart
```

## Verify restoration

Check that aaPanel's ACME file no longer contains the aacert hook:

```bash
grep "AACERT_HOOK" /www/server/panel/class/acme_v2.py \
  || echo "Original factory state verified (no hooks present)"
```

If aaPanel's Python environment is available, verify that its ACME module loads:

```bash
/www/server/panel/pyenv/bin/python3 -c \
  "import acme_v2; obj = acme_v2.acme_v2(); print('aaPanel ACME engine running in native factory mode.')"
```
