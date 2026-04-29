---
title: "AI+ Architecture"
source_file: "AI__Architecture.doc"
converted_date: "2025-09-17T11:24:59.192066"
format: "markdown"
---

# AI+ Architecture

- Core Architecture
- Distributed Processi=ng
- Queue Interface
- Local Queue
- RabbitMQ
- AWS SQS
- Worker Interface
- Docker
- =GPU-Aware Distributed Model Management System
- Detailed Com=ponent Descriptions
- Distributed Model =Manager
- Model Factory
- Model Request Manager<=/a>
- Configuration System
- Database
- Docker
- docker-compose.yml<=/li>
- Dockerfile
- Future Enhancements
- Optimization Strate=gies
- Monitoring and Loggin=g
- Other Considerations
- Multiple GPUs
- Redis Cluster
- Future Enhancements
- Kubernetes
- Isto
- Istio Architecture
- Istio data plane
- Istio control plane<=/li>
- Istio Microse=rvice Integration
- Mutual TLS

# Core Architecture

The AI+ utilities are undergoing a major refactoring to reflect the modern =needs of enterprise software. Currently we have a few bespoke utilities tha=t require a fair amount of technical intervention to deploy. We need to get= to a place where we can deploy these as containers for runtime efficiency =and easy integration.

1. HTTP API:
The system will expose its functionality through a RESTful HTTP API. These =APIs will provide endpoints for business and admin functions. This API desi=gn ensures that the system can be easily integrated into various workflows =and applications.

2. Extensibility and Configurability:
The architecture is designed with extensibility in mind. New models can be �sily integrated by adding them to the shared object storage. The system u=ses a configuration singleton that can be dynamically updated, allowing for= runtime changes to system behavior. This includes the ability to modify pr=ompts used in vision tasks, enabling the system to adapt to new use cases w=ithout code changes.

3. Error Handling and Logging:
Robust error handling and logging are integrated throughout the system. A c=ustom logger is implemented to capture detailed information about the syste=m's operation, including performance metrics, error traces, and analysis re=sults. This logging system is designed to suppress certain warnings while s=till providing comprehensive debugging information when needed.

This architecture provides a solid foundation for a powerful, flexible, =and efficient video and image analysis system. It balances performance opti=mization with modularity and extensibility, allowing for easy maintenance a=nd future enhancements. The combination of parallel processing, efficient m�ia handling, and a well-designed API makes it suitable for a wide range o=f applications, from small-scale analysis tasks to large-scale video proces=sing pipelines.

# # Distributed Processing

The AI+ Core Architecture will consist of an implementation where we can= queue and execute tasks in a distributed manner. In AI workloads, tasks li=ke model training, data preprocessing, and inference can vary in duration a=nd resource requirements. A distributed queue ensures that tasks are balanc� across multiple workers, preventing any single container from becoming a= bottleneck. This setup also allows the system to dynamically scale by addi=ng or removing workers based on demand, leading to better resource utilizat=ion and reduced processing time. Furthermore, a distributed approach enhanc=es fault tolerance, as tasks can be reassigned to other workers if a contai=ner fails, ensuring reliability and continuity in AI processing pipelines.<=/p>

In the future, we will need to support multiple servers running multiple= GPUs. In this environment:

- The Queue Interface becomes crucial for distributing work across multipl=e containers. It allows tasks to be added from one container and processed =by another.

- The Worker Interface is important for managing the execution of tasks wi=thin each container, potentially utilizing multiple GPUs.

The combination of both interfaces provides several benefits:

1. Scalability: We can easily scale out by adding more workers or container=s that connect to the same queue.

2. Flexibility: We can have different types of workers \(CPU, GPU\) processin=g tasks from the same queue.

3. Load Balancing: Tasks can be distributed evenly across available resourc=es.

4. Fault Tolerance: If a worker fails, the task remains in the queue and ca=n be picked up by another worker.

