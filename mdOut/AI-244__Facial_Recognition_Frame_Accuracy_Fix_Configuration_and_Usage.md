---
title: "AI-244: Facial Recognition Frame Accuracy Fix Configuration and Usa=ge"
source_file: "AI-244__Facial_Recognition_Frame_Accuracy_Fix_Configuration_and_Usage.doc"
converted_date: "2025-09-17T11:24:58.805123"
format: "markdown"
---

# AI-244: Facial Recognition Frame Accuracy Fix Configuration and Usa=ge

This guide explains how to configure frame processing for facial= recognition tasks. The workflow involves two main steps:

- **Initial Frame Sampling** : Frames are sampled based on a p=redefined rate \(e.g., `frame_sampling_per_minute`\).

- **Adjacent Frame Sampling** : For each frame where a face is= detected, additional frames are sampled based on the `time_offset and `offset\_direction` configurations.`

This process continues until no more faces are detected in the sampled f=rames or the frames have already been processed.

# # Key Configuration Options

## # 1\. time\_offset

### # What it does:

This setting defines the time interval \(in milliseconds\) used to determi=ne how far to look in the specified `offset_direction` for adjac=ent frames.

### # How it works:

After a face is detected in a frame, the system uses `time_offset to calculate how many frames to skip before sampling the next frame.<=/p>

The number of frames to offset is calculated as:

frame_o�set = int(frame_rate * (time_offset / 1000))

For example, if `time\_offset = 1000 ms` and `frame\_rat=e = 30 fps`, the offset is 30 frames.

### # When to use it:

Use this to control how far apart the sampled frames should be when look=ing for adjacent frames.

## # 2. offset_direction

### # What it does:

This setting determines the direction in which to sample adjacent frames= relative to the current frame.

### # Options:

- **"forward"** : Only sample frames after the current frame.<=/p>

- **"backward"** : Only sample frames before the current frame=.

- **"both"** : Sample frames both before and after the current= frame.

- **"none"** : Do not sample adjacent frames.

### # How it works:

Once a face is detected in a frame, the system uses `offset\_directi=on` to decide whether to look forward, backward, both, or not at all.=

The `time\_offset` value determines how far to look in the cho=sen direction(s).

**Example:** If `time\_offset = 1000 ms`, frame_rate = 30 fps

`, and `offset_direction = "forward", the system will sample the frame 30 frames after the current one.`

### # When to use it:

Use this to control the direction in which to search for adjacent frames= after a face is detected.

## # 3\. max\_interval

### # What it does:

This setting defines the maximum time difference \(in milliseconds\) betwe=en two consecutive frames where a face exists, to consider the face in rang=e \(still visible in the shot\).

### # How it works:

After all frames are processed and the results are gathered \(all frames =containing the face we want\), a range is built where that face exists in th=e video. If the time difference between two consecutive frames where the fa� is detected is greater than `max_interval`, the system consid=ers it as a new appearance of the face.

**Example:** If `max_interval = 1000 ms`, and =two frames where the face is detected are 1200 ms apart, they will be treat� as separate occurrences of the face.

### # When to use it:

Use this to control how long a face can be missing from consecutive fram=es before considering it to have disappeared.

# # Example Configuration

Here’s how you can set up and use these configurations in your w=orkflow:

{ "backedn":"retinaface", "identification_threshold":0.75, "frame_sampling_per_minute":30, "processing":{ "time_offset":1000, # default "offset_direction":"forward", # default "max_interval":1000 # default }}

# # Summary

- **time\_offset** : Determines how far to look in the specifie=d direction for adjacent frames.

- **offset\_direction** : Controls the direction \(forward, back=ward, both, or none\) to sample adjacent frames.

- **max\_interval** : Defines the maximum time difference betwe=en two consecutive frames where a face exists to consider it in range.

<=/li>