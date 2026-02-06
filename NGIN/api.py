from flask import Flask, jsonify
from flask_cors import CORS
import sys, os

# Ensure repo root is on sys.path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

# Import NGIN classes; try package-relative first, fall back to top-level imports
try:
    from .SimulaeCampaignGenerator import NGIN
    from .NGIN_utils.ngin_utils import load_json_from_file
except Exception:
    from SimulaeCampaignGenerator import NGIN
    from NGIN_utils.ngin_utils import load_json_from_file

app = Flask(__name__)
CORS(app, resources={r"/generate_campaign": {"origins": ["http://127.0.0.1:3000", "http://localhost:3000", "http://localhost:5173"]}})

@app.route('/')
def index():
    return jsonify({"message": "NGIN Campaign Generator API is running."})

@app.route('/generate_campaign')
def generate_campaign():
    mission_struct = load_json_from_file("NGIN/NGIN_config/story_struct.json")
    ngin_settings = load_json_from_file("NGIN/NGIN_config/ngin_settings.json")

    ngin = NGIN(mission_struct, ngin_settings, is_console=False)
    data = ngin.state.toJSON()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
