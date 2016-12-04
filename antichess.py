from python_chess import chess
import antichess_board
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

    # if len(args) >= 3 and args[2] == "debug":
    #     debug = True
    # else:
    #     debug = False

    # Player colour
    is_white = (colour == 'w' or colour == 'white')
    first_move = True
    DEFAULT_FIRST_MOVE = "b1c3"

    # Initialize the board
    # TODO: Initialize our antichess variant
    board = antichess_board.AntichessBoard()

    print "Starting Board:"
    print board
    # Input loop
    while not board.is_game_over():
        print "Val: %f" % minmax.evaluate(board)

        if board.turn:
            print "Player: %s" % "White"
        else:
            print "Player: %s" % "Black"

        if is_white == board.turn:
            # It's our turn

            while True:
                # move = raw_input("Our Move: ")
                # move = make_random_move(board)
                start = time()
                if first_move and is_white:
                    move = DEFAULT_FIRST_MOVE
                    first_move = False
                else:
                    ab = minmax.AlphaBeta(5, board)
                    move = str(ab.get_best_move(board))
                end = time()

                print "Time Taken: %d" % (end-start)

                try:
                    m = board.push_uci(move)
                    print "MOVED: %s" % m
                    break
                except ValueError:
                    print ("Illegal Move: %s" % move)
                    print_legal_moves(board)
                    continue
        else:
            # Not our turn wait for their input
            while True:
                # enemy_move = raw_input("Move: ")

                rand_move = random.randint(1, 3)

                if rand_move == 1:
                    enemy_move = make_random_move(board)
                else:
                    ab = minmax.AlphaBeta(2, board)
                    enemy_move = str(ab.get_best_move(board))

                try:
                    m = board.push_uci(enemy_move)
                    print "MOVED: %s" % m
                    break
                except ValueError:
                    print ("Illegal Move: %s" % enemy_move)
                    print_legal_moves(board)
                    continue

        print board
        print("")

    print("Final Board:")
    print(board)
    print("GAME OVER!")
    print(board.result())
    print(board.legal_moves)

    print(minmax.evaluate(board))
