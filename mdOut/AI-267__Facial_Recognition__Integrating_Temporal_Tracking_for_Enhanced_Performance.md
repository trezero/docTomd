---
title: "AI-267: Facial Recognition: Integrating Temporal Tracking for Enhan�d Performance"
source_file: "AI-267__Facial_Recognition__Integrating_Temporal_Tracking_for_Enhanced_Performance.doc"
converted_date: "2025-09-17T11:24:58.844208"
format: "markdown"
---

# AI-267: Facial Recognition: Integrating Temporal Tracking for Enhan�d Performance

# Current Implementation

The initial approach we implemented relies on a basic "sample every fram=e" strategy for face tracking:

1. Go back 1 second before the sample location.

2. Sample every frame to check for the face.

3. Store the first frame where the face is found as the Inpoint.

4. Continue sampling every frame.

5. Save the previous frame as the outpoint frame when the face disappears.<=/p>

6. Use inPoint and outPoint to generate accurate inpoint and outpoint and d=uration information.

This approach essentially re-runs face detection and embedding extractio=n on _every single frame_ \(or at least within a 1-second window\) of =the video.

This approach has several critical flaws, making it unsuitable for the d=emands of our project, _especially_ given the limitations of our cur=rent workstation:

- **Computational Overload:** The core problem is sheer compu=tational cost. Face detection and embedding extraction are computationally =intensive tasks, even with a powerful GPU like the L40S. Re-running these o=perations on every frame of high-resolution video creates a massive process=ing bottleneck. The GPU simply cannot keep up with the workload, which coul=d lead to extremely slow processing times and potentially causing system cr=ashes or instability.

- **Redundancy and Inefficiency:** Consecutive video frames o=ften contain very similar information. Re-analyzing each frame from scratch= wastes valuable GPU cycles on redundant computations. We're essentially re=-discovering the same information over and over.

- **Lack of Temporal Coherence:** The algorithm ignores the f�t that faces in a video typically move smoothly from frame to frame. It d=oesn't leverage the temporal relationships between frames, which could sign=ificantly reduce the computational burden.

- **Poor Handling of Occlusions:** Sports content, particular=ly baseball, is rife with occlusions. A player's face might be hidden by a =glove, a helmet, or another player. The "sample every frame" approach fails= as soon as an occlusion occurs, leading to premature track termination and= inaccurate results.

- **Sensitivity to Appearance Changes:** The appearance of a �ce can change due to lighting, pose, and expression. The initial embeddin=g might become less accurate over time, causing the algorithm to lose track=.

- **Arbitrary Sampling Window:** The 1-second sampling window= is an arbitrary and inflexible parameter. It's not adaptive to the actual =video content or the movement of the faces.

# Design

I propose we move to a more intelligent and efficient system built aroun=d object tracking, multi-model face recognition, and careful resource manag=ement.

- **Accurate:** Lower false positives, higher confidence in i�ntity assignments.

- **Efficient:** Maximized GPU throughput, reduced processing= time.

- **Scalable:** Handles multiple faces and long video sequenc=es.

- **Robust:** Tolerant of occlusions, lighting variations, an=d pose changes.

- **Maintainable:** Modular design for easier debugging and m=odification.

Here's a breakdown of the key components:

NOTE: This algorithm is portable, extending to the Object Detection fram=ework\!

# # **Multi-Object Tracking:**

We're integrating the DeepSORT \(Deep Simple Online and Realtime Tracking=\) algorithm. DeepSORT isn't just a tracker; it's a complete tracking-by-det�tion system. It handles:

- **Object Detection:** DeepSORT _incorporates_ an obj�t detector. While we can experiment with different detectors, we'll likel=y start with a RetinaFace model running within DeepSORT.

- **State Estimation:** DeepSORT uses a Kalman filter to pred=ict the future location of each tracked object based on its past trajectory=. This is crucial for handling brief occlusions and noisy detections.

- **Data Association:** DeepSORT uses the Hungarian algorithm= to associate new detections with existing tracks based on both location an=d appearance.

