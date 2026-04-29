---
title: "AI-938: NVIDIA Triton Server Intergration"
source_file: "AI-938__NVIDIA_Triton_Server_Intergration.doc"
converted_date: "2025-09-17T11:24:59.050848"
format: "markdown"
---

# AI-938: NVIDIA Triton Server Intergration

#

- * Overview
- Simplified Integration
- Performance and Resource Optimization
- Flexibility and Maintainability
- Observ�ility
- Gemma-3n
- =Input/Output Tensors
- Batching
- CUDA Shared Memory Integration
- Media Processing Pipeline
- Transfo=rmers
- Attention<=/a>
- Output =Tokens
- Other Implementation Notes
- Greedy Decoding Strategy
- Memory Efficiency Optimizations
- VRAM Consumption Patterns
- Faster=Whisper
- Input/Output Tensors
- Media Processing Pipeline
- Language
- Segment and Word Processing
- NVIDI=A Parakeet
- Input/Output Tensors
- Media Processing Pipeline
- Windowed Inference Solution
- Se=gmentation Logic
- =Implementation Notes
- M=odel Loading Issues
- Timestamp API Inconsistencies
- CU� Graph Problems
- Stability Improvements

# Overview

NVIDIA's Triton Inference Server is a specialized backend for serving AI= models in production. It provides a standard gRPC/HTTP API that lets us av=oid building custom deployment applications for each model. The server is a= comprehensive platform with built-in features like dynamic batching, concu=rrent execution, and a flexible backend system that supports everything fro=m Python to highly optimized TensorRT engines. Adopting Triton standardizes= our MLOps pipeline, replacing ad-hoc solutions with a scalable and optimiz� system.

## # Simplified Integration

Triton abstracts model complexity from the application layer. Our servic=es don't need to know how a model is implemented; they just make a standard= gRPC call to a named endpoint. This decoupling is powerful. For example, i=t made A/B testing FasterWhisper against Parakeet trivial. Since they share=d an identical input/output signature within Triton, the business logic cou=ld switch between them via a simple configuration change, requiring no code= redeployment.

## # **Performance and Resource Optimization**

The primary performance justification comes from the Gemma-3n implementa=tion, which saw a **3x speed increase** and a **2.5-3x r�uction in VRAM usage** after moving to Triton. These gains stem fr=om features that are complex to build and maintain in a custom service:

- **Dynamic Batching** : Triton automatically groups incoming =requests from different users into a single batch on the fly, which is one =of the most effective ways to maximize GPU throughput.

- **Concurrent Model Execution** : The server can intelligentl=y schedule and run multiple models—or multiple instances of the sam=e model—on a single GPU, overlapping operations to keep the hardwar=e saturated.

- **Efficient Memory Management** : Triton can load a single i=nstance of model weights and allow many concurrent requests to share it. Th=is drastically reduces the VRAM footprint compared to running multiple redu=ndant Python processes in separate containers.

## # **Flexibility and Maintainability**

Triton's architecture solves several long-term maintenance challenges. I=ts use of isolated backends resolves the "dependency hell" problem; each mo�l runs in its own environment, so Gemma-3n's PyTorch version will never c=onflict with Parakeet's NeMo dependencies.

This structure also provides a clear path for iterative optimization. We= can deploy a model quickly using the flexible Python backend and, if it be=comes a bottleneck, rewrite its core in a high-performance backend like Ten=sorRT. Throughout this process, the client-facing API remains unchanged, co=mpletely isolating the optimization work from the business logic.

## # **Obse=rvability**

Building robust monitoring for a custom service is a significant task. T=riton provides this out of the box, exposing a Prometheus metrics endpoint =with detailed data on GPU utilization, memory, queue times, and inference l=atency for every model.

# Gemma-3n

This implementation serves Google's Gemma-3n vision-language model throu=gh a highly optimized Triton Python backend that bypasses standard HuggingF�e preprocessing to maintain GPU-resident tensors throughout the entire pi=peline. The key innovation is avoiding CPU roundtrips for image data that o=ften exists in CUDA shared memory, providing significant performance improv=ements for video analysis workloads.

The implementation uses the HuggingFace processor exclusively for chat t=emplating and tokenization while handling all image preprocessing directly =on GPU using native PyTorch operations. This approach eliminates the overhe� of PIL/NumPy conversions and CPU-GPU memory transfers that plague standa=rd vision-language model deployments.

