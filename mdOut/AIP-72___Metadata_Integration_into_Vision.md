---
title: "AIP-72: Metadata Integration into Vision"
source_file: "AIP-72___Metadata_Integration_into_Vision.doc"
converted_date: "2025-09-17T11:24:59.149688"
format: "markdown"
---

# AIP-72: Metadata Integration into Vision

[AIP-72](https://perifery.atlassian.net/browse/AIP-72?src=con=fmacro)

# Overview

This design document outlines the integration of the SWARM service with =the Notification API module to generate metadata sidecar files as described= in the provided documentation. The goal is to enhance the Notification API='s components \(transcribe, summarize, object-detection, and face-recognitio=n\) to create and manage these sidecar files in S3 storage.

- The metadata sidecar files will always be stored in a path starting with= `.metadata`.

- The `appId` should be configurable but default to "ai-plus".<=/p>

- The `appCategory` should be configurable but default to the c=omponent name of the Notification API.

- The sidecar file name should be the original file's key with ".metadata.=json" appended.

# System A=rchitecture

# # **Not=ification API**

The Notification API will be the component that generates the sidecar in=formation for Vision. This will be a configuration flag

config.=visionMetadata = true

The four utilities will output the metadata files. In the case of the Tr=anscribe & Summarize, we will have two metadata files – transcr=ibe and summarize.

1. Transcribe

2. Summarize

3. Object Detection

4. Face Recognition

5. Translate

## # Configuration=

We will add the following configurable parameters to the Notification AP=I:

METADATA_=APP_ID = os.getenv("METADATA_APP_ID", "ai-plus")METADATA_PATH_PREFIX = ".metadata"

## # Me=tadata Sidecar Generator

We will create a new class `MetadataSidecarGenerator` with th=e following methods:

class Met�ataSidecarGenerator: def __init__(self, s3_client, bucket_name, app_id=METADATA_APP_ID): self.s3_client = s3_client self.bucket_name = bucket_name self.app_id = app_id def generate_sidecar_key(self, original_key, app_category): return f"{METADATA_PATH_PREFIX}/{self.app_id}/{app_category}/{origi=nal_key}.metadata.json" def create_sidecar_file(self, original_key, app_category, metadata): sidecar_key = self.generate_sidecar_key(original_key, app_categor=y) metadata_json = json.dumps(metadata, indent=2) self.s3_client.put_object( Bucket=self.bucket_name, Key=sidecar_key, Body=metadata_json, ContentType="application/json" ) return sidecar_key

## # Integration with Notification API Components

We will modify each Notification API component to use a `MetadataSi�carGenerator`instance – or instances, in the Transcribe/Sum=marize case:

class Not=ificationAPIComponent: def __init__(self, s3_client, bucket_name): self.s3_client = s3_client self.bucket_name = bucket_name self.metadata_generator = MetadataSidecarGenerator(s3_client, buc=ket_name) def process_file(self, file_key): # Existing processing logic result = self.perform_processing(file_key) # Generate metadata sidecar file metadata = self.format_metadata(result) sidecar_key = self.metadata_generator.create_sidecar_file( file_key, self.__class__.__name__.lower(), # Use component name as app_c=ategory metadata ) return result, sidecar_key def format_metadata(self, result): # Format the result into the desired metadata structure # This method should be implemented by each component raise NotImplementedError

For the Transcribe & Summarize piece, we will output two pieces of m=etadata – the summary and the transcription.

class Sum=marizeComponent(NotificationAPIComponent): def perform_processing(self, file_key): # Existing summarization logic pass def format_metadata(self, result): return { "summary": result["summary"], "keywords": result["keywords"] }

## # SWA=RM Service Integration

Modify the `SwarmService` class to work with the new metadata= sidecar files:

1. Update the `handleNewFile` method to check for existing metad=ata sidecar files.

2. Modify the `processItem` method to call the appropriate Notif=ication API component and generate the metadata sidecar file.

class Swa=rmService: # ... existing code ... async def handleNewFile(self, swarm_bucket, key): # ... existing code ... metadata_generator = MetadataSidecarGenerator(self.s3.client, swa=rm_bucket.bucket) sidecar_key = metadata_generator.generate_sidecar_key(key, swarm_=bucket.processor.lower()) if self.s3.client.head_object(Bucket=swarm_bucket.bucket, Key=s=idecar_key): raise Exception(f"Metadata sidecar file already exists for {key=}") # ... rest of the existing code ... def processItem(self, bucket_item_id, task_job_id): # ... existing code ... component = self.get_notification_api_component(processor) result, sidecar_key = component.process_file(bucket_item.file_key=) # Update the bucket item with the sidecar file information SwarmBucketItemDAL.update( db_session, bucket_item.id, {"metadata_sidecar_key": sidecar_key} ) # ... rest of the existing code ...

# Vision

Metadata files are located in the same bucket as the original objects. E�h application has a dedicated and well-defined path for uploading sidecar= metadata files. This path runs parallel to the original object but include=s an app-specific prefix and file-format suffix. Such a structure offers se=veral advantages. First, it allows for grouping metadata sidecar files by v=endor and app category. Second, it provides support for external apps via d=rop-in points. Lastly, it enables control of storage access per vendor or a=pplication using bucket policies for paths. This approach ensures efficient= organization and management of metadata while maintaining flexibility and =security.

**Examples**

**Limitations**

- Proposed prefix reduces maximum length of a key for original object i.e.= objects with very long keys e.g. 1024 bytes will not be capable of having =side-car metadata files.
Maximum length of a key is backend-storage specific.

- complications when original object is deleted
We should delete metadata files generated internally.
If customer applications are dropping-in metadata files, a decision needs t=o be made what to do about those i.e. delete metadata automatically vs leav=e it to the application. Configuration per customer/bucket?

- asynchronous nature means original objects may be overwritten/deleted be=fore metadata processing takes place

- automatic deletion of metadata files may cause race-condition when origi=nal object is re-uploaded. This can be mitigated by comparing the creation =time of the original and metadata files

# **Samples**

# # Summarize

{ "summary": "This video discusses the i=mpact of climate change on global ecosystems,= focusing on rising sea levels and extre=me weather events.", "keywords": "climate change, sea level =;rise, extreme weather, ecosystems, global warming="}

# # Transcribe

{ "transcription": "Loren episum etc..."}

# # Object Dete=ction

{ "time-based-metadata": [ { "time_start_milliseconds": 1000, "time_end_milliseconds": 5000, "object_class": "person", "object_detail": "face", "total_duration": "4000ms" }, { "time_start_milliseconds": 7000, "time_end_milliseconds": 12000, "object_class": "vehicle", "object_detail": "car", "total_duration": "5000ms" } ], "object-detected-1": "person", "object-detected-2": "vehicle"}

# # Facial Re=cognition

{ "time-based-metadata": [ { "time_start_milliseconds": 1000, "time_end_milliseconds": 5000, "identified_face": "John Doe"=, "confidence": 0.85, "total_duration": "4000ms" }, { "time_start_milliseconds": 7000, "time_end_milliseconds": 12000, "identified_face": "Jane Smit=h", "confidence": 0.92, "total_duration": "5000ms" } ]}

# # Auto Translat=e

{ "original_language": "ch", "translated_language": "en"}