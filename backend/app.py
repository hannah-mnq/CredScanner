from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
import re
import os
 
app = Flask(__name__)
CORS(app)

from newspaper import Article

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


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))

sbert_model = joblib.load(os.path.join(base_dir, 'sbert_model.joblib'))
classifier_model = joblib.load(os.path.join(base_dir, 'classifier_model.joblib'))
label_encoder = joblib.load(os.path.join(base_dir, 'label_encoder.joblib'))


@app.route('/')
def home():
    return 'credscanner backend is running!'


@app.route('/predict', methods = ['POST'])
def predict():
    try:
        data = request.get_json()
        input_text = data.get('text', '').strip()
        if not input_text:
            return jsonify({'error': 'No text provided'}), 400
        if is_url(input_text):
            extracted = extract_text_from_url(input_text)
            if not extracted:
                return jsonify({'error': 'Failed to extract text from URL'}), 400
            input_text = extracted

        # encoding with sbert model
        embedding = sbert_model.encode([input_text])
        # classify
        prediction = classifier_model.predict(embedding)
        # decode label 
        predicted_label = label_encoder.inverse_transform(prediction)[0]

        return jsonify({
            'input': data.get('text'),
            'extracted': input_text if is_url(data.get('text')) else None,
            'prediction' : predicted_label
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)