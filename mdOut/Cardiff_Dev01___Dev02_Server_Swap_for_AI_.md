---
title: "Cardiff Dev01 / Dev02 Server Swap for AI+"
source_file: "Cardiff_Dev01___Dev02_Server_Swap_for_AI_.doc"
converted_date: "2025-09-17T11:24:59.327860"
format: "markdown"
---

# Cardiff Dev01 / Dev02 Server Swap for AI+

Currently in Cardiff, the team requires switching AI+ node to po=int to a different Vision instance.

Step 1 - Stop the services \( at the time of writing this, we are working= with NotifiationAPI and Transcribe Summarize

On AI+ Admin [http://10.20.1.73:8080/servers](http://10.20.1.73:8080/s=ervers) go to “=Manage”

Click the stop button on “notification-api-aiplus-notification-a=pi-1” and “transcribe-summarize-aiplus-transcribe-summarize=-1”

Step 2 - Remove current mount and Remount with target Server \(160 or 162= for example\):

Reference https://arcapix.atlassian.net/wiki/spaces/=~bevans/pages/5089165411/NFS+Export+for+AI

sudo um=ount /mmfs1 sudo mount 10.20.0.{160/162}:/mmfs1 /mmfs1 #validate the mountmount | grep /mmfs1

Step 3 - Reconfigure Rabbit for both NotificationAPI and TranscribeSumma=rize

Click on “Configurations” and you will see the two servi�s listed:

Start with transcribe-summarize, click on it, and then click the �=9CService Config” , and select “RabbitMQ”

Change the following items:

Host, Username, Password, TLS \(CA File, Cert File, Key File\)

NOTE: for the cert files, we have both loaded in the ai+ node, default i=s to Dev01 node, override this to point to Dev02 by appending “\_dev=2” before the file extension.

Dev01 settings:

/etc/aiplus/certs/rabbitmq/ca.crt

/etc/aiplus/certs/rabbitmq/tls.crt

/etc/aiplus/certs/rabbitmq/tls.key

Dev02 settings:

/etc/aiplus/certs/rabbitmq/ca\_dev2.crt

/etc/aiplus/certs/rabbitmq/tls\_dev2.crt

/etc/aiplus/certs/rabbitmq/tls\_dev2.key

Step 4 - Click Save, and start up TranscribeSummarize

Go to <http://10.20.1.73:8080/servers> , and press the start =button for that service.

Step 5 - Repeat steps 3-4 for NotificationAPI.

Step 6 - Test/ Validate via Vision UI.