import copy
import math

class CheckersGame:
    def __init__(self):
        self.board = self.create_board()
        self.turn = '🔵'  # Red starts
        self.winner = None
        self.position_history = {}

    def create_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = '🔴'
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = '🔵'
        return board

    def _in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def _get_directions(self, piece):
        if piece == '🔵':
            return [(-1, -1), (-1, 1)]
        elif piece == '🔴':
            return [(1, -1), (1, 1)]
        elif piece in ['💙', '❤️']:  # Kings
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return []

    def _king_for(self, player):
        return '💙' if player == '🔵' else '❤️'

    def get_valid_moves(self, player):
        captures, moves = [], []

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece not in (player, self._king_for(player)):
                    continue

                for dx, dy in self._get_directions(piece):
                    nr, nc = r + dx, c + dy
                    if self._in_bounds(nr, nc) and self.board[nr][nc] == '.':
                        moves.append(((r, c), (nr, nc)))

                    mr, mc = r + dx, c + dy
                    er, ec = r + 2 * dx, c + 2 * dy
                    if (
                        self._in_bounds(er, ec)
                        and self.board[er][ec] == '.'
                        and self.board[mr][mc] != '.'
                        and self.board[mr][mc] not in (player, self._king_for(player))
                    ):
                        captures.append(((r, c), (er, ec)))

        return {"captures": captures, "moves": moves}

    def make_move(self, start, end):
        if self.winner:
            return False, f"Game over. {self.winner.upper()} has already won."

        sx, sy = start
        ex, ey = end
        piece = self.board[sx][sy]

        if not self._in_bounds(sx, sy) or not self._in_bounds(ex, ey):
            return False, "Move out of bounds"
        if piece == '.' or piece not in (self.turn, self._king_for(self.turn)):
            return False, "Invalid piece selection"
        if self.board[ex][ey] != '.':
            return False, "Target cell not empty"

        dx, dy = ex - sx, ey - sy
        abs_dx, abs_dy = abs(dx), abs(dy)

        all_moves = self.get_valid_moves(self.turn)
        valid = all_moves["captures"] + all_moves["moves"]
        if ((sx, sy), (ex, ey)) not in valid:
            return False, "Illegal move"

        if abs_dx == 2 and abs_dy == 2:  # Capture
            mx, my = sx + dx // 2, sy + dy // 2
            self.board[mx][my] = '.'

        self.board[ex][ey] = piece
        self.board[sx][sy] = '.'
        self._maybe_king(ex, ey)
        self._check_winner()
        self._switch_turn()
        return True, "Move successful"

    def _maybe_king(self, x, y):
        piece = self.board[x][y]
        if piece == '🔵' and x == 0:
            self.board[x][y] = '💙'
        elif piece == '🔴' and x == 7:
            self.board[x][y] = '❤️'

    def _board_key(self):
        return (tuple(tuple(row) for row in self.board), self.turn)

    def _switch_turn(self):
        key = self._board_key()
        self.position_history[key] = self.position_history.get(key, 0) + 1
        if self.position_history[key] >= 5:
            self.winner = 'draw'
        else:
            self.turn = '🔴' if self.turn == '🔵' else '🔵'

    def _check_winner(self):
        if self.winner:
            return

        red_moves = self.get_valid_moves('🔵')
        black_moves = self.get_valid_moves('🔴')
        red_pieces = any(cell in ['🔵', '💙'] for row in self.board for cell in row)
        black_pieces = any(cell in ['🔴', '❤️'] for row in self.board for cell in row)

        if not red_pieces or (not red_moves["captures"] and not red_moves["moves"]):
            self.winner = '🔴'
        elif not black_pieces or (not black_moves["captures"] and not black_moves["moves"]):
            self.winner = '🔵'

    def evaluate(self):
        red, black = 0, 0
        for row in self.board:
            for cell in row:
                if cell == '🔵':
                    red += 1
                elif cell == '💙':
                    red += 2
                elif cell == '🔴':
                    black += 1
                elif cell == '❤️':
                    black += 2
        return black - red

    def _clone(self):
        clone = CheckersGame()
        clone.board = copy.deepcopy(self.board)
        clone.turn = self.turn
        clone.winner = self.winner
        clone.position_history = copy.deepcopy(self.position_history)
        return clone

    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0 or self.winner is not None:
            return self.evaluate(), None

        player = '🔴' if maximizing else '🔵'
        moves_data = self.get_valid_moves(player)
        all_moves = moves_data["captures"] + moves_data["moves"]
        if not all_moves:
            return self.evaluate(), None

        best_move = None

        if maximizing:
            max_eval = -math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval, _ = clone.minimax(depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in all_moves:
                clone = self._clone()
                clone.make_move(*move)
                eval, _ = clone.minimax(depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def ai_move_if_needed(self):
        if self.turn != '🔴' or self.winner is not None:
            return None
        _, move = self.minimax(4, -math.inf, math.inf, True)
        if move:
            self.make_move(*move)
            return move
        return None
