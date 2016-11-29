class AlphaBeta:
    def __init__(self, depth, board):
        self.depth = depth
        self.board = board

    def minMax(self):
        return maxAlphaBeta(self.board, 0, float('-inf'), float('inf'))

    def maxAlphaBeta(self, board, curr_depth, alpha, beta):
        if curr_depth == self.depth:
            return evaluate_board(board)

        value = alpha
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = max(value, minAlphaBeta(child_board, curr_depth+1, value, beta))
            if value >= beta:
                break

        return value


    def minAlphaBeta(self, board, curr_depth, alpha, beta):
        if curr_depth == self.depth:
            return evaluate_board(board)

        value = beta
        for move in board.legal_moves:
            child_board = board.copy()
            child_board.push(move)
            value = min(value, minAlphaBeta(child_board, curr_depth+1, alpha, value))
            if value <= alpha:
                break

        return value


def evaluate_board(board):
    return 0