Standard HuggingFace vision model implementations force image data throu=gh a CPU preprocessing pipeline that includes PIL Image objects, NumPy arra=y conversions, and processor normalization steps. This design assumes image=s arrive as files or CPU arrays, which is inefficient when video frames are= already GPU-resident or transmitted through CUDA shared memory.

The implementation circumvents this entire preprocessing chain by:

- Using HuggingFace processor only for text templating and tokenization

- Implementing custom GPU-native image preprocessing with PyTorch operatio=ns

- Maintaining tensor memory layout optimizations throughout the pipeline

- Supporting direct DLPack zero-copy transfers from CUDA shared memory

=

Video processing applications typically produce frames in NHWC format \(N=umber of frames, Height, Width, Channels\) while GPU operations prefer NCHW =format \(Number of frames, Channels, Height, Width\). The implementation hand=les both layouts automatically, performing on-GPU permutations when necessa=ry to avoid CPU involvement.

# # Input/Output Tensors

- **Input:**`PROMPT`

- **Type** : `TYPE_STRING`

- **Shape** : `[1, 1]`

- **Description** : The user-provided text prompt for the mode=l. The implementation defensively handles shapes of both

`[1]` and `[1, 1]`.

- **Input:**`FRAMES`

- **Type** : `TYPE_FP16`, `TYPE_FP32`, o=r `TYPE_UINT8`

- **Shape** : `[1, num_frames, height, width, 3]` \(=NHWC\) or `[1, num_frames, 3, height, width]` \(NCHW\)

- **Description** : A tensor containing one or more video fram=es. The implementation dynamically handles various input dimensions \(3D, 4D=, or 5D\) and normalizes them for processing. It also automatically permutes= NHWC layouts to the GPU-preferred NCHW format.

- **Output:**`SUMMARY`

- **Type** : `TYPE_STRING`

- **Shape** : `[1]`

- **Description** : The generated text describing the input fr=ames.

## # Batching

Triton's batching system requires all input tensors to include a leading= batch dimension, even for single requests. This affects client implementat=ions:

- PROMPT tensor shape: `[batch_size, 1]` instead of `[1]`

- FRAMES tensor shape: `[batch_size, num_frames, height, width, 3] or `\[batch\_size, num\_frames, 3, height, width\]``

- Batch size is typically 1 for individual requests

The implementation handles variable batch dimensions by detecting the te=nsor shape and extracting the actual content appropriately. PROMPT tensors =may arrive as `[1]` or `[1,1]` depending on client co=nfiguration, requiring defensive dimension handling.

Frame tensors arrive with varying dimensions depending on client impleme=ntation:

- 5D tensors: `[batch, frames, height, width, channels]` from b=atched clients

- 4D tensors: `[frames, height, width, channels]` from direct c=lients

- 3D tensors: `[height, width, channels]` from single-image cli=ents

The implementation normalizes all inputs to 4D format before processing:=

if fram=es.dim() == 5: frames = frames.squeeze(0) # Remove batch dimensionelif frames.dim() == 3: frames = frames.unsqueeze(0) # Add frame dimension

## # CUDA Shared Memory Integration

The most significant performance optimization involves direct CUDA share=d memory access through DLPack protocol:

try: dl = frames_input.to_dlpack() # Zero-copy if from CUDA SHM frames = torch.from_dlpack(dl) dlpack_used = Trueexcept Exception: # Fallback: CPU numpy copy then GPU transfer np_frames = frames_input.as_numpy() frames = torch.from_numpy(np_frames).to(device, non_blocking=True)

When clients use CUDA shared memory for frame data, DLPack enables zero-=copy tensor creation directly on GPU. This eliminates:

- CPU memory allocation for intermediate arrays

- GPU-to-CPU memory transfers

- CPU-to-GPU memory transfers

- NumPy array creation and destruction overhead

The fallback path handles clients that provide CPU arrays, copying data =to GPU with non-blocking transfers for optimal pipeline utilization.

# # Me=dia Processing Pipeline

## #
Transformers

The primary motivation for custom text processing is to prevent unnecess=ary memory transfers when image data already exists on GPU. The standard Hu=ggingFace vision-language processing pipeline expects PIL Images or NumPy a=rrays as inputs, which forces the following inefficient memory flow:

