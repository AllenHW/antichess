from python_chess import chess
from python_chess.chess import pop_count
from multiprocessing import Pool
import operator
import multiprocessing

def unwrap_self_f(arg, **kwarg):
    return AlphaBeta._get_move_utility(*arg, **kwarg)

class AlphaBeta:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board


    def _get_move_utility(self, board):
        return self.min_alpha_beta(board, 1, float('-inf'), float('inf'))

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

    def max_alpha_beta(self, board, curr_depth, alpha, beta):
        if curr_depth >= self.depth:
            return evaluate(board)

        value = alpha
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = max(value, self.min_alpha_beta(child_board, curr_depth+1, value, beta))
            if value >= beta:
                break

        return value

    def min_alpha_beta(self, board, curr_depth, alpha, beta):
        if curr_depth >= self.depth:
            return -evaluate(board)

        value = beta
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = min(value, self.max_alpha_beta(child_board, curr_depth+1, alpha, value))
            if value <= alpha:
                break

        return value

    # Single method alphabeta
    # def alphabeta(self, board, depth, alpha, beta, maximizingPlayer):
    #     if depth == 0:
    #         return evaluate_board(board)

    #     if maximizingPlayer:
    #         move_made = False
    #         v = float('-inf')
    #         for move in board.legal_moves:
    #             move_made = True
    #             child_board = board.copy()
    #             child_board.push(move)
    #             v = max(v, self.alphabeta(child_board, depth - 1, alpha, beta, False))
    #             alpha = max(alpha, v)
    #             if beta <= alpha:
    #                 break

    #         if move_made:
    #             return v
    #         else:
    #             return evaluate_board(board)
    #     else:
    #         move_made = False
    #         v = float('inf')
    #         for move in board.legal_moves:
    #             move_made = True
    #             child_board = board.copy()
    #             child_board.push(move)
    #             v = min(v, self.alphabeta(child_board, depth - 1, alpha, beta, True))
    #             beta = min(beta, v)
    #             if beta <= alpha:
    #                 break

    #         if move_made:
    #             return v
    #         else:
    #             return evaluate_board(board)


def evaluate(board):
    total_value = 0
    material_value = evaluate_material(board)
    mobility_value = evaluate_mobility_advantage(board)

    total_value += material_value + mobility_value

    return total_value


def evaluate_material(board):
    # Base Multipliers
    BASE_KING_VALUE = 200.0
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
    # Knight
    knight_o_multi = max(1.5, t_ratio * BASE_KNIGHT_VALUE)
    knight_t_multi = max(1.5, o_ratio * BASE_KNIGHT_VALUE)

    # Bishop
    bishop_o_multi = max(1.6, t_ratio * BASE_BISHOP_VALUE)
    bishop_t_multi = max(1.6, o_ratio * BASE_BISHOP_VALUE)

    # Rook
    rook_o_multi = max(1.8, t_ratio * BASE_ROOK_VALUE)
    rook_t_multi = max(1.8, o_ratio * BASE_ROOK_VALUE)

    queen_o_multi = max(2, t_ratio * BASE_QUEEN_VALUE)
    queen_t_multi = max(2, o_ratio * BASE_QUEEN_VALUE)

    # King
    o_kings = pop_count(our_pieces & board.kings)
    t_kings = pop_count(their_pieces & board.kings)
    king_value = (o_kings - t_kings) * BASE_KING_VALUE

    # Pawns
    o_pawns = pop_count(our_pieces & board.pawns)
    t_pawns = pop_count(their_pieces & board.pawns)
    pawn_value = (o_pawns - t_pawns) * BASE_PAWN_VALUE

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
    mover_mobility = _evaluate_mobility_by_side(board, try_pseudo_capture_first)
    board.push(chess.Move.null())
    waiter_mobility = _evaluate_mobility_by_side(board, try_pseudo_capture_first)
    board.pop()

    return 0.2*(mover_mobility - waiter_mobility)


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

# def evaluate_board(board):
#     position_value = 0
#     in_check = False

#     if board.is_check():
#         in_check = True
#         position_value -= 100

#     # If is checkmate
#     if in_check and board.is_checkmate():
#         return -10000

#     our_pieces = board.occupied_co[board.turn]
#     their_pieces = board.occupied_co[not board.turn]

#     # Material Score
#     # Pawns
#     pawns = our_pieces & board.pawns
#     pawns_value = bin(pawns).count('1')

#     # Knight
#     knights = our_pieces & board.knights
#     knights_value = bin(knights).count('1') * 3

#     # Bishop
#     bishops = our_pieces & board.bishops
#     bishops_value = bin(bishops).count('1') * 3

#     # Rook
#     rooks = our_pieces & board.rooks
#     rooks_value = bin(rooks).count('1') * 5

#     # Queen
#     queens = our_pieces & board.queens
#     queens_value = bin(queens).count('1') * 9

#     position_value += pawns_value + knights_value + \
#         rooks_value + queens_value + bishops_value

#     # TODO: Add center control/Advancement value
#     rank_multi = 2
#     for rank in xrange(0, 8):
#         # White
#         if board.turn:
#             processed_rank = rank + 1
#         else:
#             processed_rank = 7 - rank + 1

#         rank_bin = bin(our_pieces & chess.BB_RANKS[rank])
#         position_value += rank_bin.count('1') * processed_rank * rank_multi

#     # Mobility
#     pseudo_legal_counter = 0
#     capture_counter = 0

#     for move in board.pseudo_legal_moves:
#         pseudo_legal_counter += 1

#         if board.is_capture(move):
#             capture_counter += 1

#     mobility_value = pseudo_legal_counter if capture_counter == 0 else capture_counter
#     position_value += 0.8 * mobility_value

#     return position_value
