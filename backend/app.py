from flask import Flask, request, jsonify
from flask_cors import CORS
from checkers import CheckersGame

app = Flask(__name__)
CORS(app)

game = CheckersGame()

@app.route("/board", methods=["GET"])
def get_board():
    return jsonify({"board": game.board, "winner": game.winner})

@app.route("/move", methods=["POST"])
def make_move():
    data = request.get_json()
    from_pos = data.get("from")
    to_pos = data.get("to")

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

    return jsonify({
        "success": True,
        "message": f"{message}" + (f" | AI moved from {ai_move[0]} to {ai_move[1]}" if ai_move else ""),
        "board": game.board,
        "winner": game.winner
    })

@app.route("/reset", methods=["POST"])
def reset_game():
    global game
    game = CheckersGame()
    return jsonify({"message": "Game reset", "board": game.board, "winner": None})

if __name__ == "__main__":
    app.run(debug=True)
