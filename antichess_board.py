from python_chess import chess
from python_chess.chess import *
import copy
import math
import itertools


class AntichessBoard(chess.Board):
    aliases = ["Anti", "Antichess"]
    uci_variant = "anti"

    def __init__(self, fen=STARTING_FEN, chess960=False):
        super(AntichessBoard, self).__init__(fen, chess960)

    def is_legal(self, move):
        if not super(AntichessBoard, self).is_legal(move):
            return False

        if self.is_capture(move):
            return True
        else:
            return not any(self.generate_legal_captures())

    def generate_evasions(self, from_mask=chess.BB_ALL, to_mask=chess.BB_ALL):
        all_evasions = []
        capture_evasions = []
        for move in super(AntichessBoard, self).generate_evasions(from_mask, to_mask):
            if self.is_capture(move):
                capture_evasions.append(move)
            all_evasions.append(move)

        if capture_evasions:
            return iter(capture_evasions)
        else:
            return iter(all_evasions)

    def generate_non_evasions(self, from_mask=chess.BB_ALL, to_mask=chess.BB_ALL):
        all_non_evasions = []
        capture_non_evasions = []
        for move in super(AntichessBoard, self).generate_non_evasions(from_mask, to_mask):
            if self.is_capture(move):
                capture_non_evasions.append(move)
            all_non_evasions.append(move)

        if capture_non_evasions:
            return iter(capture_non_evasions)
        else:
            return iter(all_non_evasions)


    def __str__(self):
        builder = []

        builder.append("   ")
        for c in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            builder.append(c + " ")
        builder.append("\n\n")


        for i, square in enumerate(SQUARES_180):
            if i % 8 == 0:
                level = math.ceil((len(SQUARES_180)-i)/8.)
                builder.append(str(int(level)))
                builder.append("  ")
            piece = self.piece_at(square)

            if piece:
                builder.append(piece.symbol())
            else:
                builder.append(".")

            if BB_SQUARES[square] & BB_FILE_H:
                if square != H1:
                    builder.append("\n")
            else:
                builder.append(" ")

        builder.append("\n\n   ")
        for c in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            builder.append(c + " ")

        return "".join(builder)