- **Appearance Modeling:** The "deep" part of DeepSORT comes =from its use of a deep learning-based appearance descriptor \(often a CNN\) t=o capture the visual characteristics of each tracked object. This allows De=epSORT to re-identify objects even after significant changes in pose or lig=hting.

DeepSORT provides the robust foundation we need to track multiple player=s throughout the game, even with frequent occlusions and complex camera mov=ements. It offloads the majority of the frame-by-frame analysis from our fa� recognition models, freeing up the L40S for more strategic tasks.

# # **Periodic Verification:**

DeepSORT provides _track IDs_ and bounding boxes. However, these =are just for tracking _objects_. We need to identify _who_ th=ose objects are. The following is a rough outline of the algorithm:

- Every _N_ frames \(we'll experiment with values like 10, 15, or 20=, balancing accuracy and performance\), we'll extract the face region from t=he bounding box provided by DeepSORT.

- We'll extract embeddings using the configured face recognition models \(e=.g. FaceNet512 and ArcFace\).

- We'll compare these embeddings to our database of known players.

for= track in deepsort.tracker.tracks: if not track.is_confirmed() or track.time_since_update > 1: continue # Skip unconfirmed or recently lost tracks track_id = track.track_id bbox = track.to_tlwh() # Get bounding box (x, y, width, height) if frame_count % REID_FREQUENCY == 0: face_region = extract_face_from_frame(frame, bbox) if face_region is not None: #Handle for if a face cannot be extract�. facenet_embedding = extract_embedding(face_region, model="F�eNet512") arcface_embedding = extract_embedding(face_region, model="A=rcFace") # Compare embeddings to our database best_match, confidence = find_best_match(facenet_embedding, a=rcface_embedding, database) if confidence > IDENTITY_THRESHOLD: # We can set this for ea=ch type of model for better accuracy. track.identity = best_match cache_identity(track_id, best_match) #We can set a timer fo=r each individual for better accuracy.

# # **Confidence Scoring**

Cosine similarity scores are just that – _similarity_ sco=res. They don't tell us anything about the _reliability_ of the mode=l or the certainty of the match. We need a confidence metric. So we will pe=rform the following steps:

- Establish baseline cosine similarity scores for each model \(FaceNet512, =ArcFace\) on our dataset. This will help us understand the typical range of =scores for correct matches.

- Combine the cosine similarity scores from the different models using a w=eighted average. Models with higher baseline reliability will receive highe=r weights.

- Implement penalties for scores that are significantly below the baseline= or for cases where the face is partially occluded.

- Consider the context of the track. If a player has been consistently ide=ntified as "Shohei Ohtani" for the past 3 minutes, we should be more confid=ent in subsequent matches.

def f=ind_best_match(facenet_embedding, arcface_embedding, database): best_match = None best_confidence = 0.0 for identity, embeddings in database.items(): facenet_similarity = cosine_similarity(facenet_embedding, embeddi=ngs["facenet"]) #Assume the database structure is the same as the extractio=n arcface_similarity = cosine_similarity(arcface_embedding, embeddi=ngs["arcface"]) # Weighted average of the similarities confidence = (FACENET_WEIGHT * facenet_similarity + ARCFACE_WEIGH=T * arcface_similarity) if confidence > best_confidence: best_confidence = confidence best_match = identity return best_match, best_confidence

# # **Identity Management**

Once we've confidently identified a player, we'll cache this association= in a lookup table \(keyed by the DeepSORT track ID\). For subsequent frames,= we'll _prioritize_ the identity matching against the cached identit=y. If the cached identity matches with high confidence, we can skip the ful=l database search. We will only perform this when REID\_FREQUENCY is met.

The vast majority of tracks will represent the same player for extended =periods. Caching the identity significantly reduces the computational load =on the GPU

Because this is DeepSORT, we can assume that if the identity cache exist=s, the identity stays relatively the same after we have run and generated a= cache key.

def cache=_identity(track_id, identity): identity_cache[track_id] = { "identity": identity, "timestamp": current_time() }def check_cache(track_id): #If the track_id exists in identity_cache and timer is running for the =correct timestamp then run this code. if track_id in identity_cache: identity_information= identity_cache[track_id] #Run processes here. del identity_cache[track_id] return identity_information