1. **Client Preparation** : Video frames exist in CUDA shared m=emory on GPU

2. **Standard Pipeline Requirement** : HuggingFace processor ex=pects CPU-based PIL/NumPy image data

3. **Forced Transfer** : GPU tensors must be moved to CPU, conv=erted to PIL/NumPy format

4. **Re-upload** : Processor converts back to PyTorch tensors a=nd moves to GPU for model inference

5. **Performance Loss** : Dual memory transfers plus CPU conver=sion overhead

The implementation bypasses this inefficient pipeline by handling image �ta directly as GPU tensors:

- **Direct CUDA Access** : Accept image tensors through DLPack= from CUDA shared memory

- **GPU-Native Processing** : Perform all normalization, resiz=ing, and format conversion on GPU

- **Text-Only Tokenization** : Use HuggingFace processor exclu=sively for chat template and text tokenization

- **Manual Token Assembly** : Combine text tokens with image p=laceholder tokens without forcing CPU conversion

This approach ensures image data never leaves GPU memory, eliminating th=e redundant GPU→CPU→GPU transfer cycle that would otherwise= dominate processing time for video analysis workloads.

The implementation leverages HuggingFace's chat template system to forma=t multi-modal conversations properly:

message=s = [ {"role": "system", "content": [{"type": "text", "text": self.system_mes=sage}]}, {"role": "user", "content": ([{"type": "image"}] * num_imgs) + [{"type"=: "text", "text": prompt}]}]

This structure places image placeholders before text content, matching G=emma-3n's expected input format for vision-language understanding.

The implementation bypasses HuggingFace's automatic image token expansio=n to maintain control over the tokenization process:

1. **Template Generation** : Create chat template without token=ization to inspect structure

2. **Manual Tokenization** : Tokenize template text to access r=aw token IDs

3. **Token ID Detection** : Locate image placeholder tokens and= soft token IDs

4. **Custom Expansion** : Replace single image tokens with sequ=ences of soft tokens

# Repla� each <image> with image_seq_length copies of <image_soft_token&=gt;for t, m in zip(ids, mask): if t == img_id: new_ids.extend([soft_id] * image_seq_length) new_mask.extend([m] * image_seq_length) else: new_ids.append(t) new_mask.append(m)

This approach ensures proper alignment between image features and token =positions while maintaining compatibility with Gemma-3n's vision encoder ou=tput dimensions.

Gemma-3n's vision encoder produces a fixed number of features per image,= typically 256 tokens. This value is extracted from the model configuration=:

image_s=eq_length = getattr(getattr(self.model.config, "vision_config", {}), "ima=ge_seq_length", 256)

The sequence length determines how many soft tokens replace each image p=laceholder, ensuring the text sequence aligns with vision encoder outputs d=uring cross-attention operations.

## # Attention

The implementation enables all available SDPA backends for optimal atten=tion computation:

os.envi=ron["PYTORCH_SDP_KERNEL"] = "flash,mem_efficient,math"torch.backends.cuda.enable_flash_sdp(True)torch.backends.cuda.enable_mem_efficient_sdp(True)torch.backends.cuda.enable_math_sdp(True)

Note: While this configuration prioritizes FlashAttention for memory eff=iciency, currently it is not supported.
We explicitly use cuDNN \(CUDA Deep Neural Network library\) is NVIDIA's hard=ware-accelerated library that provides optimized implementations of deep le=arning primitives. For attention mechanisms, cuDNN offers specialized kerne=ls that can dramatically outperform generic matrix operations by leveraging= GPU architecture features like Tensor Cores, optimized memory access patte=rns, and fused operations.

SDPA \(Scaled Dot-Product Attention\) represents the core attention comput=ation in Transformers: `Attention(Q,K,V) = softmax(QK^T/√d)V=`. When PyTorch's SDPA implementation detects compatible hardware and= software configurations, it can dispatch attention computations to cuDNN's= optimized kernels instead of using standard PyTorch operations.

The integration works through PyTorch's backend selection system:

When cuDNN kernels aren't compatible, we fall back to memory-efficient a=ttention for compatibility, and maintains math attention as a final fallbac=k to prevent "no available kernel" errors.

For Ampere and Hopper GPU architectures, TF32 precision provides signifi�nt performance improvements:

torch.s=et_float32_matmul_precision("high")torch.backends.cuda.matmul.allow_tf32 = Truetorch.backends.cudnn.allow_tf32 = True

