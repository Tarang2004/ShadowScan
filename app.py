from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS  # ✅ Added CORS support
import scanner  # Imports our refactored scanner code
import os
import datetime

app = Flask(__name__)
CORS(app)  


@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({'error': 'No URLs provided'}), 400
        
    urls_string = data['urls']
    results = scanner.run_scan(urls_string)
    
    return jsonify(results)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Serves the generated PDF report for download."""
   
    return send_from_directory(directory='.', path=filename, as_attachment=True)

def find_keywords(text, keywords):
    """Finds keywords in the given text."""
    found = []
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
    if found:
        print(f"[+] Found keywords: {', '.join(found)}")
    return found

if __name__ == '__main__':
    # Note: Do not run with debug=True in a production environment
    app.run(host='127.0.0.1', port=5000, debug=True)
