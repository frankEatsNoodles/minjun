from flask import Flask, request, jsonify, send_file
import os
import json
from datetime import datetime

app = Flask(__name__)

# Directory to store received password files
data_dir = "received_passwords"
os.makedirs(data_dir, exist_ok=True)

@app.route('/store', methods=['POST'])
def store_password():
    try:
        data = request.get_json(force=True)
        # Save each entry as a separate file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{data.get('service','unknown')}_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "success", "file": filename}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# New endpoint to retrieve credentials by service name
@app.route('/retrieve', methods=['GET'])
def retrieve_password():
    service = request.args.get('service', '').lower()
    if not service:
        return jsonify({"status": "error", "message": "Missing service parameter"}), 400
    # Find all files for the service
    files = [f for f in os.listdir(data_dir) if f.startswith(service + '_') and f.endswith('.json')]
    if not files:
        return jsonify({"status": "error", "message": f"No credentials found for {service}"}), 404
    # Sort files by timestamp (latest last)
    files.sort()
    # Optionally, return all or just the latest
    latest_file = files[-1]
    filepath = os.path.join(data_dir, latest_file)
    with open(filepath, 'r') as f:
        data = json.load(f)
    return jsonify({"status": "success", "service": service, "data": data, "file": latest_file}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
