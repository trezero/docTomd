---
title: "AI-263: F1-Score Optimization"
source_file: "AI-263__F1-Score_Optimization.doc"
converted_date: "2025-09-17T11:24:58.819040"
format: "markdown"
---

# AI-263: F1-Score Optimization

The F1-score is a single metric that combines precision and reca=ll to provide a balanced measure of a model's accuracy. It is particularly =useful when the training set has an uneven class distribution \(i.e., one cl=ass has significantly more samples than the other\), as it considers both fa=lse positives and false negatives.

- **Precision:** Also known as positive predictive value=, it measures the proportion of correctly identified positive cases \(true p=ositives\) out of all cases predicted as positive \(true positives + false po=sitives\). It answers the question: "Of all the faces the model claimed were= a match, how many were actually correct?"

- Formula: `Precision = True Positives / (True Positives + Fal=se Positives)`

- **Recall:** Also known as sensitivity or true positive= rate, it measures the proportion of correctly identified positive cases \(t=rue positives\) out of all actual positive cases \(true positives + false neg=atives\). It answers the question: "Of all the actual matches in the dataset=, how many did the model correctly identify?"

- Formula: `Recall = True Positives / (True Positives + False =Negatives)`

- **F1-score:** The harmonic mean of precision and recal=l. It gives a higher weight to lower values, so a high F1-score ensures tha=t both precision and recall are reasonably high.

- Formula: `F1-score = 2 * (Precision * Recall) / (Precision += Recall)`

**Interpretation:**

- The F1-score ranges from 0 to 1.

- An F1-score of 1 indicates perfect precision and recall \(the model has n=o false positives and no false negatives\).

- An F1-score of 0 indicates that either precision or recall is zero \(the =model is either making a lot of false positive predictions or missing many �tual positives\).

So why is the F1-score important?

- **Balances Precision and Recall:** If we only consider= precision, we might choose a model that makes very few positive prediction=s, resulting in high precision but low recall. Conversely, if you only cons=ider recall, you might choose a model that predicts everything as positive,= resulting in high recall but low precision. The F1-score helps you find a �lance between these two extremes.

- **Useful for Imbalanced Datasets:** In many real-world= scenarios, the classes are not evenly distributed. For example, in face re=cognition, there might be far more images of different people than images o=f the same person. In such cases, accuracy alone can be misleading, and the= F1-score provides a more informative metric.

In the context of face recognition similarity thresholds, we want to cho=ose a threshold that maximizes the F1-score on your validation set. This me=ans finding a threshold that gives you a good balance between correctly ide=ntifying matches \(high recall\) and avoiding false matches \(high precision\).=

# Core Concepts

# # Training Data

- **Quantity and Quality:** The performance of a face recogni=tion model heavily depends on the quantity and quality of the training data=. More data generally leads to better performance, but it's equally importa=nt to ensure that the data is clean, diverse, and representative of the fac=es the system will encounter in real-world use.

- **Diversity:** The training data should include faces with =varying poses, lighting conditions, expressions, ages, and demographic char�teristics.

- **Balance:** While perfect balance is not always achievable=, it's desirable to have a relatively balanced representation of different �mographic groups in the training data to mitigate bias.

# # Validation Data

A well-constructed validation set is crucial for evaluating the performa=nce of a face recognition system and tuning parameters such as similarity t=hresholds.

- **Representativeness:** The validation set should be repres=entative of the real-world scenarios in which the system will be used. This= includes matching the distribution of ethnicities, ages, lighting conditio=ns, image quality, and other relevant factors.

_Avoid using images that were used in the training set._

- **Pairwise Comparisons:** The validation process involves c=reating pairs of face embeddings and labeling them as "match" \(same person\)= or "non-match" \(different person\).

- **Balanced Ratio:** Aim for a roughly 1:1 \(50% match, 50% n=on-match\) ratio of match to non-match pairs in the validation set to avoid =biasing the evaluation towards either positive or negative cases.

# # Evaluation Metrics: Precision, Recall, and F1-Score

- **Precision:** Measures the proportion of correctly identif=ied positive cases \(true positives\) out of all cases predicted as positive =\(true positives + false positives\). High precision means fewer false matche=s.

- Formula: Precision = True Positives / \(True Positives + False Positive=s\)

- **Recall:** Measures the proportion of correctly identified= positive cases \(true positives\) out of all actual positive cases \(true pos=itives + false negatives\). High recall means fewer missed matches.

- Formula: Recall = True Positives / \(True Positives + False Negatives\)<=/p>

- **F1-Score:** The harmonic mean of precision and recall, pr=oviding a balanced measure of accuracy. It is particularly useful when deal=ing with imbalanced datasets.

- Formula: F1-score = 2 \* \(Precision \* Recall\) / \(Precision + Recall\)

# Creating Validation Sets: Practical Considerations

# # General Guidelines=

1. **Separate Validation Set:** Always use a separate validati=on set that is distinct from the training data.

2. **Sufficient Size:** The validation set should be large eno=ugh to provide a statistically meaningful assessment of the model's perform=ance. The size is also dictated by number of classes you need to test. For =example, to reliably test the F1 score of a model's effectiveness with X im=ages per class in the test dataset to evaluate, then at least X\*\(number of =classes\) samples are needed in the validation dataset.

3. **Real-World Scenarios:** The data in the validation set sh=ould reflect the real-world conditions the system will encounter. If the sy=stem will primarily be used on images from security cameras, the validation= data should include such images. If you are recognizing baseball players, =you need to find images of baseball players.

4. **Diversity:** The data should include diversity of faces. =Ensure you have enough different faces to be representative of the real dep=loyment environment.

# # Handlin=g Demographic Diversity

