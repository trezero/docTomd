---
title: "GPFS Commands to work with Pixstore"
source_file: "GPFS_Commands_to_work_with_Pixstore.doc"
converted_date: "2025-09-17T11:24:59.389696"
format: "markdown"
---

# GPFS Commands to work with Pixstore

# Everyday= Commands

# # Check GPFS State

/usr/lp=p/mmfs/bin/mmgetstate -a

Shows the state of all nodes in the GPFS cluster.

- * *

# # Start GPFS

/usr/lp=p/mmfs/bin/mmstartup -a

Starts GPFS on all nodes.

- * *

# # Mount Filesystem<=/h2>

/usr/lp=p/mmfs/bin/mmmount mmfs1 -a

Mounts the `mmfs1` filesystem across all nodes.

Check mount:

/usr/lp=p/mmfs/bin/mmlsmount mmfs1

- * *

# # Verify Mo=unted Filesystem

df -h |= grep mmfs

Shows mounted GPFS filesystems and usage.

- * *

# # Node-Spec=ific Operations

## # Chec=k GPFS state for a single node

/usr/lp=p/mmfs/bin/mmgetstate -N <node-name>

## # Mount mmfs1 on a single node

/usr/lp=p/mmfs/bin/mmmount mmfs1 -N <node-name>

- * *

# # SSH =& Known Hosts Management

## # Clear and =Refresh SSH Keys

for h i=n per-ai alt-mn-001.pixstor alt-sn-001.pixstor alt-gw-001.pixstor alt-ng-00=1.pixstor alt-nvme-001.pixstor \ 127.0.1.1 10.100.0.1 10.100.0.2 10.100.0.3 10.100.0.4 10.100.0.5 ;= do ssh-keygen -R "$h" >/dev/null 2>&1 || truedonessh-keyscan -H per-ai alt-mn-001.pixstor alt-sn-001.pixstor alt-gw-001.pixs=tor alt-ng-001.pixstor alt-nvme-001.pixstor \ 10.100.0.1 10.100.0.2 10.100.0.3 10.100.0.4 10.100.0.5 >>=; ~/.ssh/known_hosts

- * *

# # Quick Files=ystem Access

ls -lah= /mmfs1ls -lah /mmfs1/datals -lah /mmfs1/data/space01

Use these to validate access and contents of the Pixit filesystem.