TF32 maintains float32 dynamic range while using reduced precision for m=atrix multiplication operations, typically providing 1.5-2x speedup on mode=rn hardware.

## # Output Tokens=

Output length is controlled through the `max_new_tokens` paramet=er, defaulting to 320 tokens but configurable through Triton model paramete=rs. This setting has significant performance implications due to the auto-r=egressive nature of language model generation.

**Auto-regressive Generation Process:**

Language models generate text one token at a time in sequence, where eac=h new token depends on all previously generated tokens. This creates a fund=amentally sequential process that cannot be parallelized across the token d=imension:

1. **First Token** : Model processes the entire input context \(=image features + text prompt\) to generate token 1

2. **Second Token** : Model processes the input context PLUS to=ken 1 to generate token 2

3. **Third Token** : Model processes the input context PLUS tok=ens 1-2 to generate token 3

4. **Continue** : This pattern repeats until max\_new\_tokens is =reached or an end token is generated

The `max_new_tokens` parameter acts as a hard ceiling on gene=ration time because:

- Generation time scales roughly linearly with the number of tokens produc�

- Each new token requires attention computation over the growing sequence =length

- Longer sequences require more memory reads for key-value cache access

- The model must evaluate the stopping condition after each token

Setting `max_new_tokens` too high creates several problems:

- Even if the model could describe a scene in 50 tokens, setting max\_new\_t=okens=1000 means clients must wait for up to 1000 generation steps if the= model doesn't produce an end token

- Higher token limits require larger key-value cache allocations, reducing= concurrent request capacity

- Long generation sequences increase the probability of hitting client tim=eout limits

- The model may continue generating redundant or hallucinated content beyo=nd the useful description length

The default of 320 tokens \(roughly ~1300 characters\) represents a balanc=e between descriptive capability and performance. Unlike the vision encoder= which processes all image patches in parallel, or the initial forward pass= which processes the entire input context simultaneously, token generation =is inherently sequential. This means:

- **Vision Processing** : All image features computed in singl=e forward pass \(parallel\)

- **Initial Text Processing** : Entire prompt processed simult=aneously \(parallel\)

- **Token Generation** : Each output token requires separate f=orward pass \(sequential\)

This architectural constraint makes token limit selection one of the mos=t critical performance tuning parameters for auto-regressive vision-languag=e models.

# # O=ther Implementation Notes

## # Gre�y Decoding Strategy

The implementation enforces deterministic output through greedy decoding= configuration:

gc.do_s=ample = False # Disable sampling randomnessgc.num_beams = 1 # Single beam for deterministic outputgc.top_p = 1.0 # Disable nucleus samplinggc.temperature = 1.0 # Neutral temperature

This configuration ensures reproducible results for identical inputs, wh=ich is crucial for testing and production deployments where consistent beha=vior is required.

## # Memory Efficiency Optimizations

The implementation minimizes memory usage through several strategies:

- **bfloat16 Precision** : Reduces activation memory by 50% co=mpared to float32

- **In-place Operations** : Uses division operations that modi=fy tensors in-place where possible

- **Gradient Disabled** : `@torch.inference_mode()`= eliminates gradient computation overhead

- **Efficient Layouts** : Maintains contiguous memory layouts =throughout processing

## # VR=AM Consumption Patterns

Gemma-3n represents the largest memory consumer in the model suite, typi�lly requiring 2-4GB VRAM depending on:

- Model precision \(bfloat16 vs float32\)

- Maximum sequence length \(determined by token expansion\)

- Number of input frames \(affects pixel\_values tensor size\)

- Batch size \(though typically 1 for this deployment\)

The vision encoder and language model weights dominate memory usage, whi=le activation memory scales with input content size.

#
FasterWhisper

This implementation serves OpenAI's Whisper model through the FasterWhis=per library, which is a reimplementation optimized for speed and efficiency=. The model was specifically designed for A/B testing against the Parakeet =model, featuring identical input/output signatures to enable direct perform=ance comparisons. The implementation leverages automatic long-form audio ch=unking via BatchedInferencePipeline and includes conditional gzip compressi=on for large transcription results.

The implementation provides speech-to-text capabilities through FasterWh=isper's reimplementation of OpenAI's Whisper model. The focus is on inferen� speed improvements through optimized computation graphs and memory manag=ement, making it well-suited for production deployment where latency and th=roughput matter.