- **Representative Sampling:** The demographic composition of= the validation set should reflect the intended use case of the face recogn=ition system. If the system will be used on a diverse population, the valid=ation set should also be diverse, with a representative sample of different= races/ethnicities, genders, ages, etc.

- **Bias Detection:** A balanced dataset is not sufficient to= measure bias. Create subsets for each race/ethnicity to see the performanc=e of the system across all demographics.

- **Inclusion of Similar Faces** : It's vital to include faces= of the same ethnicity to determine whether they can properly differentiate= between two faces, in addition to measuring bias.

## # The _N_ -Player Problem and the "Shohei Ohtani" E=xample

To use a practical example, all of this comes from working on the LA Dod=gers training set. To effectively validate a face recognition model, consid=er a scenario where a training set includes multiple players from a sports =team. To validate the data for Shohei Ohtani, the validation dataset should=:

1. **Include other players with Japanese origin.**

2. **Include players that are not of Japanese origin**

# # Generating= Validation Pairs

- **Pairwise Comparisons:** Create pairs of images from the v=alidation set.

- **Match and Non-Match Labeling:** Label each pair as "match=" \(same person\) or "non-match" \(different person\).

- **Equal Proportions:** If possible, ensure there are an equ=al amount of positive and negative labels.

# # Optimizing the= F1-Score

# # Similarity Thre=sholds

- **Model-Specific Tuning:** Different face recognition model=s produce embeddings with different characteristics. Therefore, the optimal= similarity threshold for determining a match will vary from model to model=.

- **Threshold Optimization:** Iterate through a range of thre=shold values and calculate precision, recall, and F1-score on the validatio=n set for each threshold. Choose the threshold that maximizes the F1-score =or provides the desired balance between precision and recall.

- _Remember to analyze this data for all demographic groups to detect b=ias._

# # Step-by-Step Process for F1-Score Optimization

1. **Prepare Validation Data:** See sections above.

2. **Extract Embeddings:** Use the face recognition model to e=xtract face embeddings for all images in the validation set.

3. **Calculate Similarity Scores:** Calculate the similarity s=core for each pair of face embeddings in the validation set using the appro=priate metric \(Euclidean distance or cosine similarity\).

4. **Iterate Through Thresholds:** For each model, iterate thr=ough a range of potential threshold values.

5. **Calculate TP, FP, TN, FN:** For each threshold value, det=ermine the true positives \(TP\), false positives \(FP\), true negatives \(TN\), =and false negatives \(FN\) based on the ground truth labels.

6. **Calculate Precision, Recall, and F1-score:** For each thr=eshold, calculate precision, recall, and F1-score.

7. **Find Optimal Threshold:** Choose the threshold that maxim=izes the F1-score or provides the desired balance between precision and rec=all.

8. **Analyze Results for Different Demographic Subsets** : This= can help you understand if the performance of the model is consistent acro=ss all races/ethnicities.

# # Code =Implementation \(Conceptual\)

import nu=mpy as npfrom sklearn.metrics import f1_score, precision_score, recall_scoredef calculate_f1_score(embeddings, labels, metric="euclidean", thresholds= = np.arange(0.0, 1.0, 0.01)): # Assuming you have the following: # - 'embeddings': A dictionary where keys are image filenames and value=s are the embedding vectors # - 'labels': A dictionary where keys are image filenames and values ar=e the person's ID (ground truth) # - 'metric': "euclidean" or "cosine" pairs = [] # list of pairs of embeddings pair_labels = [] # 1 if images are of same class, 0 if not # Creating positive pairs: num_positive_pairs_to_create = 5000 positive_pairs_created = 0 i=0 while positive_pairs_created < num_positive_pairs_to_create and i &l=t; len(embeddings): j = 0 while positive_pairs_created < num_positive_pairs_to_create and =j < len(embeddings): if labels[i] == labels[j]: pairs.append((embeddings[i], embeddings[j])) pair_labels.append(1) positive_pairs_created +=1 j+=1 i += 1 # Creating negative pairs: num_negative_pairs_to_create = 5000 negative_pairs_created = 0 i=0 while negative_pairs_created < num_negative_pairs_to_create and i &l=t; len(embeddings): j = 0 while negative_pairs_created < num_negative_pairs_to_create and =j < len(embeddings): if labels[i] != labels[j]: pairs.append((embeddings[i], embeddings[j])) pair_labels.append(0) negative_pairs_created +=1 j+=1 i += 1 # Define a function to calculate the distance/similarity based on the m=etric def calculate_similarity(emb1, emb2, metric): if metric == "euclidean": return np.linalg.norm(emb1 - emb2) elif metric == "cosine": dot_product = np.dot(emb1, emb2) norm_emb1 = np.linalg.norm(emb1) norm_emb2 = np.linalg.norm(emb2) return dot_product / (norm_emb1 * norm_emb2) else: raise ValueError("Unsupported metric") # Calculate scores scores = [calculate_similarity(pair[0], pair[1], metric) for pair in =pairs] # Find optimal threshold by maximizing F1-score best_threshold = None best_f1_score = -1 for threshold in thresholds: # Apply threshold and get predictions if metric == "euclidean": predictions = [1 if score <= threshold else 0] * len(sco=res) elif metric == "cosine": predictions = [1 if score >= threshold else 0] * len(sco=res) # Calculate F1-score, precision, and recall f1 = f1_score(pair_labels, predictions) precision = precision_score(pair_labels, predictions) recall = recall_score(pair_labels, predictions) if f1 > best_f1_score: best_f1_score = f1 best_threshold = threshold return best_threshold, best_f1_score# Example usage:# best_threshold, best_f1_score = calculate_f1_score(embeddings, labels, =metric="euclidean")# print(f"Best Threshold: {best_threshold}, Best F1-score: {best_f1_score}"=)