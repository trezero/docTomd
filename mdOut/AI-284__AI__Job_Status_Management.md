---
title: "AI-284: AI+ Job Status Management"
source_file: "AI-284__AI__Job_Status_Management.doc"
converted_date: "2025-09-17T11:24:58.861436"
format: "markdown"
---

# AI-284: AI+ Job Status Management

- Introduction
- Design
- Components
- AI+ Utility
- RabbitMQ
- Redis
- Notification= API
- Workflow
- AI+ Common
- Integrations

# Introduction

The current architecture for managing AI job status relies heavily on di=rect HTTP callbacks from the AI+ utility to the Notification API utility. T=his approach has proven to be unreliable, particularly in scenarios where t=he API gateway experiences downtime or restarts. When the Notification API =is unavailable, the AI utility's status updates fail, leading to job failur=es and an inconsistent system state. This dependency creates a fragile syst=em where a single point of failure can disrupt critical AI inference jobs.<=/p>

To address these limitations, this document proposes a redesigned archit�ture that leverages RabbitMQ for asynchronous message queuing and Redis f=or persistent job state management. This new design aims to decouple the AI= utility from the Notification API, ensuring reliable status updates, impro=ving overall system resilience, and enabling scalability and statelessness =of the Notification API.

The primary issue stems from the direct dependency on HTTP callbacks for= status updates. If the Notification API is unavailable, the AI utility can=not communicate its status, leading to job failures. This creates a single =point of failure that negatively impacts system reliability. Additionally, =the current in-memory job state management within the AI+ utility is volati=le, lacking persistence and scalability. This limits the system's ability t=o handle high volumes of jobs and recover from failures gracefully.

# Design

We want something with these general tenents:

- **Improved Reliability:** Eliminates single points of failu=re.

- **Enhanced Scalability:** Leverages RabbitMQ and Redis for =high throughput.

- **Simplified Architecture:** Removes the need for complex H=TTP callback logic.

- **Centralized Job State Management:** Provides a single sou=rce of truth for job status.

- **Increased Flexibility:** Allows for easy integration of d=ownstream consumers and other DataCore components \(Swarm Object Storage, Pi=xit\)

Given the above, the proposed solution centers around the integration of= RabbitMQ and Redis to create a robust and scalable job status management s=ystem.

# # **Components**

## # **AI+ Utility**

This component initiates AI inference jobs, writes job state to Redis, a=nd publishes status updates to RabbitMQ. It is responsible for:

- Receiving job requests and initiating the AI inference process.

- Generating a unique `job_id` for each job.

- Writing the initial job state to Redis, including information like job\_id, `media_file`, `status`, and `tim=estamp`.

- Publishing status update messages to RabbitMQ whenever the job status ch=anges. These messages include the `job_id`, the new `status=`, and any other relevant information.

- Updating the job status in Redis as the job progresses \(e.g., "processin=g," "completed," "failed"\).

- Ensuring atomicity of updates to Redis and publishing messages to Rabbit=MQ to maintain data consistency.

## # **RabbitMQ** =

This message queue acts as a reliable intermediary for status updates. I=t is responsible for:

- Receiving status update messages from the AI Utility.

- Routing messages to the correct queue based on routing keys or exchange =configurations.

- Providing persistence and delivery guarantees to ensure that messages ar=e not lost.

- Enabling asynchronous communication between the AI Utility and the API G=ateway.

## # **Redis**

This in-memory data store provides persistent storage for job state. It =is responsible for:

- Storing job details such as `job_id`, `media_file`=, `status`, `timestamp`, and other relevant informati=on.

- Providing fast read and write access to job state data.

- Offering data persistence through mechanisms like RDB or AOF files.

<=/li>
- Enabling efficient management of job state data using data structures li=ke hashes and sets.

## # **Notificati=on API**

This component consumes status updates from RabbitMQ and sends notificat=ions to upstream consumers. It is responsible for:

- Subscribing to the appropriate RabbitMQ queue to receive status update m=essages.

- Reading the current job state from Redis using the `job_id` i=ncluded in the message.

- Determining the appropriate downstream consumers to notify based on the =job status and other relevant information.

- Sending notifications to downstream consumers \(e.g., via webhooks\)

- Acknowledging processed messages in RabbitMQ to prevent redelivery.

<=/li>

# # Workflow

1. The AI+ Utility receives a job request and initiates the inference proce=ss.

2. The AI+ Utility generates a unique `job_id` and writes the in=itial job state to Redis, including information like `job_id`, <=code>media\_file, `status`, and `timestamp`.

3. The AI+ Utility publishes a status update message to a designated Rabbit=MQ exchange. This message includes the `job_id`, `status, and any other relevant information.`

4. RabbitMQ routes the message to a dedicated queue.

5. The Notification API, acting as a consumer, retrieves messages from the =RabbitMQ queue.

6. Upon receiving a status update, the API Gateway reads the current job st=ate from Redis using the `job_id`.

7. Based on the job status and any other relevant information, the Notifica=tion API sends notifications to downstream consumers \(e.g., via webhooks\)

8. The Notification API acknowledges the message in RabbitMQ.

9. Downstream consumers receive notifications and perform actions based on =the job status, such as sending notifications, updating databases, or trigg=ering other processes.

Redis hashes provide an efficient way to store job details, allowing for= quick retrieval and updates. Unique `job_id` generation is cruc=ial. UUID's generated by the incoming API call are preferred. Redis TTLs ar=e used to manage data retention, ensuring that job data is automatically re=moved after a specified period. Redis sets or sorted sets can be used to ma=nage collections of jobs, such as active jobs or completed jobs.