5. Decoupling: The system producing tasks \(e.g., image upload service\) can � separate from the system processing tasks.

... async def start_processing(self): self.progress = 20 # <-- Not quite sure why this variable is i=mplemented this way. self.worker.start() # Set up signal handlers for graceful shutdown for sig in (signal.SIGINT, signal.SIGTERM): signal.signal(sig, self._signal_handler) try: while not self.shutdown_event.is_set(): try: item = self.queue.get(timeout=1) # Non-blocking wi=th a timeout if item: task = asyncio.create_task(self._process_work_ite=m(item)) self.processing_tasks.add(task) task.add_done_callback(self.processing_tasks.discar=d) except Exception as e: if not self.shutdown_event.is_set(): logger.error(f"Error getting item from queue: {e}") await asyncio.sleep(0.1) # Small delay to prevent tight lo=op finally: await self._shutdown() def _signal_handler(self, signum, frame): logger.info(f"Received signal {signum}. Initiating shutdown...") self.shutdown_event.set() async def _shutdown(self): logger.info("Shutting down...") self.worker.stop() # Wait for all processing tasks to complete if self.processing_tasks: await asyncio.wait(self.processing_tasks) self.worker.join() self.queue.close() logger.info("Shutdown complete.")

# # Queue Interface

The AI+ system's support for multiple queue types is a key feature that =enhances its flexibility and scalability. By implementing a pluggable queue= interface, the system can adapt to different deployment scenarios and proc=essing requirements.

## # Local Queue

The local queue option, using Python's built-in queue module, is suitabl=e for single-machine deployments or testing environments. It provides a sim=ple, in-memory queue that doesn't require any additional infrastructure. Wh=ile it doesn't support distributed processing, it's perfect for smaller-sca=le applications or development purposes.

## # RabbitMQ

RabbitMQ support adds the capability for distributed processing across m=ultiple machines. As a robust message broker, RabbitMQ allows the system to= decouple the task producers \(e.g., image uploaders\) from the consumers \(fa=cial recognition workers\). This separation enables horizontal scaling of th=e processing nodes and provides features like message persistence and advan�d routing capabilities. RabbitMQ is an excellent choice for deployments t=hat require high throughput and the ability to scale processing across a cl=uster of machines.

## # AWS SQS

The inclusion of Amazon SQS \(Simple Queue Service\) as a queue option cat=ers to cloud-native deployments, particularly those running on AWS infrastr=ucture. SQS offers a fully managed queuing service, removing the need for s=elf-managed queue infrastructure. It provides seamless scalability and inte=grates well with other AWS services. This option is ideal for deployments t=hat prioritize minimal operational overhead and want to leverage cloud-nati=ve services.

By supporting these diverse queue types, the AI+ system can be adapted t=o a wide range of deployment scenarios. Whether it's a small-scale local de=ployment, an on-premises distributed system, or a cloud-based scalable solu=tion, the appropriate queue can be selected without changing the core recog=nition logic. This flexibility not only accommodates different architectura=l needs but also allows for easy migration between different deployment mod=els as the system's requirements evolve.

# # Worker Interface

The worker interface in this facial recognition system is designed to pr=ovide a flexible and scalable approach to processing AI+ tasks. It abstract=s the underlying execution model, allowing for seamless switching between l=ocal multi-threading and distributed processing without changing the core r�ognition logic. This abstraction is crucial for adapting the system to va=rious deployment scenarios, from single-machine setups to large-scale distr=ibuted environments.

We have two primary implementations of a worker interface: LocalThreadPo=olWorker and DistributedWorker. The LocalThreadPoolWorker is designed for s=ingle-machine deployments, utilizing Python's threading module to create a =pool of worker threads. Each thread in this pool continuously pulls tasks f=rom the queue and processes them until the stop signal is received. This im=plementation is ideal for maximizing CPU utilization on a single machine, e=specially for I/O-bound tasks like facial recognition.

