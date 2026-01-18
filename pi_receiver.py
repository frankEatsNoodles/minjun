from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)


# Directory to store user vaults
data_dir = "received_passwords"
os.makedirs(data_dir, exist_ok=True)

def get_user_file(username):
    # Sanitize username for filename
    safe_user = ''.join(c for c in username if c.isalnum() or c in ('-_')).lower()
    return os.path.join(data_dir, f"user_{safe_user}.json")

@app.route('/store', methods=['POST'])
def store_password():
    try:
        data = request.get_json(force=True)
        username = data.get('username', '').strip().lower()
        service = data.get('service', '').strip().lower()
        if not username or not service:
            return jsonify({"status": "error", "message": "Missing username or service"}), 400
        user_file = get_user_file(service)
        # Load or create user vault
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                vault = json.load(f)
        else:
            vault = {}
        # Store/overwrite service credentials
        vault[service] = data
        with open(user_file, 'w') as f:
            json.dump(vault, f, indent=2)
        return jsonify({"status": "success", "user": username, "service": service}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/retrieve', methods=['GET'])
def retrieve_password():
    service = request.args.get('service', '').strip().lower()
    if not service:
        return jsonify({"status": "error", "message": "Missing service parameter"}), 400

    results = []

    for filename in os.listdir(data_dir):
        if not filename.endswith(".json"):
            continue

        user_file = os.path.join(data_dir, filename)
        with open(user_file, 'r') as f:
            vault = json.load(f)

        if service in vault:
            username = filename.replace("user_", "").replace(".json", "")
            results.append({"user": username,"service": service,"data": vault[service]})

    if not results:
        return jsonify({"status": "error", "message": f"No credentials found for service {service}"}), 404

    return jsonify({"status": "success", "results": results }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
