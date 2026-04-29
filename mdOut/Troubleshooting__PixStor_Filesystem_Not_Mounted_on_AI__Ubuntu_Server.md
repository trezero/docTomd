---
title: "Troubleshooting: PixStor Filesystem Not Mounted on AI+ Ubuntu Serve=r"
source_file: "Troubleshooting__PixStor_Filesystem_Not_Mounted_on_AI__Ubuntu_Server.doc"
converted_date: "2025-09-17T11:24:59.484401"
format: "markdown"
---

# Troubleshooting: PixStor Filesystem Not Mounted on AI+ Ubuntu Serve=r

# # Overview

This guide explains how to diagnose and fix the issue where the PixStor/=GPFS filesystem \(`mmfs1`\) appears as an empty directory and does= not show up in `df -h`.

Symptoms include:

- `/mmfs1` can be listed, but only shows empty subdirectories \(=no data\).

- `df -h` does not display `mmfs1` as a mounted file=system.

- Running GPFS commands \(`mmgetstate`, `mmmount`, mmlsmount\) results in `command not found`.

- * *

# # Root Cause

- The GPFS binaries were not in the system `PATH`.

- SSH trust between the AI+ server and PixStor cluster nodes was not estab=lished, causing GPFS commands to hang or fail.

- The filesystem was not mounted locally on the AI+ server.

- * *

# # Solution

## # Step 1: Confirm GPFS Packages are Instal=led

Run:

dpkg -l= | grep gpfs

You should see packages like `gpfs.base`, `gpfs.license.=std`, etc.
If they are missing, the PixStor client is not installed.

- * *

## # Step 2: Verify GPFS Binaries Location

Check if binaries exist:

ls /usr=/lpp/mmfs/bin

If present, prepend this directory to your PATH:

export =PATH=$PATH:/usr/lpp/mmfs/bin

\(Optional: make permanent by adding to `/etc/profile.d/gpfs.sh.)`

- * *

## # Step 3: Fix Hostname Resolution

Ensure `/etc/hosts` maps the AI+ server correctly:

sudoedi=t /etc/hosts

Add or fix:

192. 168=.18.244 per-ai

Remove any line mapping `per-ai` to `127.0.1.1`.

- * *

## # Step 4: Reset SSH Known Hosts

Clear old host key entries and re-seed them:

for h i=n per-ai alt-mn-001.pixstor alt-sn-001.pixstor alt-gw-001.pixstor alt-ng-00=1.pixstor alt-nvme-001.pixstor \ 127.0.1.1 10.100.0.1 10.100.0.2 10.100.0.3 10.100.0.4 10.100.0.5 ;= do ssh-keygen -R "$h" >/dev/null 2>&1 || truedonessh-keyscan -H per-ai alt-mn-001.pixstor alt-sn-001.pixstor alt-gw-001.pixs=tor alt-ng-001.pixstor alt-nvme-001.pixstor \ 10.100.0.1 10.100.0.2 10.100.0.3 10.100.0.4 10.100.0.5 >>=; ~/.ssh/known_hosts

- * *

## # Step 5: Verify SSH Access to Cluster Nodes=

Log in once to each PixStor node as `root` \(password from env=ironment documentation, typically `edison02`\):

ssh roo=t@alt-mn-001.pixstorssh root@alt-sn-001.pixstorssh root@alt-gw-001.pixstorssh root@alt-ng-001.pixstorssh root@alt-nvme-001.pixstor

Accept fingerprints and confirm you can log in. This step ensures GPFS c=an communicate without blocking.

- * *

## # Step 6: Start GPFS Locally

On the AI+ node \(`per-ai`\):

sudo mm=startup

Check state:

sudo mm=getstate -N per-ai

You should see:

Node nu=mber Node name GPFS state-------------------------------------7 per-ai active

- * *

## # Step 7: Mount the Filesystem

Mount `mmfs1` on the AI+ server only:

sudo mm=mount mmfs1 -N per-ai

Verify:

sudo mm=lsmount mmfs1df -h | grep mmfsls -lah /mmfs1/data/space01

Expected output:

- `mmfs1` shows in `df -h`

- `/mmfs1/data/space01` contains media data

- * *

# # Final Verification

If successful:

df -h |= grep mmfs

Shows something like:

mmfs1 = 224T 26T 199T 12% /mmfs1

And:

ls /mmf=s1/data/space01

Shows customer/media content.

- * *

# # Notes

- Always use `-N per-ai` when mounting or starting locally to a=void SSH fan-out to all nodes.

- If SSH trust is broken again, repeat **Step 4 + Step 5**.

- For repeated use, configure sudoers to allow limited GPFS commands witho=ut full root login.