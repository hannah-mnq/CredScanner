from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
import re
import os
from newspaper import Article
from googlesearch import search
from sentence_transformers import util

app = Flask(__name__)
CORS(app)

def is_url(text):
    return re.match(r'^https?://', text.strip()) is not None

def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title + ". " + article.text[:300]
    except Exception as e:
        print(f"Error extracting text from URL: {e}")
        return None

def search_and_scrape(query, top_k=5):
    urls = list(search(query, num_results=top_k))
    articles = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            articles.append((url, article.text[:500]))
        except:
            continue
    return articles

def get_rag_verdict(text, sbert_model, threshold=0.8):
    docs = search_and_scrape(text)
    if not docs:
        return "No relevant sources found online.", 0.0, None

    query_emb = sbert_model.encode([text], convert_to_tensor=True)
    doc_texts = [d[1] for d in docs]
    doc_embs = sbert_model.encode(doc_texts, convert_to_tensor=True)
    scores = util.cos_sim(query_emb, doc_embs)[0]

    top_idx = int(scores.argmax())
    top_score = float(scores[top_idx])
    top_url = docs[top_idx][0]

    if top_score >= threshold:
        verdict = f"🟢 Strong match (score: {top_score:.2f}) — Source: {top_url}"
    else:
        verdict = f"🔴 No strong match (score: {top_score:.2f}) — Closest: {top_url}"

    return verdict, top_score, top_url

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sbert_model = joblib.load(os.path.join(base_dir, 'sbert_model.joblib'))
classifier_model = joblib.load(os.path.join(base_dir, 'classifier_model.joblib'))
label_encoder = joblib.load(os.path.join(base_dir, 'label_encoder.joblib'))

@app.route('/')
def home():
    return 'credscanner backend is running!'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_text = data.get('text', '').strip()
        if not input_text:
            return jsonify({'error': 'No text provided'}), 400

        extracted = None
        if is_url(input_text):
            extracted = extract_text_from_url(input_text)
            if not extracted:
                return jsonify({'error': 'Failed to extract text from URL'}), 400
            input_text = extracted

        embedding = sbert_model.encode([input_text])
        prediction = classifier_model.predict(embedding)
        predicted_label = label_encoder.inverse_transform(prediction)[0]

        rag_verdict, top_score, top_url = get_rag_verdict(input_text, sbert_model)
        threshold = 0.8

        if top_score >= threshold:
            final_verdict = "REAL"
            explanation = f"✅ This claim is supported by strong online evidence (similarity: {top_score:.2f})."
        else:
            final_verdict = "FAKE"
            explanation = f"❌ No strong match found online (similarity: {top_score:.2f}). This claim appears unverified."

        return jsonify({
            'input': data.get('text'),
            'extracted': extracted,
            'ml_prediction': predicted_label,
            'similarity_score': round(top_score, 2),
            'matched_url': top_url,
            'final_verdict': final_verdict,
            'explanation': explanation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
