from flask import Flask, jsonify

app = Flask(__name__)

ITEMS = [
    {"id": 1, "name": "Item Satu"},
    {"id": 2, "name": "Item Dua"},
]  # BUG: Item Tiga dihapus — sengaja untuk simulasi CI gagal


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(ITEMS), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rute tidak ditemukan"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