On the other hand, the DistributedWorker is tailored for scalable, multi=-machine deployments. It leverages Celery, a distributed task queue system,= to distribute work across multiple processes or machines. This implementat=ion creates a Celery task for each work item and enqueues these tasks to be= processed by Celery workers running on various machines. The DistributedWo=rker maintains a local enqueue loop that pulls items from the facial recogn=ition system's queue and pushes them to Celery's distributed queue.

Both worker implementations handle task processing in a similar manner, �lling a provided work function for each task. This work function, typical=ly the \_process\_work\_item method of the FacialRecognition class, encapsulat=es the core logic of facial detection, embedding generation, and similarity= matching. By using a consistent interface for task processing, the system =maintains a clear separation between the worker's execution model and the a=ctual recognition logic.

The worker interface also includes error handling and dead-letter queue =\(DLQ\) functionality. If a task fails during processing, the worker can move= it to a DLQ for later inspection and potential reprocessing. This feature =enhances the system's robustness, ensuring that problematic tasks don't hal=t the entire recognition process and can be addressed separately.

# # Docker

- Nvidia GPU with CUDA. Note that nothing about this architecture preclude=s supporting other GPUs in the future, but our current needs require Nvidia=

- Ubuntu 22.04

- Docker

- \(Optional\) Kubernetes

We will deploy the various utilities we use as individual microservices,= which we can deploy in containers and in a container-management environmen=t to enhance their usability, accessibility, and maintainability. We will e=xpose the uService with a RESTful API., where other Perifery and 3rd party =utilities can easily call the model from different platforms and programmin=g languages. This reduces the complexity for developers who need to integra=te the service, as they interact with a higher-level interface rather than =diving into the intricacies of the service’s implementation. We can= also version the model API in various ways. We can either version the URL =itself or use a service mesh for versioning, A/B testing, canary deployment=s, etc.

Typically, we will architect these models in the following way.

The API will be HTTP 1.1 \(or HTTP/2, if we enable TLS\). Note that we cou=ld use gRPC as a backend for greater throughput, but the number of requests= to the model should be low enough that we don’t need that sort of =optimization. The models themselves will be shared across the server via a =loaded volume \(on nVME\).

Since the services will be deployed on Nvidia GPUs with CUDA support, we= will be using CUDA-enabled images and passing the GPU runtime to the docke=r-compose file.

# Use N=VIDIA CUDA 12.4 runtime as the base imageFROM nvidia/cuda:12.4.0-runtime-ubuntu22.04# Set the working directory in the containerWORKDIR /app# Install system dependencies and PythonRUN apt-get update && apt-get install -y \ python3-pip \ python3-dev \ libgl1-mesa-glx \ libglib2.0-0 \ git \ && rm -rf /var/lib/apt/lists/*# Set Python3 as the default PythonRUN ln -s /usr/bin/python3 /usr/bin/pythonCOPY requirements/requirements.http.txt \ requirements/requirements.gpu.txt \ requirements/requirements.groundingdino.txt \ requirements/requirements.yolo.txt \ requirements/requirements.flash_attn.txt \ requirements/_requirements.txt \ ./# Install any needed packages specifiedRUN pip3 install \ -r _requirements.txt \ -r requirements.http.txt \ -r requirements.gpu.txt \ -r requirements.groundingdino.txt \ -r requirements.yolo.txt \ --upgrade \ && rm -rf ~/.cache/pip# Install setup.py requirements for flash_attnRUN python3 -m pip install packaging==24.1 && rm -rf ~/.cache/=pip# Install flash_attn, since it needs to be managed via its own build proces=s, apparently.RUN python3 -m pip install -r requirements.flash_attn.txt --no-build-isolat=ion && rm -rf ~/.cache/pip# Copy the current directory contents into the container at /appCOPY . /app# Define environment variableENV PROJECT=aiplus# Run the API when the container launchesCMD ["python", "-m", "aiplus.rest.api"]

