import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import "animate.css";

const API_BASE = "https://checkers-game-backend-zwsi.onrender.com";

const App = () => {
  const [board, setBoard] = useState(null);
  const [message, setMessage] = useState("");
  const [selected, setSelected] = useState(null);
  const [winner, setWinner] = useState(null);

  const [moves, setMoves] = useState(() => {
    const saved = localStorage.getItem("moves");
    return saved ? JSON.parse(saved) : [];
  });

  const [lastMove, setLastMove] = useState(() => {
    const saved = localStorage.getItem("lastMove");
    return saved ? JSON.parse(saved) : null;
  });

  const [playerName, setPlayerName] = useState(() => {
    return localStorage.getItem("playerName") || "Human";
  });

  const [gameStarted, setGameStarted] = useState(() => {
    return localStorage.getItem("gameStarted") === "true";
  });

  const hasInitialized = useRef(false);

  // Persist state in localStorage
  useEffect(() => {
    localStorage.setItem("moves", JSON.stringify(moves));
  }, [moves]);

  useEffect(() => {
    localStorage.setItem("lastMove", JSON.stringify(lastMove));
  }, [lastMove]);

  useEffect(() => {
    localStorage.setItem("playerName", playerName);
  }, [playerName]);

  useEffect(() => {
    localStorage.setItem("gameStarted", gameStarted);
  }, [gameStarted]);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    const startNew = window.confirm("Do you want to start a new game?");
    if (startNew) {
      resetGame();
    } else {
      fetchBoard();
    }
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

  const formatMove = ([r1, c1], [r2, c2]) =>
    `${String.fromCharCode(65 + c1)}${r1 + 1} → ${String.fromCharCode(65 + c2)}${r2 + 1}`;

  const makeMove = async (start, end) => {
    try {
      const res = await axios.post(`${API_BASE}/move`, {
        from: start,
        to: end,
      });

      setBoard(res.data.board);
      setWinner(res.data.winner || null);
      setMessage(res.data.message || "");

      if (!res.data.success) return;

      const updatedMoves = [];

      const aiMoveMatch = res.data.message.match(
        /AI moved from \((\d), (\d)\) to \((\d), (\d)\)/
      );

      if (aiMoveMatch) {
        const from = [parseInt(aiMoveMatch[1]), parseInt(aiMoveMatch[2])];
        const to = [parseInt(aiMoveMatch[3]), parseInt(aiMoveMatch[4])];

        updatedMoves.push({
          player: "🧠 AI",
          move: formatMove(from, to),
        });

        setLastMove(to);
      } else {
        setLastMove(end);
      }

      updatedMoves.push({
        player: `🧑 ${playerName}`,
        move: formatMove(start, end),
      });

      setMoves((prev) => [...updatedMoves, ...prev]);
    } catch (err) {
      console.error(err);
      setMessage("Invalid move.");
    }
  };

  const handleCellClick = (row, col) => {
    if (winner) return;
    if (selected) {
      makeMove(selected, [row, col]);
      setSelected(null);
      if (!gameStarted) setGameStarted(true);
    } else {
      setSelected([row, col]);
    }
  };

  const resetGame = async () => {
    try {
      await axios.post(`${API_BASE}/reset`);

      // Clear localStorage and state
      localStorage.removeItem("moves");
      localStorage.removeItem("lastMove");
      localStorage.removeItem("playerName");
      localStorage.removeItem("gameStarted");

      setMoves([]);
      setLastMove(null);
      setPlayerName("Human");
      setGameStarted(false);

      fetchBoard(); // load new board
      setMessage("Game reset.");
    } catch (err) {
      console.error(err);
      setMessage("Failed to reset game.");
    }
  };

  const columnLabels = [...Array(8)].map((_, i) =>
    String.fromCharCode(65 + i)
  );

  return (
    <>
      <div className="min-h-screen bg-gray-900 text-white flex p-6">
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-bold mb-3 animate__animated animate__bounce">
            Checkers Game
          </h1>

          <div className="flex items-center gap-2 mb-2">
            <label className="text-sm">Your Name:</label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="px-2 py-1 rounded bg-gray-200 text-black text-sm disabled:opacity-50"
              disabled={gameStarted}
            />
          </div>

          <div className="text-sm text-gray-300 mb-3">
            ⚪️ = Normal Piece &nbsp;&nbsp; 🤍 = King
          </div>

          <button
            onClick={resetGame}
            className="bg-red-500 hover:bg-red-600 px-6 py-2 rounded mb-4"
          >
            🔁 Reset Game
          </button>

          {board ? (
            <div>
              <div className="flex ml-[20px] mb-1">
                <div className="w-[24px]"></div>
                {columnLabels.map((label, i) => (
                  <div
                    key={i}
                    className="w-[64px] h-[24px] text-center text-gray-300 text-sm"
                  >
                    {label}
                  </div>
                ))}
              </div>

              <div className="border-2 border-white">
                {board.map((row, rIdx) => (
                  <div key={rIdx} className="flex">
                    <div className="w-[24px] h-[64px] flex items-center justify-center text-gray-300 text-sm">
                      {rIdx + 1}
                    </div>
                    <div className="grid grid-cols-8">
                      {row.map((cell, cIdx) => {
                        const isSelected =
                          selected?.[0] === rIdx && selected?.[1] === cIdx;
                        const isLastMove =
                          lastMove?.[0] === rIdx && lastMove?.[1] === cIdx;

                        return (
                          <div
                            key={`${rIdx}-${cIdx}`}
                            className={`board-cell ${(rIdx + cIdx) % 2 === 0 ? "light" : "dark"
                              } ${isSelected ? "selected" : ""} ${isLastMove ? "last-move" : ""
                              }`}
                            onClick={() => handleCellClick(rIdx, cIdx)}
                          >
                            {cell !== "." ? cell : ""}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>Loading board...</p>
          )}
        </div>

        {/* Right Sidebar */}
        <div className="ml-10 w-80 bg-gray-800 rounded-xl p-5 shadow-lg max-h-screen overflow-y-auto">
          <p className="text-sm mb-3 text-gray-400">{message}</p>

          {winner && (
            <div className="mb-4 text-green-400 text-lg font-semibold">
              {winner === "draw" ? (
                "🤝 Game Over: It's a draw!"
              ) : winner === "🔴" ? (
                "🎉 Game Over! AI wins!"
              ) : (
                `🎉 Game Over! ${playerName} wins!`
              )}
            </div>
          )}

          <h2 className="text-xl font-bold mb-2">📜 Move History</h2>
          <div className="h-80 overflow-y-auto bg-gray-700 rounded p-3 space-y-2 text-sm">
            {moves.length === 0 ? (
              <p className="text-gray-400">No moves yet.</p>
            ) : (
              moves.map((m, idx) => (
                <div key={idx} className="border-b border-gray-600 pb-1">
                  <span className="font-bold">{m.player}</span>: {m.move}
                </div>
              ))
            )}
          </div>

          <div className="mt-6 bg-gray-700 rounded-lg p-4 text-sm leading-relaxed max-h-96 overflow-y-auto">
            <h2 className="text-lg font-bold mb-2">📘 Game Rules</h2>

            <p className="mb-2">
              🤍 = <strong>King</strong>, ⚪️ = <strong>Normal Piece</strong>
            </p>

            <p>
              <br />
              <strong>🎯 Objective</strong>
              <br />
              Capture all of your opponent’s pieces or block them so they have
              no legal moves.
            </p>

            <p className="mt-2">
              <br />
              <strong>🎮 Game Setup</strong>
              <br />
              • Played on an 8×8 board, only dark squares are used.
              <br />• Each player starts with 12 pieces on the first 3 rows of
              dark squares.
              <br />• Bottom-left square is a dark square.
            </p>

            <p className="mt-2">
              <br />
              <strong>👣 Basic Movement</strong>
              <br />
              • Pieces move diagonally forward by 1 square to an empty dark
              square.
            </p>

            <p className="mt-2">
              <br />
              <strong>✂️ Capturing (Jumping)</strong>
              <br />
              • Jump over an adjacent opponent's piece onto the empty square
              beyond.
              <br />• No pressure to jump if a capture is available.
              <br />• Multiple jumps are not allowed.
            </p>

            <p className="mt-2">
              <br />
              <strong>👑 Kinging</strong>
              <br />
              • Reach the opponent’s back row to become a 🤍 King.
              <br />• Kings can move & jump both forward and backward
              diagonally.
            </p>

            <p className="mt-2">
              <br />
              <strong>🛑 Ending the Game</strong>
              <br />
              • One player captures all opponent’s pieces or blocks all legal
              moves.
              <br />• A draw can be declared by repetition 5 times both with same moves.
            </p>

            <p className="mt-2">
              <br />
              <strong>📌 Key Rules Summary</strong>
              <br />
              • Normal pieces move forward only
              <br />• 🤍 Kings move in both directions
              <br />• Game ends by win, block, or draw
            </p>
          </div>
        </div>
      </div>

      <footer className="mt-6 mb-3 text-center text-l text-gray-400 w-full">
        Made by Het Patel
      </footer>
    </>
  );
};

export default App;
