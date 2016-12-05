from python_chess import chess
from python_chess.chess import pop_count
import math
import operator
import random

class EndgameBase:
    NOT_ENDGAME = 0
    ONE_ROOK_ENDGAME = 1        # Not implemented
    ONE_QUEEN_ENDGAME = 2       # Not implemented
    TWO_ROOKS_ENDGAME = 3       # Not implemented
    ROOK_AND_QUEEN_ENDGAME = 4  # Not implemented

    def __init__(self, board, endgame_type):
        self.board = board
        self.endgame_type = endgame_type

    def _distance(self, board, sq1, sq2):
        assert(sq1 != sq2)
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        sq2_file_index = chess.file_index(sq2)
        sq2_rank_index = chess.rank_index(sq2)

        return (abs(sq1_file_index - sq2_file_index) + abs(sq1_rank_index - sq2_rank_index))

    def _get_king_movement_area(self, board, sq1, king_sq):
        # Determines the number of squares the (enemy) king is limited to
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        if (king_file_index < sq1_file_index):
            if (king_rank_index < sq1_rank_index):
                # King SW of rook
                return (sq1_file_index * sq1_rank_index)
            else:
                # King NW of rook
                return (sq1_file_index * (7 - sq1_rank_index))
        else:
            if (king_rank_index < sq1_rank_index):
                # King SE of rook
                return ((7 - sq1_file_index) * sq1_rank_index)
            else:
                # King NE of rook
                return ((7 - sq1_file_index) * (7 - sq1_rank_index))

    def _is_king_picking(self, board, sq1, king_sq, enemy_king_sq):
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)
        enemy_king_file_index = chess.file_index(enemy_king_sq)
        enemy_king_rank_index = chess.rank_index(enemy_king_sq)

        if (enemy_king_file_index < sq1_file_index):
            if (enemy_king_rank_index < sq1_rank_index):
                # King SW of rook
                if (king_file_index < sq1_file_index and king_rank_index == sq1_rank_index):
                    return True
                if (king_rank_index < sq1_rank_index and king_file_index == sq1_file_index):
                    return True
            else:
                # King NW of rook
                if (king_file_index < sq1_file_index and king_rank_index == sq1_rank_index):
                    return True
                if (king_rank_index > sq1_rank_index and king_file_index == sq1_file_index):
                    return True
        else:
            if (enemy_king_rank_index < sq1_rank_index):
                # King SE of rook
                if (king_file_index > sq1_file_index and king_rank_index == sq1_rank_index):
                    return True
                if (king_rank_index < sq1_rank_index and king_file_index == sq1_file_index):
                    return True
            else:
                # King NE of rook
                if (king_file_index > sq1_file_index and king_rank_index == sq1_rank_index):
                    return True
                if (king_rank_index > sq1_rank_index and king_file_index == sq1_file_index):
                    return True
        return False

    def _both_kings_same_quadrant(self, board, queen_sq, king_sq, enemy_king_sq):
        queen_file_index = chess.file_index(queen_sq)
        queen_rank_index = chess.rank_index(queen_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)
        enemy_king_file_index = chess.file_index(enemy_king_sq)
        enemy_king_rank_index = chess.rank_index(enemy_king_sq)

        QUAD_SW = 1
        QUAD_SE = 2
        QUAD_NW = 3
        QUAD_NE = 4

        quad_king = QUAD_SW
        quad_enemy_king = QUAD_SW

        if (king_file_index < queen_file_index):
            if (king_rank_index < queen_rank_index):
                # King SW of rook
                quad_king = QUAD_SW
            else:
                # King NW of rook
                quad_king = QUAD_NW
        else:
            if (king_rank_index < queen_rank_index):
                # King SE of rook
                quad_king = QUAD_SE
            else:
                # King NE of rook
                quad_king = QUAD_NE

        if (enemy_king_file_index < queen_file_index):
            if (enemy_king_rank_index < queen_rank_index):
                # Enemy king SW of rook
                quad_enemy_king = QUAD_SW
            else:
                # Enemy king NW of rook
                quad_enemy_king = QUAD_NW
        else:
            if (enemy_king_rank_index < queen_rank_index):
                # Enemy king SE of rook
                quad_enemy_king = QUAD_SE
            else:
                # Enemy king NE of rook
                quad_enemy_king = QUAD_NE

        return quad_king == quad_enemy_king

    def _is_piece_protected_by_king(self, board, sq1, king_sq):
        assert(sq1 != king_sq)
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        return (abs(sq1_file_index - king_file_index) <= 1 and abs(sq1_rank_index - king_rank_index) <= 1)

    def _get_finish_move_endgame_1(self, board, rook_sq, king_sq, enemy_king_sq):
        rook_file_index = chess.file_index(rook_sq)
        rook_rank_index = chess.rank_index(rook_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)
        enemy_king_file_index = chess.file_index(enemy_king_sq)
        enemy_king_rank_index = chess.rank_index(enemy_king_sq)

        move = None

        if (king_rank_index == enemy_king_rank_index):
            if (abs(king_file_index - enemy_king_file_index) == 2):
                if (abs(rook_rank_index - king_rank_index) == 1):
                    move = chess.SQUARE_NAMES[rook_sq] + chess.SQUARE_NAMES[rook_rank_index * 8 + king_file_index]
        
        if (king_file_index == enemy_king_file_index):
            if (abs(king_rank_index - enemy_king_rank_index) == 2):
                if (abs(rook_file_index - king_file_index) == 1):
                    move = chess.SQUARE_NAMES[rook_sq] + chess.SQUARE_NAMES[king_rank_index * 8 + rook_sq % 8]

        return move

    # ONE_ROOK_ENDGAME
    def _get_move_endgame_1(self, board):
        assert(len(board.pieces(chess.ROOK, board.turn)) == 1)
        assert(len(board.pieces(chess.KING, board.turn)) == 1)
        assert(len(board.pieces(chess.KING, not board.turn)) == 1)
        
        best_move = None
        
        rook_sq = list(board.pieces(chess.ROOK, board.turn))[0]
        king_sq = list(board.pieces(chess.KING, board.turn))[0]
        enemy_king_sq = list(board.pieces(chess.KING, not board.turn))[0]
        is_rook_attacked = list(board.attackers(not board.turn, rook_sq))
        is_rook_protected = self._is_piece_protected_by_king(board, rook_sq, king_sq)
        min_enemy_king_area = self._get_king_movement_area(board, rook_sq, enemy_king_sq)
        
        if min_enemy_king_area == 2:
            best_move = self._get_finish_move_endgame_1(board, rook_sq, king_sq, enemy_king_sq)
            if best_move:
                return str(best_move)
        
        legal_moves = list(board.legal_moves)
        child_boards = []

        min_total_d = float("inf")
        prev_best_move = legal_moves[0]
        best_move = legal_moves[0]

        for move in legal_moves:
            child_board = board.copy()
            child_board.push(move)
            if (child_board.is_checkmate()):
                # Make this move as it will checkmate
                best_move = move
                break
            elif (child_board.is_check() or child_board.is_stalemate()):
                continue
            else:
                rook_sq = list(child_board.pieces(chess.ROOK, not child_board.turn))[0]
                king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                enemy_king_area = self._get_king_movement_area(child_board, rook_sq, enemy_king_sq)
                child_is_rook_attacked = list(child_board.attackers(child_board.turn, rook_sq))
                child_is_rook_protected = self._is_rook_protected(child_board, rook_sq, king_sq)
                
                if self._is_king_picking(child_board, rook_sq, king_sq, enemy_king_sq):
                    # Don't make this move as the king is picking the rook
                    continue
                if child_is_rook_attacked and not child_is_rook_protected:
                    # Don't make this move as it leaves our rook unprotected and attacked
                    continue
                elif child_is_rook_attacked:
                    assert(child_is_rook_protected)
                    d = self._distance(child_board, king_sq, rook_sq) + self._distance(child_board, rook_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
                
                    if (enemy_king_area <= min_enemy_king_area) and (d <= min_total_d):
                        if (enemy_king_area == min_enemy_king_area) and (d == min_total_d):
                            if (random.random() < 0.5):
                                continue
                        min_total_d = d
                        min_enemy_king_area = enemy_king_area
                        prev_best_move = best_move
                        best_move = move
                elif not child_is_rook_protected:
                    assert(not child_is_rook_attacked)
                    d = self._distance(child_board, king_sq, rook_sq) + self._distance(child_board, rook_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
                
                    if (d <= min_total_d):
                        if (d == min_total_d):
                            if (random.random() < 0.5):
                                continue
                        min_total_d = d
                        prev_best_move = best_move
                        best_move = move
                else:
                    d = self._distance(child_board, king_sq, rook_sq) + self._distance(child_board, rook_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
                
                    if  (d <= min_total_d) and (enemy_king_area <= min_enemy_king_area):
                        if (enemy_king_area == min_enemy_king_area) and (d == min_total_d):
                            if (random.random() < 0.5):
                                continue
                        min_total_d = d
                        prev_best_move = best_move
                        best_move = move
                    
        return str(best_move)

    # ONE_QUEEN_ENDGAME
    def _get_move_endgame_2(self, board):
        assert(len(board.pieces(chess.QUEEN, board.turn)) == 1)
        assert(len(board.pieces(chess.KING, board.turn)) == 1)
        assert(len(board.pieces(chess.KING, not board.turn)) == 1)
        
        best_move = None
        
        queen_sq = list(board.pieces(chess.QUEEN, board.turn))[0]
        queen_sq_copy = queen_sq
        king_sq = list(board.pieces(chess.KING, board.turn))[0]
        king_sq_copy = king_sq
        enemy_king_sq = list(board.pieces(chess.KING, not board.turn))[0]
        
        min_enemy_king_area = self._get_king_movement_area(board, queen_sq, enemy_king_sq)
        enemy_king_trapped = min_enemy_king_area == 3

        legal_moves = list(board.legal_moves)

        min_total_d = float("inf")
        prev_best_move = None
        best_move = legal_moves[0]
        kings_same_quadrant = False

        if (self._both_kings_same_quadrant(board, queen_sq, king_sq, enemy_king_sq)):
            kings_same_quadrant = True

        # if kings_same_quadrant:
        #     # Take first queen move that doesn't stalemate and doesn't check
        #     # This is to deal with cases like "8/8/8/8/8/5Q2/8/K1k5 w - - 0 1"
        #     kings_same_quadrant = False
        #     print "Best move kings are in same quadrant, looking for queen move"
        #     for move in legal_moves:
        #         print "Move {0}".format(move)
        #         print "Move from {0} king was at {1} queen was at {2}".format(move.from_square, king_sq_copy, queen_sq_copy)
        #         child_board = board.copy()
        #         child_board.push(move)
                
        #         queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
        #         king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
        #         enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                
        #         if (self._both_kings_same_quadrant(board, queen_sq, king_sq, enemy_king_sq)):
        #             kings_same_quadrant = True
        #         if not (child_board.is_checkmate() or child_board.is_check() or child_board.is_stalemate()):
        #             best_move = move
        #             print "New best move {0}".format(best_move)
        #             break

        for move in legal_moves:
            print "Move: {0}".format(move)
            child_board = board.copy()
            child_board.push(move)
            if (child_board.is_checkmate()):
                # Make this move as it will checkmate
                best_move = move
                break
            elif (child_board.is_check() or child_board.is_stalemate()):
                continue
            else:
                queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
                king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                enemy_king_area = self._get_king_movement_area(child_board, queen_sq, enemy_king_sq)
                d = self._distance(child_board, king_sq, enemy_king_sq)
                print "d: {0} min_d: {1}".format(d, min_total_d)
                
                if (enemy_king_trapped):
                    print "Test"
                    if (d <= min_total_d):
                        if (enemy_king_area <= min_enemy_king_area):
                            min_enemy_king_area = enemy_king_area
                            min_total_d = d
                            prev_best_move = best_move
                            best_move = move
                    # d = self._distance(child_board, king_sq, queen_sq) + self._distance(child_board, queen_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
                # d = self._distance(child_board, queen_sq, enemy_king_sq)
                elif (enemy_king_area < min_enemy_king_area):
                # if (enemy_king_area <= min_enemy_king_area) and (d <= min_total_d):
                    # if (enemy_king_area == min_enemy_king_area) and (d == min_total_d):
                    #     if (random.random() < 0.5):
                    #         continue
                    # min_total_d = d
                    min_enemy_king_area = enemy_king_area
                    prev_best_move = best_move
                    best_move = move
        
        print "First best move {0}".format(best_move)
        
        if not prev_best_move:
            print "PROBLEM"
            # assert(kings_same_quadrant)
            min_total_d = float("inf")
            # Take good queen move that doesn't stalemate and doesn't check
            # This is to deal with cases like "8/8/8/8/8/5Q2/8/K1k5 w - - 0 1"
            # kings_same_quadrant = False
            print "Best move kings are in same quadrant, looking for queen move"
            for move in legal_moves:
                print "Move {0}".format(move)
                print "Move from {0} king was at {1} queen was at {2}".format(move.from_square, king_sq_copy, queen_sq_copy)
                child_board = board.copy()
                child_board.push(move)
                
                queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
                king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                
                if not (child_board.is_checkmate() or child_board.is_check() or child_board.is_stalemate()):
                    d = self._distance(child_board, queen_sq, enemy_king_sq)
                    if (self._is_piece_protected_by_king(child_board, queen_sq, king_sq)) and (d < min_total_d):
                        best_move = move
                        print "New best move {0}".format(best_move)
                        continue

        return str(best_move)

    def get_best_move(self, board):
        if self.endgame_type == self.ONE_ROOK_ENDGAME:
            return self._get_move_endgame_1(board)
        elif self.endgame_type == self.ONE_QUEEN_ENDGAME:
            return self._get_move_endgame_2(board)

        print "Endgame {0} called but not implemented yet, exiting".format(self.endgame_type)
        exit(0)