version=: '3.8'services: object-detection: build: . ports: - "${PORT:-9001}:${PORT:-9001}" volumes: - ${VIDEO_DIR:-./videos}:/app/videos:ro - ${OUTPUT_DIR:-./outputs}:/app/outputs - /opt/aiplus/models:/opt/aiplus/models environment: - DEBUG=1 - VIDEO_DIR=/home/aiplus/testdata - OUTPUT_DIR=/home/aiplus/tests # USED FOR DEBUG ONLY! - PORT=${PORT:-9001} deploy: resources: reservations: devices: - driver: nvidia count: all capabilities: [gpu]

If these microservices are deployed in Kubernetes, the models and weight=s can be deployed in a Persistent Volume and Persistent Volume Claim, for s=haring across multiple nodes.

apiVers=ion: v1kind: PersistentVolumemetadata: name: ai-model-storagespec: capacity: storage: 10Gi accessModes: - ReadWriteMany nfs: path: /dev/nvme0n1p2/models server: aiplus.datacore.com

apiVers=ion: v1kind: PersistentVolumeClaimmetadata: name: ai-model-storage-claimspec: accessModes: - ReadWriteMany resources: requests: storage: 1000Gi

# GPU-Aw=are Distributed Model Management System

Multiple containers can make use of various models to perform business t=asks. However, the GPU itself is a finite resource, and AI models can take =up a significant memory footprint. This GPU-Aware Distributed Model Managem=ent System is designed to efficiently manage AI models across multiple Dock=er containers, optimizing GPU resource utilization. This system enables coo=rdinated loading, unloading, and sharing of models while maintaining awaren=ess of GPU memory constraints.

The system consists of the following components:

- Multiple Docker containers running AI models

- A Redis container for shared state management

- Shared storage volume for model persistence

The high-level flow is as follows:

1. AI containers use DistributedModelManager to load, access, and release m=odels.

2. A shared Redis cache maintains metadata about loaded models and facilita=tes distributed locking.

3. Shared storage holds serialized model files accessible to all containers=.

4. GPU usage is monitored across containers to inform loading/unloading dec=isions.

IMPORTANT NOTE: If our system incorporates the Roboflow and/or Nvidia Tr=iton inference servers, we will also need to build hooks into them to bette=r monitor the GPU utilization so we can make better decisions.

# # Detailed Component= Descriptions

## # Distributed Model Manage=r

The Distributed Model Manager is the core component responsible for the �tual handling of model files and their metadata. It interfaces with Redis= for distributed state management and a shared file system for model storag=e. Its key functions include:

- Loading models into GPU memory and persisting them to shared storage

=
- Unloading models when they're no longer needed or when GPU memory is con=strained

- Tracking model metadata, including reference counts and last used timest=amps

- Providing thread-safe operations through distributed locking mechanisms<=/p>

- Monitoring GPU memory usage to inform loading/unloading decisions

The DistributedModelManager ensures efficient use of GPU resources acros=s multiple containers, preventing redundant model loading and managing memo=ry constraints. It provides a consistent interface for other components to =interact with the underlying model storage and GPU resources.

For NVIDIA GPUs, we will implement `_check_gpu_memory_usage() using the NVIDIA Management Library (NVML):`

import py=nvmldef _check_gpu_memory_usage(self): pynvml.nvmlInit() handle = pynvml.nvmlDeviceGetHandleByIndex(0) info = pynvml.nvmlDeviceGetMemoryInfo(handle) pynvml.nvmlShutdown() return info.used / info.total

TODO: Add implementation for other GPUs

The base thresholds are as follows:

- Set a GPU memory usage threshold \(e.g., 80%\)

- Trigger unloading operations when threshold is exceeded

When unloading a model, we will use the following heuristics:

1. Identify models with zero reference count

