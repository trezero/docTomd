---
title: "AI-266: Migrating from Euclidean Distance to Cosine Similarity"
source_file: "AI-266__Migrating_from_Euclidean_Distance_to_Cosine_Similarity.doc"
converted_date: "2025-09-17T11:24:58.831580"
format: "markdown"
---

# AI-266: Migrating from Euclidean Distance to Cosine Similarity

We needed to change the facial recognition workflow with a funda=mental change: switch from using Euclidean distance to cosine similarity fo=r comparing facial embeddings. This change was driven by the need to improv=e the accuracy and robustness of the system, particularly in dealing with h=igh-dimensional data and normalized embeddings.

# Original Implementation

The initial face recognition system followed a standard approach:

1. **Face Detection:** Faces were detected in images using a f�e detection algorithm \(e.g., one provided by DeepFace or OpenCV\).

2. **Embedding Generation:** A pre-trained face recognition mo�l \(e.g., FaceNet512, ArcFace\) was used to generate a numerical representa=tion \(embedding\) of each detected face. This embedding captured the key fac=ial features in a high-dimensional vector.

3. **Database Storage:** The facial embeddings were stored in =a vector database \(ChromaDB\), along with associated metadata \(e.g., name, I=D, image source\). The database was configured to use Euclidean distance \(L2= distance\) as the metric for comparing vectors.

4. **Recognition:**

- Given a query image, the face was detected, and its embedding was genera=ted.

- The system queried the database to find the embedding that was closest t=o the query embedding, based on Euclidean distance.

- If the Euclidean distance between the query embedding and the closest da=tabase embedding was below a certain threshold, the system declared a match= and identified the face.

Euclidean distance was chosen initially because:

- It is a simple and widely used distance metric.

- It is readily available in most vector databases \(including ChromaDB\).

Despite the initial rationale, several problems were observed with the E=uclidean distance-based approach:

1. **Unintuitive Distance Values:** The raw Euclidean distance= values were difficult to interpret as a measure of similarity. The range o=f possible distance values depended on the characteristics of the embedding= space and the magnitude of the vector components, making it challenging to= set an appropriate threshold.

2. **Sensitivity to Vector Magnitude:** Euclidean distance is =sensitive to the magnitude \(length\) of the vectors. This meant that two vec=tors pointing in roughly the same direction \(i.e., representing similar fac=es\) could have a large Euclidean distance if one vector had a significantly= larger magnitude than the other.

3. **Inconsistent Results:** The system produced inconsistent =and unreliable recognition results, particularly with faces that were not p=erfectly aligned or had variations in lighting or expression.

As an example, the core of our problem was that a higher distance meant =different things under different situations:

- High distance = similar: if a face looks similar when the l2 norm of a=ll other is 0, then these small faces will have high distances to them\!

=
- Low distance = Dissimilar: if a face looks dissimilar with 1e99 pixels=, then the vectors will be extremely large\!

It also made it hard to set a threshold - should the high faces count or= not? Since a model can only operate on a certain subset, then there has to= be a more robust and consistent signal in order to make these determinatio=ns.

# Cosine Similarity

After careful analysis, it was decided to switch to using cosine similar=ity for comparing facial embeddings.

Cosine similarity offered several advantages over Euclidean distance for= this application:

**Directly Measures Angular Similarity:** Cosine similarity= measures the angle between two vectors, which is a more intuitive and robu=st measure of similarity than Euclidean distance, especially in high-dimens=ional spaces. The angle is a better indicator of whether two vectors are po=inting in the same direction, regardless of their magnitudes.

**Inherent Normalization:** Cosine similarity is inherently= normalized for vector magnitude. This means that the similarity score is n=ot affected by the length of the vectors, only their direction. This is par=ticularly important when working with face embeddings, as the magnitude of =the embedding vector typically doesn't have any meaningful interpretation i=n terms of facial identity.

**Better Performance in High Dimensions:** In high-dimensio=nal spaces, Euclidean distance can become less effective as a measure of si=milarity due to the "curse of dimensionality." As the number of dimensions =increases, the distances between vectors tend to become more uniform, makin=g it harder to distinguish between similar and dissimilar vectors. Cosine s=imilarity is less susceptible to this problem.

**Natural Range:** Cosine similarity is naturally bounded b=etween -1 and 1, where:

1. 1 indicates perfect similarity \(vectors pointing in the same direction\).=

2. 0 indicates orthogonality \(vectors are unrelated\).

3. -1 indicates perfect dissimilarity \(vectors pointing in opposite directi=ons\).

This natural range makes it easier to set meaningful thresholds and inte=rpret the similarity scores.

