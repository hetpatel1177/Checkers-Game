import copy
import math
from typing import Dict, Tuple, List


class CheckersGame:
    """
    Simple 8×8 Checkers engine.

    • 🔵 / 💙 – Blue man / king  (human)
    • 🔴 / ❤️ – Red  man / king  (AI)

    Blue starts.  Kings can move diagonally in both directions.
    A draw is declared after the same position occurs 5 times.
    """

    def __init__(self) -> None:
        self.board: List[List[str]] = self._create_board()
        self.turn: str = "🔵"              # Blue begins
        self.winner: str | None = None
        self.position_history: Dict[str, int] = {}

    # ─────────────────────── Board helpers ────────────────────── #

    @staticmethod
    def _create_board() -> List[List[str]]:
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

    # ───────────────────── Valid‑move logic ───────────────────── #

    def get_valid_moves(
        self, player: str
    ) -> Dict[str, List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
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
                    mr, mc = r + dx, c + dy
                    er, ec = r + 2 * dx, c + 2 * dy
                    if (
                        self._in_bounds(er, ec)
                        and self.board[er][ec] == "."
                        and self.board[mr][mc] != "."
                        and self.board[mr][mc] not in (player, self._king_for(player))
                    ):
                        captures.append(((r, c), (er, ec)))
        return {"captures": captures, "moves": moves}

    # ────────────────────── Make a move ───────────────────────── #

    def make_move(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Tuple[bool, str]:
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

        legal_moves = self.get_valid_moves(self.turn)
        if ((sx, sy), (ex, ey)) not in (
            legal_moves["captures"] + legal_moves["moves"]
        ):
            return False, "Illegal move."

        # Handle capture
        dx, dy = ex - sx, ey - sy
        if abs(dx) == 2:
            self.board[sx + dx // 2][sy + dy // 2] = "."

        # Move piece
        self.board[ex][ey], self.board[sx][sy] = piece, "."
        self._maybe_king(ex, ey)

        self._record_position()
        self._check_winner()
        if not self.winner:
            self.turn = "🔴" if self.turn == "🔵" else "🔵"
        return True, "Move successful."

    def _maybe_king(self, x: int, y: int) -> None:
        if self.board[x][y] == "🔵" and x == 0:
            self.board[x][y] = "💙"
        elif self.board[x][y] == "🔴" and x == 7:
            self.board[x][y] = "❤️"

    # ─────────────── Draw detection & win check ──────────────── #

    def _serialize_position(self) -> str:
        return "/".join("".join(row) for row in self.board) + "|" + self.turn

    def _record_position(self) -> None:
        key = self._serialize_position()
        self.position_history[key] = self.position_history.get(key, 0) + 1
        if self.position_history[key] >= 2:
            self.winner = "draw"

    def _check_winner(self) -> None:
        if self.winner:
            return
        blue_valid = self.get_valid_moves("🔵")
        red_valid = self.get_valid_moves("🔴")
        blue_has_pieces = any(cell in ("🔵", "💙") for row in self.board for cell in row)
        red_has_pieces = any(cell in ("🔴", "❤️") for row in self.board for cell in row)

        if not blue_has_pieces or not (blue_valid["captures"] or blue_valid["moves"]):
            self.winner = "🔴"
        elif not red_has_pieces or not (red_valid["captures"] or red_valid["moves"]):
            self.winner = "🔵"

    # ─────────────────────── AI (minimax) ─────────────────────── #

    def evaluate(self) -> int:
        blue, red = 0, 0
        for row in self.board:
            for cell in row:
                if cell == "🔵":
                    blue += 1
                elif cell == "💙":
                    blue += 2
                elif cell == "🔴":
                    red += 1
                elif cell == "❤️":
                    red += 2
        return red - blue  # AI (red) wants to maximize this

    def _clone(self) -> "CheckersGame":
        clone = CheckersGame()
        clone.board = copy.deepcopy(self.board)
        clone.turn = self.turn
        clone.winner = self.winner
        clone.position_history = copy.deepcopy(self.position_history)
        return clone

    def minimax(
        self, depth: int, alpha: int, beta: int, maximizing: bool
    ) -> Tuple[int, Tuple[Tuple[int, int], Tuple[int, int]] | None]:
        if depth == 0 or self.winner:
            return self.evaluate(), None

        player = "🔴" if maximizing else "🔵"
        all_moves = self.get_valid_moves(player)["captures"] + self.get_valid_moves(
            player
        )["moves"]
        if not all_moves:
            return self.evaluate(), None

        best_move = None
        if maximizing:
            best_eval = -math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval_, _ = clone.minimax(depth - 1, alpha, beta, False)
                if eval_ > best_eval:
                    best_eval, best_move = eval_, move
                alpha = max(alpha, eval_)
                if beta <= alpha:
                    break
            return best_eval, best_move
        else:
            best_eval = math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval_, _ = clone.minimax(depth - 1, alpha, beta, True)
                if eval_ < best_eval:
                    best_eval, best_move = eval_, move
                beta = min(beta, eval_)
                if beta <= alpha:
                    break
            return best_eval, best_move

    # Let AI play if it's red's turn
    def ai_move_if_needed(
        self,
    ) -> Tuple[Tuple[int, int], Tuple[int, int]] | None:
        if self.turn != "🔴" or self.winner:
            return None
        _, move = self.minimax(4, -math.inf, math.inf, True)
        if move:
            self.make_move(*move)
            return move
        return None