The proposed architecture completely eliminates the need for direct HTTP= callbacks. All status updates and job completion events are managed within= the RabbitMQ and Redis ecosystem. This decoupling significantly improves s=ystem reliability and eliminates the risk of job failures due to Notificati=on API unavailability.

By removing the reliance on HTTP callbacks and utilizing RabbitMQ and Re=dis, the Notification API can be scaled horizontally. Multiple instances of= the Notification API can be deployed to handle increased request loads. Th=e Notification API does not need to maintain any local job state, as all jo=b information is stored in Redis. This allows for easy scaling and failover=. Furthermore, requests can be load-balanced across multiple Notification A=PI instances.

- The architecture allows for multiple downstream consumers to listen to t=he job completion queue.

- **Synchronization Considerations:**

- **Idempotency:** Ensure that downstream consumers can handl=e duplicate messages without causing unintended side effects.

- **Distributed Locking:** If necessary, implement distribute=d locking mechanisms \(e.g., using Redis\) to coordinate actions between mult=iple consumers.

- **Message Ordering:** If message order is critical, ensure =that RabbitMQ delivers messages in the required order.

**3.7. Downstream Consumer Design:**

- Downstream consumers receive notifications from the API Gateway and perf=orm actions based on the job status.

- They can perform various actions, such as sending notifications, updatin=g databases, or triggering other processes.

- These consumers are designed to be independent and scalable, allowing fo=r flexible handling of job completion events.

## # **AI+ Common**

Because the job handling and queue management is integral to the AI+ eco=system, it should be in a common library so that all utilities can implemen=t it seamlessly.

Example utility implementation:

import re=disimport pikaimport uuid# Redis connectionredis_client = redis.Redis(host='localhost', port=6379, db=0)# RabbitMQ connection parameterscredentials = pika.PlainCredentials('guest', 'guest')connection = pika.BlockingConnection(pika.ConnectionParameters('localhost=', credentials=credentials))channel = connection.channel()# Declare the job status queuechannel.queue_declare(queue='job_status_queue')def process_job(media_file): job_id = str(uuid.uuid4()) # Write initial job state to Redis redis_client.hset(f"job:{job_id}", mapping={ "status": "started", "media_file": media_file, "timestamp": datetime.datetime.now().isoformat() }) # Publish initial status message to RabbitMQ channel.basic_publish(exchange='', routing_key='job_status_queue', =body=job_id) # ... (Process the AI inference job) ... # Update job status in Redis and publish to RabbitMQ as the job progres=ses # ... # Example: Job completed redis_client.hset(f"job:{job_id}", "status", "completed") channel.basic_publish(exchange='', routing_key='job_status_queue', =body=job_id)# Example usageprocess_job("/path/to/media.mp4")

The Notification API can implement something like the following:

import pi=kaimport redis# RabbitMQ connection parameterscredentials = pika.PlainCredentials('guest', 'guest')connection = pika.BlockingConnection(pika.ConnectionParameters('localhost=', credentials=credentials))channel = connection.channel()# Declare the job status queuechannel.queue_declare(queue='job_status_queue')# Redis connectionredis_client = redis.Redis(host='localhost', port=6379, db=0)def callback(ch, method, properties, body): job_id = body.decode() # Read job status from Redis job_status = redis_client.hget(f"job:{job_id}", "status") # Send notifications based on job status # ... # Acknowledge the message ch.basic_ack(delivery_tag=method.delivery_tag)# Consume messages from the queuechannel.basic_consume(queue='job_status_queue', on_message_callback=cal=lback)print(' [*] Waiting for messages. To exit press CTRL+C')channel.start_consuming()

# Integrations

The inherent flexibility and decoupling provided by the RabbitMQ archite=cture allows for seamless integration of additional system components, such= as our upcoming SOS and Ngenea integrations. By leveraging RabbitMQ as a c=entral messaging backbone, we can establish efficient and reliable communic=ation pathways between various services, fostering interoperability and ext=ensibility within our ecosystem.

For instance, with the SOS integration, the file events generated from o=ur Object Storage pipeline can be published to a dedicated exchange in Rabb=itMQ. The NotificationAPI, already configured as a consumer, can subscribe =to this exchange and receive these file events. Upon receiving an event tha=t triggers an AI job, the NotificationAPI can parse the event data, extract= relevant information like the file path, and subsequently make an HTTP req=uest to the appropriate AI utility to initiate the job. This approach maint=ains the decoupling between components, as the SOS pipeline remains unaware= of the AI utilities, and the NotificationAPI acts as an intermediary, faci=litating communication through well-defined messages.

Similarly, the Ngenea integration can follow a similar pattern. File eve=nts from the NVMe storage, once published to RabbitMQ, can be consumed by t=he NotificationAPI, which would then trigger the relevant AI utility based =on the event data. This consistent approach to integrating new components u=sing RabbitMQ as the messaging backbone promotes a modular and scalable arc=hitecture. Furthermore, by utilizing RabbitMQ's features like topic-based r=outing, we can create fine-grained subscriptions, allowing consumers to sel�tively receive only the events they are interested in. This enhances effi=ciency and reduces unnecessary message processing. This extensible architec=ture enables us to seamlessly incorporate future components and services, f=ostering a cohesive and interconnected ecosystem driven by the robust capab=ilities of RabbitMQ.