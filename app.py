import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from filelock import FileLock

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
APP_PIN = os.getenv("APP_PIN", "1234")

DATA_FILE = os.path.join(BASE_DIR, "data.json")
LOCK_FILE = os.path.join(BASE_DIR, "data.json.lock")

def get_data():
    """Reads data from the JSON file with locking to prevent concurrent access issues."""
    if not os.path.exists(DATA_FILE):
        default_data = {
            "children": [
                {"id": 1, "name": os.getenv("CHILD_1_NAME", "Child 1"), "balance": 0.0, "is_active": True, "history": []},
                {"id": 2, "name": os.getenv("CHILD_2_NAME", "Child 2"), "balance": 0.0, "is_active": False, "history": []},
                {"id": 3, "name": os.getenv("CHILD_3_NAME", "Child 3"), "balance": 0.0, "is_active": False, "history": []},
                {"id": 4, "name": os.getenv("CHILD_4_NAME", "Child 4"), "balance": 0.0, "is_active": False, "history": []}
            ]
        }
        save_data(default_data)
        return default_data

    lock = FileLock(LOCK_FILE, timeout=5)
    with lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_data(data):
    """Writes data to the JSON file with locking."""
    lock = FileLock(LOCK_FILE, timeout=5)
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def is_authenticated():
    """Checks if the user has a valid session PIN."""
    return session.get("authenticated") is True

@app.route("/")
def index():
    """Main dashboard route."""
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page and authentication logic."""
    if is_authenticated():
        return redirect(url_for("index"))
        
    if request.method == "POST":
        pin = request.form.get("pin")
        if pin == APP_PIN:
            session["authenticated"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid PIN")
        
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    """Logs the user out."""
    session.pop("authenticated", None)
    return redirect(url_for("login"))

@app.route("/api/data", methods=["GET"])
def api_get_data():
    """API endpoint to get the current state of children's accounts."""
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    data = get_data()
    return jsonify(data)

@app.route("/api/transaction", methods=["POST"])
def api_transaction():
    """API endpoint to add a transaction to a child's account."""
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    req_data = request.json
    child_id = req_data.get("child_id")
    amount = req_data.get("amount")
    description = req_data.get("description", "Transaction")
    
    if not child_id or amount is None:
        return jsonify({"error": "Missing parameters"}), 400
        
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400
        
    data = get_data()
    child_found = False
    
    for child in data["children"]:
        if child["id"] == int(child_id):
            child_found = True
            child["balance"] += amount
            
            transaction = {
                "id": str(uuid.uuid4()),
                "date": datetime.now().isoformat(),
                "amount": amount,
                "description": description,
                "balance_after": child["balance"]
            }
            # Add to history at the beginning
            child["history"].insert(0, transaction)
            # Keep only last 50 transactions
            child["history"] = child["history"][:50]
            break
            
    if not child_found:
        return jsonify({"error": "Child not found"}), 404
        
    save_data(data)
    return jsonify({"success": True, "message": "Transaction recorded"})

@app.route("/api/settings", methods=["POST"])
def api_settings():
    """API endpoint to update family settings (names and active slots)."""
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    req_data = request.json
    children_settings = req_data.get("children", [])
    
    data = get_data()
    
    for setting in children_settings:
        child_id = int(setting.get("id"))
        for child in data["children"]:
            if child["id"] == child_id:
                if "name" in setting:
                    child["name"] = setting["name"]
                if "is_active" in setting:
                    # Child 1 is always active
                    if child_id == 1:
                        child["is_active"] = True
                    else:
                        child["is_active"] = bool(setting["is_active"])
                break
                
    save_data(data)
    return jsonify({"success": True, "message": "Settings updated"})

@app.route("/api/reset_child", methods=["POST"])
def api_reset_child():
    """API endpoint to reset a child's balance and history."""
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    req_data = request.json
    child_id = req_data.get("child_id")
    
    if not child_id:
        return jsonify({"error": "Missing child_id"}), 400
        
    data = get_data()
    child_found = False
    
    for child in data["children"]:
        if child["id"] == int(child_id):
            child_found = True
            child["balance"] = 0.0
            child["history"] = []
            break
            
    if not child_found:
        return jsonify({"error": "Child not found"}), 404
        
    save_data(data)
    return jsonify({"success": True, "message": "Child data reset"})

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)