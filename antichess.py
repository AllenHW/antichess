from python_chess import chess
from python_chess.chess import pop_count
import antichess_board
import endgame
import minmax

import random
import sys
from time import time


def make_random_move(board):
    moves = list(board.legal_moves)

    if moves:
        move_index = random.randint(0, len(moves) - 1)
        return str(moves[move_index])

    return None


def get_endgame_type(board):
    NOT_ENDGAME = 0
    ONE_ROOK_ENDGAME = 1
    ONE_QUEEN_ENDGAME = 2
    TWO_ROOKS_ENDGAME = 3
    ROOK_AND_QUEEN_ENDGAME = 4

    o_pieces = pop_count(board.occupied_co[board.turn])
    t_pieces = pop_count(board.occupied_co[not board.turn])

    if t_pieces > 1:
        return NOT_ENDGAME

    o_rooks = len(list(board.pieces(chess.ROOK, board.turn)))
    o_queens = len(list(board.pieces(chess.QUEEN, board.turn)))

    if o_pieces == 2 and o_rooks == 1:
        return ONE_ROOK_ENDGAME
    elif o_pieces == 2 and o_queens == 1:
        return ONE_QUEEN_ENDGAME
    elif o_pieces == 3 and o_rooks == 2:
        return TWO_ROOKS_ENDGAME
    elif o_pieces == 3 and o_rooks == 1 and o_queens == 1:
        return ROOK_AND_QUEEN_ENDGAME

    return NOT_ENDGAME


def print_legal_moves(board):
    for move in board.legal_moves:
        print move


if __name__ == "__main__":
    args = sys.argv

    # Commandline Parse

    if len(args) < 2:
        print "Usage: antichess <colour>"
        print "One of (b, w, black, white)"
        exit(0)

    colour = args[1].lower()

    if colour != 'w' and colour != 'b' and \
            colour != 'white' and colour != 'black':
        print "Usage: antichess <colour>"
        print "One of (b, w, black, white)"
        exit(0)

    # Player colour
    is_white = (colour == 'w' or colour == 'white')
    first_move = True
    DEFAULT_FIRST_MOVE = "b1c3"

    # Initialize the board
    board = antichess_board.AntichessBoard()

    # Input loop
    while not board.is_game_over():
        if is_white == board.turn:
            # It's our turn
            use_default = False

            while True:
                endgame_type = get_endgame_type(board)

                if not use_default and endgame_type and endgame_type <= 4:
                    eg = endgame.EndgameBase(board, endgame_type)
                    move = eg.get_best_move(board)
                elif first_move and is_white:
                    move = DEFAULT_FIRST_MOVE
                    first_move = False
                else:
                    ab = minmax.AlphaBeta(4, 1000, board)
                    move = str(ab.get_best_move(board))

                try:
                    m = board.push_uci(move)
                    print(m.uci())
                    break
                except ValueError:
                    use_default = True
                    # print ("Illegal Move: %s" % move)
                    # print_legal_moves(board)

                    continue
        else:
            # Not our turn wait for their input
            while True:
                enemy_move = raw_input()

                # rand_move = random.randint(2, 3)

                # if rand_move == 1:
                #     enemy_move = make_random_move(board)
                # else:
                #     ab = minmax.AlphaBeta(3, 100, board)
                #     enemy_move = str(ab.get_best_move(board))

                try:
                    m = board.push_uci(enemy_move)
                    break
                except ValueError:
                    # print ("Illegal Move: %s" % enemy_move)
                    # print_legal_moves(board)
                    continue

        # print board
        # print("")

    # print("GAME OVER!")
    # print(board.result())