The switch to cosine similarity involved the following steps:

**Embedding Normalization:** It was ensured that all facial= embeddings were L2 normalized to unit length _before_ storing them =in the database. This is a crucial step because cosine similarity is most e�ective when used with normalized vectors. L2 normalization involves divid=ing each element of the vector by its L2 norm \(Euclidean norm\), resulting i=n a vector with a magnitude of 1.

**ChromaDB Configuration:** The ChromaDB collection was rec=onfigured to use cosine similarity as the distance metric. This involved se=tting the "hnsw:space" metadata parameter to "cosine" during collection cre=ation or update.

**Similarity Calculation:** The code for calculating simila=rity scores was updated to use cosine similarity instead of Euclidean dista=nce. With normalized vectors, cosine similarity can be efficiently computed= using a dot product:

c=osine_similarity = np.dot(embedding1, embedding2)

**Threshold Adjustment:** The similarity threshold used for= face recognition was adjusted to reflect the new range of cosine similarit=y values \(i.e., -1 to 1\).

Okay, let's add a section explaining HNSW and detailing the configuratio=n choices made for ourr face recognition system:

# ChromaDB

It’s important to understand, in detail, exactly WHAT a vector d=atabase does under the hood. At its core, ChromaDB uses an algorithm called= Hierarchical Navigable Small World \(HNSW\) internally to measure distances �tween vectors. HNSW implements efficient nearest neighbor search. The mai=n problem for searching "close vectors" in high dimensionality is that it's= a _huge_ processing workload that can lead to massive slowdowns and= even crashes.

It builds a multi-layer graph structure, where each layer is a "small wo=rld" graph. In a small world graph, most nodes are not direct neighbors of �ch other, but most nodes can be reached from every other by a small numbe=r of hops or steps.

This is an "approximate" method. The goal is _not_ to find the ab=solute nearest neighbors with 100% certainty \(which would be too slow\). Ins=tead, it aims to find neighbors that are "close enough" with high probabili=ty, and it does so very quickly. For any dataset over a few hundred data sa=mples, HNSW is usually the best candidate for indexing and running high-dim=ensional data.

Some advantages

- **Speed:** HNSW provides fast nearest-neighbor search, espe=cially in high-dimensional spaces.

- **Scalability:** It can efficiently handle large datasets.<=/p>

- **Accuracy vs. Speed Trade-off:** HNSW allows us to tune th=e trade-off between search accuracy and speed by adjusting its configuratio=n parameters.

## # HNSW Configuration Parameters

The behavior of HNSW is controlled by several configuration parameters:<=/p>

- **space:** This parameter specifies the distance metric use=d to measure the distance between vectors. It determines how the HNSW graph= is built and how similarity searches are performed. In our system, we are =using "cosine" to support the properties of a unit vector as detailed in th=e last section. The alternative is L2, which requires more steps.

- **M \(Maximum Connections per Layer\):** This parameter contr=ols the maximum number of connections \(neighbors\) that each node can have i=n each layer of the graph.

- Higher M values create a denser graph, which can improve search accuracy= but also increase memory usage and indexing time.

- Lower M values create a sparser graph, which reduces memory usage and in�xing time but can potentially decrease search accuracy.

- A typical range for M is 16-64. Our implementation uses 16 set as a defa=ult.

- **ef\_construction \(Construction Effort\):** This parameter c=ontrols the thoroughness of the index building process. It determines how m=uch time the algorithm spends exploring the graph structure during index cr�tion.

- Higher ef\_construction values result in a more accurate index but also i=ncrease indexing time.

- Lower ef\_construction values reduce indexing time but can potentially de=crease search accuracy.

- A higher ef\_construction often comes with a higher search, so to better =manage accuracy, there must be a reasonable threshold.

- **ef\_search \(Search Effort\):** This parameter controls how =thoroughly the index is searched during query time. It determines how many =potential neighbors the algorithm explores during the search process.

- Higher ef\_search values result in more accurate search results but also =increase query latency \(search time\).

- Lower ef\_search values reduce query latency but can potentially decrease= search accuracy.

For our face recognition system, we have chosen the following HNSW confi=guration parameters, which are shown in the code:

- "hnsw:space": "cosine": As discussed in detail earlier, we are using cos=ine similarity as the distance metric.

- "hnsw:ef\_construction": Because we're assuming we're adding fewer nodes =to the training dataset and that accuracy is key, then it must have a large=r value.

- "hnsw:search\_ef": This should be a reasonable number, from 50-100, based= on how the data is expected.

These values represent a trade-off between accuracy and performance.