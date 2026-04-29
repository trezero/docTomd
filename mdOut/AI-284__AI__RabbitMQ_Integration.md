---
title: "AI-284: AI+ RabbitMQ Integration"
source_file: "AI-284__AI__RabbitMQ_Integration.doc"
converted_date: "2025-09-17T11:24:58.916211"
format: "markdown"
---

# AI-284: AI+ RabbitMQ Integration

The AI+ platform currently operates through an HTTP-based API th=at provides asynchronous processing capabilities for media files. This desi=gn document outlines the integration of RabbitMQ to enable event-driven pro�ssing while maintaining the existing HTTP interface. The integration will= allow AI+ services to consume events from storage systems and other trigge=rs, process media files, and publish results back through RabbitMQ exchange=s.

The key challenge is transitioning from a pull-based HTTP model to a pus=h-based event model while ensuring reliable message processing, maintaining= job state consistency, and providing visibility into processing status acr=oss distributed systems.

## # Related Docum=entation

- **PixStore Integration** : See Pixstor files=ystem integration using RabbitMQ for the complete specification of even=ts published by the storage layer

- **Vision Integration** : See [Vision Metadata= Integration using RabbitMQ](3D"https://claude.ai/chat/referenced-doc") for the metadata consumption specification<=/p>

# # System Architec=ture

## # HTTP-Based Pr=ocessing

The existing AI+ system follows a traditional asynchronous HTTP pattern:=

�=8C────────=E2��────┐ POST /process =E2��───────�=94�─────┐ Process =E2��───────�=94�─────┐│ Client │ ────�=80────────=E2��───► │ AI+ API �=82 ───────�=80────► │ Worker �=94�│ │ ◄───�=80─ 202 ──────�=94�─ │ │ │ =Pool │└───────�=94�─────┘ = └──────�=80──────┘ = └──────�=94�──────┘ │ │ = │ │ GET /job_status/{id} │ = │ └──────�=94�───────�=80────────=E2��───────�=94�───►│ = │ │ = │ │ POST callback = │ │◄─�=94�───────�=80────────=E2��───────�=94�──┘

This model works well for direct client interactions but doesn't scale e�iciently for event-driven scenarios where multiple storage systems need t=o trigger processing based on file events.

## # Hy=brid HTTP and RabbitMQ Processing

The enhanced architecture introduces RabbitMQ as an additional trigger m�hanism while preserving the HTTP interface:

= ┌─────=E2��───────�=94�───────�=80────────=E2��───────�=94�──┐ │ RabbitMQ Broker = │ │ = │ │ ┌───=E2��───────�=94�─────┐ ┌�=94�───────�=80─────┐ │ │ │PixStore Events │ =E2��Status Exchange│ │ │ │ Exchange │ =E2�� │ │ │ └───=E2��────┬──�=94�─────┘ └�=94�─────┬─�=80─────┘ │ │ │ =E2�� │ │ ┌───=E2��────▼──�=94�─────┐ ┌�=94�─────▼─�=80─────┐ │ │ │ Processing Queue│ =E2�� Status Queue │ │ │ └───=E2��────┬──�=94�─────┘ └�=94�───────�=80─────┘ │ └────�=94�──────┼�=80────────=E2��───────�=94�───────�=80───┘ │┌───────�=94�─────┐ = │ ┌───�=94�───────�=80─┐│ PixStore │ File Events │ = │ Vision ││ (S3) │────�=80────────=E2��───────�=94�►│ │ Metadata │└───────�=94�─────┘ = │ │ Service │ ▼ └=E2��─────▲─�=94�────┘┌───────�=94�─────┐ =E2��───────�=94�──────┐ = ││ Client │ ────HTTP�=94�───► │ Notification │= ││ │ ◄───�=80────────= │ API │ │└───────�=94�─────┘ =E2��──────┬�=94�──────┘ = │ │ =E2�� ┌────=E2��─▼─────�=94�─┐ │ │ AI+ Service │─�=94�───────�=80────────=E2�� │ (MetaGen) │ Publish R=esults └────=E2��───────�=94�─┘