2. Among zero-reference models, unload the least recently used

3. If no zero-reference models, wait for releases or raise an exception

=

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

- Identifies and unloads the least recently used model with zero reference=s

- `_consider_unloading(model_name)`

- Decides whether to unload a model based on current system state

- `get_model_usage()`

- Retrieves current usage statistics for all models

## # Model Factory

The Model Factory is responsible for dynamically determining which model=s are required for each incoming request. It abstracts the model selection =logic away from the application routes, allowing for flexible and configura=ble model requirements. The Model Factory:

- Loads and parses a configuration file specifying default model requireme=nts for different routes

- Retrieves model specifications from environment variables

- Handles customer-specific model requirements

- Processes request-specific model parameters

By centralizing the model selection logic, the Model Factory allows for �sy updates to model requirements without changing application code. It su=pports a variety of use cases, from static route-based model selection to d=ynamic, customer-specific model loading, all configurable through external =means.

import osimport jsonfrom flask import requestclass ModelFactory: def __init__(self, config_path='config/model_config.json'): self.config = self._load_config(config_path) self.env_models = self._load_env_models() def _load_config(self, config_path): with open(config_path, 'r') as f: return json.load(f) def _load_env_models(self): return {k[6:]: v for k, v in os.environ.items() if k.startswith('MO�L_')} def get_required_models(self, route): models = set() # Add models from configuration if route in self.config: models.update(self.config[route].get('models', [])) # Add models from environment variables models.update(self.env_models.values()) # Add customer-specific models from HTTP headers, for instance. customer_id = request.headers.get('X-Customer-ID') if customer_id and customer_id in self.config.get('customers', {}): models.update(self.config['customers'][customer_id].get('models=', [])) # Add models from request parameters if 'models' in request.json: models.update(request.json['models']) return list(models)

## # Model Request Manager

The Model Request Manager acts as a bridge between the web application r=outes and the model management system. It wraps each route to ensure that a=ll required models are loaded before the route logic is executed. Its prima=ry functions include:

- Interfacing with the ModelSelector to determine required models for each= request

- Checking if required models are loaded and initiating loading if necessa=ry

- Updating reference counts for models when they're used

- Handling errors and returning appropriate HTTP responses \(e.g., 429 for =unavailable models\)

- Releasing models \(decrementing reference counts\) after request completio=n

This manager abstracts the complexities of model management away from th=e application logic, allowing developers to focus on implementing the core =functionality of each route without worrying about model availability or re=source management.

The base operation is:

1. Check if required models are loaded

2. Update reference counts

3. Handle errors and return appropriate HTTP responses

4. Release models after the workflow completes

from func=tools import wrapsfrom flask import request, jsonifyfrom distributed_model_manager import DistributedModelManagerclass ModelRequestManager: def __init__(self, model_manager: DistributedModelManager): self.model_manager = model_manager def require_models(self): def decorator(f): @wraps(f) def wrapped(*args, **kwargs): route = request.endpoint try: # Dynamically determine required models required_models = self.model_selector.get_required_mo�ls(route) # Check and load required models unavailable_models = self._ensure_models_loaded(requi=red_models) if unavailable_models: return self._models_unavailable_response(unavailabl=e_models) # Update reference counts self._increment_ref_counts(required_models) # Execute the wrapped function result = f(*args, **kwargs) return result except Exception as e: return self._error_response(str(e)) finally: # Release models if 'required_models' in locals(): self._release_models(required_models) return wrapped return decorator def _ensure_models_loaded(self, model_names): unavailable_models = [] for model_name in model_names: if not self.model_manager.is_model_loaded(model_name): try: self.model_manager.load_model(model_name, self._get_mod=el_class(model_name)) except Exception: unavailable_models.append(model_name) return unavailable_models def _increment_ref_counts(self, model_names): for model_name in model_names: self.model_manager.increment_ref_count(model_name) def _release_models(self, model_names): for model_name in model_names: self.model_manager.release_model(model_name) def _models_unavailable_response(self, unavailable_models): response = { "error": "Required models unavailable", "unavailable_models": unavailable_models, "message": "The server is currently unable to handle the reques=t due to a temporary overloading or maintenance of the server." } return jsonify(response), 429 def _error_response(self, error_message): response = { "error": "Internal server error", "message": error_message } return jsonify(response), 500 def _get_model_class(self, model_name): # TODO: Implement logic to map model_name to its corresponding clas=s # This could be a simple dictionary lookup or a more complex factor=y pattern pass

