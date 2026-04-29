---
title: "AI-1036: Metasight, an Object Intelligence Platform"
source_file: "AI-1036__Metasight,_an_Object_Intelligence_Platform.doc"
converted_date: "2025-09-17T11:24:58.752446"
format: "markdown"
---

# AI-1036: Metasight, an Object Intelligence Platform

This epic outlines the architecture for the Metasight Object Int=elligence Platform. The system's goal is to transform a raw video archive i=nto a powerful, searchable knowledge base.

The core strategy is a hybrid AI approach, utilizing two distinct, state=-of-the-art models to enrich video data. This provides both rich, human-rea�ble metadata and best-in-class visual search capabilities. The architectu=re is designed as a scalable, event-driven system of microservices.

Existing object detection systems often generate a high rate of false po=sitives from dynamic environmental factors like swaying trees or changing s=hadows. This leads to alert fatigue and reduces the reliability of automate=d monitoring.

The foundational strategy is to implement a two-stage process to add a l=ayer of "common sense" to detection:

1. **Contextual Analysis:** First, a Vision-Language Model \(VL=M\) analyzes the scene to provide a high-level, semantic understanding \(e.g.=, _"This is a backyard with trees swaying in the wind"_\).

2. **Informed Detection:** This contextual understanding is th=en used to dynamically tune the parameters of a primary object detector. Fo=r example, if "swaying trees" are identified, the confidence threshold for �tecting a "person" can be raised to prevent misclassification of moving b=ranches.

The platform's long-term vision evolves from a real-time alerting system= into a persistent, searchable intelligence archive. The goal is to empower= a user to instantly find any object or event across the entire video histo=ry.

An analyst needs to query the system with complex, natural-language ques=tions or visual examples to find specific moments, such as:

- _"Show me all instances of a delivery truck in the driveway last week=."_

- _"Find every appearance of this specific person across all cameras." <=/em>_

To enable this, every detected object must be enriched with detailed met�ata and indexed for fast, multi-modal search.

# Metasight

Metasight converts sampled video frames into structured, search-ready re=cords by orchestrating Florence-2 for descriptive, task-prompted analysis a=nd DINOv3 for universal visual features, then packaging both into a single =record for indexing in Milvus. This implements our two-stage strategy and s=upports a searchable intelligence archive rather than a detector-only syste=m.

1. A frame arrives from the upstream sampler with metadata \(video\_id, times=tamp, source\_uri\).

2. Metasight performs:

- Step 1: Florence-2 task processing \(dense region captioning, object dete=ction, optional OCR/grounding\).

- Step 2: DINOv3 feature extraction for frame and optional ROI/bbox embedd=ings.

- Optional Step 3: context-aware validation to reduce false positives.

=
3. Metasight assembles a canonical record and writes to Milvus collections.=

The Metasight service is the core of the intelligence platform, transfor=ming raw video frames into structured, searchable records. It a�omplishes this by orchestrating two specialized AI models: Florence-2 for= descriptive, task-prompted analysis, and DINOv3 for generating universal v=isual features. Metasight then packages the outputs from both models into a= single, comprehensive record for indexing in a Milvus vector database. Thi=s two-stage strategy supports the platform's evolution from a simple detect=or into a searchable intelligence archive.

# # **System Flow and Context**

The overall workflow begins when a video frame, along with its associate=d metadata \(such as `video_id` and `timestamp`\), arri=ves from the video processor. Metasight then executes a multi-step enrichme=nt process. First, it performs task-based processing with Florence-2, runni=ng prompts for dense region captioning, object detection, and optional task=s like OCR or phrase grounding. Next, it uses DINOv3 for feature extraction=, generating a powerful embedding for the entire frame and, if configured, =for specific regions of interest or bounding boxes within it.

An optional third step involves context-aware validation, which applies =spatial, temporal, and semantic checks to the detected objects to reduce fa=lse positives. Finally, Metasight assembles all generated data =into a canonical record and writes it to the appropriate Milvus collections=. It's important to note that while Metasight is designed to integrate with= a broader event-driven architecture, concerns like real-time alerting and =downstream API consumption are considered out of scope for this core compon=ent.

