from python_chess import chess
import antichess_board

import sys


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

    # Initialize the board
    # TODO: Initialize our antichess variant
    board = antichess_board.AntichessBoard()

    # Input loop
    while not board.is_game_over():
        print board
        if is_white == board.turn:
            # It's our turn
            print "Our Turn!"

            # TODO: Call our move generation
            break
        else:
            # Not our turn wait for their input
            while True:
                enemy_move = raw_input("Move: ")

                try:
                    board.push_uci(enemy_move)
                    break
                except ValueError:
                    print ("Illegal Move")
                    continue

        print("")