## # Configuration System

The Configuration System provides a flexible way to specify model requir=ements for different scenarios. It consists of:

- A JSON configuration file that specifies default models for different ro=utes and customer-specific models

- Environment variables for globally required models

- Request parameters for dynamic, request-specific model requirements

<=/li>

This multi-layered approach to configuration allows for both static, pre=-defined model requirements and dynamic, runtime model selection. It suppor=ts a wide range of use cases, from simple, static model assignments to comp=lex, customer-specific model configurations that can be updated without cod=e changes.

{ "/predict": { "models": ["base_model", "feature_extractor"] }, "/batch_process": { "models": ["batch_model"] }, "customers": { "customer1": { "models": ["customer1_specific_model"] }, "customer2": { "models": ["customer2_specific_model"] } }}

## # Database

Shared state is crucial in our distributed model management system to en=sure consistency and coordination across multiple containers or nodes. It a=llows all instances of the DistributedModelManager to have a unified view o=f which models are loaded, their reference counts, and their last used time=stamps. This shared state prevents redundant loading of models, enables eff=icient resource utilization, and facilitates coordinated decision-making fo=r model unloading. Redis is our initial choice for managing this shared sta=te due to its speed, simplicity, and built-in support for distributed locks=. It offers low-latency data access, which is vital for quick decision-maki=ng in model management, and its \(rather rudimentary\) pub/sub mechanism can � leveraged for pseudo-real-time updates across the system.

However, as the system scales or requirements evolve, alternatives to Re=dis might be considered. For instance, Etcd might be preferred in Kubernete=s environments for its tight integration with the ecosystem and support for= distributed consensus. Additionally, in cloud-native environments, managed= services like AWS ElastiCache could be considered for their scalability an=d reduced operational overhead. The choice among these alternatives would d=epend on factors such as scale of deployment, specific consistency requirem=ents, integration with existing infrastructure, and the need for advanced q=uerying capabilities on the shared state.

Regardless of the shared state chosen, the key-value pairs storing model= metadata:

- Key: `model_info_{model_name}`

- Value: JSON object containing:

- `path`: Path to model file in shared storage

- `last_used`: Timestamp of last usage

- `ref_count`: Current reference count

We will use Redis-based locks for all operations that modify shared stat=e. For multi-step operations, these operations will be within a Redis trans�tion to ensure atomicity.

from redi=s_lock import Lockwith Lock(self.redis, f"model_lock_{model_name}"): # Perform thread-safe operations

# # Docker

### # docker-compose.yml

version=: '3'services: redis: image: redis:latest ports: - "6379:6379" model_service_1: build: . volumes: - ./shared_models:/shared/models environment: - REDIS_HOST=redis deploy: resources: reservations: devices: - driver: nvidia count: 1 capabilities: [gpu] model_service_2: # Similar configuration to model_service_1volumes: shared_models:

### # Dockerfile

FROM py=torch/pytorch:latestRUN pip install redis redis-lock pynvmlCOPY . /appWORKDIR /appCMD ["python", "your_model_script.py"]

# # Future Enhancements

## # Optimization Strategies

Here, we will discuss various optimizations we can consider for managing= models in finite GPU space. We will implement a preloading mechanism for f=requently used models:

def prelo�_models(self, model_names): for name in model_names: self.load_model(name, get_model_class(name)) # Set a minimum reference count to keep in memory self._set_min_ref_count(name, 1)

We can implement an adaptive unloading algorith. We can enhance a `=_consider_unloading` function to consider factors like:

- Model size

- Loading time

- Usage frequency

- Time since last use

To tie these all together, we will implement a background task to period=ically check for and potentially unload zero-reference models:

import as=yncioasync def periodic_cleanup(self, interval=300): # 5 minutes while True: self._cleanup_unused_models() await asyncio.sleep(interval)def _cleanup_unused_models(self): for model_name in self.get_model_usage(): if self.get_model_usage()[model_name]['ref_count'] == 0: self._consider_unloading(model_name)

Some other points

1. Validation: Add validation to ensure that requested models \(especially f=rom user input\) are allowed and exist.

2. Prioritization: Implement a priority system for model loading when GPU m=emory is constrained.

3. Logging and Monitoring: Add detailed logging to track which models are b=eing used for each request and by which customers.

4. Model Versioning: Extend the system to handle different versions of mode=ls for different customers or use cases.

5. Error Handling: Implement more granular error handling for cases where s=pecific models fail to load.

This updated design provides a highly flexible and abstracted way to man=age model dependencies for your workflow entry points. It allows for easy c=onfiguration changes and customer-specific customizations without modifying= the core application logic.

## # Monitoring and Logging

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

- Frequent model thrashing \(repeated loading/unloading\)

- High contention on specific models

## # Other Considerations

### # Multiple GPUs

Extend the system to manage multiple GPUs:

- Track per-GPU memory usage

- Implement load balancing across GPUs

### # Redis Cluster

For high-scale deployments, consider using Redis Cluster for improved pe=rformance and reliability.

## # Future Enhancements

- Dynamic GPU allocation based on model requirements and current load

<=/li>
- Integration with container orchestration systems \(e.g., Kubernetes\) for =automated scaling

- Implementation of model versioning and rollback capabilities

- Support for distributed training across multiple containers

- Timeout Handling: we can consider adding a timeout for model loading to =prevent long waits.

- Queueing: For more advanced scenarios, we could implement a request queu=e when models are unavailable instead of immediately returning a 429 error.=

# Kubernetes

TBD

# # Isto