The implementation handles feature-length audio content without memory o=verflow, maintains accuracy across diverse audio conditions, and provides d=etailed timestamp information for downstream processing workflows.

The implementation uses Whisper's "large-v3" model, which represents the= most capable version available at the time of development. Model selection= balances accuracy requirements against computational resources, with large=-v3 providing the best transcription quality for challenging audio content =including movies, podcasts, and low-quality recordings.

Device selection automatically detects CUDA availability and falls back =to CPU processing when GPU resources are unavailable. This flexibility ensu=res the service remains functional even when VRAM is constrained by other m=odels.

Compute precision defaults to float16 but can be overridden through the =WHISPER\_COMPUTE\_TYPE environment variable. Float16 provides significant mem=ory savings and performance improvements on modern GPUs while maintaining t=ranscription accuracy for most content. The precision can be adjusted to fl=oat32 for maximum accuracy when computational resources allow, or to int8 f=or extreme memory constraints.

The BatchedInferencePipeline represents a significant architectural adva=ntage over manual chunking approaches. This pipeline automatically handles =segmentation of long-form audio into manageable chunks, applies overlapping= windows to prevent word loss at boundaries, and manages batch processing t=o maximize GPU utilization.

The pipeline includes built-in Voice Activity Detection \(VAD\) that autom=atically identifies speech segments and skips silence or non-speech audio. =This VAD capability reduces processing time by focusing computation on spee=ch content while maintaining transcription completeness.

Unlike custom windowing implementations that require manual overlap mana=gement and boundary condition handling, the pipeline encapsulates best prac=tices for long-form transcription including optimal chunk sizing and timest=amp alignment across segments.

# # Input/Output Tensors

- **Input:**`AUDIO`

- **Type** : `TYPE_STRING`

- **Description** : A tensor containing the raw bytes of an au=dio file.

- **Input:**`LANGUAGE`**\(Optional\)**

- **Type** : `TYPE_STRING`

- **Description** : The language of the audio in two-letter IS=O 639-1 format \(e.g., "en", "es"\). If omitted, the model will automatically= detect the language.

- **Input:**`TASK`**\(Optional\)**
- **Type** : `TYPE_STRING`

**Description** : Specifies the task, either "transcribe" \(d�ault\) or "translate" \(to English\).

- **Output:**`TRANSCRIPT_JSON`**/`TRANSCRIPT_GZIPPED`**

- **Type** : `TYPE_STRING`

- **Description** : A JSON string containing the transcription=. For payloads over 10KB, the response is gzip compressed and returned in t=he

`TRANSCRIPT_GZIPPED` tensor. The JSON includes segment-level =text, timestamps, and word-level details if requested.

- **Output:**`LANGUAGE_OUT`

- **Type** : `TYPE_STRING`

- **Description** : The detected language of the audio.

# # =
Media Processing Pipeline

Audio ingestion uses PyAV for universal container format support, handli=ng mp4, mp3, flac, wav, and other common audio/video formats through a sing=le code path. The decoder extracts the first available audio stream from an=y container, eliminating the need for format-specific preprocessing or exte=rnal conversion tools.

Resampling to 16kHz mono is performed using av.AudioResampler with forma=t="s16" for 16-bit signed integer output, layout="mono" for single chan=nel audio, and rate=16000 to match Whisper's expected input format. The r=esampling process includes automatic sample rate conversion from any source= rate, channel mixing for multi-channel sources, and format conversion from= various bit depths.

The frame-by-frame decoding approach efficiently handles large media fil=es by processing audio in chunks rather than loading entire files into memo=ry. This streaming approach prevents memory exhaustion when processing hour=s of audio content while supporting optional duration limiting for testing =or preview workflows.

## # Language

The implementation supports both automatic language detection and explic=it language specification through the LANGUAGE input parameter. When no lan=guage is specified, Whisper's built-in detection examines audio characteris=tics and linguistic patterns to identify the source language automatically.= This detection works reliably for major world languages and many regional =variants.

Task configuration supports both transcription and translation modes thr=ough the TASK parameter. Transcription mode produces text in the source lan=guage, while translation mode converts speech to English text regardless of= the input language. This dual capability enables workflows that require ei=ther faithful transcription or English-language processing of multilingual =content.

## # S=egment and Word Processing

