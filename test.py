from minmax import *
import antichess_board
import chess
import time
# board = antichess_board.AntichessBoard()
# board.push_uci('e2e4')


# import pdb; pdb.set_trace()

count = 10000
copy_total = 0
push_total = 0

b1 = chess.Board()
moves = list(b1.legal_moves)

for i in xrange(0, count):
    start = time.time()
    cp_board = b1.copy()
    cp_board.push(moves[0])
    end = time.time()

    copy_total += end - start

    start = time.time()
    b1.push(moves[0])
    b1.pop()
    end = time.time()

    push_total += end - start

copy_avg = (copy_total / float(count))
push_avg = (push_total / float(count))
print "COPY AVG: %.20f" % copy_avg
print "PUSH AVG: %.20f" % push_avg
print "COPY/PUSH: %.20f" % (copy_avg / push_avg)
