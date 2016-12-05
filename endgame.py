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

    def _distance(self, board, rook_sq, king_sq):
        assert(rook_sq != king_sq)
        rook_file_index = chess.file_index(rook_sq)
        rook_rank_index = chess.rank_index(rook_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        return (abs(rook_file_index - king_file_index) + abs(rook_rank_index - king_rank_index))

    def _get_king_movement_area(self, board, rook_sq, king_sq):
        rook_file_index = chess.file_index(rook_sq)
        rook_rank_index = chess.rank_index(rook_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        if (king_file_index < rook_file_index):
            if (king_rank_index < rook_rank_index):
                # King SW of rook
                return (rook_file_index * rook_rank_index)
            else:
                # King NW of rook
                return (rook_file_index * (7 - rook_rank_index))
        else:
            if (king_rank_index < rook_rank_index):
                # King SE of rook
                return ((7 - rook_file_index) * rook_rank_index)
            else:
                # King NE of rook
                return ((7 - rook_file_index) * (7 - rook_rank_index))

    def _is_king_picking(self, board, rook_sq, king_sq, enemy_king_sq):
        rook_file_index = chess.file_index(rook_sq)
        rook_rank_index = chess.rank_index(rook_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)
        enemy_king_file_index = chess.file_index(enemy_king_sq)
        enemy_king_rank_index = chess.rank_index(enemy_king_sq)

        if (enemy_king_file_index < rook_file_index):
            if (enemy_king_rank_index < rook_rank_index):
                # King SW of rook
                if (king_file_index < rook_file_index and king_rank_index == rook_rank_index):
                    return True
                if (king_rank_index < rook_rank_index and king_file_index == rook_file_index):
                    return True
            else:
                # King NW of rook
                if (king_file_index < rook_file_index and king_rank_index == rook_rank_index):
                    return True
                if (king_rank_index > rook_rank_index and king_file_index == rook_file_index):
                    return True
        else:
            if (enemy_king_rank_index < rook_rank_index):
                # King SE of rook
                if (king_file_index > rook_file_index and king_rank_index == rook_rank_index):
                    return True
                if (king_rank_index < rook_rank_index and king_file_index == rook_file_index):
                    return True
            else:
                # King NE of rook
                if (king_file_index > rook_file_index and king_rank_index == rook_rank_index):
                    return True
                if (king_rank_index > rook_rank_index and king_file_index == rook_file_index):
                    return True
        return False

    def _is_rook_protected(self, board, rook_sq, king_sq):
        assert(rook_sq != king_sq)
        rook_file_index = chess.file_index(rook_sq)
        rook_rank_index = chess.rank_index(rook_sq)
        king_file_index = chess.file_index(king_sq)
        king_rank_index = chess.rank_index(king_sq)

        return (abs(rook_file_index - king_file_index) <= 1 and abs(rook_rank_index - king_rank_index) <= 1)

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
        is_rook_protected = self._is_rook_protected(board, rook_sq, king_sq)
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

    def get_best_move(self, board):
        if self.endgame_type == self.ONE_ROOK_ENDGAME:
            return self._get_move_endgame_1(board)

        return None
        # print "Endgame {0} not implemented yet, exiting".format(self.endgame_type)
        # exit(0)
