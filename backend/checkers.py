import copy
import math
from typing import Dict, Tuple, List


class CheckersGame:
    """
    Simple 8×8 checkers game engine
    • 🔵 / 💙  – Blue man / king (human)
    • 🔴 / ❤️  – Red man / king (AI)
    Human (blue) moves first.
    """

    def __init__(self):
        self.board: List[List[str]] = self._create_board()
        self.turn: str = "🔵"  # blue (human) starts
        self.winner: str | None = None
        self.position_history: Dict[str, int] = {}

    def to_dict(self) -> dict:
        """Return a JSON‑serialisable representation of the game."""
        return {
            "board": self.board,
            "turn": self.turn,
            "winner": self.winner,
            "position_history": self.position_history,
        }

    @staticmethod
    def from_dict(data: dict) -> "CheckersGame":
        g = CheckersGame()
        g.board = data["board"]
        g.turn = data["turn"]
        g.winner = data.get("winner")
        g.position_history = data.get("position_history", {})
        return g

    def _create_board(self) -> List[List[str]]:
        board = [["." for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = "🔴"
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = "🔵"
        return board

    @staticmethod
    def _in_bounds(x: int, y: int) -> bool:
        return 0 <= x < 8 and 0 <= y < 8

    @staticmethod
    def _get_directions(piece: str) -> List[Tuple[int, int]]:
        if piece == "🔵":
            return [(-1, -1), (-1, 1)]
        if piece == "🔴":
            return [(1, -1), (1, 1)]
        if piece in ("💙", "❤️"):  # kings
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return []

    @staticmethod
    def _king_for(player: str) -> str:
        return "💙" if player == "🔵" else "❤️"

    def get_valid_moves(self, player: str) -> Dict[str, List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        captures, moves = [], []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece not in (player, self._king_for(player)):
                    continue
                for dx, dy in self._get_directions(piece):
                    nr, nc = r + dx, c + dy
                    if self._in_bounds(nr, nc) and self.board[nr][nc] == ".":
                        moves.append(((r, c), (nr, nc)))
                    er, ec = r + 2 * dx, c + 2 * dy
                    mr, mc = r + dx, c + dy
                    if self._in_bounds(er, ec) and self.board[er][ec] == ".":
                        middle = self.board[mr][mc]
                        if middle != "." and middle not in (player, self._king_for(player)):
                            captures.append(((r, c), (er, ec)))
        return {"captures": captures, "moves": moves}

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[bool, str]:
        if self.winner:
            return False, f"Game over – {self.winner} already won."

        sx, sy = start
        ex, ey = end
        piece = self.board[sx][sy]

        if not self._in_bounds(sx, sy) or not self._in_bounds(ex, ey):
            return False, "Move out of bounds."
        if piece == "." or piece not in (self.turn, self._king_for(self.turn)):
            return False, "Invalid piece selection."
        if self.board[ex][ey] != ".":
            return False, "Target cell not empty."

        all_moves = self.get_valid_moves(self.turn)
        legal = all_moves["captures"] + all_moves["moves"]
        if ((sx, sy), (ex, ey)) not in legal:
            return False, "Illegal move."

        dx, dy = ex - sx, ey - sy
        if abs(dx) == 2:
            mx, my = sx + dx // 2, sy + dy // 2
            self.board[mx][my] = "."

        self.board[ex][ey] = piece
        self.board[sx][sy] = "."
        self._maybe_king(ex, ey)

        self._record_position()
        self._check_winner()
        if not self.winner:
            self.turn = "🔴" if self.turn == "🔵" else "🔵"

        return True, "Move successful."

    def _maybe_king(self, x: int, y: int):
        piece = self.board[x][y]
        if piece == "🔵" and x == 0:
            self.board[x][y] = "💙"
        elif piece == "🔴" and x == 7:
            self.board[x][y] = "❤️"

    def _serialize_position(self) -> str:
        rows = ["".join(row) for row in self.board]
        return "/".join(rows) + "|" + self.turn

    def _record_position(self):
        key = self._serialize_position()
        self.position_history[key] = self.position_history.get(key, 0) + 1
        if self.position_history[key] >= 5:
            self.winner = "draw"

    def _check_winner(self):
        if self.winner:
            return
        blue_moves = self.get_valid_moves("🔵")
        red_moves = self.get_valid_moves("🔴")
        blue_pieces = any(cell in ("🔵", "💙") for row in self.board for cell in row)
        red_pieces = any(cell in ("🔴", "❤️") for row in self.board for cell in row)

        if not blue_pieces or (not blue_moves["captures"] and not blue_moves["moves"]):
            self.winner = "🔴"
        elif not red_pieces or (not red_moves["captures"] and not red_moves["moves"]):
            self.winner = "🔵"

    def evaluate(self) -> int:
        blue_score = 0
        red_score = 0
        for row in self.board:
            for cell in row:
                if cell == "🔵":
                    blue_score += 1
                elif cell == "💙":
                    blue_score += 2
                elif cell == "🔴":
                    red_score += 1
                elif cell == "❤️":
                    red_score += 2
        return red_score - blue_score

    def _clone(self) -> "CheckersGame":
        clone = CheckersGame()
        clone.board = copy.deepcopy(self.board)
        clone.turn = self.turn
        clone.winner = self.winner
        clone.position_history = copy.deepcopy(self.position_history)
        return clone

    def minimax(self, depth: int, alpha: int, beta: int, maximizing: bool) -> Tuple[int, Tuple[Tuple[int, int], Tuple[int, int]] | None]:
        if depth == 0 or self.winner:
            return self.evaluate(), None

        player = "🔴" if maximizing else "🔵"
        all_moves = self.get_valid_moves(player)["captures"] + self.get_valid_moves(player)["moves"]
        if not all_moves:
            return self.evaluate(), None

        best_move = None
        if maximizing:
            max_eval = -math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval_, _ = clone.minimax(depth - 1, alpha, beta, False)
                if eval_ > max_eval:
                    max_eval, best_move = eval_, move
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval_, _ = clone.minimax(depth - 1, alpha, beta, True)
                if eval_ < min_eval:
                    min_eval, best_move = eval_, move
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def ai_move_if_needed(self) -> Tuple[Tuple[int, int], Tuple[int, int]] | None:
        """Let the AI (red) move when it’s its turn."""
        if self.turn != "🔴" or self.winner:
            return None
        _, move = self.minimax(4, -math.inf, math.inf, True)
        if move:
            self.make_move(*move)
            return move
        return None
