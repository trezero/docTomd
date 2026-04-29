---
title: "Manual Removal of AI+ Installer"
source_file: "Manual_Removal_of_AI__Installer.doc"
converted_date: "2025-09-17T11:24:59.399298"
format: "markdown"
---

# Manual Removal of AI+ Installer

## # Currently, there is **no one-click or official way** to r=emove the AI+ installer along with its installation data and the AI+ Admin.=

To **completely wipe AI+ Admin** and all its related servic=es, containers, and configurations from your system, follow the steps below= **carefully**.

This guide assumes, you are having a server where you are only running s=ervices installed through **AI+ Admin**. So, we will remove a =lot of containers, images, volumes, and networks and do some system pruning=.

**Important:** If manual removal is not successful, it�=80�s **best to create a new user** and perform a fresh inst=allation. This ensures no residual conflicts, as the installer currently do=esn’t support upgrades.

- * *

## # Ste=p-by-Step Removal Instructions:

### # 1\. **Stop =the pm2 process**

Remove AI+ folder and common tool folders:

pm2 sto=p allpm2 delete all

- * *

### # 2\. **Delete environment and config directories**

Remove AI+ folder and common tool folders:

rm -rf =~/.aiplus ~/.aws ~/.docker ~/.npm ~/.nvm ~/.pm2

- * *

### # 3=. **Stop and remove all Docker containers**

docker =stop $(docker ps -aq)docker rm -f $(docker ps -aq)

- * *

### # 4\. Remove Docker images and volumes

docker =rmi -f $(docker images -q)docker volume rm $(docker volume ls -q)

- * *

### # 5\. **Clean up Docker networks and system resources**

docker =network prune -fdocker system prune -a --volumes -f

- * *

### # **6\. Remove crontab entries \(used to authenticat=e docker to aws ECR\)**

# Warni=ng this is irreversible so all crontab entries will be lost.# If you don't want that, you can mannually open the crontab entries and ed=it.# Remove all crontab entriescrontab -r

- * *

### # 7\. **Check for active services on known AI+ ports**

AI+ Admin and it’s services runs on ports like:

- `8080` – Common web apps

- `11434` – Ollama

- `9003` – MetaGen

Run:

sudo ne=tstat -tulpn | grep -E '8080|11434|9003'

- * *

### # 8=. **Kill processes running on these ports**

For each PID returned:

sudo ki=ll -9 <PID>

Repeat for `11434`, `9003`, etc.

- * *

## # 9\. Remove Authorized SSH Keys for Fresh Installation

If you're preparing the system for a **completely fresh installati=on** under a new or reset user, it's good practice to remove any exi=sting SSH public keys that may have been used for earlier access.

To remove the existing SSH keys:

rm ~/.s=sh/authorized_keys

> **Note:** This will remove all authorized SSH keys for the =current user.
> If you want to selectively remove keys, open the file using a text editor a=nd delete the specific lines:

nano ~/=.ssh/authorized_keys