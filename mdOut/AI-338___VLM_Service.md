---
title: "AI-338: VLM Service"
source_file: "AI-338___VLM_Service.doc"
converted_date: "2025-09-17T11:24:58.964619"
format: "markdown"
---

# AI-338: VLM Service

# Video Analysis Pipeline<=/h1>

Here's a look at the architecture for our video processing pipeline. Aft=er a good bit of experimentation, the implementation ends up being more eff=icient, and specifically tailored to the way modern Vision Language Models =\(VLMs\) work. The core philosophy is to treat the VLM's inference step as th=e most expensive part of the entire process \(because it is, by an order of =magnitude\) and optimize everything around making that step as efficient as =possible.

The overall workflow can be broken down into two main stages: a pre-flig=ht**** stage where we gather and organize all our data, and an= inference stage where we interact with the model.

[Video =File] -> [Stage 1: Pre-Flight] -> [Stage 2: Execution] -> [Final R=esults]

This design might seem a little counterintuitive at first. One might thi=nk that a streaming pipeline, where we process frames as soon as they're av=ailable, would be faster. However, testing and analysis showed that the cos=t of a single VLM inference call \(around two minutes in testing\) is so high= that it's far better to spend a little extra time upfront \(about 40 second=s\) to prepare perfectly optimized batches. Consider the following real-worl=d metrics of performance on an NVIDIA L40S card:

- **VLM Inference Time:** 120 seconds

- **Total Frame Extraction Time:** 40 seconds

An extra, non-optimally packed inference call would cost 120 seconds. Th=e _total_ time saved by overlapping the entire 40-second extraction =process is, at most, 40 seconds. Therefore, any workflow that risks even on=e extra inference call is a net loss.

Thus the current implementation, which prioritizes creating the absolute= minimum number of batches, is the correct one because the number of VLM in�rence calls is the single most important metric to minimize.

# # Pre-Flight

This first stage is all about gathering the necessary ingredients and or=ganizing them for the main event. It ensures we don't send the VLM too much=, too little, or poorly organized data.

= +---------------------------+ +-----------------------=---+[Video File] --------> | 1. Scene Detection | ---> | 2. Dynami=c Frame Sampling| | (PySceneDetect w/ scaling)| | (Calculate fram=e counts) | +---------------------------+ +----------------=----------+ | V +---------------------------+ +----------------=----------+| 4. Batch Planning | <--- | 3. Bulk Frame Extraction || (The "Pre-Flight Check") | | (Optimized OpenCV pass) | +---------------------------+ +----------------=----------+ | V [Optimized Batch Plan]

1. **Scene Detection:** We start by running the video through =PySceneDetect. This gives us natural, context-aware boundaries for analysis=. To make this step faster without sacrificing much accuracy, we employ a d=ynamic downscaling algorithm. It automatically calculates a downscale facto=r to bring any source video \(4K, 1080p, etc.\) to a consistent, smaller reso=lution like 360p for analysis. This is much faster and more robust than har�oding rules for specific resolutions.

2. **Dynamic Frame Sampling:** Once we have our scenes, we dec=ide how many frames we actually need from each one. We've eschewed a simple=, fixed frames-per-second approach. Instead, we use a dynamic algorithm tha=t calculates the target number of frames based on the scene's duration, bou=nded by a configurable minimum and maximum. A short 6-second scene might ge=t 12 frames, while a long 30-second scene gets 60. This prevents us from se=nding the VLM excess data for a secne; we’re building an appropriat=e amount of context for the length of each scene

3. **Bulk Frame Extraction:** With a master list of every sing=le timestamp we need from the entire video, we make one pass using our hard=ware-accelerated OpenCV extractor. Its smart-seeking logic minimizes expens=ive seek operations by only seeking across large time gaps and reading sequ=entially over small ones. This is vastly more efficient than seeking for ea=ch and every frame individually.

4. **The "Pre-Flight Check" \(Batch Planning\):** This is the br=ains of the operation. We take the full list of prepared scenes and run the=m through a greedy packing algorithm. The only rule is to pack as many scen=es as possible into a single batch without letting the _total frame coun=t_ of that batch exceed a hard computational limit \(which would cause C=UDA OOM errors\). This algorithm naturally allows for mixing a large scene w=ith a few small scenes, ensuring no space is wasted. This step produces a f=inal, immutable "batch plan."

NOTE: Any scene that is too large on its own is skipped and flagged. Later,= we might want to build heuristics to fit the number of frames into a proce=ssable batch.

# # Inference

With the plan in hand, the execution stage is clean and predictable. We =are no longer making decisions on the fly; we are simply executing the opti=mized plan.

= +------------------+[Optimized Batch Plan] ---> [ For each batch... ] ---> | VLM Inferenc=e | (List of Batches) | (Batch a, b, c) | +------------------+ | V +------------------+ | Reassembly | | (Using indices) | +------------------+ | V [Final Results] (in order)

The key here is that we've attached the original `scene_index to our data from the very beginning. This index travels with the scene da=ta through every step, allowing us to correctly reassemble the final result=s in their original order, even though the scenes were processed in reorgan=ized, optimized batches.`

For the inference step itself, we can leverage model-level optimizations=. Techniques like **Flash Attention 2** and **quantizati=on** are employed directly on the model to attack the two-minute inf=erence time, as this provides a greater performance dividend than any furth=er pipeline tweaks.