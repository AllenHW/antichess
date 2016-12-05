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

    def _is_knight_distance_away(self, board, sq1, sq2):
        assert(sq1 != sq2)
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        sq2_file_index = chess.file_index(sq2)
        sq2_rank_index = chess.rank_index(sq2)

        file_diff = abs(sq1_file_index - sq2_file_index) 
        rank_diff = abs(sq1_rank_index - sq2_rank_index)

        return (file_diff == 1 and rank_diff == 2) or (file_diff == 2 and rank_diff == 1)

    def _get_king_movement_area(self, board, sq1, king_sq):
        # Determines the number of squares the (enemy) king is limited to
        sq1_file_index = chess.file_index(sq1)
        sq1_rank_index = chess.rank_index(sq1)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        if (sq1_file_index == king_file_index or sq1_rank_index == king_rank_index):
            return float("inf")

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

        quad_king = None
        quad_enemy_king = None

        if (king_file_index < queen_file_index):
            if (king_rank_index < queen_rank_index):
                # King SW of rook
                quad_king = QUAD_SW
            elif (king_rank_index > queen_rank_index):
                # King NW of rook
                quad_king = QUAD_NW
        elif (king_file_index > queen_file_index):
            if (king_rank_index < queen_rank_index):
                # King SE of rook
                quad_king = QUAD_SE
            elif (king_rank_index > queen_rank_index):
                # King NE of rook
                quad_king = QUAD_NE

        if (enemy_king_file_index < queen_file_index):
            if (enemy_king_rank_index < queen_rank_index):
                # Enemy king SW of rook
                quad_enemy_king = QUAD_SW
            elif (enemy_king_rank_index > queen_rank_index):
                # Enemy king NW of rook
                quad_enemy_king = QUAD_NW
        elif (enemy_king_file_index > queen_file_index):
            if (enemy_king_rank_index < queen_rank_index):
                # Enemy king SE of rook
                quad_enemy_king = QUAD_SE
            elif (enemy_king_rank_index > queen_rank_index):
                # Enemy king NE of rook
                quad_enemy_king = QUAD_NE

        return quad_king and quad_enemy_king and quad_king == quad_enemy_king

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

    def _get_finish_move_endgame_2(self, board, queen_sq, king_sq, enemy_king_sq):
        queen_file_index = chess.file_index(queen_sq)
        queen_rank_index = chess.rank_index(queen_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)
        enemy_king_file_index = chess.file_index(enemy_king_sq)
        enemy_king_rank_index = chess.rank_index(enemy_king_sq)

        move = None

        if (queen_sq == chess.E2) and (king_sq == chess.E1) and (enemy_king_sq == chess.G1):
            return "e2d2"
        elif (queen_sq == chess.D2) and (king_sq == chess.D1) and (enemy_king_sq == chess.B1):
            return "d2e2"
        elif (queen_sq == chess.B4) and (king_sq == chess.A4) and (enemy_king_sq == chess.A2):
            return "b4b5"
        elif (queen_sq == chess.B5) and (king_sq == chess.A5) and (enemy_king_sq == chess.A7):
            return "b5b4"
        elif (queen_sq == chess.D7) and (king_sq == chess.D8) and (enemy_king_sq == chess.B8):
            return "d7e7"
        elif (queen_sq == chess.E7) and (king_sq == chess.E8) and (enemy_king_sq == chess.G8):
            return "e7d7"
        elif (queen_sq == chess.G5) and (king_sq == chess.H5) and (enemy_king_sq == chess.H7):
            return "g5g4"
        elif (queen_sq == chess.G4) and (king_sq == chess.G4) and (enemy_king_sq == chess.H2):
            return "g4g5"

        if (queen_sq == chess.E2) and (king_sq == chess.E1) and (enemy_king_sq == chess.H1):
            return "e2g4"
        elif (queen_sq == chess.D2) and (king_sq == chess.D1) and (enemy_king_sq == chess.A1):
            return "d2b4"
        elif (queen_sq == chess.B4) and (king_sq == chess.A4) and (enemy_king_sq == chess.A1):
            return "b4d2"
        elif (queen_sq == chess.B5) and (king_sq == chess.A5) and (enemy_king_sq == chess.A8):
            return "b5d7"
        elif (queen_sq == chess.D7) and (king_sq == chess.D8) and (enemy_king_sq == chess.A8):
            return "d7b5"
        elif (queen_sq == chess.E7) and (king_sq == chess.E8) and (enemy_king_sq == chess.H8):
            return "e7g5"
        elif (queen_sq == chess.G5) and (king_sq == chess.H5) and (enemy_king_sq == chess.H8):
            return "g5e7"
        elif (queen_sq == chess.G4) and (king_sq == chess.H4) and (enemy_king_sq == chess.H1):
            return "g4e2"

        if (queen_sq == chess.D2) and (king_sq == chess.E1) and (enemy_king_sq == chess.H1):
            return "e1f2"
        elif (queen_sq == chess.E2) and (king_sq == chess.D1) and (enemy_king_sq == chess.A1):
            return "d1c2"
        elif (queen_sq == chess.B5) and (king_sq == chess.A4) and (enemy_king_sq == chess.A1):
            return "a4b3"
        elif (queen_sq == chess.B4) and (king_sq == chess.A5) and (enemy_king_sq == chess.A8):
            return "a5b6"
        elif (queen_sq == chess.E7) and (king_sq == chess.D8) and (enemy_king_sq == chess.A8):
            return "d8c7"
        elif (queen_sq == chess.D7) and (king_sq == chess.E8) and (enemy_king_sq == chess.H8):
            return "e8f7"
        elif (queen_sq == chess.G4) and (king_sq == chess.H5) and (enemy_king_sq == chess.H8):
            return "h5g6"
        elif (queen_sq == chess.G5) and (king_sq == chess.H4) and (enemy_king_sq == chess.H1):
            return "h4g3"

        return move

    # ONE_ROOK_ENDGAME
    def _get_move_endgame_1(self, board):        
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
                child_is_rook_protected = self._is_piece_protected_by_king(child_board, rook_sq, king_sq)
                
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
        queen_sq = list(board.pieces(chess.QUEEN, board.turn))[0]
        queen_sq_copy = queen_sq
        king_sq = list(board.pieces(chess.KING, board.turn))[0]
        king_sq_copy = king_sq
        enemy_king_sq = list(board.pieces(chess.KING, not board.turn))[0]
        
        min_enemy_king_area = self._get_king_movement_area(board, queen_sq, enemy_king_sq)
        enemy_king_trapped = min_enemy_king_area == 3

        legal_moves = list(board.legal_moves)

        # min_total_d = float("inf")
        min_total_d = self._distance(board, king_sq, enemy_king_sq)
        prev_best_move = None
        best_move = legal_moves[0]
        backup_move = None
        kings_same_quadrant = False
        queen_knight_distance_away = self._is_knight_distance_away(board, queen_sq, enemy_king_sq)

        kings_same_quadrant = self._both_kings_same_quadrant(board, queen_sq, king_sq, enemy_king_sq)
        if self._is_knight_distance_away(board, queen_sq, enemy_king_sq):
            print "Queen knight distance away from king"

        finish_move = self._get_finish_move_endgame_2(board, queen_sq, king_sq, enemy_king_sq)
        if finish_move:
            print "Finish move: {0}".format(finish_move)
            return finish_move

        for move in legal_moves:
            print "===== CASE TWO ======="
            print move
            child_board = board.copy()
            child_board.push(move)
            if (child_board.is_checkmate()):
                # Make this move as it will checkmate
                prev_best_move = best_move
                best_move = move
                break
            elif (child_board.is_check() or child_board.is_stalemate()):
                continue
            # elif queen_knight_distance_away and move.from_square == queen_sq:
            #     continue
            else:
                queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
                king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                enemy_king_area = self._get_king_movement_area(child_board, queen_sq, enemy_king_sq)
                d = self._distance(child_board, king_sq, enemy_king_sq)
                child_is_queen_attacked = list(child_board.attackers(child_board.turn, queen_sq))
                child_is_queen_protected = self._is_piece_protected_by_king(child_board, queen_sq, king_sq)
                # print "enemy_king_sq {0} enemy_king_area {1}".format(enemy_king_sq, enemy_king_area)
                print "Enemy king trapped? {0}".format(enemy_king_trapped)
                print "enemy king area {0} min_area {1}".format(enemy_king_area, min_enemy_king_area)
                
                # if self._is_king_picking(child_board, queen_sq, king_sq, enemy_king_sq):
                #     print "Case 1"
                #     continue
                if child_is_queen_attacked and not child_is_queen_protected:
                    print "Queen attacked and not protected"
                    continue
                elif self._both_kings_same_quadrant(child_board, queen_sq, king_sq, enemy_king_sq):
                    print "Same quadrant"
                    continue
                if (enemy_king_trapped):
                    if (d < min_total_d):
                        if (enemy_king_area <= min_enemy_king_area):
                            min_enemy_king_area = enemy_king_area
                            min_total_d = d
                            prev_best_move = best_move
                            best_move = move

                elif (enemy_king_area <= min_enemy_king_area) and (d <= min_total_d):
                # elif (enemy_king_area < min_enemy_king_area) and (d < min_total_d):
                    min_enemy_king_area = enemy_king_area
                    prev_best_move = best_move
                    best_move = move
                    # return str(best_move)

        print "Case two best move {0}".format(best_move)
        if prev_best_move:
            print "Case one sufficient, returning move {0}".format(best_move)
            return str(best_move)
        else:
            print "Onto case 1"

        if queen_knight_distance_away:
            print "======== CASE ONE ========="
            for move in legal_moves:
                print move
                child_board = board.copy()
                child_board.push(move)
                if (child_board.is_checkmate()):
                    # Make this move as it will checkmate
                    prev_best_move = best_move
                    best_move = move
                    break
                elif (child_board.is_check() or child_board.is_stalemate()):
                    continue
                # elif queen_knight_distance_away and move.from_square == queen_sq:
                #     continue
                else:
                    queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
                    king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                    enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                    enemy_king_area = self._get_king_movement_area(child_board, queen_sq, enemy_king_sq)
                    d = self._distance(child_board, king_sq, enemy_king_sq)
                    
                    if (d < min_total_d):
                        min_total_d = d
                        prev_best_move = best_move
                        best_move = move
            print "Queen knight distance away, returning best move {0}".format(best_move)
            return str(best_move)

        print "Case THREE??????"

        print "prev best move {0}".format(prev_best_move)
        print "best move {0}".format(best_move)
        print "min_d {0}".format(min_total_d)

        # Check case where enemy king trapped and min_total_d = inf

        if not prev_best_move or (enemy_king_trapped and min_total_d == float("inf")):
            prev_best_move = None
            print "****************PROBLEM"
            # exit(0)
            min_total_d = float("inf")
            # Take good queen move that doesn't stalemate and doesn't check
            # This is to deal with cases like "8/8/8/8/8/5Q2/8/K1k5 w - - 0 1"
            for move in legal_moves:
                print "Move {0}".format(move)
                # kings_same_quadrant = False
                child_board = board.copy()
                child_board.push(move)
                
                queen_sq = list(child_board.pieces(chess.QUEEN, not child_board.turn))[0]
                king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
                enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
                enemy_king_area = self._get_king_movement_area(child_board, queen_sq, enemy_king_sq)
                child_is_queen_attacked = list(child_board.attackers(child_board.turn, queen_sq))
                child_is_queen_protected = self._is_piece_protected_by_king(child_board, queen_sq, king_sq)
                
                print "enemy king area {0}".format(enemy_king_area)
                # if (self._both_kings_same_quadrant(child_board, queen_sq, king_sq, enemy_king_sq)):
                #     kings_same_quadrant = True

                if not (child_board.is_stalemate() and (not child_is_queen_attacked or child_is_queen_protected)):
                    if (random.random() < 0.5):
                        best_move = move
                        break

                # print "checkmate? {0} stalemate? {1}".format(child_board.is_checkmate(), child_board.is_stalemate())
                # if not (child_board.is_checkmate() or child_board.is_stalemate()):
                #     d = self._distance(child_board, queen_sq, enemy_king_sq)
                #     print "d: {0} min_d: {1}".format(d, min_total_d)
                #     # if (d < min_total_d):
                #     print "is queen protected by king after move? {0}".format(self._is_piece_protected_by_king(child_board, queen_sq, king_sq))
                #     if self._is_piece_protected_by_king(child_board, queen_sq, king_sq):
                #         backup_move = move
                #     if (self._is_piece_protected_by_king(child_board, queen_sq, king_sq)) and (enemy_king_area <= min_enemy_king_area) and not kings_same_quadrant:
                #         print "Found better move {0}".format(move)
                #         # min_total_d = d
                #         min_enemy_king_area = enemy_king_area
                #         prev_best_move = best_move
                #         best_move = move
                #         continue

        print "Backup move: {0}".format(backup_move)
        if not prev_best_move:
            best_move = backup_move
        return str(best_move)

    def _get_move_endgame_3_and_4(self, board):        
        rook_sq = list(board.pieces(chess.ROOK, board.turn))[0]
        king_sq = list(board.pieces(chess.KING, board.turn))[0]
        enemy_king_sq = list(board.pieces(chess.KING, not board.turn))[0]
        
        is_rook_attacked = list(board.attackers(not board.turn, rook_sq))
        is_rook_protected = self._is_piece_protected_by_king(board, rook_sq, king_sq)
        min_enemy_king_area = self._get_king_movement_area(board, rook_sq, enemy_king_sq)
        
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
                child_is_rook_protected = self._is_piece_protected_by_king(child_board, rook_sq, king_sq)
                
                if child_is_rook_attacked and not child_is_rook_protected:
                    # Make this move to simplify to ONE_ROOK_ENDGAME
                    best_move = move
                    break
            
                d = self._distance(child_board, king_sq, rook_sq) + self._distance(child_board, rook_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
            
                if  (d <= min_total_d) and (enemy_king_area <= min_enemy_king_area):
                    if (enemy_king_area == min_enemy_king_area) and (d == min_total_d):
                        if (random.random() < 0.5):
                            continue
                    min_total_d = d
                    prev_best_move = best_move
                    best_move = move
        
        return str(best_move)

    # def _get_move_endgame_4(self, board):
    #     assert(len(board.pieces(chess.ROOK, board.turn)) == 1)
    #     assert(len(board.pieces(chess.QUEEN, board.turn)) == 1)
    #     assert(len(board.pieces(chess.KING, board.turn)) == 1)
    #     assert(len(board.pieces(chess.KING, not board.turn)) == 1)
        
    #     rook_sq = list(board.pieces(chess.ROOK, board.turn))[0]
    #     king_sq = list(board.pieces(chess.KING, board.turn))[0]
    #     enemy_king_sq = list(board.pieces(chess.KING, not board.turn))[0]
        
    #     is_rook_attacked = list(board.attackers(not board.turn, rook_sq))
    #     is_rook_protected = self._is_piece_protected_by_king(board, rook_sq, king_sq)
    #     min_enemy_king_area = self._get_king_movement_area(board, rook_sq, enemy_king_sq)
        
    #     legal_moves = list(board.legal_moves)
    #     child_boards = []

    #     min_total_d = float("inf")
    #     prev_best_move = legal_moves[0]
    #     best_move = legal_moves[0]

    #     for move in legal_moves:
    #         child_board = board.copy()
    #         child_board.push(move)
    #         if (child_board.is_checkmate()):
    #             # Make this move as it will checkmate
    #             best_move = move
    #             break
    #         elif (child_board.is_check() or child_board.is_stalemate()):
    #             continue
    #         else:
    #             rook_sq = list(child_board.pieces(chess.ROOK, not child_board.turn))[0]
    #             king_sq = list(child_board.pieces(chess.KING, not child_board.turn))[0]
    #             enemy_king_sq = list(child_board.pieces(chess.KING, child_board.turn))[0]
    #             enemy_king_area = self._get_king_movement_area(child_board, rook_sq, enemy_king_sq)
    #             child_is_rook_attacked = list(child_board.attackers(child_board.turn, rook_sq))
    #             child_is_rook_protected = self._is_piece_protected_by_king(child_board, rook_sq, king_sq)
                
    #             if child_is_rook_attacked and not child_is_rook_protected:
    #                 # Make this move to simplify to ONE_QUEEN_ENDGAME
    #                 best_move = move
    #                 break
            
    #             d = self._distance(child_board, king_sq, rook_sq) + self._distance(child_board, rook_sq, enemy_king_sq) + self._distance(child_board, king_sq, enemy_king_sq)
            
    #             if  (d <= min_total_d) and (enemy_king_area <= min_enemy_king_area):
    #                 if (enemy_king_area == min_enemy_king_area) and (d == min_total_d):
    #                     if (random.random() < 0.5):
    #                         continue
    #                 min_total_d = d
    #                 prev_best_move = best_move
    #                 best_move = move
        
    #     return str(best_move)

    def get_best_move(self, board):
        if self.endgame_type == self.ONE_ROOK_ENDGAME:
            assert(len(board.pieces(chess.ROOK, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, not board.turn)) == 1)
            return self._get_move_endgame_1(board)
        elif self.endgame_type == self.ONE_QUEEN_ENDGAME:
            assert(len(board.pieces(chess.QUEEN, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, not board.turn)) == 1)
            return self._get_move_endgame_2(board)
        elif self.endgame_type == self.TWO_ROOKS_ENDGAME:
            assert(len(board.pieces(chess.ROOK, board.turn)) == 2)
            assert(len(board.pieces(chess.KING, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, not board.turn)) == 1)
            return self._get_move_endgame_3_and_4(board)
        elif self.endgame_type == self.ROOK_AND_QUEEN_ENDGAME:
            assert(len(board.pieces(chess.ROOK, board.turn)) == 1)
            assert(len(board.pieces(chess.QUEEN, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, board.turn)) == 1)
            assert(len(board.pieces(chess.KING, not board.turn)) == 1)
            return self._get_move_endgame_3_and_4(board)

        print "Endgame {0} called but not implemented yet, exiting".format(self.endgame_type)
        exit(0)
