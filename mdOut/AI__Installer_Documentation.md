---
title: "AI+ Installer Documentation"
source_file: "AI__Installer_Documentation.doc"
converted_date: "2025-09-17T11:24:59.245599"
format: "markdown"
---

# AI+ Installer Documentation

# # **Overview**

The AI+ Installer does the installation of AI+ services, including sytem= pre-checks, AWS configuration, and service integrations via a web-based UI=.

This guide is going to help you in following the steps required to insta=ll it on a fresh system.

- * *

# # **1\. Prerequisit=es**

Before starting the installation:

- Ensure GPU \(Nvidia\) drivers are correctly installed.

- Copy the AI+ installation file to the **home directory** of= the user that will install the AI+ Admin Panel and run the AI+ services.
- Syntax:

scp <=;path_to_installer_file> <remote_user>@<remote_host>:<tar=get_directory>

- For example:

scp aip=lus-installer-2025_07_23 aiplus-testing@10.161.0.72:~

- Make the installer file as an executable. For example:

chmod +=x aiplus-installer-2025_07_23

- * *

# # **2\. Runni=ng the Installer**

## # **Step 1: =Launch Installer**

- Run the installer file. For example:

./aipl=us-installer-2025_07_23)

- Open your browser and go to `http://hostIP:3000`.

## # **S=tep 2: Accept License Agreement**

- Click **Next**.

- Read the **End User License Agreement \(EULA\)**.

- Scroll to the bottom and click **Agree & Next**.

## # **Step 3=: Requirements Check**

- Review hardware and system requirements.

- Click **Next**.

## # **Step =4: Installation Prompt**

- Give the password for the user \(sudo access is required for installing s=ome packages\)

- Click **Install.**

- * *

# # **3\. AWS Conf=iguration**

The installer requires AWS credentials to fetch the images of the servic=es from ECR:

## # **Step 1:= Enter Credentials**

- **AWS Access Key ID** → Click **Send** =

- **AWS Secret Access Key** → Click **Send**

- **Default Region** \(optional\) → Click **Send <=/strong>**

- **Default Output Format** \(optional\) → Click Send

## # **Ste=p 2: Continue Installation**

- Click **Next** to proceed.

- * *

# # **4.= Completing the Installation**

- Click **Install** to begin the installation.

- Once finished, click the provided link to open the **Admin UI.**

- It should be at the `http://hostIP:8080` endpoint.

- * *

# # **5\. �sy Setup Wizard \(Admin UI\)**

## # **Step 1:= Service Selection**

- Click **Next** on the welcome screen.

- Select the services you want to install \(e.g MetaGen\).

- Click **Next**.

## # Step 2: Integration Configuration

- Choose the integrations you want to configure. \(e.g Iris\)

- Click **Next**.

## # **Step 3: M=ount Path Setup**

- For any selected integration, **set the mount path as** /mmfs1/data.

- Click **Next**.

## # **Step 4: Con=firmation**

- Review your selections.

- Click **Install** to begin the final setup.

> Note: Installation time may vary based on selected services and internet= connection.

## # **Step 5: Compl=etion**

- Once installation completes, click **Finish**. You will be =then redirected to the **AI+ Admin UI.**

- * *

# # **6\. Post-In=stallation**

You can now access and manage AI+ services via the **Admin UI.**

You can do things such as stop, start, restart them as well as view logs=, check API docs for any selected service, pull various versions from ECR f=or any of the services.

- * *

# # **7\. Addi=tional References**

### # For more reference, download the detailed insta=llation guide in PDF format: