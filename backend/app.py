from datetime import datetime, timedelta
from bson import ObjectId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os

from checkers import CheckersGame

# ───────────────────────── Configuration ─────────────────────── #

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://ggpatel1234567:hetpatel1209@moves.xr4yahn.mongodb.net/?retryWrites=true&w=majority&appName=moves",
)
DB_NAME = "checkers_db"
COLLECTION_NAME = "games"

# ─────────────────────── Flask & Mongo setup ─────────────────── #

app = Flask(__name__)
CORS(app)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
games_collection = db[COLLECTION_NAME]

# ─────────────────────── Helper functions ────────────────────── #


def cleanup_old_games(hours: int = 12) -> None:
    """Delete games not touched in the last `hours` hours."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    games_collection.delete_many({"last_updated": {"$lt": cutoff}})


def game_to_dict(game: CheckersGame) -> dict:
    return {
        "board": game.board,
        "winner": game.winner,
        "last_updated": datetime.utcnow(),
    }


def dict_to_game(data: dict) -> CheckersGame:
    game = CheckersGame()
    game.board = data["board"]
    game.winner = data["winner"]
    return game


def valid_object_id(oid: str) -> bool:
    try:
        ObjectId(oid)
        return True
    except Exception:
        return False


# ───────────────────────────── Routes ────────────────────────── #

@app.route("/start", methods=["POST"])
def start_game():
    cleanup_old_games()
    game = CheckersGame()
    result = games_collection.insert_one(game_to_dict(game))
    gid = str(result.inserted_id)
    return jsonify({"game_id": gid, "board": game.board, "winner": game.winner})


@app.route("/board/<game_id>", methods=["GET"])
def get_board(game_id):
    if not valid_object_id(game_id):
        return jsonify({"error": "Invalid game ID"}), 400

    data = games_collection.find_one({"_id": ObjectId(game_id)})
    if not data:
        return jsonify({"error": "Game not found"}), 404

    game = dict_to_game(data)
    return jsonify({"board": game.board, "winner": game.winner})


@app.route("/move/<game_id>", methods=["POST"])
def make_move(game_id):
    if not valid_object_id(game_id):
        return jsonify({"error": "Invalid game ID"}), 400

    data = games_collection.find_one({"_id": ObjectId(game_id)})
    if not data:
        return jsonify({"error": "Game not found"}), 404

    game = dict_to_game(data)
    payload = request.get_json(force=True)
    from_pos = payload.get("from")
    to_pos = payload.get("to")

    if from_pos is None or to_pos is None:
        return jsonify({"success": False, "message": "Missing move data"}), 400

    success, msg = game.make_move(tuple(from_pos), tuple(to_pos))
    if not success:
        return jsonify(
            {"success": False, "message": msg, "board": game.board, "winner": game.winner}
        )

    ai_move = game.ai_move_if_needed()
    if ai_move:
        msg += f" | AI moved from {ai_move[0]} to {ai_move[1]}"

    games_collection.update_one(
        {"_id": ObjectId(game_id)}, {"$set": game_to_dict(game)}
    )

    return jsonify(
        {"success": True, "message": msg, "board": game.board, "winner": game.winner}
    )


@app.route("/reset/<game_id>", methods=["POST"])
def reset_game(game_id):
    if not valid_object_id(game_id):
        return jsonify({"error": "Invalid game ID"}), 400

    game = CheckersGame()
    result = games_collection.update_one(
        {"_id": ObjectId(game_id)}, {"$set": game_to_dict(game)}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Game not found"}), 404

    return jsonify({"message": "Game reset", "board": game.board, "winner": None})


@app.route("/ping")
def ping():
    """Quick health‑check endpoint."""
    try:
        games_collection.find_one()
        return "MongoDB Connected ✅"
    except Exception as e:
        return f"Connection Error ❌: {str(e)}", 500


# ─────────────────────────── Run local ───────────────────────── #

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