## # Message Flow Di=agram

The complete message flow through the system demonstrates how events tri=gger processing and results are distributed:

�=8C────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80──┐│ Complete Message Flow = │├───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��──┤│ = ││ 1. Storage Event = ││ PixStore ──► pixstor-fs-events-xchg =E2��─► Notification API ││ = ││ 2. Service Routing = ││ Notification API ──► Check Config �=94�─► Generate JobID ──► Route = ││ = ││ 3. AI+ Processing = ││ HTTP POST /process ──► AI+ Service =E2��─► Process ──► Generate Me=tadata ││ = ││ 4. Status Updates = ││ AI+ Service ──► Status Message �=80─► RabbitMQ Status Exchange ││ = ││ 5. Result Publication = ││ AI+ Service ──► Format Result �=80─► vision-metadata-xchg ││ = │└───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��──┘

# # PixStor=e Storage Integration

For S3-based storage, AI+ integrates with PixStore which publishes files=ystem events:

- **Exchange** : `pixstor-fs-events-xchg` \(fanout\)<=/p>

- **Queue** : `pixstor-fs-events-xchg_notification-api`

- **Events** : FileCreated, FileMoved, FileDeleted

- **Message format** : Includes S3 object details and optional= inode information

The Notification API consumes these events and routes them to appropriat=e AI+ services based on configuration.

# # Queue Mana=gement Strategy

Queue management is critical for maintaining system reliability and perf=ormance. The design employs several strategies to ensure efficient message =processing and system stability.

## # Queu=e Configuration and Topology

Process=ing Queue Configuration: Name: pixstor-fs-events-xchg_notification-api Type: Quorum Queue Durability: Durable Auto-delete: False Arguments: x-message-ttl: 86400000 # 24 hours x-max-length: 10000 # Maximum queue depth x-overflow: drop-head # Drop oldest messages when full x-dead-letter-exchange: ai-plus-dlx x-delivery-limit: 3 # Max retries before DLX

## # Consumer Manage=ment

The system implements intelligent consumer management to handle varying =workloads:

�=8C────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��──┐│ Consumer Scaling Logic �=94�├───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───┤│ �=94�│ Queue Depth < 100: 1 consumer (normal operation) �=94�│ Queue Depth 100-500: 2 consumers (moderate load) �=82│ Queue Depth 500-1000: 4 consumers (high load) �=82│ Queue Depth > 1000: Max consumers + alert �=94�│ �=94�│ Scale Down: When queue depth < 50% threshold for 5 min �=94�│ �=94�└───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───┘

## # Messag=e Processing Guarantees

To ensure at-most-once processing, the system implements a careful ackno=wledgment strategy:

# Pseud=ocode for message processing in Notification APIasync def process_message(channel, method, properties, body): try: # 1. Parse and validate message message = parse_message(body) validate_message(message) # 2. Extract event details event_name = message.get('eventName') s3_object = message.get('source', {}).get('s3object', {}) # 3. Check configuration for routing services = get_services_for_file(s3_object['bucket'], s3_object['=key']) # 4. Generate unique job ID job_id = generate_job_id() # 5. Acknowledge message BEFORE forwarding channel.basic_ack(delivery_tag=method.delivery_tag) # 6. Forward to AI+ services via HTTP for service in services: await forward_to_service(service, job_id, message) except ValidationError: # Invalid message - reject without requeue channel.basic_reject(delivery_tag=method.delivery_tag, requeue=�lse) except Exception as e: # Temporary failure - reject with requeue channel.basic_reject(delivery_tag=method.delivery_tag, requeue==True)

## # Que=ue Monitoring and Health Checks

The system continuously monitors queue health to prevent overload and en=sure timely processing:

�=8C────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───┐│ Queue Health Dashboard �=94�├───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�────┤│ �=94�│ Metric Warning Critical �=94�│ ───────=E2��───────�=94�───── ──�=94�───────�=80─── ────�=80────────=E2��─── ││ Queue Depth > 5,000 > 8,000 =E2��│ Message Age > 30 minutes > 1 hour =E2��│ Consumer Utilization > 80% > 95% =E2��│ Unacked Messages > 100 > 500 =E2��│ DLX Queue Size > 10 > 50 =E2��│ �=94�│ Actions: �=94�│ - Warning: Scale consumers, alert ops team �=94�│ - Critical: Pause producers, emergency scaling �=94�│ �=94�└───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�────┘

## # Backpre=ssure and Flow Control

To prevent system overload, the design implements backpressure mechanism=s:

Produce=r ──► RabbitMQ ──► Consumer= ──► Processing Pipeline ▲ │ │ �=94� │ │ │ �=94� └──────�=80─────┴──=E2��───────�=94�─┴─────�=80────────=E2��┘ Backpressure Signals: - Queue full (x-overflow) - Consumer capacity reached - Processing pipeline saturated

**Backpressure Strategies:**

1. **Producer Side:**

- Implement publisher confirms

- Retry with exponential backoff when queue is full

- Alert when unable to publish for extended periods

2. **Consumer Side:**

- Prefetch limit per consumer \(e.g., prefetch\_count=10\)

- Dynamic consumer scaling based on queue depth

- Graceful degradation when overwhelmed

3. **Processing Pipeline:**

- Worker pool with maximum capacity

- Job queuing with priority support

- Resource-based admission control

# # Deta=iled Message Specifications

## # PixStore Event= Format

For S3 storage events from PixStore, the system receives FileCreated and= FileMoved events:

### # FileCreated Event=

{ "eventTime": "2025-03-10T15:29:06.667Z", "eventName": "FileCreated", "tenantId": "iris", "source": { "fsInode": { "fsid": "3156238734335410383", "ino": "296962", "igen": "1105424809" }, "s3object": { "host": "datacore-swarm-ftl.com:8053", "bucket": "images", "key": "Examples of ingest/image.png", "etag": "9ffe930837cca7d70c71bdf5f589a8ae-1", "mtime": 1741620429792 } }}

## # HTTP Requ=est to AI+ Services

The Notification API transforms PixStore events into HTTP r=equests for AI+ services with special fields to indicate RabbitMQ result pu=blishing:

