---
title: "AI+ Scheduling and Inference Management"
source_file: "AI__Scheduling_and_Inference_Management.doc"
converted_date: "2025-09-17T11:24:59.288498"
format: "markdown"
---

# AI+ Scheduling and Inference Management

## # Architecture

The proposed design is a decoupled, event-driven system centered around =a persistent state store and a dedicated inference server. This model separ=ates application logic from resource-intensive model execution, ensuring re=liability, scalability, and efficient resource management.

### # **System= Diagram**

+------=-----------+ 1. Job Request +-----------------+| User/Client | -----------------> | Coordinator API |+-----------------+ +-------+---------+ | | 2. Create Job in Redis | & Notify Scheduler v+--------------------------------+ +-------+---------+ +-----------=-------------+| Redis | <--4b| Central | 4a. | Rabbit=MQ || (Job State). | ---->| Scheduler | <---| (Ev=ent Trigger) |+--------------------------------+ +-------+---------+ +----------=--------------+ ^ | | 8. Update Final State | 5. Dispatch Task | | +---------+-----------------------------+------------------------------+ | | v v+-----------------------------+ +--------------=----------+| Pre/Post-processing Worker | | CPU-Only W=orker || (e.g., VLM Logic) | | (e.g., Transc=ription) |+-------------+---------------+ +--------------=----------+ | | 6. Inference Request v+-----------------------------+ 7. Manages GPU +--------------=--+| NVIDIA Triton Server | --------------------------> | GPU Hard=ware |+-----------------------------+ +--------------=--+

### # **Com=ponent Summary**

- **Coordinator API:** The public-facing entry point that val=idates requests and creates initial job records in Redis.

- **Redis:** The **Single Source of Truth** for =the entire system, storing all job states and resource locks.

- **RabbitMQ:** A lightweight message bus used to send event =notifications \(e.g., "new job created"\) to trigger the scheduler.

- **Central Scheduler:** The "brain" of the system. It reads =state from Redis and dispatches tasks to appropriate workers based on resou=rce availability.

- **Workers \(Pre/Post-processing & CPU-Only\):** Stateless= containers that execute the business logic of a task. They read job detail=s from Redis, perform work \(which may include calling Triton\), and write re=sults back to Redis.

- **NVIDIA Triton Server:** A dedicated, high-performance ser=vice that runs the AI models, manages GPU memory, and handles all low-level= inference operations.

## # **Scheduler and Coordinator Architecture**

The Central Scheduler is the operational brain of the entire AI workflow=. It replaces a simple first-in, first-out queueing model with an intellige=nt, state-aware dispatch system. Its primary responsibility is to orchestra=te the execution of all jobs by allocating tasks to the appropriate workers= based on job requirements and real-time resource availability.

### # Core Logic and Operation

The scheduler is fundamentally **state-driven and resource-aware, not queue-driven. It operates on a continuous loop, making decisio=ns by querying Redis, which serves as the single source of truth.**

- **State-Driven Operation:** The scheduler does not pull job=s from a RabbitMQ queue. Instead, it directly queries Redis for all jobs wi=th a `status` of `pending`. This allows it to have a =complete view of all available work at all times.

- **GPU-Aware Dispatch:** Before dispatching any GPU-intensiv=e job, the scheduler checks for the existence of a distributed lock in Redi=s \(e.g., a key named `gpu:0:lock`\). It will only dispatch a job =with `gpu_requirement: "high"` if this lock is not present.

<=/li>
- **Parallel Execution:** The scheduler's logic is designed f=or maximum throughput. While the GPU is busy processing a long-running task=, the scheduler continues its loop, actively looking for and dispatching jo=bs with `gpu_requirement: "none"` to CPU-only workers.

- **Priority Handling:** Because it queries the entire set of= pending jobs, the scheduler can easily implement prioritization. It can so=rt the pending jobs by a `priority` field before selecting the n=ext one to run.

### # **=Workflow and Triggers**

The scheduler is triggered to run its decision loop through a hybrid mod=el, making it both responsive and resilient.

1. **Event-Driven Trigger \(RabbitMQ\):** When a new job is crea=ted or a worker releases the GPU lock, it can publish a lightweight, conten=t-free message to a RabbitMQ queue that the scheduler listens to. This prom=pts the scheduler to immediately run its loop, ensuring no time is wasted.<=/p>

