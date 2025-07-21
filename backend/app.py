from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from checkers import CheckersGame
import os

# ─── Config ─────────────────────────────────────────────────────
MONGO_URI = "mongodb+srv://ggpatel1234567:hetpatel1209@moves.xr4yahn.mongodb.net/?retryWrites=true&w=majority&appName=moves"
DB_NAME = "checkers_db"
COLLECTION_NAME = "games"

# ─── App Init ────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─── Mongo Setup ─────────────────────────────────────────────────
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
games_collection = db[COLLECTION_NAME]

# ─── Helper: Clean old games ─────────────────────────────────────
def cleanup_old_games():
    cutoff = datetime.utcnow() - timedelta(hours=1)
    games_collection.delete_many({"last_updated": {"$lt": cutoff}})

# ─── Helper: Convert CheckersGame ↔ dict ─────────────────────────
def game_to_dict(game: CheckersGame):
    return {
        "board": game.board,
        "winner": game.winner,
        "last_updated": datetime.utcnow()
    }

def dict_to_game(data):
    game = CheckersGame()
    game.board = data["board"]
    game.winner = data["winner"]
    return game

# ─── Routes ──────────────────────────────────────────────────────

@app.route("/start", methods=["POST"])
def start_game():
    cleanup_old_games()
    game = CheckersGame()
    game_data = game_to_dict(game)
    result = games_collection.insert_one(game_data)
    return jsonify({
        "game_id": str(result.inserted_id),
        "board": game.board,
        "winner": game.winner
    })


@app.route("/board/<game_id>", methods=["GET"])
def get_board(game_id):
    cleanup_old_games()
    data = games_collection.find_one({"_id": ObjectId(game_id)})
    if not data:
        return jsonify({"error": "Game not found"}), 404

    game = dict_to_game(data)
    return jsonify({
        "board": game.board,
        "winner": game.winner
    })


@app.route("/move/<game_id>", methods=["POST"])
def make_move(game_id):
    data = games_collection.find_one({"_id": ObjectId(game_id)})
    if not data:
        return jsonify({"error": "Game not found"}), 404

    game = dict_to_game(data)
    move_data = request.get_json()
    from_pos = move_data.get("from")
    to_pos = move_data.get("to")

    if from_pos is None or to_pos is None:
        return jsonify({"message": "Missing move data"}), 400

    success, message = game.make_move(from_pos, to_pos)
    if not success:
        return jsonify({
            "success": False,
            "message": message,
            "board": game.board,
            "winner": game.winner
        })

    ai_move = game.ai_move_if_needed()
    message += f" | AI moved from {ai_move[0]} to {ai_move[1]}" if ai_move else ""

    # Save updated game
    games_collection.update_one(
        {"_id": ObjectId(game_id)},
        {"$set": game_to_dict(game)}
    )

    return jsonify({
        "success": True,
        "message": message,
        "board": game.board,
        "winner": game.winner
    })

@app.route("/ping")
def ping():
    try:
        games_collection.find_one()
        return "MongoDB Connected ✅"
    except Exception as e:
        return f"Connection Error ❌: {str(e)}"

@app.route("/reset/<game_id>", methods=["POST"])
def reset_game(game_id):
    game = CheckersGame()
    game_data = game_to_dict(game)

    result = games_collection.update_one(
        {"_id": ObjectId(game_id)},
        {"$set": game_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Game not found"}), 404

    return jsonify({
        "message": "Game reset",
        "board": game.board,
        "winner": None
    })


# ─── Run App ─────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
