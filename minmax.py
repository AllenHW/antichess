from python_chess import chess
from python_chess.chess import pop_count
from quiescent_search import is_quiet_position
from quiescent_search import quiescent_search
from multiprocessing import Pool
import operator
import multiprocessing

def unwrap_self_f(arg, **kwarg):
    return AlphaBeta._get_move_utility(*arg, **kwarg)


class AlphaBeta:
    def __init__(self, depth, factor, board):
        self.factor = factor
        self.board = board
        self.depth = depth

    def _get_move_utility(self, board):
        return self.min_alpha_beta(board, 1, 1, float('-inf'), float('inf'))

    def get_best_move(self, board):
        legal_moves = list(board.legal_moves)

        child_boards = []
        for move in legal_moves:
            child_board = board.copy()
            child_board.push(move)
            child_boards.append(child_board)

        pool = Pool(processes=4)
        utilities = pool.map(unwrap_self_f, zip([self]*len(child_boards), child_boards))
        index, value = max(enumerate(utilities), key=operator.itemgetter(1))

        pool.terminate()
        return legal_moves[index]

    def min_max(self):
        return self.max_alpha_beta(self.board, 0, float('-inf'), float('inf'))

    def max_alpha_beta(self, board, curr_depth, curr_factor, alpha, beta):
        if curr_depth >= self.depth and curr_factor >= self.factor:
            if is_quiet_position(board):
                return evaluate(board)
            else:
                return quiescent_search(board, alpha, beta, evaluate)

        value = alpha
        move_found = False
        legal_moves = list(board.legal_moves)
        legal_moves_len = len(legal_moves)
        for i, move in enumerate(legal_moves):
            move_found = True
            child_board = board.copy()
            child_board.push(move)
            value = max(value, self.min_alpha_beta(child_board, curr_depth + 1, curr_factor*legal_moves_len, value, beta))
            if value >= beta or (curr_depth >= self.depth and curr_factor*(i+1) >= self.factor):
                break

        return value if move_found else float('-inf')

    def min_alpha_beta(self, board, curr_depth, curr_factor, alpha, beta):
        if curr_depth >= self.depth and curr_factor >= self.factor:
            if is_quiet_position(board):
                return -evaluate(board)
            else:
                return -quiescent_search(board, alpha, beta, evaluate)

        value = beta
        move_found = False
        legal_moves = list(board.legal_moves)
        legal_moves_len = len(legal_moves)
        for i, move in enumerate(legal_moves):
            move_found = True
            child_board = board.copy()
            child_board.push(move)
            value = min(value, self.max_alpha_beta(child_board, curr_depth + 1, curr_factor*legal_moves_len, alpha, value))
            if value <= alpha or (curr_depth >= self.depth and curr_factor*(i+1) >= self.factor):
                break

        return value if move_found else float('inf')


def evaluate(board):
    total_value = 0
    material_value = 20*evaluate_material(board)
    mobility_value = evaluate_mobility_advantage(board)
    if is_end_game(board):
        piece_table_value = evaluate_piece_tables(board, 0.5)
    else:
        piece_table_value = 0

    total_value += material_value + mobility_value + piece_table_value

    return total_value


def evaluate_material(board):
    # Base Multipliers
    BASE_KING_VALUE = 2000.0
    BASE_PAWN_VALUE = 1.0
    BASE_BISHOP_VALUE = 3.3
    BASE_KNIGHT_VALUE = 3.2
    BASE_ROOK_VALUE = 5.0
    BASE_QUEEN_VALUE = 9.0

    mat_val = 0

    our_pieces = board.occupied_co[board.turn]
    o_piece_count = pop_count(our_pieces)

    their_pieces = board.occupied_co[not board.turn]
    t_piece_count = pop_count(their_pieces)

    # Modified Multipliers
    t_ratio = (16.0 - t_piece_count) / 16.0
    o_ratio = (16.0 - o_piece_count) / 16.0

    pawn_o_multi = 1.2 if t_ratio < 0.5 else BASE_PAWN_VALUE
    pawn_t_multi = 1.2 if o_ratio < 0.5 else BASE_PAWN_VALUE

    # Knight
    knight_o_multi = max(3.0, t_ratio * BASE_KNIGHT_VALUE)
    knight_t_multi = max(3.0, o_ratio * BASE_KNIGHT_VALUE)

    # Bishop
    bishop_o_multi = max(2.7, t_ratio * BASE_BISHOP_VALUE)
    bishop_t_multi = max(2.7, o_ratio * BASE_BISHOP_VALUE)

    # Rook
    rook_o_multi = max(3.5, t_ratio * BASE_ROOK_VALUE)
    rook_t_multi = max(3.5, o_ratio * BASE_ROOK_VALUE)

    queen_o_multi = max(7, t_ratio * BASE_QUEEN_VALUE)
    queen_t_multi = max(7, o_ratio * BASE_QUEEN_VALUE)

    # King
    o_kings = pop_count(our_pieces & board.kings)
    t_kings = pop_count(their_pieces & board.kings)
    king_value = (o_kings - t_kings) * BASE_KING_VALUE

    # Pawns
    o_pawns = pop_count(our_pieces & board.pawns)
    t_pawns = pop_count(their_pieces & board.pawns)
    pawn_value = pawn_o_multi * o_pawns - pawn_t_multi * t_pawns

    # Knight
    o_knights = pop_count(our_pieces & board.knights)
    t_knights = pop_count(their_pieces & board.knights)
    knight_value = knight_o_multi * o_knights - knight_t_multi * t_knights

    # Bishop
    o_bishops = pop_count(our_pieces & board.bishops)
    t_bishops = pop_count(their_pieces & board.bishops)
    bishop_value = bishop_o_multi * o_bishops - bishop_t_multi * t_bishops

    # Rook
    o_rooks = pop_count(our_pieces & board.rooks)
    t_rooks = pop_count(their_pieces & board.rooks)
    rook_value = rook_o_multi * o_rooks - rook_t_multi * t_rooks

    # Queen
    o_queens = pop_count(our_pieces & board.queens)
    t_queens = pop_count(their_pieces & board.queens)
    queen_value = queen_o_multi * o_queens - queen_t_multi * t_queens

    mat_val += pawn_value + knight_value + bishop_value \
        + rook_value + queen_value + king_value

    return mat_val