# # <=strong>Component Design

Metasight is responsible for accepting video frames and their minimal me=tadata, running the Florence-2 and DINOv3 models to produce their respectiv=e outputs, and applying the optional validation pass. It then emits canonic=al records formatted for efficient, batch-friendly insertion into Milvus. T=he service communicates with other internal components via HTTP/JSON, with =the potential for asynchronous input and output through a RabbitMQ topic in= the future.

Logically, Metasight is composed of several internal components. A Prepr=ocessor converts incoming image data into batched tensors and performs on-G=PU resizing and normalization. The Object Detection and Indexing Process in=terface with the Triton server to manage the distinct contracts for Florenc=e-2 and DINOv3. A Validator component encapsulates the logic for spatial, t=emporal, and semantic consistency checks. Finally, an Assembler merges the =outputs from all previous stages, assigns unique IDs, and prepares the data= for the Milvus collections.

The processing sequence begins by receiving a batch of frames, which are= then run through the DINOv3 model once to produce universal feature embedd=ings. These features are then reused where supported for the various Floren�-2 tasks, such as object detection and dense region captioning. A compreh=ensive list of detections is built, which includes the class, confidence sc=ore, bounding box, descriptive attributes, and the associated frame and bou=nding box embeddings. If enabled, the validation logic is applied before th=e final records are emitted for indexing.

# # O=bject Detection

This service is the core of the system. It receives a batch of video fra=mes and orchestrates a sequence of AI calls via the NVIDIA Triton server.

- **Input:** A message containing a raw video frame \(e.g., HW=C, UINT8 NumPy array\).

- **Step 1: Descriptive Analysis \(Florence-2\)**

- **Action:** The frame is sent to the Florence-2 model.

<=/li>
- **Task:** The model is prompted with a task like `"<=;DENSE_REGION_CAPTION>"`.

- **Output:** A structured JSON object containing a list of a=ll detected objects, each with its bounding box, a simple label, and a deta=iled, human-readable caption. This output provides the rich, descriptive me=tadata.

- **Step 2: Feature Extraction \(DINOv3\)**

- **Action:** The same frame is sent to the DINOv3 model.

=
- **Task:** The model processes the image to extract its deep= visual features.

- **Output:** A single, high-dimensional image embedding vect=or. This vector is a mathematical signature of the frame's visual content, =optimized for similarity search.

# # <=strong>Indexing Process

- **Input:** The JSON metadata from Florence-2 and the image =embedding vector from DINOv3.

- **Action:** The service assembles these two pieces of data,= along with source information \(video path, timestamp\), into a single, comp=rehensive record.

- **Output:** This record is inserted into the Milvus databas=e.

Field Name| Data Type| Dimensions| Description
---|---|---|---
**pk\_id**| `Int64`| N/A| A unique, auto-incrementing primary key for each record.
**image\_embedding**| `Vector`| \(e.g., 1024\)| The DINOv3 embedding for powerful visual similarity search.
**source\_video**| `VarChar`| \(e.g., 256\)| Path or identifier for the source video file. Indexed for filtering.=
**timestamp**| `Int64`| N/A| Unix epoch timestamp of the frame. Indexed for time-range filtering.=
**metadata\_json**| `JSON`| N/A| The complete JSON blob from Florence-2, containing all detected objects,= bboxes, and captions.

# **Object Intelligence Engine**

# # Domain-Agnostic Object Recognition

## # Sy=stem Overview

This is a universal object training system that works for any object typ=e - from industrial equipment to retail products, medical devices, agricult=ural machinery, to guitars. The system learns from examples without requiri=ng model retraining.

The complete flow

1. **Initial Detection** : Frame contains unknown vacuum �=92 Florence-2 says "vacuum cleaner" → DINOv3 creates embedding

