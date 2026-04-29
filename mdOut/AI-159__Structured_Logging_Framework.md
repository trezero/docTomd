---
title: "AI-159: Structured Logging Framework"
source_file: "AI-159__Structured_Logging_Framework.doc"
converted_date: "2025-09-17T11:24:58.783058"
format: "markdown"
---

# AI-159: Structured Logging Framework

- Architectur=e
- JSON Logging=
- Logging =Pipeline
- Development vs. Production Considerations
- Core Comp=onents
- Configurat=ion
- Implement=ation
- Dynamically Adjusting Log Levels
- Loading Configuration from a File
- Logging= Practices
- Field Ma=nagement
- Docker= Integration
- =Elasticsearch Field Types
- Data Dict=ionary

This logging framework provides structured, flexible, and easily configu=rable logging for Python applications. It integrates structlog for structur� logs and Python's built-in logging module for precise control, with cust=om features for runtime configurability across development and production e=nvironments.

- **Dynamic Logger Configuration** : Modify log levels and act=ivate/deactivate specific loggers during runtime

- **Structured Logging** : Output logs in JSON format for anal=ytics platforms like Elasticsearch or Splunk

- **Accurate Callsite Information** : Ensure logs accurately r�erence the calling file, function, and line number

- **Custom Log Levels** : Support additional levels, such as T=RACE, for detailed debugging

# Architecture

# # JSON Logging

All AI+ logs will be in JSON format. The industry has widely adopted str=uctured logging at the application level for several compelling reasons:

- **Reliability** : Application-generated structured logs guar=antee correct format

- **Field consistency** : Developers ensure consistent field n=aming

- **Native nested object support** : Complex objects are handl� appropriately

- **Collection tool independence** : Logs maintain structure r=egardless of collection mechanism

Structured logging represents a significant advancement over traditional= text-based logging by eliminating complex parsing and pre-processing befor=e ingestion into analytics platforms like Elasticsearch. When applications =emit plaintext logs, processing pipelines must implement regex patterns, gr=ok filters, or custom parsers to extract information—approaches tha=t are brittle, require maintenance when log formats change, and introduce p=rocessing overhead in high-volume environments.

Our structured JSON logging approach delivers logs to Elasticsearch alre�y organized into properly typed fields with consistent naming. This "sche=ma on write" at the application level avoids the error-prone "schema on rea=d" approach of traditional logging. The benefits include reduced processing= overhead, higher reliability by eliminating potential parsing failures, an=d immediate analyzability without waiting for pre-processing to complete.

Because our application precisely controls its log structure and fields,= we gain consistency across all environments—the same log from a lo�l development machine, a Docker container, or a Kubernetes pod will have =identical structure. This consistency is invaluable when building dashboard=s, alerts, and automated analysis tools that depend on predictable field na=mes and types.

# # Logging Pipeli=ne

All logs will be shipped directly from Docker to Fluent Bit using the Fl=uentd logging driver. This approach offers significant advantages over trad=itional file-based logging by eliminating the need to manage log file rotat=ion, compression, archiving, and cleanup processes. The streamlined method =reduces disk I/O operations, prevents log file buildup, and ensures logs ar=e immediately available in our analytics platform without delay or data los=s during rotations.

The opt-in nature of this configuration gives precise control over which= containers' logs are collected, allowing filtering of noisy services at th=e source rather than through post-processing. This architecture also provid=es a seamless migration path to Kubernetes, where the same logging patterns= can be implemented through pod specifications and cluster-wide logging con=figurations.

# # Development vs. Production Considerations

Our implementation previously used pretty-printed JSON for improved cons=ole readability during development:

def pre=tty_print_json(logger, method_name, event_dict): """ Pretty-prints JSON logs to the console for readability. """ event_dict["event"] = json.dumps(event_dict["event"], indent=4) \ if isinstance(event_dict["event"], (dict, list)) else event_dict["e=vent"] return event_dict

While this approach helps with local debugging, it creates problems when= forwarding logs to analytics platforms:

- Console logs must be machine-readable—pretty-printed logs with i=ndentation are difficult to parse

- Structured data must remain as objects, not be converted to strings

<=/li>
- Field types must maintain consistency across all log messages

# # Core Components=

**AiPlusBoundLogger**

- Extends structlog's BoundLogger

- Dynamically injects metadata including filename, func\_name, and lineno i=nto logs

**Dynamic Configuration**

- Configures log levels from a dictionary or file

- Allows runtime adjustments via Python's logging hierarchy

**Processors**

- JSONRenderer for structured log output

- TimeStamper to add timestamps

