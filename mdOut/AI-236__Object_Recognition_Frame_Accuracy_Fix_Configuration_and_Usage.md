---
title: "AI-236: Object Recognition Frame Accuracy Fix Configuration and Usa=ge"
source_file: "AI-236__Object_Recognition_Frame_Accuracy_Fix_Configuration_and_Usage.doc"
converted_date: "2025-09-17T11:24:58.794316"
format: "markdown"
---

# AI-236: Object Recognition Frame Accuracy Fix Configuration and Usa=ge

This guide explains how to configure frame processing for object= detection tasks. The workflow involves two main steps:

- **Initial Frame Sampling** : Frames are sampled based on a p=redefined rate \(e.g., `frame_sampling_per_minute`\).

- **Adjacent Frame Sampling** : For each frame where an object= is detected, additional frames are sampled based on the `time_offset<=/code> and `offset\_direction` configurations.`

This process continues until no more objects are detected in the sampled= frames or the frames have already been processed.

# # Key Configuration Options

## # 1\. time\_offset

### # What it does:

This setting defines the time interval \(in milliseconds\) used to determi=ne how far to look in the specified `offset_direction` for adjac=ent frames.

### # How it works:

After an object is detected in a frame, the system uses `time_offse=t` to calculate how many frames to skip before sampling the next fram=e.

The number of frames to offset is calculated as:

frame_o�set = int(frame_rate * (time_offset / 1000))

For example, if `time_offset = 1000 ms` and `frame_rat=e = 30 fps`, the offset is 30 frames.

### # When to use it:

Use this to control how far apart the sampled frames should be when look=ing for adjacent frames.

## # 2\. offset\_direction

### # What it does:

This setting determines the direction in which to sample adjacent frames= relative to the current frame.

### # Options:

- **"forward"** : Only sample frames after the current frame.<=/p>

- **"backward"** : Only sample frames before the current frame=.

- **"both"** : Sample frames both before and after the current= frame.

- **"none"** : Do not sample adjacent frames.

### # How it works:

Once an object is detected in a frame, the system uses `offset_dire=ction` to decide whether to look forward, backward, both, or not at a=ll.

The `time_offset` value determines how far to look in the cho=sen direction\(s\).

**Example:** If `time_offset = 1000 ms`, frame\_rate = 30 fps, and `offset_direction = "forward", the system will sample the frame 30 frames after the current one.`

### # When to use it:

Use this to control the direction in which to search for adjacent frames= after an object is detected.

## # 3\. max\_interval

### # What it does:

This setting defines the maximum time difference \(in milliseconds\) betwe=en two consecutive frames where an object exists, to consider the object in= range \(still visible in the shot\).

### # How it works:

After all frames are processed and the results are gathered \(all frames =containing the object we want\), a range is built where that object exists i=n the video. If the time difference between two consecutive frames where th=e object is detected is greater than `max_interval`, the system =considers it as a new appearance of the object.

**Example:** If `max_interval = 1000 ms`, and =two frames where the object is detected are 1200 ms apart, they will be tre=ated as separate occurrences of the object.

### # When to use it:

Use this to control how long an object can be missing from consecutive f=rames before considering it to have disappeared.

# # Example Configuration

Here’s how you can set up and use these configurations in your w=orkflow:

{ "vision_model": "phi3", "object_detection_model": "groundingdino", "frame_sampling_per_minute": 10, "vision_tasks": [ { "object": "car", "detail": "lamborghini" } ], "time_offset": 1000, # default "offset_direction": "forward", # default "max_interval": 1000 # default}

# # Summary

- **time\_offset** : Determines how far to look in the specifie=d direction for adjacent frames.

- **offset\_direction** : Controls the direction \(forward, back=ward, both, or none\) to sample adjacent frames.

- **max\_interval** : Defines the maximum time difference betwe=en two consecutive frames where an object exists to consider it in range.