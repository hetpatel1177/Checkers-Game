import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import "animate.css";

const API_BASE = "https://checkers-game-backend-zwsi.onrender.com";

const App = () => {
  /* ─────────── Core game state ─────────── */
  const [gameId, setGameId]   = useState(() => localStorage.getItem("gameId"));
  const [board,  setBoard]    = useState(null);
  const [winner, setWinner]   = useState(null);
  const [message, setMessage] = useState("");

  /* selection / UX */
  const [selected,   setSelected]   = useState(null);
  const [moves,      setMoves]      = useState(() =>
    JSON.parse(localStorage.getItem("moves") || "[]")
  );
  const [lastMove,   setLastMove]   = useState(() =>
    JSON.parse(localStorage.getItem("lastMove") || "null")
  );

  /* meta */
  const [playerName, setPlayerName] = useState(
    () => localStorage.getItem("playerName") || "Human"
  );
  const [gameStarted, setGameStarted] = useState(
    () => localStorage.getItem("gameStarted") === "true"
  );

  const hasInit = useRef(false);

  /* ─────────── Persist in localStorage ─────────── */
  useEffect(() => { localStorage.setItem("gameId",     gameId     || ""); }, [gameId]);
  useEffect(() => { localStorage.setItem("moves",      JSON.stringify(moves)); }, [moves]);
  useEffect(() => { localStorage.setItem("lastMove",   JSON.stringify(lastMove)); }, [lastMove]);
  useEffect(() => { localStorage.setItem("playerName", playerName); }, [playerName]);
  useEffect(() => { localStorage.setItem("gameStarted", String(gameStarted)); }, [gameStarted]);

  /* ─────────── First load / resume ─────────── */
  useEffect(() => {
    if (hasInit.current) return;
    hasInit.current = true;

    (async () => {
      if (gameId) {
        const keep = window.confirm("Continue your previous game?\n\nOK = continue • Cancel = new");
        keep ? fetchBoard() : startNew();
      } else {
        startNew();
      }
    })();
  }, []); // eslint-disable-line

  /* ─────────── Backend helpers ─────────── */
  const startNew = async () => {
    try {
      const { data } = await axios.post(`${API_BASE}/start`);
      setGameId(data.game_id);
      setBoard(data.board);
      setWinner(data.winner);
      setMoves([]); setLastMove(null);
      setGameStarted(false);
      setMessage("New game created.");
    } catch (err) {
      console.error(err);
      setMessage("Failed to start a new game.");
    }
  };

  const fetchBoard = async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/board/${gameId}`);
      setBoard(data.board); setWinner(data.winner || null);
    } catch (err) {
      console.error(err);
      setMessage("Could not fetch board, starting a new game.");
      startNew();
    }
  };

  const makeMove = async (start, end) => {
    if (winner) return;
    try {
      const { data } = await axios.post(`${API_BASE}/move/${gameId}`, { from: start, to: end });

      setBoard(data.board);
      setWinner(data.winner || null);
      setMessage(data.message || "");

      if (!data.success) return;

      const history = [];
      const ai = data.message.match(/AI moved from \((\d), (\d)\) to \((\d), (\d)\)/);
      if (ai) {
        const from = [Number(ai[1]), Number(ai[2])];
        const to   = [Number(ai[3]), Number(ai[4])];
        history.push({ player: "🧠 AI", move: formatMove(from, to) });
        setLastMove(to);
      } else {
        setLastMove(end);
      }

      history.push({ player: `🧑 ${playerName}`, move: formatMove(start, end) });
      setMoves((prev) => [...history, ...prev]);
    } catch (err) {
      console.error(err);
      setMessage("Invalid move.");
    }
  };

  const resetGame = async () => {
    try {
      await axios.post(`${API_BASE}/reset/${gameId}`);
      setMoves([]); setLastMove(null); setPlayerName("Human"); setGameStarted(false);
      await fetchBoard();
      setMessage("Game reset.");
    } catch (err) {
      console.error(err);
      setMessage("Reset failed.");
    }
  };

  /* ─────────── Helpers ─────────── */
  const handleClick = (r, c) => {
    if (winner) return;
    if (selected) {
      makeMove(selected, [r, c]);
      setSelected(null);
      if (!gameStarted) setGameStarted(true);
    } else {
      setSelected([r, c]);
    }
  };

  const formatMove = ([r1, c1], [r2, c2]) =>
    `${String.fromCharCode(65 + c1)}${r1 + 1} → ${String.fromCharCode(65 + c2)}${r2 + 1}`;

  const columnLabels = [...Array(8)].map((_, i) => String.fromCharCode(65 + i));

  /* ─────────── UI ─────────── */
  return (
    <>
      <div className="min-h-screen bg-gray-900 text-white flex p-6">
        {/* Board column */}
        <div className="flex flex-col items-center">
          <h1 className="text-4xl font-bold mb-3 animate__animated animate__bounce">
            Checkers Game
          </h1>

          {/* name input */}
          <div className="flex items-center gap-2 mb-2">
            <label className="text-sm">Your Name:</label>
            <input
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              disabled={gameStarted}
              className="px-2 py-1 rounded bg-gray-200 text-black text-sm disabled:opacity-50"
            />
          </div>

          <div className="text-sm text-gray-300 mb-3">
            ⚪️ = Man &nbsp;&nbsp; 🤍 = King
          </div>

          {/* controls */}
          <div className="flex gap-3 mb-4">
            <button onClick={resetGame} className="bg-red-500 hover:bg-red-600 px-6 py-2 rounded">
              🔁 Reset
            </button>
            <button onClick={startNew}  className="bg-blue-500 hover:bg-blue-600 px-6 py-2 rounded">
              ➕ New
            </button>
          </div>

          {/* board */}
          {board ? (
            <>
              {/* column labels */}
              <div className="flex ml-[20px] mb-1">
                <div className="w-[24px]" />
                {columnLabels.map((l) => (
                  <div key={l} className="w-[64px] h-[24px] text-center text-gray-300 text-sm">{l}</div>
                ))}
              </div>

              <div className="border-2 border-white">
                {board.map((row, rIdx) => (
                  <div key={rIdx} className="flex">
                    {/* row label */}
                    <div className="w-[24px] h-[64px] flex items-center justify-center text-gray-300 text-sm">
                      {rIdx + 1}
                    </div>
                    <div className="grid grid-cols-8">
                      {row.map((cell, cIdx) => {
                        const sel   = selected?.[0] === rIdx && selected?.[1] === cIdx;
                        const recent= lastMove?.[0] === rIdx && lastMove?.[1] === cIdx;
                        return (
                          <div
                            key={`${rIdx}-${cIdx}`}
                            onClick={() => handleClick(rIdx, cIdx)}
                            className={`board-cell ${(rIdx + cIdx) % 2 ? "dark" : "light"}
                                        ${sel ? "selected" : ""} ${recent ? "last-move" : ""}`}
                          >
                            {cell !== "." && cell}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p>Loading board…</p>
          )}
        </div>

        {/* Sidebar */}
        <div className="ml-10 w-80 bg-gray-800 rounded-xl p-5 shadow-lg max-h-screen overflow-y-auto">
          <p className="text-sm mb-3 text-gray-400">{message}</p>

          {winner && (
            <div className="mb-4 text-green-400 text-lg font-semibold">
              {winner === "draw" ? "🤝 Draw!" : winner === "🔴" ? "🎉 AI wins!" : `🎉 ${playerName} wins!`}
            </div>
          )}

          <h2 className="text-xl font-bold mb-2">📜 Moves</h2>
          <div className="h-80 overflow-y-auto bg-gray-700 rounded p-3 space-y-2 text-sm">
            {moves.length ? (
              moves.map((m, i) => (
                <div key={i} className="border-b border-gray-600 pb-1">
                  <span className="font-bold">{m.player}</span>: {m.move}
                </div>
              ))
            ) : (
              <p className="text-gray-400">No moves yet.</p>
            )}
          </div>

          {/* Rules (trimmed for brevity) */}
          <div className="mt-6 bg-gray-700 rounded-lg p-4 text-sm leading-relaxed max-h-96 overflow-y-auto">
            <h2 className="text-lg font-bold mb-2">📘 Rules</h2>
            <p className="mb-2">🤍 = King, ⚪️ = Man</p>
            {/* … keep your existing rules text … */}
          </div>
        </div>
      </div>

      <footer className="mt-6 mb-3 text-center text-gray-400 w-full">
        Made by Het Patel
      </footer>
    </>
  );
};

export default App;
