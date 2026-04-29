---
title: "Fix NVIDIA Driver issue causing inability to boot"
source_file: "Fix_NVIDIA_Driver_issue_causing_inability_to_boot.doc"
converted_date: "2025-09-17T11:24:59.375558"
format: "markdown"
---

# Fix NVIDIA Driver issue causing inability to boot

If your Ubuntu 22 system no longer boots due to NVIDIA driver is=sues, you can use a recovery method to purge the NVIDIA drivers from the co=mmand line. Here's a step-by-step guide:

## # 1\. **Boot into Recovery Mode**

- Reboot your system.

- Hold **Shift** or press **Esc** during boot to= access the GRUB menu.

- Select **Advanced options for Ubuntu**.

- Choose a **Recovery mode** kernel.

## # 2\. =**Drop to Root Shell**

- In the recovery menu, choose **Root** to drop into a root s=hell.

## # 3\. **Remount File System with Write Permissions**

By default, the file system is mounted as read-only. Remount it as read-=write:

bash

Copy code

`mount -o remount,rw /`

## # =4. **Purge NVIDIA Drivers**

Run the following commands to remove all NVIDIA-related packages:

bash

Copy code

`apt-get purge '^nvidia-.*' -y apt-get autoremove --purge -y apt-ge=t clean`

## # 5\. **Reinstall Default Nouveau Driver \(Optional\)=**

If you want to fall back to the open-source Nouveau driver:

bash

Copy code

`apt-get install xserver-xorg-video-nouveau -y`

## # 6\. Update GRUB

Update your GRUB configuration to ensure smooth booting:

bash

Copy code

`update-grub`

## # 7\. =**Reboot the System**

Exit the root shell and reboot:

bash

Copy code

`reboot`

Your system should now boot with the NVIDIA drivers removed. Let me know= if you encounter any issues during these steps.