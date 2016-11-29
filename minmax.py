class AlphaBeta:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board


    def get_best_move(self, board):
        best_move = (None, float('-inf'))

        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            utility = self.min_alpha_beta(child_board, 0, float('-inf'), float('inf'))
            if best_move[1] < utility:
                best_move = (move, utility)

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


def evaluate_board(board):
    position_value = 0

    # Basic inverse piece valuation
    active_pieces = board.occupied_co[board.turn]

    # Pawns
    pawns = active_pieces & board.pawns
    pawns_value = bin(pawns).count('1')

    # Knight
    knights = active_pieces & board.knights
    knights_value = bin(knights).count('1') * (1 / 3.0)

    # Bishop
    bishops = active_pieces & board.bishops
    bishops_value = bin(bishops).count('1') * (1 / 3.0)

    # Rook
    rooks = active_pieces & board.rooks
    rooks_value = bin(rooks).count('1') * (1 / 5.0)

    # Queen
    queens = active_pieces & board.queens
    queens_value = bin(queens).count('1') * (1 / 9.0)

    position_value += pawns_value + knights_value + \
        rooks_value + queens_value + bishops_value

    return position_value