[I=stio](https://istio.io/) is an open source service mesh designed to make it easier to =connect, manage and secure traffic between, and obtain telemetry about micr=oservices running in containers. Istio is a collaboration between IBM, Goog=le and Lyft.

“[What i=s a Service Mesh?](https://glasnostic.com/blog/=what-is-a-service-mesh-istio-linkerd-envoy-consul/)”

_A service mesh is not a “mesh of services.” It is a =mesh of Layer 7 proxies that microservices can use to completely abstract t=he network away. Service meshes are designed to solve the many challenges d=evelopers face when talking to remote endpoints._
---

Despite the advantages of abstracting the network away, service meshes a=re not as widely used as one would expect. There are competing standa=rds out there – for instance Linkerd and Consul have their own conc=ept of a service mesh, and they don't integrate well together. While =the performance of service meshes vary with the implementation, there is a =significant amount of new complexity that they bring. They are r=ather new on the scene, and the general space is still evolving.

Service meshes require an investment in a platform that can be difficult= to justify when applications are still evolving. The impact on appli�tion performance when compared to direct calls across the network can be =substantial. For an orchestration application like AI+, this ma=y not be too much of a penalty, since the amount of computational processin=g is minimal compared to network I/O. The tooling to diagnose and rem�iate connectivity and other issues simply don't exist, but again, we are =using a small subset of Istio's functionality. We don't necessarily w=ant developers to become experts in Istio to be able to troubleshoot issues=.

## # Istio Architecture

Istio service mesh consists of a data plane and a control plane.

### # Istio data plane

The Istio data plane is typically composed of [Envoy p=roxies](https://envoyproxy.github.io/envoy/) that are deployed as sidecars within each container on the =Kubernetes pod. These proxies take on the task of establishing connections =to other services and managing the communication between them.

### # Istio control plane

The [Pilot](https://istio.io/docs/concep=ts/traffic-management/#pilot-and-envoy) com=ponent is responsible for configuring the data plane. Apart from defining b=asic proxy behaviors, it also allows a user to specify routing rules betwee=n proxies as well as failure recovery features.

The [Mixer](https://istio.io/docs/concep=ts/policies-and-telemetry/) component of Is=tio collects traffic metrics and can respond to various queries from the da=ta plane such as authorization, access control or quota checks. Depending o=n which adapters are enabled, it can also interface with logging and monito=ring systems.

[Citadel](https://istio.io/docs/concepts/securi=ty/) is the component that allows develop=ers to build zero-trust environments based on service identity rather than =network controls. It is responsible for assigning certificates to each serv=ice and can also accept external certificate authority keys when needed.

## # Istio Microservice =Integration

TBD: The prototype will use the following Istio concepts. There is= a singular [Gateway](https://istio.io/docs/refere=nce/config/networking/gateway/) object that ro=utes all requests from the Istio Ingress Gateway to all component [Virtual Services](https://istio.io/docs/reference/config/networkin=g/virtual-service/).

apiVers=ion: networking.istio.io/v1alpha3kind: Gatewaymetadata: name: uservice-gateway namespace: tenant1spec: selector: istio: ingressgateway # use Istio default gateway implem=entation servers:port: number: 80 name: http protocol: HTTP hosts:"aiplus.datacore.com"

The Virtual Service will route various URIs to their component parts.

apiVers=ion: networking.istio.io/v1alpha3kind: VirtualServicemetadata: name: ObjectDetection namespace: tenant1spec: hosts: "aiplus.datacore.com" gateways: uservice-gateway

Other VirtualService concepts we can use:

- [Weight=-based routing](https://istio.io/docs/reference/confi=g/networking/virtual-service/#HTTPRouteDestination)

- [HTTP retry polici=es](https://istio.io/docs/reference/confi=g/networking/virtual-service/#HTTPRetry)

Finally, there are [Destina=tion Rules](https://istio.io/d=ocs/reference/config/networking/destination-rule/) that control load balancing and circuit breaking options to =the various microservices.

apiVers=ion: networking.istio.io/v1beta1kind: DestinationRulemetadata: name: accountservice-rulespec: host: accountservice.AI+.svc.cluster.local trafficPolicy: loadBalancer: simple: LEAST_CONN connectionPool: tcp: maxConnections: 100 connectTimeout: 30ms tcpKeepalive: time: 7200s interval: 75s

## # Mutual TLS

Since Istio 1.4, all communications between the side cars and pods are d=one over Mutual TLS.

Istio tunnels service-to-service communication through the client- and s=erver-side PEPs, which are implemented as Envoy proxies<=/a>. When a workload sends a request to another workload using mutual TLS a=uthentication, the request is handled as follows:

1. Istio re-routes the outbound traffic from a client to the client�=99s local sidecar Envoy.

2. The client side Envoy starts a mutual TLS handshake with the server side= Envoy. During the handshake, the client side Envoy also does a [secure naming](https://istio.io/latest/docs/concepts/security=/#secure-naming) check to verify th=at the service account presented in the server certificate is authorized to= run the target service.

3. The client side Envoy and the server side Envoy establish a mutual TLS c=onnection, and Istio forwards the traffic from the client side Envoy to the= server side Envoy.

4. After authorization, the server side Envoy forwards the traffic to the s=erver service through local TCP connections.

However, this has the consequence of forcing everything to communicate o=ver TLS, including any infrastructure services. This is sub-optimal, especi=ally when distributed databases are deployed across multiple machines and g=eographic regions.