The pipeline generates segments that represent natural speech boundaries= identified through acoustic and linguistic analysis. Each segment includes= start and end timestamps aligned to speech content, transcribed text with =automatic punctuation and capitalization, and word-level detail when reques=ted through word\_timestamps=True.

Word-level processing provides granular timing information essential for= subtitle generation, audio-visual alignment, and advanced analysis workflo=ws. Each word object includes the actual text content with whitespace norma=lized, start and end timestamps rounded to millisecond precision, and confi�nce scores that indicate transcription certainty.

The confidence scoring mechanism helps identify potentially problematic =transcriptions where manual review might be beneficial. Low confidence scor=es often correlate with challenging audio conditions, technical terminology=, or speech patterns that deviate from training data distributions.

#
NVIDIA Parakeet

This implementation serves NVIDIA's Parakeet-TDT-0.6B-v2 ASR model, whic=h is a NeMo RNNT \(Recurrent Neural Network Transducer\) with TDT \(Token and =Duration Time\) modeling and a FastConformer encoder.

Parakeet-TDT uses an RNNT architecture with a FastConformer encoder. Whi=le this is not a decoder-only Transformer with full quadratic self-attentio=n, long audio sequences still stress memory and runtime due to encoder stat=e management, convolutional subsampling operations, predictor and joint net=work passes, and timestamp alignment buffer requirements.

Triton hosts models through Python backend classes that expose initializ=e, execute, and finalize methods. Each Python model process holds its own G=PU memory allocations. Running multiple Python-backend models with instance=\_group count greater than 1 multiplies VRAM usage by creating multiple copi=es of model weights.

PyTorch's CUDA caching allocator can cause memory fragmentation where "s=tale" chunks result in allocation failures even when total free memory appe=ars sufficient. This requires careful allocator configuration and environme=nt variable tuning.

# # Input/Output Tensors

- **Input:**`AUDIO_PATH`

- **Type** : `TYPE_STRING`

**Description** : The absolute filesystem path to the audio =or video file.

- **Input:**`TIMESTAMPS`**\(Optional\)**

- **Type** : `TYPE_STRING`

- **Description** : Specifies the desired timestamp granularit=y. Accepts "word" \(default\), "segment," or "all".

- **Output:**`TRANSCRIPT_JSON`**/`TRANSCRIPT_GZIPPED`**

- **Type** : `TYPE_STRING`

- **Description** : A JSON string containing the transcription=. For payloads over 10KB, the response is gzip compressed and returned in t=he

`TRANSCRIPT_GZIPPED` tensor. The JSON includes segment-level =text, timestamps, and word-level details if requested.

# # =Media Processing Pipeline

Audio ingestion uses PyAV to decode any container format including mp4, =mp3, flac, and wav files. The pipeline extracts audio streams, resamples to= 16kHz mono using av.AudioResampler with format="s16", layout="mono", a=nd rate=16000, then normalizes the resulting int16 data to float32 in the= range \[-1, 1\].

Processing a 4,000-second audio file \(equivalent to a 128MB mp3 at 16kHz= mono\) in a single pass creates enormous intermediate tensors. Even though =Parakeet doesn't use full quadratic attention, RNNT decoders maintain buffe=rs and state for each time step while encoders hold activations for each fr=ame. The encoder's subsampling reduces some memory pressure, but hours of a=udio still cause memory to balloon beyond available VRAM.

## # =Windowed Inference Solution

The solution implements windowed or "buffered" inference that slices aud=io into fixed-size windows of 30 seconds with 0.6 to 1.0 seconds of overlap= between adjacent windows. Each window is processed independently through <=code>model.transcribe\(\), and the resulting word timestamps are shift� by the window's start offset to create global timestamps.

Overlap deduplication prevents word repetition at window boundaries by d=ropping any word whose start time is less than `(last_end - time_strid=e)`. This approach guarantees bounded GPU memory usage regardless of =input duration while avoiding word loss at window transitions.

## # Segmenta=tion Logic

The implementation needed to generate coarse segments for metadata and V=LM alignment while providing fine-grained words for MAM processing. Rather =than trusting model-specific "segment" objects that vary across NeMo versio=ns, segments are built from word timestamps using a simple, configurable po=licy.