{ "job_id": "job-uuid-12345", // Generated by Notification API "media_file": "images/Examples of ingest/image.png", "callback_url": null, // NULL indicates RabbitMQ publishing "config": { "tenant_id": "iris", "source_event": "FileCreated", "result_destination": { "type": "rabbitmq", "exchange": "vision-metadata-xchg", // Default, configurable "routing_key": "" }, "source": { // Original source from PixStore event "s3object": { "host": "datacore-swarm-ftl.com:8053", "bucket": "images", "key": "Examples of ingest/image.png", "etag": "9ffe930837cca7d70c71bdf5f589a8ae-1" } } }}

When `callback_url` is null and `result_destination.type=` is "rabbitmq", the AI+ service publishes results to RabbitMQ instea=d of making an HTTP callback.

## # Status Update= Messages

Status messages provide real-time visibility into job processing:

{ "eventTime": "2025-01-17T10:31:00.000Z", "eventName": "JobStatusUpdate", "jobId": "job-uuid-12345", "tenantId": "tenant-123", "correlationId": "corr-uuid-11111", "status": "PROCESSING", "previousStatus": "WAITING", "progress": { "percentage": 45, "currentStep": "frame_analysis", "totalSteps": 5, "estimatedTimeRemaining": 180 }, "details": { "message": "Analyzing video frames for object detection", "framesProcessed": 450, "totalFrames": 1000, "currentFPS": 15.5 }, "resources": { "cpuUsage": 78.5, "memoryUsage": 3.2, "gpuUsage": 0 }, "source": { "s3object": { "bucket": "media-files", "key": "videos/2025/01/customer-video.mp4" } }}

# # Configurat=ion Management

## # Servic=e Routing Configuration

The Notification API uses Consul configuration to determine how to route= PixStore events:

notific=ation_api: routing: # Processing rules by bucket buckets: media-content: # Watch specific folders within bucket watch_folders: - path: "videos/ingest/" recursive: true file_patterns: - "*.mp4" - "*.mov" - "*.avi" exclude_patterns: - "*_temp.*" - "*_processing.*" services: - metagen - object-detection - path: "images/raw/" recursive: false file_patterns: - "*.jpg" - "*.png" - "*.tiff" services: - metagen - facial-recognition documents: # Process entire bucket watch_folders: - path: "/" recursive: true file_patterns: - "*.pdf" - "*.docx" services: - summarization # Service endpoints services: metagen: endpoint: "http://ai-plus-metagen.service.consul:8080/process" enabled: true max_file_size: "10GB" timeout: 3600 facial-recognition: endpoint: "http://ai-plus-facial.service.consul:8080/process" enabled: false max_file_size: "50MB" timeout: 300 # Result destination defaults result_destinations: default: type: "rabbitmq" exchange: "vision-metadata-xchg" # Service-specific overrides summarization: type: "rabbitmq" exchange: "document-metadata-xchg"

## # RabbitMQ Con=figuration

The RabbitMQ integration extends the existing BaseConfig system:

{ "service": { "component_name": "notification-api", "host": "0.0.0.0", "port": 8080 }, "rabbitmq": { "enabled": true, "connection": { "host": "rabbitmq.service.consul", "port": 5672, "vhost": "/", "username": "{vault.rabbitmq.username}", "password": "{vault.rabbitmq.password}", "connection_attempts": 3, "retry_delay": 2, "heartbeat": 600, "blocked_connection_timeout": 300 }, "tls": { "enabled": true, "verify_mode": "CERT_REQUIRED", "ca_path": "/etc/aiplus/certs/ca.pem" }, "consumer": { "prefetch_count": 10, "auto_ack": false, "exclusive": false, "consumer_tag": "notification-api" }, "exchanges": { "pixstore": { "name": "pixstor-fs-events-xchg", "type": "fanout", "durable": true }, "status": { "name": "ai-plus-status-xchg", "type": "topic", "durable": true }, "result": { "name": "vision-metadata-xchg", "type": "fanout", "durable": true } }, "queues": { "processing": { "name": "pixstor-fs-events-xchg_notification-api", "durable": true, "exclusive": false, "auto_delete": false, "arguments": { "x-message-ttl": 86400000, "x-max-length": 10000, "x-overflow": "drop-head", "x-dead-letter-exchange": "ai-plus-dlx", "x-delivery-limit": 3 } } } }}

# # S3 Event Process=ing

This section details the specific implementation for processing S3 stora=ge events from PixStore.

## # S3 Pro�ssing State Management

AI+ services use S3 object metadata to track processing state per servic=e:

# S3 Me=tadata Schemax-amz-meta-ai-plus-{service}-status: "processed|failed"x-amz-meta-ai-plus-{service}-time: "2025-01-17T10:00:00Z"x-amz-meta-ai-plus-{service}-version: "1.0.0"x-amz-meta-ai-plus-{service}-error: "error message if failed"# Example for metagen servicex-amz-meta-ai-plus-metagen-status: "processed"x-amz-meta-ai-plus-metagen-time: "2025-01-17T10:00:00Z"x-amz-meta-ai-plus-metagen-version: "1.0.0"

## # Sequence Diagrams=

### # FileCreated Event Processing

This sequence shows the complete flow from file upload to metadata index=ing in Vision.

sequenc�iagram participant User participant S3 as S3 Storage participant PS as PixStore participant RMQ as RabbitMQ participant NA as Notification API participant AI as AI+ Service participant Vision Note over User,Vision: Happy Path - New File Processing User->>S3: PUT object (video.mp4) S3->>PS: Object created notification PS->>PS: Detect new file PS->>RMQ: Publish FileCreated event Note right of PS: Exchange: pixstor-fs-events-xchg<br/>Event incl=udes S3 location,<br/>tenant ID, etag, mtime RMQ->>NA: Deliver FileCreated message Note right of RMQ: Queue: pixstor-fs-events-xchg_notification-api NA->>NA: Validate message format NA->>NA: Check routing configuration Note right of NA: - Is bucket monitored?<br/>- Does path match wa=tch folder?<br/>- Which services should process? alt File should be processed NA->>NA: Generate job ID NA->>RMQ: ACK message NA->>AI: POST /process Note right of NA: job_id: generated<br/>callback_url: null<=;br/>result_destination: rabbitmq AI->>AI: Detect RabbitMQ mode Note right of AI: callback_url is null,<br/>use RabbitMQ for =results AI->>S3: HEAD object (check metadata) S3-->>AI: Object metadata AI->>AI: Check if already processed Note right of AI: Look for x-amz-meta-ai-plus-metagen-status alt Not yet processed AI->>S3: GET object (download file) S3-->>AI: File content AI->>AI: Process with MetaGen Note right of AI: Generate metadata:<br/>- Summary<br/=>- Keywords<br/>- Scene analysis AI->>S3: Update object metadata Note right of AI: Set x-amz-meta-ai-plus-metagen-status = "pr=ocessed" AI->>RMQ: Publish MetadataGenerated event Note right of AI: Exchange: vision-metadata-xchg<br/>Incl=ude source S3 location<br/>and generated metadata RMQ->>Vision: Deliver metadata Vision->>Vision: Index metadata Vision->>Vision: Associate with source file Vision->>RMQ: ACK message else Already processed AI->>NA: 200 OK (already processed) end else File should not be processed NA->>RMQ: ACK message (skip) Note right of NA: File doesn't match routing rules end

### # Extended Use Case 1: FileMoved During Processi=ng

This sequence shows how AI+ handles file movements t=hat occur while processing is in progress.

sequenc�iagram participant User participant S3 participant PS as PixStore participant RMQ as RabbitMQ participant NA as Notification API participant AI as AI+ Service participant Vision Note over AI: Currently processing video.mp4 (50% complete) User->>S3: Copy object to archive/video.mp4 User->>S3: Delete original video.mp4 S3->>PS: Object deleted + created notifications PS->>PS: Correlate as move operation PS->>RMQ: Publish FileMoved event Note right of PS: source: bucket/video.mp4<br/>target: bucket/arc=hive/video.mp4 RMQ->>NA: Deliver FileMoved message NA->>NA: Check if job exists for source Note right of NA: Track active jobs by S3 location alt Job exists for source file NA->>AI: POST /update-location Note right of NA: Notify AI+ of new location AI->>AI: Check active jobs AI->>S3: HEAD source object alt Source still accessible (race condition) S3-->>AI: Object exists AI->>AI: Continue processing AI->>AI: Update job target location Note right of AI: Will publish result with<br/>new locati=on AI->>NA: 200 OK AI->>AI: Complete processing AI->>S3: Update metadata at NEW location Note right of AI: Set processed flag on archive/video.mp4 AI->>RMQ: Publish MetadataGenerated Note right of AI: source points to NEW location else Source no longer accessible S3-->>AI: 404 Not Found AI->>AI: Cancel active job AI->>NA: 200 OK (job cancelled) Note right of NA: Wait for new FileCreated<br/>at target =location end else No active job for file NA->>RMQ: ACK FileMoved (ignore) Note right of NA: Not currently processing this file end

### # Extended Use Case 2: Duplicate Processing Prevention

This sequence demonstrates how the system prevents d=uplicate processing when multiple events arrive.

sequenc�iagram participant PS as PixStore participant RMQ as RabbitMQ participant NA1 as Notification API 1 participant NA2 as Notification API 2 participant AI as AI+ Service participant S3 PS->>RMQ: Publish FileCreated Note over RMQ: Multiple consumers for HA par Concurrent Delivery RMQ->>NA1: FileCreated (video.mp4) and RMQ->>NA2: FileCreated (video.mp4) end NA1->>NA1: Generate job-id-1 NA2->>NA2: Generate job-id-2 NA1->>RMQ: ACK message NA2->>RMQ: ACK message par Both send to AI+ NA1->>AI: POST /process (job-id-1) and NA2->>AI: POST /process (job-id-2) end AI->>S3: HEAD object (check metadata) S3-->>AI: No processed flag AI->>AI: Accept job-id-1 AI->>NA1: 202 Accepted AI->>S3: Set processing flag (atomic) Note right of AI: x-amz-meta-ai-plus-metagen-processing = "true" AI->>S3: HEAD object (for job-id-2) S3-->>AI: Processing flag exists AI->>NA2: 409 Conflict (already processing) Note right of AI: Another job is processing this file

## # Message Pro�ssing Logic

### # FileCreated Event Handler \(Notification API\)

RECEIVE= FileCreated Event├─ Validate message structure│ └─ REJECT if invalid (no requeue)├─ Extract S3 location (bucket, key, host)├─ Check if tenant is enabled│ └─ ACK and skip if disabled├─ Check routing configuration│ ├─ Match bucket│ ├─ Match path against watch folders│ ├─ Check file patterns│ └─ Check exclude patterns│ └─ ACK and skip if no match├─ Get list of services to invoke├─ Generate unique job ID├─ ACK message ← Critical: Acknowledge early├─ For each service│ ├─ Build HTTP request│ │ ├─ Set job_id│ │ ├─ Set callback_url = null│ │ └─ Set result_destination = rabbitm=q│ └─ POST to service endpoint└─ Track active jobs

### # FileMoved Event Handler \(Notification API\)

RECEIVE= FileMoved Event├─ Validate message structure│ └─ REJECT if invalid (no requeue)├─ Extract source and target locations├─ Search active jobs by source location├─ IF job found│ ├─ Notify AI+ service of location change│ └─ Update job tracking└─ ACK message

# # Error Han=dling and Recovery

## # Error Categories and Handling Strategies

�=8C────────=E2��───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��─────┐│ Error Handling Matrix =E2��├───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�──────┤│ =E2��│ Error Type Action Recovery �=94�│ ───────=E2��───────�=94�─ ──────�=94�───────�=80── ─────�=80────────=E2��─── ││ Invalid Message Reject (no requeue) Log to DLX �=94�│ Unknown Event ACK and ignore Log warning �=94�│ S3 Access Denied Mark failed in S3 Manual intervention�=94�│ File Too Large ACK and skip Log warning �=94�│ Processing Error Retry in AI+ Up to 3x �=94�│ Service Down Requeue message Backoff & retry =E2��│ Queue Full Publisher confirm Backpressure �=94�│ =E2��└───────�=94�───────�=80────────=E2��───────�=94�───────�=80────────=E2��───────�=94�──────┘

## # Dead Let=ter Queue Processing

Failed messages are routed to a dead letter exchange for investigation:<=/p>

Main Qu=eue ──X──> Processing Failed ─=E2��> Dead Letter Exchange │ ▼ Dead Letter Queue │ ▼ Manual Investigation

# # Monitor=ing and Observability

## # Metrics

The system tracks essential metrics for operational visibility:

# Metri=cs collection exampleclass QueueMetrics: def __init__(self): self.queue_depth = Gauge('rabbitmq_queue_depth', 'Current queue d=epth') self.message_age = Histogram('rabbitmq_message_age_seconds', 'Age= of messages when processed') self.processing_duration = Histogram('job_processing_duration_sec=onds', 'Job processing time') self.messages_published = Counter('rabbitmq_messages_published_to=tal', 'Total messages published') self.messages_consumed = Counter('rabbitmq_messages_consumed_tota=l', 'Total messages consumed') self.messages_failed = Counter('rabbitmq_messages_failed_total', ='Total messages failed') self.routing_decisions = Counter('notification_api_routing_total'=, 'Routing decisions by service')

## # Health C=heck Implementation

{ "service": "notification-api", "status": "healthy", "components": { "rabbitmq": { "connected": true, "queue": "pixstor-fs-events-xchg_notification-api", "consumers": 2, "messages_ready": 15, "messages_unacked": 3 }, "routing": { "configured_buckets": ["media-content", "documents"], "enabled_services": ["metagen"], "disabled_services": ["facial-recognition", "object-detection"] }, "jobs": { "active": 12, "completed_last_hour": 234, "failed_last_hour": 2 } }}

# Implementati=on Details

Notific=ation API → RabbitMQ Exchange → AI+ Service Queues �=92 Processing → Results

# # Class Respon=sibilities

## # **Notificati=on API**

**Role** : Entry point for S3 events:

- Receives S3 events via HTTP endpoints

- Validates event data

- Publishes events to RabbitMQ exchange

- Maintains single point of message origin

**Key Methods** :

- `handle_file_created()` \- Processes S3 FileCreated events

=
- `handle_file_moved()` \- Processes S3 FileMoved events

- `publish_s3_event()` \- Publishes to RabbitMQ exchange

## # **B=aseHandler** \(`BaseHandler`\)

**Role** : Base RabbitMQ infrastructure:

- RabbitMQ connection management

- Exchange and queue setup

- Message consumption with at-most-once delivery

- Health monitoring and metrics

**Key Methods** :

- `start()` \- Initialize connection and consumers

- `process_message()` \- Abstract method for message processing<=/p>

- `publish_message()` \- Publish messages to exchanges

## # <=strong>AI Service Handler \(`MetagenHandler`\)

**Role** : Service-specific RabbitMQ handling:

- Inherits from `RabbitMQBaseHandler`

- Routes messages to appropriate processors

- Manages job lifecycle

- Publishes status updates and results

**Key Methods** :

- `process_message()` \- Main message processing entry point

=
- `_handle_file_created()` \- Handle FileCreated events

- `_handle_file_moved()` \- Handle FileMoved events

- `publish_status()` \- Publish job status updates

- `publish_result()` \- Publish processing results

## # <=strong>EventProcessor \(`S3EventProcessor`\)

**Role** : Event processing logic:

- Validates message structure

- Applies processing rules \(bucket/folder/pattern matching\)

- Creates job metadata

- Handles file movement and deletion logic

**Key Methods** :

- `process_file_created_event()` \- Process FileCreated events

- `process_file_moved_event()` \- Handle file moves during proce=ssing

- `validate_message_structure()` \- Validate incoming messages

- `create_processing_job()` \- Create job from event data

## # Core Processor \(`MetagenProcessor`\)

**Role** : Business logic processing **Responsibilitie=s** :

- Downloads files from S3

- Performs actual AI processing \(metadata extraction\)

- Returns processing results

**Key Methods** :

- `process_video()` \- Process video files

- `process_image()` \- Process image files

## # 7\. **Service Orchestrator** \(`MetagenService`\)<=/h3>

**Role** : Service coordination **Responsibilities:**

- Coordinates all components

- Manages job queue and processing

- Provides service health and status

- Handles startup/shutdown

**Key Methods** :

- `startup()` \- Initialize all components

- `_process_jobs()` \- Background job processing

- `get_health()` \- Service health status

# # Data Flow

## # 1\. **Event =Ingestion**

S3 Even=t → Notification API → RabbitMQ Exchange (notification-even=ts-xchg)

## # 2\. **M=essage Distribution**

Exchang=e → Queues (notification-events-xchg_metagen, notification-events-x=chg_summarization, etc.)

## # 3\. **Ser=vice Processing**

Queue =E2�� AIServiceRabbitMQHandler.process_message() → S3EventProce=ssor → Job Creation

## # 4\. **Job Pro�ssing**

Job Que=ue → MetagenService._process_jobs() → MetagenProcessor �=86� Results

## # 5\. **Resu=lt Publishing**

Results= → RabbitMQ (vision-metadata-xchg) + HTTP Callbacks

# # Message Examples

## # FileCreated Event \(from Notification API\)

{ "eventTime": "2025-07-01T10:30:00.000Z", "eventName": "FileCreated", "tenantId": "tenant-001", "source": "notification-api", "s3object": { "bucket": "media-content", "key": "videos/ingest/sample.mp4", "size": 1048576, "contentType": "video/mp4", "etag": "abc123def456" }}

## # FileMoved Event \(from Notification API\)

{ "eventTime": "2025-07-01T10:35:00.000Z", "eventName": "FileMoved", "tenantId": "tenant-001", "source": "notification-api", "source": { "bucket": "media-content", "key": "videos/ingest/sample.mp4" }, "target": { "bucket": "media-content", "key": "videos/processed/sample.mp4" }}

## # =Job Status Update \(to Status Exchange\)

{ "eventTime": "2025-07-01T10:32:00.000Z", "eventName": "JobStatusUpdate", "jobId": "job-uuid-123", "tenantId": "tenant-001", "status": "PROCESSING", "progress": { "percentage": 50, "currentStep": "Extracting metadata", "estimatedTimeRemaining": 60 }, "details": { "message": "Processing video content", "service": "metagen" }}

## # Metadata =Result \(to Vision\)

{ "eventTime": "2025-07-01T10:35:00.000Z", "eventName": "MetadataGenerated", "appId": "ai-plus/metagen", "tenantId": "tenant-001", "source": { "s3object": { "bucket": "media-content", "key": "videos/processed/sample.mp4", "etag": "abc123def456" } }, "dataVersion": "1.0.0", "data": { "summary": "A sample video showing outdoor activities", "keywords": ["outdoor", "nature", "activity"], "duration": 120, "resolution": "1920x1080", "scenes": [ {"timestamp": 0, "description": "Opening scene"}, {"timestamp": 60, "description": "Main activity"} ] }}

# # Processing �cision Flow

## # Configuration-Based Processing Rules

# In Rabb=itMQConfig.should_process_file()bucket = "media-content"key = "videos/ingest/sample.mp4"content_type = "video/mp4"service = "metagen"# Check bucket configurationbucket_config = config.get("processing.s3_monitoring.buckets.media-conten=t")# Check watch foldersfor folder in bucket_config["watch_folders"]: if key.startswith(folder["path"]) and service in folder["services"]: # Check file patterns if matches_pattern(key, folder["file_patterns"]): return Truereturn False

# # Error Handli=ng Strategy

## # Message Level

- **Invalid Structure** : Reject without requeue → Dea=d letter

- **Unknown Event Type** : ACK and ignore

- **Missing Required Fields** : Reject without requeue

## # Processing Level

- **File Not Found** : ACK and skip \(file may have been delete=d\)

- **Processing Timeout** : Retry with exponential backoff

<=/li>
- **Resource Exhaustion** : Stop consuming temporarily

## # System Level

- **RabbitMQ Disconnect** : Automatic reconnection with backof=f

- **S3 Unavailable** : Retry with exponential backoff

# # Key Design Deci=sions

## # 1\. **=At-Most-Once Delivery**

- Single Notification API ensures no duplicate events

- RabbitMQ consumer acknowledgment only after job creation

- No need for S3 metadata state management

## # 2\. Job Lifecycle Management

WAITING= → PROCESSING → FINISHED/FAILED/CANCELLED

## # 3\. Result Publishing Options

- **RabbitMQ** : `rabbitmq://vision-metadata-xchg`<=/p>

- **HTTP** : `https://external-api/callback`

- **Both** : Primary + Secondary destinations

## # 4=. **Configuration-Driven Processing**

- Bucket/folder/pattern matching

- Service-specific file type support

- Tenant enablement/disablement

# # Integration Poin=ts

# Minimal= integration requiredclass ExistingAIService: async def startup(self): # Add RabbitMQ handler self.rmq_handler = MetagenRabbitMQHandler(...) await self.rmq_handler.start() async def process_job(self, job_id, file_path, config): # Existing processing logic unchanged result = await self.existing_processor(file_path) # Add result publishing if self.rmq_handler: await self.rmq_handler.publish_result(job_id, result)