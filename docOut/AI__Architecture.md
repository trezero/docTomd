# AI+ Architecture

- [Core Architecture](#AI+Architecture-CoreArchitecture)
    - [Distributed Processing](#AI+Architecture-DistributedProcessing)
    - [Queue Interface](#AI+Architecture-QueueInterface)
          - [Local Queue](#AI+Architecture-LocalQueue)
          - [RabbitMQ](#AI+Architecture-RabbitMQ)
          - [AWS SQS](#AI+Architecture-AWSSQS)
    - [Worker Interface](#AI+Architecture-WorkerInterface)
    - [Docker](#AI+Architecture-Docker)
- [GPU-Aware Distributed Model Management System](#AI+Architecture-GPU-AwareDistributedModelManagementSystem)
    - [Detailed Component Descriptions](#AI+Architecture-DetailedComponentDescriptions)
          - [Distributed Model Manager](#AI+Architecture-DistributedModelManager)
          - [Model Factory](#AI+Architecture-ModelFactory)
          - [Model Request Manager](#AI+Architecture-ModelRequestManager)
          - [Configuration System](#AI+Architecture-ConfigurationSystem)
          - [Database](#AI+Architecture-Database)
    - [Docker](#AI+Architecture-Docker.1)
          - [docker-compose.yml](#AI+Architecture-docker-compose.yml)
          - [Dockerfile](#AI+Architecture-Dockerfile)
    - [Future Enhancements](#AI+Architecture-FutureEnhancements)
          - [Optimization Strategies](#AI+Architecture-OptimizationStrategies)
          - [Monitoring and Logging](#AI+Architecture-MonitoringandLogging)
          - [Other Considerations](#AI+Architecture-OtherConsiderations)
                  - [Multiple GPUs](#AI+Architecture-MultipleGPUs)
                  - [Redis Cluster](#AI+Architecture-RedisCluster)
          - [Future Enhancements](#AI+Architecture-FutureEnhancements.1)
- [Kubernetes](#AI+Architecture-Kubernetes)
    - [Isto](#AI+Architecture-Isto)
          - [Istio Architecture](#AI+Architecture-IstioArchitecture)
                  - [Istio data plane](#AI+Architecture-Istiodataplane)
                  - [Istio control plane](#AI+Architecture-Istiocontrolplane)
          - [Istio Microservice Integration](#AI+Architecture-IstioMicroserviceIntegration)
          - [Mutual TLS](#AI+Architecture-MutualTLS)

 ![aiplus.drawio.png](4e2fc473007c8d3b1a1e36a69f4a8887ed61e55743514ea95c02cc609f981441)

# Core Architecture

The AI+ utilities are undergoing a major refactoring to reflect the modern needs of enterprise software. Currently we have a few bespoke utilities that require a fair amount of technical intervention to deploy. We need to get to a place where we can deploy these as containers for runtime efficiency and easy integration.

1. HTTP API:
   The system will expose its functionality through a RESTful HTTP API. These APIs will provide endpoints for business and admin functions. This API design ensures that the system can be easily integrated into various workflows and applications.
2. Extensibility and Configurability:
   The architecture is designed with extensibility in mind. New models can be easily integrated by adding them to the shared object storage. The system uses a configuration singleton that can be dynamically updated, allowing for runtime changes to system behavior. This includes the ability to modify prompts used in vision tasks, enabling the system to adapt to new use cases without code changes.
3. Error Handling and Logging:
   Robust error handling and logging are integrated throughout the system. A custom logger is implemented to capture detailed information about the system's operation, including performance metrics, error traces, and analysis results. This logging system is designed to suppress certain warnings while still providing comprehensive debugging information when needed.

This architecture provides a solid foundation for a powerful, flexible, and efficient video and image analysis system. It balances performance optimization with modularity and extensibility, allowing for easy maintenance and future enhancements. The combination of parallel processing, efficient media handling, and a well-designed API makes it suitable for a wide range of applications, from small-scale analysis tasks to large-scale video processing pipelines.

## Distributed Processing

The AI+ Core Architecture will consist of an implementation where we can queue and execute tasks in a distributed manner. In AI workloads, tasks like model training, data preprocessing, and inference can vary in duration and resource requirements. A distributed queue ensures that tasks are balanced across multiple workers, preventing any single container from becoming a bottleneck. This setup also allows the system to dynamically scale by adding or removing workers based on demand, leading to better resource utilization and reduced processing time. Furthermore, a distributed approach enhances fault tolerance, as tasks can be reassigned to other workers if a container fails, ensuring reliability and continuity in AI processing pipelines.

In the future, we will need to support multiple servers running multiple GPUs. In this environment:

- The Queue Interface becomes crucial for distributing work across multiple containers. It allows tasks to be added from one container and processed by another.
- The Worker Interface is important for managing the execution of tasks within each container, potentially utilizing multiple GPUs.

The combination of both interfaces provides several benefits:

1. Scalability: We can easily scale out by adding more workers or containers that connect to the same queue.
2. Flexibility: We can have different types of workers (CPU, GPU) processing tasks from the same queue.
3. Load Balancing: Tasks can be distributed evenly across available resources.
4. Fault Tolerance: If a worker fails, the task remains in the queue and can be picked up by another worker.
5. Decoupling: The system producing tasks (e.g., image upload service) can be separate from the system processing tasks.

```
...
    async def start_processing(self):
        self.progress = 20 # -- Not quite sure why this variable is implemented this way.
        self.worker.start()

        # Set up signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)

        try:
            while not self.shutdown_event.is_set():
                try:
                    item = self.queue.get(timeout=1)  # Non-blocking with a timeout
                    if item:
                        task = asyncio.create_task(self._process_work_item(item))
                        self.processing_tasks.add(task)
                        task.add_done_callback(self.processing_tasks.discard)
                except Exception as e:
                    if not self.shutdown_event.is_set():
                        logger.error(f"Error getting item from queue: {e}")
                await asyncio.sleep(0.1)  # Small delay to prevent tight loop
        finally:
            await self._shutdown()

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}. Initiating shutdown...")
        self.shutdown_event.set()

    async def _shutdown(self):
        logger.info("Shutting down...")
        self.worker.stop()

        # Wait for all processing tasks to complete
        if self.processing_tasks:
            await asyncio.wait(self.processing_tasks)

        self.worker.join()
        self.queue.close()
        logger.info("Shutdown complete.")
```

## Queue Interface

The AI+ system's support for multiple queue types is a key feature that enhances its flexibility and scalability. By implementing a pluggable queue interface, the system can adapt to different deployment scenarios and processing requirements.

### Local Queue

The local queue option, using Python's built-in queue module, is suitable for single-machine deployments or testing environments. It provides a simple, in-memory queue that doesn't require any additional infrastructure. While it doesn't support distributed processing, it's perfect for smaller-scale applications or development purposes.

### RabbitMQ

RabbitMQ support adds the capability for distributed processing across multiple machines. As a robust message broker, RabbitMQ allows the system to decouple the task producers (e.g., image uploaders) from the consumers (facial recognition workers). This separation enables horizontal scaling of the processing nodes and provides features like message persistence and advanced routing capabilities. RabbitMQ is an excellent choice for deployments that require high throughput and the ability to scale processing across a cluster of machines.

### AWS SQS

The inclusion of Amazon SQS (Simple Queue Service) as a queue option caters to cloud-native deployments, particularly those running on AWS infrastructure. SQS offers a fully managed queuing service, removing the need for self-managed queue infrastructure. It provides seamless scalability and integrates well with other AWS services. This option is ideal for deployments that prioritize minimal operational overhead and want to leverage cloud-native services.

By supporting these diverse queue types, the AI+ system can be adapted to a wide range of deployment scenarios. Whether it's a small-scale local deployment, an on-premises distributed system, or a cloud-based scalable solution, the appropriate queue can be selected without changing the core recognition logic. This flexibility not only accommodates different architectural needs but also allows for easy migration between different deployment models as the system's requirements evolve.

## Worker Interface

The worker interface in this facial recognition system is designed to provide a flexible and scalable approach to processing AI+ tasks. It abstracts the underlying execution model, allowing for seamless switching between local multi-threading and distributed processing without changing the core recognition logic. This abstraction is crucial for adapting the system to various deployment scenarios, from single-machine setups to large-scale distributed environments.

We have two primary implementations of a worker interface: LocalThreadPoolWorker and DistributedWorker. The LocalThreadPoolWorker is designed for single-machine deployments, utilizing Python's threading module to create a pool of worker threads. Each thread in this pool continuously pulls tasks from the queue and processes them until the stop signal is received. This implementation is ideal for maximizing CPU utilization on a single machine, especially for I/O-bound tasks like facial recognition.

On the other hand, the DistributedWorker is tailored for scalable, multi-machine deployments. It leverages Celery, a distributed task queue system, to distribute work across multiple processes or machines. This implementation creates a Celery task for each work item and enqueues these tasks to be processed by Celery workers running on various machines. The DistributedWorker maintains a local enqueue loop that pulls items from the facial recognition system's queue and pushes them to Celery's distributed queue.

Both worker implementations handle task processing in a similar manner, calling a provided work function for each task. This work function, typically the _process_work_item method of the FacialRecognition class, encapsulates the core logic of facial detection, embedding generation, and similarity matching. By using a consistent interface for task processing, the system maintains a clear separation between the worker's execution model and the actual recognition logic.

The worker interface also includes error handling and dead-letter queue (DLQ) functionality. If a task fails during processing, the worker can move it to a DLQ for later inspection and potential reprocessing. This feature enhances the system's robustness, ensuring that problematic tasks don't halt the entire recognition process and can be addressed separately.

## Docker

- Nvidia GPU with CUDA. Note that nothing about this architecture precludes supporting other GPUs in the future, but our current needs require Nvidia
- Ubuntu 22.04
- Docker
- (Optional) Kubernetes

We will deploy the various utilities we use as individual microservices, which we can deploy in containers and in a container-management environment to enhance their usability, accessibility, and maintainability. We will expose the uService with a RESTful API., where other Perifery and 3rd party utilities can easily call the model from different platforms and programming languages. This reduces the complexity for developers who need to integrate the service, as they interact with a higher-level interface rather than diving into the intricacies of the service’s implementation. We can also version the model API in various ways. We can either version the URL itself or use a service mesh for versioning, A/B testing, canary deployments, etc.

Typically, we will architect these models in the following way.

The API will be HTTP 1.1 (or HTTP/2, if we enable TLS). Note that we could use gRPC as a backend for greater throughput, but the number of requests to the model should be low enough that we don’t need that sort of optimization. The models themselves will be shared across the server via a loaded volume (on nVME).

Since the services will be deployed on Nvidia GPUs with CUDA support, we will be using CUDA-enabled images and passing the GPU runtime to the docker-compose file.

```
# Use NVIDIA CUDA 12.4 runtime as the base image
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Python
RUN apt-get update  apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
     rm -rf /var/lib/apt/lists/*

# Set Python3 as the default Python
RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements/requirements.http.txt \
    requirements/requirements.gpu.txt \
    requirements/requirements.groundingdino.txt \
    requirements/requirements.yolo.txt \
    requirements/requirements.flash_attn.txt \
    requirements/_requirements.txt \
    ./

# Install any needed packages specified
RUN pip3 install \
    -r _requirements.txt \
    -r requirements.http.txt \
    -r requirements.gpu.txt \
    -r requirements.groundingdino.txt \
    -r requirements.yolo.txt \
    --upgrade \
     rm -rf ~/.cache/pip

# Install setup.py requirements for flash_attn
RUN python3 -m pip install packaging==24.1   rm -rf ~/.cache/pip

# Install flash_attn, since it needs to be managed via its own build process, apparently.
RUN python3 -m pip install -r requirements.flash_attn.txt --no-build-isolation  rm -rf ~/.cache/pip

# Copy the current directory contents into the container at /app
COPY . /app

# Define environment variable
ENV PROJECT=aiplus

# Run the API when the container launches
CMD ["python", "-m", "aiplus.rest.api"]
```

```
version: '3.8'

services:
  object-detection:
    build: .
    ports:
      - "${PORT:-9001}:${PORT:-9001}"
    volumes:
      - ${VIDEO_DIR:-./videos}:/app/videos:ro
      - ${OUTPUT_DIR:-./outputs}:/app/outputs
      - /opt/aiplus/models:/opt/aiplus/models
    environment:
      - DEBUG=1
      - VIDEO_DIR=/home/aiplus/testdata
      - OUTPUT_DIR=/home/aiplus/tests # USED FOR DEBUG ONLY!
      - PORT=${PORT:-9001}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

If these microservices are deployed in Kubernetes, the models and weights can be deployed in a Persistent Volume and Persistent Volume Claim, for sharing across multiple nodes.

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ai-model-storage
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  nfs:
    path: /dev/nvme0n1p2/models
    server: aiplus.datacore.com
```

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-model-storage-claim
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1000Gi
```

# GPU-Aware Distributed Model Management System

Multiple containers can make use of various models to perform business tasks. However, the GPU itself is a finite resource, and AI models can take up a significant memory footprint. This GPU-Aware Distributed Model Management System is designed to efficiently manage AI models across multiple Docker containers, optimizing GPU resource utilization. This system enables coordinated loading, unloading, and sharing of models while maintaining awareness of GPU memory constraints.

The system consists of the following components:

- Multiple Docker containers running AI models
- A Redis container for shared state management
- Shared storage volume for model persistence

The high-level flow is as follows:

1. AI containers use DistributedModelManager to load, access, and release models.
2. A shared Redis cache maintains metadata about loaded models and facilitates distributed locking.
3. Shared storage holds serialized model files accessible to all containers.
4. GPU usage is monitored across containers to inform loading/unloading decisions.

IMPORTANT NOTE: If our system incorporates the Roboflow and/or Nvidia Triton inference servers, we will also need to build hooks into them to better monitor the GPU utilization so we can make better decisions.

## Detailed Component Descriptions

### Distributed Model Manager

The Distributed Model Manager is the core component responsible for the actual handling of model files and their metadata. It interfaces with Redis for distributed state management and a shared file system for model storage. Its key functions include:

- Loading models into GPU memory and persisting them to shared storage
- Unloading models when they're no longer needed or when GPU memory is constrained
- Tracking model metadata, including reference counts and last used timestamps
- Providing thread-safe operations through distributed locking mechanisms
- Monitoring GPU memory usage to inform loading/unloading decisions

The DistributedModelManager ensures efficient use of GPU resources across multiple containers, preventing redundant model loading and managing memory constraints. It provides a consistent interface for other components to interact with the underlying model storage and GPU resources.

For NVIDIA GPUs, we will implement `_check_gpu_memory_usage()` using the NVIDIA Management Library (NVML):

```
import pynvml

def _check_gpu_memory_usage(self):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    pynvml.nvmlShutdown()
    return info.used / info.total
```

TODO: Add implementation for other GPUs

The base thresholds are as follows:

- Set a GPU memory usage threshold (e.g., 80%)
- Trigger unloading operations when threshold is exceeded

When unloading a model, we will use the following heuristics:

1. Identify models with zero reference count
2. Among zero-reference models, unload the least recently used
3. If no zero-reference models, wait for releases or raise an exception

The sample API flow is best illustrated by this:

- `load_model(model_name, model_class, *args, **kwargs)`

    - Loads a model or retrieves an already loaded model
    - Increments reference count
    - Updates last used timestamp
- `get_model(model_name, model_class)`

    - Retrieves an already loaded model
    - Increments reference count
    - Updates last used timestamp
- `release_model(model_name)`

    - Decrements reference count
    - Triggers potential unloading if reference count reaches zero
- `unload_model(model_name)`

    - Removes model from shared storage and Redis metadata
    - Only executed if reference count is zero
- `_load_model_from_disk(model_name, model_class, *args, **kwargs)`

    - Deserializes model from shared storage
- `_check_gpu_memory_usage()`

    - Monitors GPU memory utilization
- `_unload_least_recently_used()`

    - Identifies and unloads the least recently used model with zero references
- `_consider_unloading(model_name)`

    - Decides whether to unload a model based on current system state
- `get_model_usage()`

    - Retrieves current usage statistics for all models

### Model Factory

The Model Factory is responsible for dynamically determining which models are required for each incoming request. It abstracts the model selection logic away from the application routes, allowing for flexible and configurable model requirements. The Model Factory:

- Loads and parses a configuration file specifying default model requirements for different routes
- Retrieves model specifications from environment variables
- Handles customer-specific model requirements
- Processes request-specific model parameters

By centralizing the model selection logic, the Model Factory allows for easy updates to model requirements without changing application code. It supports a variety of use cases, from static route-based model selection to dynamic, customer-specific model loading, all configurable through external means.

```
import os
import json
from flask import request

class ModelFactory:
    def __init__(self, config_path='config/model_config.json'):
        self.config = self._load_config(config_path)
        self.env_models = self._load_env_models()

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    def _load_env_models(self):
        return {k[6:]: v for k, v in os.environ.items() if k.startswith('MODEL_')}

    def get_required_models(self, route):
        models = set()

        # Add models from configuration
        if route in self.config:
            models.update(self.config[route].get('models', []))

        # Add models from environment variables
        models.update(self.env_models.values())

        # Add customer-specific models from HTTP headers, for instance.
        customer_id = request.headers.get('X-Customer-ID')
        if customer_id and customer_id in self.config.get('customers', {}):
            models.update(self.config['customers'][customer_id].get('models', []))

        # Add models from request parameters
        if 'models' in request.json:
            models.update(request.json['models'])

        return list(models)
```

### Model Request Manager

The Model Request Manager acts as a bridge between the web application routes and the model management system. It wraps each route to ensure that all required models are loaded before the route logic is executed. Its primary functions include:

- Interfacing with the ModelSelector to determine required models for each request
- Checking if required models are loaded and initiating loading if necessary
- Updating reference counts for models when they're used
- Handling errors and returning appropriate HTTP responses (e.g., 429 for unavailable models)
- Releasing models (decrementing reference counts) after request completion

This manager abstracts the complexities of model management away from the application logic, allowing developers to focus on implementing the core functionality of each route without worrying about model availability or resource management.

The base operation is:

1. Check if required models are loaded
2. Update reference counts
3. Handle errors and return appropriate HTTP responses
4. Release models after the workflow completes

```
from functools import wraps
from flask import request, jsonify
from distributed_model_manager import DistributedModelManager

class ModelRequestManager:
    def __init__(self, model_manager: DistributedModelManager):
        self.model_manager = model_manager

    def require_models(self):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                route = request.endpoint
                try:
                    # Dynamically determine required models
                    required_models = self.model_selector.get_required_models(route)

                    # Check and load required models
                    unavailable_models = self._ensure_models_loaded(required_models)
                    if unavailable_models:
                        return self._models_unavailable_response(unavailable_models)

                    # Update reference counts
                    self._increment_ref_counts(required_models)

                    # Execute the wrapped function
                    result = f(*args, **kwargs)

                    return result
                except Exception as e:
                    return self._error_response(str(e))
                finally:
                    # Release models
                    if 'required_models' in locals():
                        self._release_models(required_models)

            return wrapped
        return decorator

    def _ensure_models_loaded(self, model_names):
        unavailable_models = []
        for model_name in model_names:
            if not self.model_manager.is_model_loaded(model_name):
                try:
                    self.model_manager.load_model(model_name, self._get_model_class(model_name))
                except Exception:
                    unavailable_models.append(model_name)
        return unavailable_models

    def _increment_ref_counts(self, model_names):
        for model_name in model_names:
            self.model_manager.increment_ref_count(model_name)

    def _release_models(self, model_names):
        for model_name in model_names:
            self.model_manager.release_model(model_name)

    def _models_unavailable_response(self, unavailable_models):
        response = {
            "error": "Required models unavailable",
            "unavailable_models": unavailable_models,
            "message": "The server is currently unable to handle the request due to a temporary overloading or maintenance of the server."
        }
        return jsonify(response), 429

    def _error_response(self, error_message):
        response = {
            "error": "Internal server error",
            "message": error_message
        }
        return jsonify(response), 500

    def _get_model_class(self, model_name):
        # TODO: Implement logic to map model_name to its corresponding class
        # This could be a simple dictionary lookup or a more complex factory pattern
        pass
```

### Configuration System

The Configuration System provides a flexible way to specify model requirements for different scenarios. It consists of:

- A JSON configuration file that specifies default models for different routes and customer-specific models
- Environment variables for globally required models
- Request parameters for dynamic, request-specific model requirements

This multi-layered approach to configuration allows for both static, pre-defined model requirements and dynamic, runtime model selection. It supports a wide range of use cases, from simple, static model assignments to complex, customer-specific model configurations that can be updated without code changes.

```
{
    "/predict": {
        "models": ["base_model", "feature_extractor"]
    },
    "/batch_process": {
        "models": ["batch_model"]
    },
    "customers": {
        "customer1": {
            "models": ["customer1_specific_model"]
        },
        "customer2": {
            "models": ["customer2_specific_model"]
        }
    }
}
```

### Database

Shared state is crucial in our distributed model management system to ensure consistency and coordination across multiple containers or nodes. It allows all instances of the DistributedModelManager to have a unified view of which models are loaded, their reference counts, and their last used timestamps. This shared state prevents redundant loading of models, enables efficient resource utilization, and facilitates coordinated decision-making for model unloading. Redis is our initial choice for managing this shared state due to its speed, simplicity, and built-in support for distributed locks. It offers low-latency data access, which is vital for quick decision-making in model management, and its (rather rudimentary) pub/sub mechanism can be leveraged for pseudo-real-time updates across the system.

However, as the system scales or requirements evolve, alternatives to Redis might be considered. For instance, Etcd might be preferred in Kubernetes environments for its tight integration with the ecosystem and support for distributed consensus. Additionally, in cloud-native environments, managed services like AWS ElastiCache could be considered for their scalability and reduced operational overhead. The choice among these alternatives would depend on factors such as scale of deployment, specific consistency requirements, integration with existing infrastructure, and the need for advanced querying capabilities on the shared state.

Regardless of the shared state chosen, the key-value pairs storing model metadata:

- Key: `model_info_{model_name}`
- Value: JSON object containing:

    - `path`: Path to model file in shared storage
    - `last_used`: Timestamp of last usage
    - `ref_count`: Current reference count

We will use Redis-based locks for all operations that modify shared state. For multi-step operations, these operations will be within a Redis transaction to ensure atomicity.

```
from redis_lock import Lock

with Lock(self.redis, f"model_lock_{model_name}"):
    # Perform thread-safe operations
```

## Docker

#### docker-compose.yml

```
version: '3'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  model_service_1:
    build: .
    volumes:
      - ./shared_models:/shared/models
    environment:
      - REDIS_HOST=redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  model_service_2:
    # Similar configuration to model_service_1

volumes:
  shared_models:
```

#### Dockerfile

```
FROM pytorch/pytorch:latest

RUN pip install redis redis-lock pynvml

COPY . /app
WORKDIR /app

CMD ["python", "your_model_script.py"]
```

## Future Enhancements

### Optimization Strategies

Here, we will discuss various optimizations we can consider for managing models in finite GPU space. We will implement a preloading mechanism for frequently used models:

```
def preload_models(self, model_names):
    for name in model_names:
        self.load_model(name, get_model_class(name))
        # Set a minimum reference count to keep in memory
        self._set_min_ref_count(name, 1)
```

We can implement an adaptive unloading algorith. We can enhance a `_consider_unloading` function to consider factors like:

- Model size
- Loading time
- Usage frequency
- Time since last use

To tie these all together, we will implement a background task to periodically check for and potentially unload zero-reference models:

```
import asyncio

async def periodic_cleanup(self, interval=300):  # 5 minutes
    while True:
        self._cleanup_unused_models()
        await asyncio.sleep(interval)

def _cleanup_unused_models(self):
    for model_name in self.get_model_usage():
        if self.get_model_usage()[model_name]['ref_count'] == 0:
            self._consider_unloading(model_name)
```

Some other points

1. Validation: Add validation to ensure that requested models (especially from user input) are allowed and exist.
2. Prioritization: Implement a priority system for model loading when GPU memory is constrained.
3. Logging and Monitoring: Add detailed logging to track which models are being used for each request and by which customers.
4. Model Versioning: Extend the system to handle different versions of models for different customers or use cases.
5. Error Handling: Implement more granular error handling for cases where specific models fail to load.

This updated design provides a highly flexible and abstracted way to manage model dependencies for your workflow entry points. It allows for easy configuration changes and customer-specific customizations without modifying the core application logic.

### Monitoring and Logging

TODO: Implement comprehensive logging for all major operations:

- Model loading/unloading
- Reference count changes
- GPU memory usage fluctuations

TODO: Collect and store metrics for analysis:

- Model load times
- Frequency of model usage
- GPU memory utilization over time

TODO: Set up alerts for critical situations:

- GPU memory nearing capacity
- Frequent model thrashing (repeated loading/unloading)
- High contention on specific models

### Other Considerations

#### Multiple GPUs

Extend the system to manage multiple GPUs:

- Track per-GPU memory usage
- Implement load balancing across GPUs

#### Redis Cluster

For high-scale deployments, consider using Redis Cluster for improved performance and reliability.

### Future Enhancements

- Dynamic GPU allocation based on model requirements and current load
- Integration with container orchestration systems (e.g., Kubernetes) for automated scaling
- Implementation of model versioning and rollback capabilities
- Support for distributed training across multiple containers
- Timeout Handling: we can consider adding a timeout for model loading to prevent long waits.
- Queueing: For more advanced scenarios, we could implement a request queue when models are unavailable instead of immediately returning a 429 error.

# Kubernetes

TBD

## Isto

[Istio](https://istio.io/)is an open source service mesh designed to make it easier to connect, manage and secure traffic between, and obtain telemetry about microservices running in containers. Istio is a collaboration between IBM, Google and Lyft.

“[What is a Service Mesh?](https://glasnostic.com/blog/what-is-a-service-mesh-istio-linkerd-envoy-consul/)”

*A service mesh is not a “mesh of services.” It is a mesh of Layer 7 proxies that microservices can use to completely abstract the network away. Service meshes are designed to solve the many challenges developers face when talking to remote endpoints.*
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Despite the advantages of abstracting the network away, service meshes are not as widely used as one would expect. There are competing standards out there – for instance Linkerd and Consul have their own concept of a service mesh, and they don't integrate well together. While the performance of service meshes vary with the implementation, there is a significant amount of new complexity that they bring.They are rather new on the scene, and the general space is still evolving.

Service meshes require an investment in a platform that can be difficult to justify when applications are still evolving. The impact on application performance when compared to direct calls across the network can be substantial. For an orchestration application like AI+, this may not be too much of a penalty, since the amount of computational processing is minimal compared to network I/O. The tooling to diagnose and remediate connectivity and other issues simply don't exist, but again, we are using a small subset of Istio's functionality. We don't necessarily want developers to become experts in Istio to be able to troubleshoot issues.

### Istio Architecture

Istio service mesh consists of a data plane and a control plane.

#### Istio data plane

The Istio data plane is typically composed of[Envoy proxies](https://envoyproxy.github.io/envoy/)that are deployed as sidecars within each container on the Kubernetes pod. These proxies take on the task of establishing connections to other services and managing the communication between them.

#### Istio control plane

The[Pilot](https://istio.io/docs/concepts/traffic-management/#pilot-and-envoy)component is responsible for configuring the data plane. Apart from defining basic proxy behaviors, it also allows a user to specify routing rules between proxies as well as failure recovery features.

The[Mixer](https://istio.io/docs/concepts/policies-and-telemetry/)component of Istio collects traffic metrics and can respond to various queries from the data plane such as authorization, access control or quota checks. Depending on which adapters are enabled, it can also interface with logging and monitoring systems.

[Citadel](https://istio.io/docs/concepts/security/)is the component that allows developers to build zero-trust environments based on service identity rather than network controls. It is responsible for assigning certificates to each service and can also accept external certificate authority keys when needed.

### Istio Microservice Integration

TBD: The prototype will use the following Istio concepts. There is a singular [Gateway](https://istio.io/docs/reference/config/networking/gateway/) object that routes all requests from the Istio Ingress Gateway to all component [Virtual Services](https://istio.io/docs/reference/config/networking/virtual-service/).

```
apiVersion: networking.istio.io/v1alpha3

kind: Gateway
metadata:
 name: uservice-gateway
 namespace: tenant1
spec:
 selector:
 istio: ingressgateway # use Istio default gateway implementation
 servers:
port:
 number: 80
 name: http
 protocol: HTTP
 hosts:
"aiplus.datacore.com"
```

The Virtual Service will route various URIs to their component parts.

```
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService

metadata:
 name: ObjectDetection
 namespace: tenant1

spec:
 hosts:
    "aiplus.datacore.com"
 gateways:
     uservice-gateway
```

Other VirtualService concepts we can use:

- [Weight-based routing](https://istio.io/docs/reference/config/networking/virtual-service/#HTTPRouteDestination)
- [HTTP retry policies](https://istio.io/docs/reference/config/networking/virtual-service/#HTTPRetry)

Finally, there are [Destination Rules](https://istio.io/docs/reference/config/networking/destination-rule/) that control load balancing and circuit breaking options to the various microservices.

```
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: accountservice-rule
spec:
  host: accountservice.AI+.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30ms
        tcpKeepalive:
          time: 7200s
          interval: 75s
```

### Mutual TLS

Since Istio 1.4, all communications between the side cars and pods are done over Mutual TLS.

Istio tunnels service-to-service communication through the client- and server-side PEPs, which are implemented as[Envoy proxies](https://envoyproxy.github.io/envoy/). When a workload sends a request to another workload using mutual TLS authentication, the request is handled as follows:

1. Istio re-routes the outbound traffic from a client to the client’s local sidecar Envoy.
2. The client side Envoy starts a mutual TLS handshake with the server side Envoy. During the handshake, the client side Envoy also does a[secure naming](https://istio.io/latest/docs/concepts/security/#secure-naming)check to verify that the service account presented in the server certificate is authorized to run the target service.
3. The client side Envoy and the server side Envoy establish a mutual TLS connection, and Istio forwards the traffic from the client side Envoy to the server side Envoy.
4. After authorization, the server side Envoy forwards the traffic to the server service through local TCP connections.

However, this has the consequence of forcing everything to communicate over TLS, including any infrastructure services. This is sub-optimal, especially when distributed databases are deployed across multiple machines and geographic regions.
