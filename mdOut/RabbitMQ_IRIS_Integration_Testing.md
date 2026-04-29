---
title: "RabbitMQ IRIS Integration Testing"
source_file: "RabbitMQ_IRIS_Integration_Testing.doc"
converted_date: "2025-09-17T11:24:59.428298"
format: "markdown"
---

# RabbitMQ IRIS Integration Testing

# # Transcribe Summarize Testing

- Jul 18, 2025: Erik was able to successfully connect to the RMQ server. H=e’s going to update the aipluscommon module which T&S \(and Noti=fication API\) need to be rebuilt with to properly connect: [=AI-812](3D"https://perifery.atlassian.net/browse/AI-812") \- RabbitMQ does not pass the correct SSL connection cont=ext Done

- Jul 19, 2025: [Justin Toribio](https://perifer=y.atlassian.net/wiki/people/712020:24328ab5-a766-4724-bd74-fe21ffe69928?ref=3Dconfluence) was ab=le to connect to the node 1 RMQ from his local env. He tested some jobs and= they successfully published to the vision metadata exchange.

- <=/li>
- [https://github.com/workflow-intelligence-nexus/TranscribeSumm=arize/pull/28](https=://github.com/workflow-intelligence-nexus/TranscribeSummarize/pull/28) is approved. [Jamie Sabin=o](h=ttps://perifery.atlassian.net/wiki/people/712020:01864eaf-d220-4f25-85a8-d9�fb325efb?ref=confluence) just needs to fix the build, re-deploy the image to Lambda 1, and we=E2��ll confirm everything looks good there as well.

- This PR also fixes this bug: [AI-813](https://perifery.atlassi=an.net/browse/AI-813) \- Transcr=ibeSummarize R1 Bug - Consul showing 2 different services for T&S, Rabb=itMq connection issue Done =

- Jul 20, 2025: Gareth requested changes to the data payload format, track� by this ticket: [AI-815](https://perifery.atlassian.net/browse=/AI-815) \- TranscribeSummarize =R1 Bug - Need to align message data to Vision exchange Done

- [Justin Toribio](https://perifery.atlassian.ne=t/wiki/people/712020:24328ab5-a766-4724-bd74-fe21ffe69928?ref=confluence) made the changes, pu=blished another test job to the vision exchange and asked Gareth to review.= If he gives the thumbs up, I will create the PR. I need to fix the unit te=sts due to the changes.

# # Notificati=on API Testing

- Jul 20, 2025: [Bedri Bahru \(Unlicensed\)](https://perifer=y.atlassian.net/wiki/people/712020:224068bd-1695-42a9-8521-cb15b95812f4?ref=3Dconfluence) updated aipluscommon version on No=tificationAPI and was able to connect, consume a “FileCreated�=9C event message and successfully trigger T&S with the correct structu=re and payload. Tested on both local \(no TLS\) and node 1/ftl-dev-sn-01\(TLS\)= RMQ servers.

- update the T&S payload to include **tenant\_id**

- PR: [https://github.com/StartupAgile-WIN/NotificationAPI/pull/45](h=ttps://github.com/StartupAgile-WIN/NotificationAPI/pull/45) \(Approved=/Merged\)

- Jul 21, 2025: NotificationAPI Deployment and Verification on `lambd�`

- Configuration Verification

- Verified that **Iris** was enabled via **ConfigGUI / =Consul**.

- Confirmed **T &S** was correctly configured via **=ConfigGUI / Consul**.

- Updated **RabbitMQ configurations** in **Consul:**

- Set correct **endpoint** and **credentials** \(=host, username, password\).

- Specified valid **TLS certificate paths**.

- Configured `queues/processing/name_template` under **na=me\_template**.

- Container and Connectivity

- Verified that **TLS certificate paths** were properly mount� to the **NotificationAPI** container.

- Confirmed that **NotificationAPI** successfully connected t=o **RabbitMQ**.

- T&S Registration and Event Processing

- Registered a folder with **T &S** as the processor, alon=g with the default processing config using the **IrisBucket** =object via **NotificationAPI Swagger**.

- Dropped an audio/video file into the configured **bucket folder.**

- Verified that a **FileCreated** event was successfully proc=essed.

- Confirmed that the correct **payload** \(event info and proc=essing config\) was sent to **T &S**.

- Jul 22, 2025: A new bug \( [AI-838](https://perifery.atlassian.=net/browse/AI-838) \- Notificati=on API - Configured Buckets not Working as expected. Done \) was discovered when configuring and testi=ng the bucket/space root \(space01/\) and dropping files in subfolders.

- Further testing revealed the issue is specific to the root folder and th=e config inheritance process works on configured folders and subfolders

=
- [Be=dri Bahru \(Unlicensed\)](https://perifery.atlassian.ne=t/wiki/people/712020:224068bd-1695-42a9-8521-cb15b95812f4?ref=confluence) Verified the bug on lambda2, made the changes to= fix the bug and tested and verified the bug is fixed

- PR: [Pull 48](https://github.com/workflow-intel=ligence-nexus/NotificationAPI/pull/48) \(Merged=\)