Segmentation begins with the first word and creates new segments when ei=ther a pause of at least SEGMENT\_MIN\_GAP\_S \(default 0.7 seconds\) occurs, or= when the current segment duration exceeds SEGMENT\_MAX\_DURATION\_S \(default seconds\).

To avoid micro-segments, any fragment with fewer than SEGMENT\_MIN\_WORDS =words is merged into the previous segment rather than standing alone.

Text reconstruction uses a punctuation-aware joining algorithm that prev=ents extra spaces around punctuation marks like parentheses and other speci=al characters.

This approach yields stable start/end time and text blocks without depen=ding on internal model chunking behavior that may change between versions.<=/p>

# # Implem=entation Notes

NeMo’s documentation and implementation are often at odds with e�h other.

## # Model L=oading Issues

Initial attempts used `ASRModel.from_pretrained(model_name="nvidi=a/parakeet-tdt-0.6b-v2", map_location=device, cache_dir=...)` but= some NeMo versions reject the cache\_dir parameter and raise errors.

The preferred solution calls `from_pretrained(model_name=..., map=_location=...)` without cache\_dir and lets HuggingFace environment =variables like HUGGING\_FACE\_HUB\_CACHE and HF\_HOME control caching behavior.= The fallback approach downloads the .nemo checkpoint via huggingface\_hub a=nd calls `ASRModel.restore_from(restore_path=...)`.

## # Timestamp API Inconsistencies

Official documentation suggests two approaches for timestamp generation:=

- Direct method: `asr_model.transcribe(..., timestamps=True)`=

- Configuration method: Set `preserve_alignments=True`, compute\_timestamps=True, and `rnnt_timestamp_type="word" in decoding config, then read `hyp.timestamp\['word'\]` or <=code>hyp.timestep['word']`

In practice, the direct method fails with `TypeError: EncDecRNNTMod=el.transcribe() got an unexpected keyword argument 'timestamps'`. The= configuration approach triggers warnings like "If compute\_timesteps is set=, then preserve\_alignments must also be set."

API variations across versions include different parameter names where s=ome builds expect `compute_timestamps` while others use `co=mpute_timesteps`. Strategy names can be "greedy\_batch" or "greedy". N=eMo contains intentional typos in some parameter names like "seperator" ins=tead of "separator".

The production solution builds a defensive decoding configuration that t=ries parameter variants in sequence while always maintaining `preserve=_alignments=True`, `rnnt_timestamp_type="word"`, and a=ppropriate separator settings. The implementation logs which configuration =variant succeeds for debugging purposes.

Timestamp extraction handles multiple possible attribute names on the hy=pothesis object including `hyp.timestamp`, `hyp.timestamps<=/code>, and `hyp.timestep`. Within each word entry, the code pre�rs absolute time values like `start\_time` and `end\_time when available, otherwise it maps frame offset values like `star=t_offset` and `end_offset` to seconds using the RNNT strid=e calculation: `time_stride_sec = 8 * model.cfg.preprocessor.window_=stride`, which typically equals approximately 0.08 seconds.``

Character-level timestamps are intentionally never computed to reduce co=mputational overhead and memory usage.

## # CUDA Gra=ph Problems

The implementation frequently encountered "CUDA error: an illegal memory= access was encountered" errors, often occurring on chunk number 2 during t=he second processing window.

Root cause analysis revealed that when cuda-python version 12.3 or highe=r is installed, NeMo attempts to enable CUDA Graphs with conditional nodes =for the TDT while-loop. Graph capture is extremely sensitive to shape chang=es, internal memory allocations, and capture-unsafe kernel operations, caus=ing failures during graph replay.

Mixed precision operations using fp16 can stress fused kernels, particul=arly with certain GPU driver and CUDA toolkit combinations.

## # Stab=ility Improvements

The solution disables CUDA Graphs by uninstalling cuda-python from the T=riton container image. NeMo will display a benign warning about conditional= nodes being unavailable, but this eliminates the graph capture instability=.

Force fp32 precision without autocast during decode operations to avoid =fragile mixed-precision kernels that can cause crashes.

Environment configuration includes allocator and debugging settings:

- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_=mb:256`

- `CUDA_LAUNCH_BLOCKING=1` when debugging to get precise erro=r stack traces

Future optimizations if CUDA Graphs are revisited could include padding =the final window to match the length of previous windows so replay shapes r=emain consistent, and maintaining `instance_group.count=1` to =avoid multi-process capture interactions.