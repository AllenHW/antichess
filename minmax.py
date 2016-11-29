class AlphaBeta:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board


    def get_best_move(self, board):
        best_move = (None, float('-inf'))

        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            utility = min_alpha_beta(child_board, 0, float('-inf'), float('inf'))
            if best_move[1] > utility:
                best_move = (move, utility)

        return best_move[0]

    def min_max(self):
        return max_alpha_beta(self.board, 0, float('-inf'), float('inf'))

    def max_alpha_beta(self, board, curr_depth, alpha, beta):
        if curr_depth == self.depth:
            return evaluate_board(board)

        value = alpha
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = max(value, min_alpha_beta(child_board, curr_depth+1, value, beta))
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
            value = min(value, max_alpha_beta(child_board, curr_depth+1, alpha, value))
            if value <= alpha:
                break

        return value


def evaluate_board(board):
    return 0