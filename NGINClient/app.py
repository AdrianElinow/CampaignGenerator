from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NGIN Campaign Generator</title>
</head>
<body>
    <h1>NGIN Campaign Client</h1>
    <button onclick="generateCampaign()">Generate Campaign</button>
    <pre id="output"></pre>

    <script>
        async function generateCampaign() {
            const response = await fetch('http://localhost:5000/generate_campaign');
            const data = await response.json();
            document.getElementById('output').textContent = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(port=3000, debug=True)