- StackInfoRenderer for detailed exception stack traces

**TRACE Log Level**

- Adds a TRACE level below DEBUG, ideal for verbose debugging

# # Configuration

Example Configuration File \(logging\_config.json\):

{ "default_level": "WARNING", "loggers": { "aiplus": "DEBUG", "aiplus.facialRecognition": "INFO", "other.module": "ERROR" }}

This file defines:

- A default global log level \(WARNING\)

- Specific log levels for individual loggers

# # Implementation<=/h2>

from lo=gger import get_loggerlogger = get_logger("aiplus.facialRecognition")logger.info("Processing started for facial recognition.")logger.error("An error occurred while analyzing the image.")

Output:

{ "event": "Processing started for facial recognition.", "filename": "example.py", "func_name": "<module>", "lineno": 7, "timestamp": "2024-11-21 17:50:00"}{ "event": "An error occurred while analyzing the image.", "filename": "example.py", "func_name": "<module>", "lineno": 8, "timestamp": "2024-11-21 17:50:01"}

## # =Dynamically Adjusting Log Levels

from lo=gger import update_logger_level# Enable TRACE level logging for a specific loggerupdate_logger_level("aiplus.facialRecognition", "TRACE")# Disable a logger by setting its level to WARNINGupdate_logger_level("aiplus.facialRecognition", "WARNING")

## # =Loading Configuration from a File

from lo=gger import configure_logger, load_config_from_file# Load logging configuration dynamicallyconfig = load_config_from_file("logging_config.json")configure_logger(config)

## # Logging Pract=ices

- Use structured logging for easy integration with analytics tools

- Start with high log levels \(ERROR or WARNING\) in production, enabling lo=wer levels \(DEBUG or TRACE\) only when troubleshooting

- Dynamically update log levels at runtime to minimize downtime during deb=ugging

## # Field Manageme=nt

1. **Use constants for field names** : Define field names as co=nstants to prevent typos and ensure consistency

2. **Document field types explicitly** : Always include expecte=d data types to prevent index mapping conflicts

3. **Review new fields** : All new log fields should be reviewe=d before being added to production

4. **Create index templates** : Define Elasticsearch index temp=lates to set expected field types before data ingestion

5. **Consider field cardinality** : High-cardinality fields can= impact performance

6. **Use namespacing for component-specific fields** : Prefix f=ields with component identifiers to avoid collisions

# Docker Integ=ration

The docker container, either through the runtime or Docker Compose, can � configured to send the logs directly to Fluent Bit

While we use Fluent Bit as our log collector, Docker's logging driver is= named "fluentd" rather than "fluent-bit." This naming can cause confusion,= but it has a logical explanation. The Fluentd protocol was established fir=st, and Fluent Bit was designed to be compatible with this protocol. When D=ocker introduced logging drivers, they implemented the "fluentd" driver to =support the Fluentd forward protocol. This protocol is supported by both Fl=uentd and Fluent Bit, making them interoperable.

Fluent Bit is a lightweight, resource-efficient alternative to Fluentd d=esigned specifically for containerized environments and edge computing. Des=pite the difference in names, both use the same communication protocol, all=owing us to use Docker's "fluentd" driver to send logs directly to our Flue=nt Bit service.

Here's an example of how to configure services in a Docker Compose file =to use the Fluentd logging driver with Fluent Bit:

version=: '3'services: facial-recognition: image: aiplus/facial-recognition:latest logging: driver: fluentd options: fluentd-address: localhost:24224 tag: docker.facial-recognition fluentd-async-connect: "true" # Other service configuration... transcribe-summarize: image: aiplus/transcribe-summarize:latest logging: driver: fluentd options: fluentd-address: localhost:24224 tag: docker.transcribe-summarize labels: "log-level,component" labels: log-level: info component: nlp # Other service configuration... fluent-bit: image: fluent/fluent-bit:latest ports: - "24224:24224" - "24224:24224/udp" volumes: - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf - ./parsers.conf:/fluent-bit/etc/parsers.conf # Other service configuration...

With this configuration, container logs are sent directly to Fluent Bit =running on port 24224 without intermediate file storage. The `tag option provides a namespace for the logs, while `labels` allo=ws for additional metadata to be included with each log entry. This approac=h creates a clean, efficient logging pipeline that eliminates file manageme=nt overhead while providing rich context for log analysis.`

# Elasti=csearch Field Types

During development we encountered an Elasticsearch error:

"failed= to parse field [event] of type [text] in document with id 'tz-JbZUBzsUltXZ=OvLiM'. Preview of field's value: '{processing_time=0.000s, status_code=3D404, event=HTTP Response, body={detail=Job ID not found}}'"