def evaluate_mobility_advantage(board, try_pseudo_capture_first=False):
    return 0
    mover_mobility = _evaluate_mobility_by_side(board, try_pseudo_capture_first)
    board.push(chess.Move.null())
    waiter_mobility = _evaluate_mobility_by_side(board, try_pseudo_capture_first)
    board.pop()

    return 0.5 * (mover_mobility - waiter_mobility)


def _evaluate_mobility_by_side(board, try_pseudo_capture_first=False):
    # Mobility
    if not try_pseudo_capture_first:
        pseudo_legal_counter = 0
        capture_counter = 0

        for move in board.pseudo_legal_moves:
            pseudo_legal_counter += 1
            if board.is_capture(move):
                capture_counter += 1

        mobility_value = pseudo_legal_counter if capture_counter == 0 else capture_counter
    else:
        if any(generate_pseudo_legal_captures()):
            mobility_value = len(generate_pseudo_legal_captures())
        else:
            mobility_value = len(pseudo_legal_moves)

    return mobility_value


# WHITE SIDE
# pawn piece table
PAWN_TABLE_W = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0]

KNIGHT_TABLE_W = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50]

BISHOP_TABLE_W = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20]

ROOKS_TABLE_W = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0]

QUEEN_TABLE_W = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20]

KING_TABLE_W_MIDDLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20]

KING_TABLE_W_END = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50]

# BLACK SIDE
PAWN_TABLE_B = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0]

KNIGHT_TABLE_B = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50]

BISHOP_TABLE_B = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20]

ROOKS_TABLE_B = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0]

QUEEN_TABLE_B = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20]

KING_TABLE_B_MIDDLE = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30]

KING_TABLE_B_END = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -50,-40,-30,-20,-20,-30,-40,-50]

def evaluate_piece_tables(board, weight):
    turn = board.turn

    white_value = _evaluate_white_piece_tables(board)
    black_value = _evaluate_black_piece_tables(board)

    if turn:
        return (white_value - black_value) * weight
    else:
        return (black_value - white_value) * weight


def is_end_game(board):
    our_pieces = board.occupied_co[board.turn]
    o_piece_count = pop_count(our_pieces)

    their_pieces = board.occupied_co[not board.turn]
    t_piece_count = pop_count(their_pieces)

    if o_piece_count <= 5 and t_piece_count <= 5:
        return True

    return False


def _evaluate_white_piece_tables(board):
    value = 0
    # SquareSet of pawns
    pawns = board.pieces(chess.PAWN, chess.WHITE)
    knights = board.pieces(chess.KNIGHT, chess.WHITE)
    bishops = board.pieces(chess.BISHOP, chess.WHITE)
    rooks = board.pieces(chess.ROOK, chess.WHITE)
    queens = board.pieces(chess.QUEEN, chess.WHITE)
    kings = board.pieces(chess.KING, chess.WHITE)

    # Pawns
    for p in pawns:
        value += PAWN_TABLE_W[63 - p]

    # Knights
    for k in knights:
        value += KNIGHT_TABLE_W[63 - k]

    # Bishops
    for b in bishops:
        value += BISHOP_TABLE_W[63 - b]

    # Rooks
    for r in rooks:
        value += ROOKS_TABLE_W[63 - r]

    # Queen
    for q in queens:
        value += QUEEN_TABLE_W[63 - q]

    # King
    if is_end_game(board):
        king_table = KING_TABLE_W_END
    else:
        king_table = KING_TABLE_W_MIDDLE
    # TODO ADD ENDGAME TABLE
    for king in kings:
        value += king_table[63 - king]

    return value


def _evaluate_black_piece_tables(board):
    value = 0
    # SquareSet of pawns
    pawns = board.pieces(chess.PAWN, chess.BLACK)
    knights = board.pieces(chess.KNIGHT, chess.BLACK)
    bishops = board.pieces(chess.BISHOP, chess.BLACK)
    rooks = board.pieces(chess.ROOK, chess.BLACK)
    queens = board.pieces(chess.QUEEN, chess.BLACK)
    kings = board.pieces(chess.KING, chess.BLACK)

    # Pawns
    for p in pawns:
        value += PAWN_TABLE_B[63 - p]

    # Knights
    for k in knights:
        value += KNIGHT_TABLE_B[63 - k]

    # Bishops
    for b in bishops:
        value += BISHOP_TABLE_B[63 - b]

    # Rooks
    for r in rooks:
        value += ROOKS_TABLE_B[63 - r]

    # Queen
    for q in queens:
        value += QUEEN_TABLE_B[63 - q]

    # King
    if is_end_game(board):
        king_table = KING_TABLE_B_END
    else:
        king_table = KING_TABLE_B_MIDDLE
    # TODO ADD ENDGAME TABLE
    for king in kings:
        value += king_table[63 - king]

    return value
