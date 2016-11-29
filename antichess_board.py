from python_chess import chess
import copy
import itertools


class AntichessBoard(chess.Board):
    aliases = ["Anti", "Antichess"]
    uci_variant = "anti"

    def is_legal(self, move):
        if not super(AntichessBoard, self).is_legal(move):
            return False

        if self.is_capture(move):
            return True
        else:
            return not any(self.generate_pseudo_legal_captures())

    def generate_evasions(self, from_mask=chess.BB_ALL, to_mask=chess.BB_ALL):
        found_capture = False
        for move in self.generate_pseudo_legal_captures(from_mask, to_mask):
            if not super(AntichessBoard, self).is_into_check(move):
                yield move
            found_capture = True

        if not found_capture:
            not_them = to_mask & ~self.occupied_co[not self.turn]
            for move in super(Antichess, self).generate_evasions(from_mask, not_them):
                yield move

    def generate_non_evasions(self, from_mask=chess.BB_ALL, to_mask=chess.BB_ALL):
        found_capture = False
        for move in self.generate_pseudo_legal_captures(from_mask, to_mask):
            if not super(AntichessBoard, self).is_into_check(move):
                yield move
            found_capture = True

        if not found_capture:
            not_them = to_mask & ~self.occupied_co[not self.turn]
            for move in super(AntichessBoard, self).generate_non_evasions(from_mask, not_them):
                yield move

