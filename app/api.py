from flask import Flask, jsonify
import os
from dotenv import load_dotenv

# Load env file based on ENV var, fallback to .env.staging for local dev
env_name = os.environ.get("ENV", "staging")
env_file = f".env.{env_name}" if env_name in ("staging", "prod", "production") else ".env.example"
load_dotenv(dotenv_path=env_file, override=False)  # override=False: real env vars take priority

app = Flask(__name__)

ITEMS = [
    {"id": 1, "name": "Item Satu"},
    {"id": 2, "name": "Item Dua"},
    {"id": 3, "name": "Item Tiga"},
]


def _build_item(item: dict) -> dict:
    """Tambahkan field fitur baru jika FEATURE_NEW_CHECKOUT aktif."""
    result = item.copy()
    if os.environ.get("FEATURE_NEW_CHECKOUT", "false").lower() == "true":
        result["new_feature"] = True
    return result


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify([_build_item(i) for i in ITEMS]), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rute tidak ditemukan"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    env = os.environ.get("ENV", "development")
    print(f"[INFO] Menjalankan server di lingkungan: {env}, port: {port}")
    print(f"[INFO] FEATURE_NEW_CHECKOUT: {os.environ.get('FEATURE_NEW_CHECKOUT', 'false')}")
    app.run(host="0.0.0.0", port=port, debug=(env != "production"))
