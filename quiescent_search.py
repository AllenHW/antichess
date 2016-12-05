def is_quiet_position(board):
    # Not quiet if currently in check
    if board.is_check:
        return False

    # Not quiet if last move was a capture move
    last_move = board.pop()
    if board.is_capture(last_move):
        board.push(last_move)
        return False

    board.push(last_move)
    return True


def quiescent_search(board, alpha, beta, eval_func):
    stand_pat = eval_func(board)

    if stand_pat >= beta:
        return beta

    if alpha < stand_pat:
        alpha = stand_pat

    for capture_move in board.generate_legal_captures():
        board.push(capture_move)
        score = -quiescent_search(board, -beta, -alpha, eval_func)
        board.pop()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha
