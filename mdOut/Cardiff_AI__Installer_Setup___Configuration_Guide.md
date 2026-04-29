---
title: "Cardiff AI+ Installer Setup & Configuration Guide"
source_file: "Cardiff_AI__Installer_Setup___Configuration_Guide.doc"
converted_date: "2025-09-17T11:24:59.316585"
format: "markdown"
---

# Cardiff AI+ Installer Setup & Configuration Guide

# # Step 1: Login to AI+ Configuration Panel

Access the configuration panel for AI+ services via:

**URL:**[http://10.20.1.73:8080/servers](http://10.20.1.s:8080/servers)

Ensure that the installer is completed and the server is active.

- * *

# # Step 2: Copy TLS Certificates from Pixstore Ser=ver

To configure RabbitMQ with TLS, you need to securely transfer the requir� certificates from the Pixstore server to the AI+ Server.

## # Source \(Pixstore\) Path

The certificates are located at:

/var/li=b/pixstor/iris/mcs-runtime/mcs-core/rabbitmq/tls

> SSH into the Pixstore server at `10.20.0.160` using the provi�d credentials.
>
> **IP** : 10.20.0.160
>
> **Username** : root
>
> **Password** : edison2

## # Example=:

ssh roo=t@10.20.0.160cd /var/lib/pixstor/iris/mcs-runtime/mcs-core/rabbitmq/tlsls

Expected files:

ca.crt = tls.crt tls.key

## # Copy certificates to AI+ Server

Run the following `scp` command **from the Pixstore ser=ver** to securely copy the files:

scp ca.=crt tls.crt tls.key aiuser@10.20.1.73:/opt/aiplus/certs/rabbitmq

> Ensure that the `/opt/aiplus/certs/rabbitmq` directory alread=y exists on the AI+ Server. If not, create it:

mkdir -=p /opt/aiplus/certs/rabbitmq

## # Verify files on the AI+ Server

Log in to the AI+ Server and confirm the certificates are copied correct=ly:

ls /opt=/aiplus/certs/rabbitmq

Expected output:

ca.crt = tls.crt tls.key

- * *

# # Step 3: Update Configuration GUI

1. Open [http://10.20.1.73:8080/configuration](http://10.20.1.73:8080/configura=tion) in your bro=wser.

2. Go to **Transcribe Summarize → RabbitMQ → Connecti=on**.

3. Enable the **TLS** checkbox.

4. Set the certificate paths to the following:

CA File= : /etc/aiplus/certs/rabbitmq/ca.crtCert File : /etc/aiplus/certs/rabbitmq/tls.crtKey File : /etc/aiplus/certs/rabbitmq/tls.key

> These should point to the mounted path as configured within the containe=r, not necessarily the same as `/opt/` from the host machine.

- * *

## # RabbitMQ Configuration

Fill in the following RabbitMQ details:

- **Host:** `10.20.0.160`

- **Port:** `5671`

- **Username** : jdZRJ0fnfeSd

- **Password** : J00kK9dxJ5VTUxrSgIFl79M1

- * *

# # Step 4: Configure TNS \(Transcrib=e Summarize\) via Server Management

1. Navigate to **Servers → Manage → TNS Config**

1. Ensure your `docker-compose.yml` file for the **Transcr=ibe Summarize** service contains the correct volume mappings and env=ironment variables.

## # Required `volumes:` Section

volumes=: - ${IRIS_MOUNT_POINT:-/mmfs1/data}:/app/media - ${RABBITMQ_CERTS:-/opt/aiplus/certs}:/etc/aiplus/certs

## # Required `environment:` Variables

PORT=�03MEDIA_DIR=/opt/aiplus/mediaOUTPUT_DIR=/opt/aiplus/outputsIRIS_MOUNT_POINT=/mmfs1/dataRABBITMQ_CERTS=/opt/aiplus/certsIMAGE=832471001844.dkr.ecr.us-east-1.amazonaws.com/aiplus/transcribe-summ=arize:1.1.0-rc5

> Confirm that all directories are correctly mounted and the environment v=ariables are accurately reflected in the compose file.

- * *

# # Step 5: Update RabbitMQ Exchange Status in Consu=l

After the Transcribe Summarize container is configured and RabbitMQ cert=s are in place, update the exchange status in **Consul** to en=sure proper routing and connection status.

1. Open the Consul UI:
[http://10.20.1.73:8500/ui/dc1/kv/services/transcribe-sum=marize/rabbitmq/exchanges/status/](http://10.20.1=.73:8500/ui/dc1/kv/services/transcribe-summarize/rabbitmq/exchanges/status/=)

2. Click **Create** to add a new key-value pair.

3. Set the following:

- **Key** = `enabled`

- **Value** = `false`

1. Click **Save** to confirm.

> This disables the exchange by default; it can be toggled to `true after validation steps or service readiness checks.`

- * *

# # Step 6: Configure Notification API Settings

## # 1\. Access Notification API Configuration

Navigate to **configuration → notification-api.**

## # 2\. =TLS Section

- Go to the **TLS** section.

- Confirm that **Enabled** is set to **false**.<=/p>

## # =3. Verify Systems

Ensure that the **Systems** field is set to:

iris

- * *

# # Step 7: Configure RabbitMQ for Notification API

Update the RabbitMQ settings **manually** , just like in the= Transcribe Summarize setup.

## # RabbitMQ → Connection

Field| Value
---|---
Enabled| `true`
Host| `10.20.0.160`
Port| `5671`
Username| jdZRJ0fnfeSd
Password| J00kK9dxJ5VTUxrSgIFl79M1

- * *

## # RabbitMQ → TLS

Field| Path
---|---
Enabled| `true`
CA File| `/etc/aiplus/certs/rabbitmq/ca.crt`
Cert File| `/etc/aiplus/certs/rabbitmq/tls.crt`
Key File| `/etc/aiplus/certs/rabbitmq/tls.key`

- * *

## # RabbitMQ → Exchanges →= Queue Name Template

Update the **Processing Queue Name Template** field with:

pixstor=-fs-events-xchg_{service.component_name}

Then save the configuration.

- * *

# # Step 9: Verify Queue Name Template in Consul

1. Open Consul at: [http://10.20.1.73:8500/ui/dc1/kv/services/notifi�tion-api/rabbitmq/queues/processing/name\_template/edit](http://10.20.1.73:850=0/ui/dc1/kv/services/notification-api/rabbitmq/queues/processing/name_templ=ate/edit)

2. Confirm that the value is set to:

"pixsto=r-fs-events-xchg_{service.component_name}"

- * *

# # Step 10: Restart Notification API Service

After all configurations are saved and verified:

1. Go to the server where the notification-api service is running.

2. Restart the service.

> Make sure the new settings \(certs, queue name templates, etc.\) are picke=d up properly after the restart.

- * *

# # **Step 11: Configure** =`TranscribeSummarize`**Folder to be Processed**

1. **Access Vision UI:**

- Open the Vision interface:
🔗 [https://ca-sn-dev-01.om.cardifflab:9505/](https://ca-sn-dev-01.om.car=difflab:9505/)

- Log in using the **Vision credentials** :

- **Username** : admin-1071

- **Password** : fFlM1EcJdY

2. **Create Folder in Vision and** navigate to the **con=figuration → transcribe-summarize**

- Click on **“Add”** to create a new folder c=onfiguration.

- When prompted:

- **Bucket Name** : Enter the appropriate bucket where files a=re stored.

- **Path** : Set the correct path where the media/files are ex=pected.

3. **Update Config Fields:**

- In the newly added folder config, add **new fields** and pr=ompts.

4. **Add a Test File:**

- Go to vision folder.

- Click on **upload file**.

- Upload a media file for testing.

5. **Verify:**

- Ensure the file is successfully added.

- Confirm that the **new field and its value** are correctly =displayed in the processing view.

- * *

**Reference for Setup at ALT System \(Similar to Cardiff Setup\):
Use the following Miro board as a reference for configuring the cardiff sys=tem setup. It closely mirrors the Cardiff setup and contains necessary conf=iguration details:

[https://miro.com/app/=board/uXjVKBXiPcc=/?moveToWidget=3458764636109907977&cot=14](https://miro.com/app/board/uXjVKBXiPcc=/?moveToWidget=3D3458764636109907977&cot=14) **