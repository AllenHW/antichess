import chess

import sys


if __name__ == "__main__":
    args = sys.argv

    # Commandline Parse

    if len(args) != 2:
        print "Usage: antichess <color>"
        print "One of (b,w,black,white)"

        exit(0)

    color = args[1].lower()

    # Start the game
    
