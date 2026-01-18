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
        user_file = get_user_file(username)
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
    username = request.args.get('username', '').strip().lower()
    service = request.args.get('service', '').strip().lower()
    if not username or not service:
        return jsonify({"status": "error", "message": "Missing username or service parameter"}), 400
    user_file = get_user_file(username)
    if not os.path.exists(user_file):
        return jsonify({"status": "error", "message": f"No credentials found for user {username}"}), 404
    with open(user_file, 'r') as f:
        vault = json.load(f)
    if service not in vault:
        return jsonify({"status": "error", "message": f"No credentials found for service {service}"}), 404
    return jsonify({"status": "success", "user": username, "service": service, "data": vault[service]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