2. **Periodic Trigger \(Timer\):** As a fallback and for general= resilience, the scheduler also runs its loop on a regular, short interval =\(e.g., every 1-2 seconds\). This ensures that any missed messages do not hal=t the system.

The core of the scheduler can be implemented as a standalone service run=ning the following logic:

def sch�uler_loop(): while True: # 1. Check GPU Resource State from Redis gpu_is_busy = redis_client.exists("gpu:0:lock") # 2. Handle GPU-Bound Jobs if the GPU is free if not gpu_is_busy: # Query Redis for the highest priority pending GPU job job_id = find_pending_gpu_job_from_redis() if job_id: # Atomically lock GPU and update job status redis_client.set("gpu:0:lock", job_id) update_job_status_in_redis(job_id, "running") # Dispatch to the appropriate worker dispatch_job_via_http(job_id) # 3. Handle CPU-Bound Jobs (always, in parallel) cpu_job_id = find_pending_cpu_job_from_redis() if cpu_job_id: update_job_status_in_redis(cpu_job_id, "running") dispatch_job_via_http(cpu_job_id) # Wait for the next cycle or an event trigger wait_for_trigger_or_timeout(2.0)

### # Summary of Responsibilities

- Continuously monitor the state of pending jobs and resources in Redis.

- Managing the distributed lock for the GPU resource.

- Dispatching jobs to appropriate worker services.

- Updating job statuses in Redis from `pending` to `runnin=g`.

- Operating independently of the workers, ensuring the system is resilient= to worker failures.

## # **Job Lifecycle and State Management**

Job management is elevated from an implicit, in-app concern to an explic=it, centralized process. The entire lifecycle of a job, from creation to co=mpletion, is tracked through a state machine within Redis, which acts as th=e single source of truth. This approach provides complete visibility, resil=ience, and a clear record for every task processed by the system.

### # **The Job Object: Single Source of Truth**

Every task submitted to the system is represented by a single hash objec=t in Redis, keyed by a unique `job_id`. This object contains all= information related to the job and is the authoritative record of its stat=e.

A standard job object includes the following fields:

- `job_id`: A unique identifier \(e.g., UUID\) generated by the C=oordinator upon creation.

- `status`: The current state of the job in its lifecycle \(e.g.=, `pending`, `running`, `completed`, failed\).

- `task_type`: A string identifying the type of work to be done= \(e.g., `vlm_processing`, `audio_transcription`\).

=
- `gpu_requirement`: Specifies the required hardware resource \(=`high` or `none`\). This is critical for the Scheduler=.

- `priority`: A numerical priority \(e.g., 1-10\) to allow the Sc=heduler to prioritize important jobs.

- `created_at`: The UTC timestamp of the job's creation.

- `updated_at`: The UTC timestamp of the last status change.

- `input_payload`: A JSON string containing the inputs for the =job, such as file paths, user prompts, or other parameters.

- `result`: A JSON string containing the output of a successful=ly completed job.

- `error_message`: A string detailing the reason for failure if= the job's status is `failed`.

### # **Jo=b State Lifecycle**

A job progresses through a well-defined state machine. The `status<=/code> field in the Redis hash is updated at each transition.`

= +-----------+ | Scheduler | | Dispatches| +-----+-----+ | v[ Pending ] ---------> [ Running ] | +---------------+---------------+ | | +-----v-----+ +------v----+ | Worker | | Worker | | Completes | | Fails | +-----------+ +-----------+ | | v v [ Completed ] [ Failed ]

- `pending`: The initial state. The job has been created and sa=ved to Redis but has not yet been selected for execution by the Scheduler.<=/p>

- `running`: The Scheduler has selected the job for execution a=nd has dispatched it to a worker. For GPU jobs, this state is set concurren=tly with the acquisition of the GPU lock.

- `completed`: A terminal state. The worker has successfully fi=nished the task, written the output to the `result` field, and r=eleased any acquired resources.

- `failed`: A terminal state. The worker encountered an unrecov=erable error during processing and has written details to the `error_m=essage` field.

### # Component Responsibilities

- **Coordinator:**

- **Creates** the job object in Redis with `status: "pen=ding"`.

