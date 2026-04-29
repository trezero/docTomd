---
title: "Troubleshooting: Pixstore commands not in path of client system"
source_file: "Troubleshooting__Pixstore_commands_not_in_path_of_client_system.doc"
converted_date: "2025-09-17T11:24:59.472524"
format: "markdown"
---

# Troubleshooting: Pixstore commands not in path of client system

# GPFS Commands: Run as **root Only \(PATH Setup\)**

# # Why<=/h2>

- GPFS tools fan out over SSH and manage cluster state.

- For safety and consistency, we run them **as root only** \(n=o permission changes on `/usr/lpp/mmfs`\).

- * *

# # Option A — Use a r=oot shell \(`sudo -i`\) and set PATH for root

1. Open a root login shell:

sudo -i

1. Add GPFS bin to **root’s** PATH \(persistent\):

cat >=;> /root/.bashrc <<'EOF'# GPFS (Spectrum Scale) tools in PATH for rootif [ -d /usr/lpp/mmfs/bin ] && [[ ":$PATH:" != *":/usr/lpp/mmfs/b=in:"* ]]; then export PATH="$PATH:/usr/lpp/mmfs/bin"fiEOFcat >> /root/.profile <<'EOF'# Ensure PATH for login shellsif [ -d /usr/lpp/mmfs/bin ] && [[ ":$PATH:" != *":/usr/lpp/mmfs/b=in:"* ]]; then export PATH="$PATH:/usr/lpp/mmfs/bin"fiEOF

1. Reload and verify:

source =/root/.bashrcwhich mmgetstate

> From now on, in a root shell, just run:

mmgetst=ate -ammstartupmmmount mmfs1 -N per-aimmlsmount mmfs1

- * *

# # Option B — Keep using sudo <cmd> from your user

By default, `sudo` uses its own **secure\_path** =which might not include GPFS. Add it **for sudo only** \(does n=ot affect non-root users\).

1. Edit sudoers safely:

sudo vi=sudo

1. Append \(or merge with existing `secure_path`\) so it includes =`/usr/lpp/mmfs/bin`:

Default=s secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/b=in:/usr/lpp/mmfs/bin"

1. Verify:

sudo wh=ich mmgetstate

> Now you can run:

sudo mm=getstate -asudo mmmount mmfs1 -N per-ai

- * *

# # Option C — Lightwe=ight root-only shims \(no PATH edits\)

Create tiny wrappers in `/usr/local/sbin` \(already in root�=80�s PATH\). These call the real binaries but still require root to be us�ul.

sudo te=e /usr/local/sbin/mmgetstate >/dev/null <<'EOF'#!/usr/bin/env bashexec /usr/lpp/mmfs/bin/mmgetstate "$@"EOFsudo chmod 755 /usr/local/sbin/mmgetstatefor c in mmstartup mmmount mmlsmount mmumount mmshutdown; do sudo tee /usr/local/sbin/$c >/dev/null <<EOF#!/usr/bin/env bashexec /usr/lpp/mmfs/bin/$c "\$@"EOF sudo chmod 755 /usr/local/sbin/$cdone

Verify:

sudo -iwhich mmgetstatemmgetstate -a

- * *

# # Recommended Usage

- Day-to-day:

sudo -i= # become rootmmgetstate -ammmount mmfs1 -N per-ai

- If you prefer staying as your user:

- Use **Option B** once → `sudo mmgetstate -a works everywhere.`

> **Note:** We intentionally **did not** relax d=irectory permissions on `/usr/lpp/mmfs` or expose GPFS to non-ro=ot users.