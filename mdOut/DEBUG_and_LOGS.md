---
title: "DEBUG and LOGS"
source_file: "DEBUG_and_LOGS.doc"
converted_date: "2025-09-17T11:24:59.344848"
format: "markdown"
---

# DEBUG and LOGS

List of example commands for AI+ service logs

1 - **View events for a file uploaded to Vision** \(example =file name uploaded to vision “js2-test.mp4” \), this will lo=ok for the file name and pull the CorrelationID to scan all logs/events for= this file in NotificationID \(which can be used for sub services, Transcrib=eSummarize etc.\)

aiplus-=testing@lambda1:~$ docker logs --since 10m notification-api-aiplus-notifica=tion-api-1 2>&1 | awk -v target="js2-test.mp4" ' $0 ~ target { corr = ""; n = split($0, a, /"CorrelationId": "/); if (n > 1) { split(a[2], b, "\""); corr = b[1]; } } corr != "" && $0 ~ corr'