# AI+ 2.0 Release Notes

**Release Date:** June 2024

**Bundle Name:** AI+ 2.0 OnPrem Suite

---

#### Purpose

This release introduces AI+ 2.0, a comprehensive suite of onPrem AI features designed for seamless integration with SWARM, OM, and iconik. AI+ 2.0 offers advanced capabilities in media management, including transcription, summarization, translation, facial recognition, and object recognition. This bundle aims to enhance operational efficiency and media content management with robust, localized AI solutions.

#### What’s New in AI+ 2.0?

- **Advanced Transcription::** Automatically transcribe and generate robust metadata values in multiple languages for any number of metadata fields across all of an organization’s media content. (Now able to be run 100% on prem with no $/sec required for OpenAI anymore.)
- **AutoTranslation:** Translate the spoken audio of selected media content into multiple languages. AutoTranslation supports over 20 languages, enabling broader content accessibility.
- **Facial Recognition:** Identify and tag individuals within your media library based on a simple training process which can occur directly within iconik or through our APIs.
- **Robust Object Detection:** **:** Go beyond Object Detection to Object Recognition where we combine the power of standard Object Detection models with Vision based models to find specific objects within media files. Instead of just being able to find a car, find the Ford F-150 for example. All with no traditional object detection training required. ‌

---

#### Bundle Contents

- **AI+ Transcribe and Summarize Module:** NLP models and processing scripts for transcription and summarization.
- **AI+ AutoTranslation Module:** Language translation models and integration scripts.
- **AI+ Facial Recognition Module:** Pre-trained facial recognition models and tagging scripts.
- **AI+ Object Recognition Module:** Object detection models and classification scripts.
- **Notification API:** The Notification API is a Python-based application designed to send real-time alerts and notifications to users about relevant events and updates within the media management system.

---

#### System Requirements

To fully leverage the capabilities of AI+ 2.0, the following system specifications are required:

**Minimum Server Specifications**

### CPU

- Processor: Intel Xeon or AMD EPYC series
- Cores: Minimum 16 cores (32 threads)
- Clock Speed: Base clock speed of 2.6 GHz or higher

### Memory (RAM)

- Minimum: 128 GB
- Recommended: 256 GB or higher for better performance and handling large datasets

### GPU

- Model: NVIDIA Tesla, A100, V100, or RTX 6000 series or newer
- CUDA Cores: Minimum 5,000 CUDA cores
- VRAM: Minimum 24 GB VRAM; Recommended 48 GB VRAM for optimal performance
- Generation: The oldest supported generation should be the NVIDIA Volta architecture (e.g., V100) or newer

### Storage

- Type: NVMe SSD
- Capacity: Minimum 2 TB (consider more storage based on dataset size)
- Additional Storage: High-speed network-attached storage (NAS) or SAN for large datasets

### Networking

- Network Interface: 10GbE network interface card (NIC) or faster
- Additional: Consider multiple NICs for redundancy and better throughput

### Power Supply

- Redundant Power Supplies: Recommended for high availability and reliability

**Recommended Software Environment**

### Operating System

- Ubuntu 20.04 LTS or newer

### CUDA Toolkit

- Version 11.0 or newer

---

#### Installation and Configuration

1. Ensure that the NVIDIA drivers are up to date to avoid compatibility issues.
2. See specific deployment documentation in Miro for each workflow

    1. [https://miro.com/app/board/uXjVKHM4ekg=/?moveToWidget=3458764590801194638cot=14](https://miro.com/app/board/uXjVKHM4ekg=/?moveToWidget=3458764590801194638&cot=14)
    2. [https://miro.com/app/board/uXjVKJtVPd0=/?moveToWidget=3458764590801431892cot=14](https://miro.com/app/board/uXjVKJtVPd0=/?moveToWidget=3458764590801431892&cot=14)
    3. [https://miro.com/app/board/uXjVKZI6WDo=/?moveToWidget=3458764590800405570cot=14](https://miro.com/app/board/uXjVKZI6WDo=/?moveToWidget=3458764590800405570&cot=14)
    4. [https://miro.com/app/board/uXjVKfQ0Ksg=/?moveToWidget=3458764590802626271cot=14](https://miro.com/app/board/uXjVKfQ0Ksg=/?moveToWidget=3458764590802626271&cot=14)
