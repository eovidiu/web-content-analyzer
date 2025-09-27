#!/usr/bin/env python3
"""
Web Server for Web Content Analyzer
Provides HTTP API for analyzing websites
"""

import os
import sys
import json
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_content_analyzer.simple_analyzer import SimpleWebContentAnalyzer
from web_content_analyzer.config import Config

app = Flask(__name__)

# HTML Template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Content Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .result { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007cba; }
        .error { border-left-color: #dc3545; }
        .success { border-left-color: #28a745; }
        input[type="url"] { width: 70%; padding: 10px; margin: 10px 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a8b; }
        .keywords { list-style: none; padding: 0; }
        .keywords li { background: #e3f2fd; padding: 5px 10px; margin: 2px 0; border-radius: 3px; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>🔍 Web Content Analyzer</h1>
    <p>Extract the top 10 keywords from any website using AI analysis</p>

    <div class="container">
        <form id="analyzeForm">
            <input type="url" id="urlInput" placeholder="https://example.com" required>
            <button type="submit">Analyze Website</button>
        </form>
    </div>

    <div id="results"></div>

    <script>
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('urlInput').value;
            const resultsDiv = document.getElementById('results');

            resultsDiv.innerHTML = '<div class="result"><div class="loading">🔄 Analyzing website...</div></div>';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });

                const result = await response.json();

                if (result.status === 'success') {
                    const keywords = result.keywords.map((k, i) => `<li>${i+1}. ${k}</li>`).join('');
                    resultsDiv.innerHTML = `
                        <div class="result success">
                            <h3>✅ ${result.url}</h3>
                            <p><strong>Processing time:</strong> ${result.processing_time.toFixed(2)}s</p>
                            <h4>Top 10 Keywords:</h4>
                            <ul class="keywords">${keywords}</ul>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ Analysis Failed</h3>
                            <p><strong>URL:</strong> ${result.url}</p>
                            <p><strong>Error:</strong> ${result.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="result error">
                        <h3>❌ Request Failed</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "service": "web-content-analyzer"})

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """API endpoint to analyze a single URL"""
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400

        url = data['url']

        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return jsonify({"error": "URL must start with http:// or https://"}), 400

        # Initialize analyzer
        config = Config()
        analyzer = SimpleWebContentAnalyzer(config)

        # Analyze the URL
        result = analyzer.analyze_url(url)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch', methods=['POST'])
def analyze_batch():
    """API endpoint to analyze multiple URLs"""
    try:
        data = request.get_json()

        if not data or 'urls' not in data:
            return jsonify({"error": "URLs array is required"}), 400

        urls = data['urls']

        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({"error": "URLs must be a non-empty array"}), 400

        if len(urls) > 10:
            return jsonify({"error": "Maximum 10 URLs allowed per batch"}), 400

        # Initialize analyzer
        config = Config()
        analyzer = SimpleWebContentAnalyzer(config)

        # Analyze the URLs
        results = analyzer.analyze_batch(urls)

        return jsonify({
            "results": results,
            "summary": {
                "total": len(results),
                "successful": sum(1 for r in results if r['status'] == 'success'),
                "failed": sum(1 for r in results if r['status'] == 'failed')
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    print(f"🚀 Starting Web Content Analyzer server on port {port}")
    print(f"🌐 Web interface: http://localhost:{port}")
    print(f"🔧 API endpoint: http://localhost:{port}/api/analyze")

    app.run(host='0.0.0.0', port=port, debug=debug)