=
2. **Human Labels** : User labels it as "Shark Vertex AZ2002" =E2�� System stores embedding as template

3. **Future Recognition** : New frame → DINOv3 embeddin=g → Compare to all templates → Similarity > threshold =E2�� Identified as "Shark Vertex AZ2002"

4. **Continuous Improvement** : More examples → Update �ntroid → Adjust threshold → Better recognition

# # �sic User Journey

1. **When we label a vacuum as "Shark Vertex AZ2002"** , the sy=stem stores the DINOv3 embedding \(768-dimensional vector\) of that vacuum as= a template.

2. **In future frames** , every detected vacuum gets its own DI=NOv3 embedding extracted.

3. **Recognition happens via cosine similarity** : The new embe�ing is compared to all stored templates. If similarity > threshold \(ty=pically 0.75-0.90\), it's identified as that specific product.

## # The Recognition Function:

# For e�h detected object in a frame:object_embedding = dinov3_model.extract_features(object_crop)# Compare to ALL customer templatesfor template in customer_templates: similarity = cosine_similarity(object_embedding, template["centroid"]=) if similarity > template["threshold"]: # This IS a Shark Vertex AZ2002!

- DINOv3 embeddings of the same object \(even from different angles\) have h=igh similarity \(typically 0.8-0.95\)

- Different objects have lower similarity \(typically 0.3-0.7\)

- The threshold is dynamically adjusted based on variance in training samp=les

## # Advan=tages:

- **No model retraining needed** \- just store and compare emb�dings

- **Works with 1 sample** but improves with more \(5-20 ideal\)=

- **Real-time recognition** \- just vector comparison

- **Customer isolation** \- SharkNinja's templates don't affec=t other customers

## # Practical Considerations:

- Store templates in memory for fast matching \(loading once per session\)

- Use centroids \(average of multiple embeddings\) for robust matching

- Implement feedback loops to continuously improve templates

- Queue low-confidence matches for human review

# # De=sign Overview

## # **The Template Manager**

This component is the "write path" of the system and is responsible for =the lifecycle of object templates. It combines the logic from the `Gen=ericTemplateManager` and `HierarchicalObjectClassifier`. W=hen a human labels an unknown object \(e.g., providing "Shark Vertex AZ2002"= for a "vacuum cleaner"\), the Template Manager:

1. Receives the new label and the associated embeddings of the example imag=es.

2. Checks if a template for this object already exists.

3. If it's a new object, it creates a new record, calculates the initial ce=ntroid and similarity threshold, and inserts it into the `object_templ=ates` collection in Milvus.

4. If the object already exists, it updates the template by recalculating t=he centroid with the new example embedding and adjusting the similarity thr=eshold based on the increased sample variance.

## # **The Recognition Engine**

This is the real-time "read path" of the system. It's a high-throughput =service that takes an unknown object detected by Metasight and attempts to =identify it. For each detected object, the Recognition Engine:

1. Receives the object's DINOv3 embedding and its base\_class from Florence-=2.

2. Constructs an efficient Milvus query. It first filters by customer\_id an=d the base\_class to dramatically narrow the search space.

3. Performs a vector similarity search on the remaining templates using the= object's embedding.

4. If the top match's similarity score is greater than that template's spec=ific `similarity_threshold`, it returns a positive identificatio=n.

## # **The Unidentified Object Queue**

This component closes the continuous improvement loop. If the Recognitio=n Engine cannot find a match for an object that exceeds the required thresh=old, it forwards the object's data \(embedding, base\_class, source video ref=erence\) to a dedicated queue. This queue feeds a labeling interface where a= human operator can review the unknown objects and submit them to the Templ=ate Manager for training, making the system smarter over time.

System Component| Reads From...| Writes To...| Purpose
---|---|---|---
**Detection Workflow**| N/A| `frame_archive`, `object_detections`| Logs all raw visual evidence and general descriptions.
**Recognition Engine**| `object_detections`, `object_templates`| N/A| Cross-references new evidence against known identities to find a match.<=/p>
**Training System \(Human-in-the-loop\)**| \(Labeling Queue\)| `object_templates`| Creates new "known identity" records based on human feedback.