- Populates all initial fields, including `job_id`, `task_=type`, `input_payload`, and `gpu_requirement`.<=/p>

- **Scheduler:**

- **Reads** jobs with `status: "pending"`.

- Upon dispatching a job, **updates** its status to `run=ning`.

- **Worker \(Pre/Post-processing or CPU-Only\):**

- Receives a `job_id` from the Scheduler.

- **Reads** the full job object from Redis to get its instruc=tions.

- Performs the core business logic.

- **Writes** the output to the `result` field or e=rror details to the `error_message` field.

- **Updates** the job's status to its terminal state \(`c=ompleted` or `failed`\).

- For GPU jobs, its final action is to **release the GPU lock in Redis.**

### # =**Data Persistence and Retention**

To ensure durability, Redis is configured with a persistence mechanism \(=e.g., AOF - Append Only File\) to prevent the loss of active jobs during a r=estart. To prevent the database from growing indefinitely, a Time-To-Live \(=TTL\) is set on all jobs once they enter a terminal state \(`completed or `failed`), ensuring automatic cleanup of old records af=ter a configured period (e.g., 24 hours or so).

Here is the augmented wiki section, incorporating your latest implementatio=n insights, subtle Triton behaviors, and pain points encountered during the= Gemma-3n deployment:`

**NVIDIA Triton**

This section details the move from in-app model management to a dedicate=d, high-performance inference server. The NVIDIA Triton Inference Server be=comes the sole component responsible for direct GPU interaction, loading an=d unloading models, and executing inference requests. This standardizes mod=el serving and abstracts the hardware complexity away from the rest of the =application.

**The Triton Model Repository**

Triton discovers and manages models through a structured filesystem dire=ctory known as the Model Repository. This repository is the central locatio=n for all models the server can potentially serve. Each model resides in it=s own subdirectory, which contains its configuration and versioned files.

The directory structure is as follows:

/path/t=o/model_repository/└── gemma_3n/ # The name of the mode=l to be used in API calls ├── config.pbtxt # The model's configur=ation file └── 1/ # A version subdirecto=ry for the model files └── ... # Model files (e.g., T=ensorRT engine, ONNX file, or Python script)

Triton monitors this repository and can load new models, unload unused o=nes, or update to new versions dynamically based on its configuration and p=olicies.

**Model Configuration \(config.pbtxt\)**

Each model directory must contain a config.pbtxt file. This file is the =explicit declaration of the model's contract and configuration. It defines:=

- Backend: Specifies which Triton backend should be used to run the model =\(e.g., tensorrt\_llm, python, onnxruntime\).

- Input/Output Tensors: Defines the name, data type, and shape of each inp=ut and output tensor. This creates a formal API for the model.

- Dynamic Batching: Configures how Triton should group incoming requests t=o maximize GPU throughput.

- Instance Groups: Specifies how many copies of the model should be loaded= onto one or more GPUs.

**Backend Selection**

Choosing the right backend is critical for performance and flexibility. =For a Transformers-based model like gemma-3n, the primary options are:

- TensorRT-LLM Backend: Provides the highest performance. Requires convert=ing the Hugging Face model to a TensorRT engine. Ideal for static, latency-=sensitive production use.

- Python Backend: Offers the most flexibility. Allows use of native Python= libraries \(e.g., transformers\) within `model.py`. Ideal for pro=totype models or complex pre/post-processing that can't be easily separated=.

**Python Backend Subtleties**

While powerful, the Python backend introduces several non-obvious pitfal=ls:

- `pb_utils.get_input_tensor_by_name(...).as_numpy()` returns r=aw NumPy arrays, not PyTorch tensors. If working with structured inputs \(e.=g., sequences of images\), these often must be unpacked, converted to `=PIL.Image`, and repackaged for your pipeline.

- The processor's `apply_chat_template()` accepts a Python list= of messages. However, the result is a dictionary, and passing it incorrect=ly to `model.generate(**inputs)` will raise errors like:
TypeError: ... argument after \*\* must be a mapping, not Tensor

=
- `.to(device)` must be applied **per input** , not= on the entire dictionary. You must individually call `.to(device, dty=pe)` on each tensor inside `inputs`.

- `CudaSharedMemoryRegion` returned from `create_shared_me=mory_region` cannot be directly passed to `register_cuda_shared_=memory`. You must first call `get_raw_handle()` to extract= the low-level handle bytes. The naming convention here is misleading.

<=/li>

Example fix:

raw_han=dle = cuda_shared_memory.get_raw_handle(shm_region)grpc_client.register_cuda_shared_memory(name, raw_handle, device_id, byte_s=ize)

**Interaction with Pre/Post-processing Workers**

The application worker no longer loads any part of the model onto the GP=U. It acts purely as a network client to Triton.

The worker's responsibilities are strictly defined:

- Pre-processing: Executes all high-level logic, such as `create_batc=h_plan()` or `check_context_window()`. It prepares data \(e=.g., prompt strings, NumPy image arrays\) to match the tensor API defined in= `config.pbtxt`.

- API Call: Packages the data into an HTTP or gRPC request and sends it to= the Triton inference endpoint \(e.g., `POST /v2/models/gemma_3n/infer<=/code>).`

- Post-processing: Receives raw output tensors and applies business logic =\(e.g., `_extract_narrative()`\) to produce structured outputs.

**Limitations**

Triton is a highly optimized inference engine. It excels at managing CUD=A streams, dynamic batching, and concurrent execution. However:

- It has no awareness of, nor does it care about, higher-level business co=ncepts like job queues or GPU contention across models.

- As discussed above, it will not prevent multiple large models from loadi=ng simultaneously, even if that causes an out-of-memory \(OOM\) condition. Ou=r architecture resolves this through our resource management pipeline.

- Owns the high-level job queue and prioritization logic

- Enforces which models may be loaded at a given time

- Prevents GPU contention through controlled model dispatching

**Troubleshooting Insights**

- Image batch inputs often require `np.ascontiguousarray()` and= reshaping to avoid type or shape mismatches.

- Dynamic batching does not help when using shared memory regions unless <=code>max\_batch\_size is set explicitly and batching is enabled in config.pbtxt.

- Avoid unnecessary use of `Image.resize((224, 224), 224)` whic=h causes `Unknown resampling filter` errors. Always use the Image.Resampling.X enum.

- Torch will emit a `TensorFloat32 tensor cores ... not enabled warning. You may resolve this with:`

torch.s=et_float32_matmul_precision('high')

- The Python backend cannot reuse shared memory regions without proper raw= handle rebinding — even if it previously registered them. Shared m=emory lifecycle must be tightly controlled.

- * *

This separation of concerns between Triton and the Central Scheduler all=ows each system to play to its strengths, resulting in a stable, GPU-effici=ent, and scalable architecture. Triton provides performance and flexibility=. The rest of the system ensures intelligent orchestration.

## # **Kubernete=s**

In a multi-GPU environment that spans multiple machines, the architectur=e must evolve to manage these distributed resources. Kubernetes is the only= practical way to achieve this, as it provides the necessary primitives for= discovery, scheduling, and lifecycle management across machine boundaries.=

### # **Architecture for Distributed Management**

- **Granular Resource Tracking \(Redis\):** The single `gp=u:lock` is replaced by a set of granular locks for each GPU on each n=ode \(e.g., `gpu:node-a:0:lock`, `gpu:node-b:0:lock`\).=

- **Resource Discovery:** A custom Kubernetes Operator is int=roduced. This operator watches the Kubernetes API. When a new GPU-enabled n=ode joins the cluster, the operator automatically registers its available G=PUs in the Redis inventory, making them visible to the scheduler.

- **Targeted Dispatch \(Scheduler\):** The scheduler's logic is= enhanced:

1. It queries Redis for any available GPU lock across the entire cluster.

2. Upon finding and acquiring a specific lock \(e.g., `gpu:node-b:0:loc=k`\), it must ensure the worker pod runs on that specific node.

3. It achieves this by creating the worker pod with a `nodeAffinity or `nodeSelector` rule in its manifest, targeting the label=s of the specific node (`node-b`).`

- **Local Triton Interaction:** The worker pod starts on the =correct node. It then connects to the local Triton instance on that same no� and performs the explicit `load -> infer -> unload` lif�ycle. When complete, it releases the specific Redis lock \(`gpu:node-=b:0:lock`\), making that individual GPU available cluster-wide.