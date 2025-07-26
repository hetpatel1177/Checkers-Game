from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient, ASCENDING
from datetime import datetime
import uuid
from checkers import CheckersGame

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# MongoDB setup
client = MongoClient("mongodb+srv://ggpatel1234567:hetpatel1209@moves.xr4yahn.mongodb.net/?retryWrites=true&w=majority&appName=moves")
try:
    print("✅ Checking MongoDB connection...")
    client.admin.command('ping')
    print("✅ MongoDB connected.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

db = client["checkers_db"]
games = db["games"]

# ✅ Ensure TTL index exists (runs once at startup)
games.create_index([("created_at", ASCENDING)], expireAfterSeconds=3600)

def serialize_game(game: CheckersGame):
    safe_history = {
        str(k): v for k, v in game.position_history.items()
    }
    return {
        "board": game.board,
        "winner": game.winner,
        "turn": game.turn,
        "position_history": safe_history
    }

def deserialize_game(data):
    game = CheckersGame()
    game.board = data["board"]
    game.winner = data.get("winner")
    game.turn = data["turn"]
    game.position_history = {
        k: v for k, v in data.get("position_history", {}).items()
    }
    return game

@app.route("/create_game", methods=["POST"])
def create_game():
    game = CheckersGame()
    game_id = str(uuid.uuid4())
    games.insert_one({
        "_id": game_id,
        **serialize_game(game),
        "created_at": datetime.utcnow()  # ✅ timestamp for TTL
    })
    return jsonify({"game_id": game_id, "board": game.board})

@app.route("/board/<game_id>", methods=["GET"])
def get_board(game_id):
    doc = games.find_one({"_id": game_id})
    if not doc:
        return jsonify({"error": "Game not found"}), 404

    return jsonify({
        "board": doc["board"],
        "winner": doc.get("winner")
    })

@app.route("/move/<game_id>", methods=["POST"])
def move(game_id):
    try:
        doc = games.find_one({"_id": game_id})
        if not doc:
            return jsonify({"success": False, "message": "Game not found"}), 404

        game = deserialize_game(doc)
        data = request.get_json()
        start = data.get("from")
        end = data.get("to")

        print("⬅️ Move requested:", start, "to", end)
        print("🔄 Current turn:", game.turn)

        valid_moves = game.get_valid_moves(game.turn)
        print("✅ Valid moves:", valid_moves)

        success, msg = game.make_move(start, end)

        ai_move = None
        if success and game.turn == '🔴':
            ai_move = game.ai_move_if_needed()
            if ai_move:
                msg += f" | AI moved from {ai_move[0]} to {ai_move[1]}"

        games.update_one(
            {"_id": game_id},
            {"$set": {
                **serialize_game(game)
            }}
        )

        return jsonify({
            "success": success,
            "message": msg,
            "board": game.board,
            "winner": game.winner
        })

    except Exception as e:
        print("❌ ERROR in /move:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/reset/<game_id>", methods=["POST"])
def reset_game(game_id):
    game = CheckersGame()
    games.update_one(
        {"_id": game_id},
        {"$set": {
            **serialize_game(game),
            "created_at": datetime.utcnow()  # ✅ reset TTL
        }},
        upsert=True
    )
    return jsonify({"board": game.board, "message": "Game reset."})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