# Database Schema

The Milvus collection is designed for hybrid search, storing both the ve=ctor for similarity search and the detailed metadata for filtering.

## # **Video Frame Archive**

This collection is the master library, serving as the system's "source o=f truth" for every video frame that has been analyzed. It is designed for b=road, scene-level searches and historical review.

Field Name| Data Type| Dimensions| Indexing| Description
---|---|---|---|---
**pk\_id**| `Int64`| N/A| Primary Key| A unique, auto-incrementing primary key for each record.
**image\_embedding**| `Vector`| \(e.g., 1024\)| Vector \(HNSW\)| The DINOv3 embedding for powerful visual similarity search.
**source\_video**| `VarChar`| \(e.g., 256\)| Scalar| Path or identifier for the source video file. Indexed for filtering.=
**timestamp**| `Int64`| N/A| Scalar| Unix epoch timestamp of the frame. Indexed for time-range filtering.=
**metadata**| `JSON`| N/A| Scalar| The complete JSON blob from Florence-2, containing all detected objects,= bboxes, and captions.

## # Object Index

For every individual object identified within a frame, a separate, dedic=ated record is created here. This enables highly specific, object-centric s�rches.

Field Name| Data Type| Dimensions| Indexing| Description
---|---|---|---|---
**detection\_id**| `VarChar`| N/A| Primary Key| A unique identifier for each specific object detection.
**frame\_id**| `Int64`| N/A| Scalar| Foreign key linking back to the `pk_id` in the `video_fr=ames` collection.
**object\_class**| `VarChar`| 128| Scalar| The object's classification \(e.g., "person," "vehicle"\).
**confidence**| `Float`| N/A| Scalar| The detection confidence score from the model \(0.0-1.0\).
**bbox\_embedding**| `Vector`| 512| Vector \(HNSW\)| A DINOv3 embedding of just the object's bounding box crop for specific v=isual search.
**bbox\_coordinates**| `JSON`| N/A| None| The object's bounding box coordinates, e.g., \[x1, y1, x2, y2\].
**attributes**| `JSON`| N/A| None| Additional attributes from Florence-2, such as color or pose.

## # Video Summary

This collection provides a holistic, summary view of an entire video file. =It allows for efficient searching and categorization of videos without need=ing to process their individual frames.

Field Name| Data Type| Dimensions| Indexing| Description
---|---|---|---|---
**video\_id**| `VarChar`| N/A| Primary Key| A unique identifier for the video file, serving as the primary key.
**global\_video\_embedding**| `Vector`| 1024| Vector \(HNSW\)| A single embedding representing the thematic content of the entire video=.
**duration\_seconds**| `Int64`| N/A| Scalar| The total duration of the video in seconds.
**processing\_completed**| `Int64`| N/A| Scalar| Unix epoch timestamp indicating when the video was fully processed.
**quality\_metrics**| `JSON`| N/A| None| A JSON blob containing any relevant quality or processing metrics.

### # <=strong>Object Templates

The object template is the heart of the recognition engine. It stores th=e "ground truth" for every specific object trained. It directly enables the= "few-shot learning" capability.

Field Name| Data Type| Dimensions| Description| Indexing
---|---|---|---|---
**template\_id**| `Int64`| | Primary key for the object template.| Primary Key
**centroid\_embedding**| `FloatVector`| | The DINOv3 embedding representing the object's visual centroid.| Vector Index \(HNSW\)
**customer\_id**| `VarChar`| | Identifier for the customer/tenant who owns the template.| Partition Key
**object\_label**| `VarChar`| | The specific, human-provided label \(e.g., "Shark Vertex AZ2002"\).| Scalar Index
**base\_class**| `VarChar`| | The general category from Florence-2 \(e.g., "vacuum cleaner"\). Used for =pre-filtering.| Scalar Index