from python_chess import chess

class AlphaBeta:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board

    def get_best_move(self, board):
        best_move = (None, float('-inf'))

        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            utility = self.min_alpha_beta(child_board, 1, float('-inf'), float('inf'))
            if utility >= best_move[1]:
                best_move = (move, utility)

        if not best_move[0]:
            print "no best move"
            return list(board.legal_moves)[0]

        return best_move[0]

    def min_max(self):
        return self.max_alpha_beta(self.board, 0, float('-inf'), float('inf'))

    def max_alpha_beta(self, board, curr_depth, alpha, beta):
        if curr_depth == self.depth:
            return evaluate_board(board)

        value = alpha
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = max(value, self.min_alpha_beta(child_board, curr_depth+1, value, beta))
            if value >= beta:
                break

        return value

    def min_alpha_beta(self, board, curr_depth, alpha, beta):
        if curr_depth == self.depth:
            return evaluate_board(board)

        value = beta
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = min(value, self.max_alpha_beta(child_board, curr_depth+1, alpha, value))
            if value <= alpha:
                break

        return value

    # Single method alphabeta
    def alphabeta(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0:
            return evaluate_board(board)

        if maximizingPlayer:
            move_made = False
            v = float('-inf')
            for move in board.legal_moves:
                move_made = True
                child_board = board.copy()
                child_board.push(move)
                v = max(v, self.alphabeta(child_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

            if move_made:
                return v
            else:
                return evaluate_board(board)
        else:
            move_made = False
            v = float('inf')
            for move in board.legal_moves:
                move_made = True
                child_board = board.copy()
                child_board.push(move)
                v = min(v, self.alphabeta(child_board, depth - 1, alpha, beta, True))
                beta = min(beta, v)
                if beta <= alpha:
                    break

            if move_made:
                return v
            else:
                return evaluate_board(board)


def evaluate_board(board):
    position_value = 0
    in_check = False

    if board.is_check():
        in_check = True
        position_value -= 500

    # If is checkmate
    if in_check and board.is_checkmate():
        return -1000 # float('-inf')

    # Basic inverse piece valuation
    active_pieces = board.occupied_co[board.turn]

    # Pawns
    pawns = active_pieces & board.pawns
    pawns_value = bin(pawns).count('1')

    # Knight
    knights = active_pieces & board.knights
    knights_value = bin(knights).count('1') * 3#(1 / 3.0)

    # Bishop
    bishops = active_pieces & board.bishops
    bishops_value = bin(bishops).count('1') * 3 #(1 / 3.0)

    # Rook
    rooks = active_pieces & board.rooks
    rooks_value = bin(rooks).count('1') * 5#(1 / 5.0)

    # Queen
    queens = active_pieces & board.queens
    queens_value = bin(queens).count('1') * 9#(1 / 9.0)

    position_value += pawns_value + knights_value + \
        rooks_value + queens_value + bishops_value

    # TODO: Add center control/Advancement value
    rank_multi = 2
    for rank in xrange(0, 8):
        # White
        if board.turn:
            processed_rank = rank + 1
        else:
            processed_rank = 7 - rank + 1

        rank_bin = bin(active_pieces & chess.BB_RANKS[rank])
        position_value += rank_bin.count('1') * processed_rank * rank_multi

    # Mobility
    mobility_value = len(board.pseudo_legal_moves)
    position_value += 0.8 * mobility_value

    return position_value