Originally, our HTTP event logger used a nested structure:

logger.=info({ "event": "HTTP Response", "status_code": response.status_code, "body": response_body_json, "processing_time": f"{process_time:.3f}s",})

We refactored to use a flattened structure with consistent field names:<=/p>

logger.=info("HTTP Response", HttpEventAttributes.HTTP_STATUS_CODE, response.status_code, HttpEventAttributes.HTTP_RESPONSE_BODY, response_body_json, HttpEventAttributes.PROCESSING_TIME, f"{process_time:.3f}s")

The issue was a **field type collision**. Our application s=ent an `event` as a complex object, but Elasticsearch had previo=usly mapped this field as a text field. Once Elasticsearch creates a mappin=g for a field, it enforces consistent typing.

Elasticsearch dynamically creates field mappings when it first encounter=s a field in a document. This process, called "dynamic mapping," automatica=lly determines the data type based on the first value it sees. For example,= if the first document contains `"event": "HTTP Request"`, Elast=icsearch will map the `event` field as a `text` type.= If a subsequent document tries to use that same field name with a differen=t type \(like a nested object\), Elasticsearch will reject the document with =a mapping error.

This “type enforcement” is a fundamental aspect of Elast=icsearch's design that ensures data consistency and query predictability. H=owever, it can cause significant problems in logging systems where differen=t components might use the same field names differently. Once a field mappi=ng is established in an index, it cannot be changed without reindexing all =the data. This "schema on write" approach makes it **critical to plan field structures before data ingestion begins and to maintain a c=omprehensive data dictionary that all logging components adhere to. For tim=e-series logging with daily or weekly indices, these collisions might only =appear periodically as new indices are created, making them particularly di�icult to diagnose without understanding Elasticsearch's mapping behavior.=**

This highlights the **critical need for a centralized data diction=ary** that defines field names, types, and semantics to prevent fiel=d collisions as different components independently create log fields.

**I cannot stress enough how critical this piece is\! We MUST NOT H=AVE COLLISIONS in an ElasticSearch index. Otherwise WE WILL LOSE DATA.**

# Data Dictionary=

Field Name| Type| Description| Used By
---|---|---|---
**Common Fields**| | |
`log_level`| String| Log severity level \(TRACE/DEBUG/INFO/WARNING/ERROR\)| All logs
`log_channel`| String| Logger name/module identifier| All logs
`timestamp`| DateTime| When the log was generated \(ISO format\)| All logs
`filename`| String| Source file that generated the log| All logs
`func_name`| String| Function name that generated the log| All logs
`lineno`| Integer| Line number where the log was generated| All logs
**HTTP Event Fields**| | |
`URL`| String| Request URL path| HTTP logging
`HttpMethod`| String| HTTP method \(GET/POST/PUT/DELETE\)| HTTP logging
`HttpParameters`| Object| Query parameters| HTTP logging
`HttpRequestBody`| Object| JSON request body| HTTP logging
`HttpRequestBodyRaw`| String| Raw request body when not JSON| HTTP logging
`HttpResponseBody`| Object| JSON response body| HTTP logging
`HttpResponseBodyRaw`| String| Raw response body when not JSON| HTTP logging
`HttpRequestHeaders`| Object| HTTP request headers| HTTP logging
`HttpStatusCode`| Integer| HTTP response status code| HTTP logging
`ProcessingTime`| String| Request processing duration| HTTP/Service logs
`ResultCode`| String| Operation result code| HTTP/Service logs
**Facial Recognition Fields**| | |
`PersonName`| String| Identified person's name| Facial recognition
`ImagePath`| String| Path to the analyzed image| Facial recognition
`ModelName`| String| ML model used for recognition| Facial recognition
`FrameNumber`| Integer| Frame number in video sequence| Facial recognition
`FrameTimestamp`| DateTime| Timestamp of the analyzed frame| Facial recognition
**Service Fields**| | |
`ComponentName`| String| Component generating the event| Service logs
`ConnectionTimeout`| Integer| Connection timeout in ms| Service logs
`EndpointReference`| String| Service endpoint identifier| Service logs
`EventType`| String| Type of event being logged| Service logs
`HostName`| String| Host machine name| Service logs
`ServiceName`| String| Name of the service| Service logs
`TargetPort`| Integer| Port of the target service| Service logs
`Exception`| String| Exception message| Error logs
`TraceId`| String| Distributed tracing ID| All services
`ErrorType`| String| Type/class of error| Error logs
`ErrorMessage`| String| Human-readable error message| Error logs