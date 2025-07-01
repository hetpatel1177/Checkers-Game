import React, { useEffect, useState } from "react";
import axios from "axios";
import 'animate.css';
const API_BASE = "http://127.0.0.1:5000"; // Flask backend URL

const App = () => {
  const [board, setBoard] = useState(null);
  const [message, setMessage] = useState("");
  const [selected, setSelected] = useState(null);
  const [winner, setWinner] = useState(null);

  useEffect(() => {
    fetchBoard();
  }, []);

  const fetchBoard = async () => {
    try {
      const res = await axios.get(`${API_BASE}/board`);
      setBoard(res.data.board);
      setWinner(res.data.winner || null);
    } catch (err) {
      console.error(err);
      setMessage("Failed to fetch board.");
    }
  };

  const handleCellClick = (row, col) => {
    if (winner) return;
    if (selected) {
      makeMove(selected, [row, col]);
      setSelected(null);
    } else {
      setSelected([row, col]);
    }
  };

  const makeMove = async (start, end) => {
    try {
      const res = await axios.post(`${API_BASE}/move`, {
        from: start,
        to: end,
      });
      setBoard(res.data.board);
      setMessage(res.data.message || "Move made.");
      setWinner(res.data.winner || null);
    } catch (err) {
      console.error(err);
      setMessage("Invalid move.");
    }
  };

  const resetGame = async () => {
    try {
      await axios.post(`${API_BASE}/reset`);
      fetchBoard();
      setMessage("Game reset.");
      setWinner(null);
    } catch (err) {
      console.error(err);
      setMessage("Failed to reset game.");
    }
  };

  return (
    <div className="flex p-4 text-white min-h-screen">
      <div className="flex-col max-w-3xl mx-auto">
      <h1 className="het text-4xl font-extrabold mb-4 animate__bounce">Checkers Game</h1>

      <button
        onClick={resetGame}
        className="bg-black text-white text-s px-5 py-1 rounded mb-6"
      >
        Reset Game
      </button>
      
        {board ? (
          <div className="board">
            {board.map((row, rIdx) => (
              <div key={rIdx} className="board-row">
                {row.map((cell, cIdx) => (
                  <div
                    key={`${rIdx}-${cIdx}`}
                    className={`board-cell ${(rIdx + cIdx) % 2 === 0 ? "light" : "dark"}
                      ${selected?.[0] === rIdx && selected?.[1] === cIdx ? "selected" : ""}`}
                    onClick={() => handleCellClick(rIdx, cIdx)}
                  >
                    {cell !== "." ? cell : ""}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <p>Loading board...</p>
        )}
      </div>
      <div className="flex-col w-80 mx-10 p-4 bg-gray-800 rounded-lg">
        <p className="mt-4 text-red-500">{message}
          
        </p>

        {winner && (
          <div className="mt-4 text-green-400 text-xl font-bold">
            {winner === "draw"
              ? "🤝 Game Over: It's a draw!"
              : `🎉 Game Over! ${winner.toUpperCase()} wins!`}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
