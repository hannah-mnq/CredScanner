# CredScanner – Fake News Detection using SBERT and RAG-style Similarity

CredScanner is an AI-powered fake news detection system that analyzes user-submitted claims or URLs and determines whether they are likely to be real or fake. It combines traditional machine learning classification with retrieval-augmented techniques by semantically comparing the input with live web content.

---

## Features

- Supports both raw text claims and article URLs as input
- Uses Sentence-BERT (SBERT) to convert text into semantic embeddings
- Classifies input using a trained XGBoost model
- Performs real-time Google search to retrieve related articles
- Applies cosine similarity scoring between input and retrieved content
- Returns a final verdict based on both machine learning and similarity evidence

---

## Tech Stack

| Component           | Tool/Library             |
|--------------------|--------------------------|
| Backend Framework  | Flask                    |
| Embedding Model    | Sentence-BERT (SBERT)    |
| Classifier         | XGBoost                  |
| Web Scraping       | newspaper3k              |
| Web Search         | googlesearch-python      |
| Similarity Metric  | Cosine similarity (SBERT)|
| API Design         | Flask RESTful API        |

---
## How It Works

1. **Input Handling**  
   - If the input is a URL, the system extracts the article content using `newspaper3k`.
   - If it's plain text, it is used directly.

2. **Machine Learning Prediction**  
   - The text is converted into embeddings using SBERT.
   - A trained XGBoost classifier predicts the label ("REAL" or "FAKE").

3. **Semantic Evidence Retrieval**  
   - The input is used as a query to perform a Google search.
   - Top articles are scraped and encoded using SBERT.
   - Cosine similarity is computed between the input and each article.

4. **Final Verdict**  
   - If the highest similarity score exceeds a defined threshold (e.g., 0.8), the claim is considered supported.
   - Otherwise, it is marked as unverified or potentially fake.

---
