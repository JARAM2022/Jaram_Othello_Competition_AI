from copy import deepcopy
from random import shuffle
import socketio
import math
import numpy as np
import zlib
import time
PLAYER = {
    1: 'W',
    0: 'B',
    'W': 1,
    'B': 0
}
INFINITI = 999999

class NoPlaceableError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


# AI를 위한 오델로 게임판
# ref : https://github.com/yuxuan006/Othello
class AiBoard:

    def opponent(self, x):
        """ Given a string representing a color (must be either "B" or "W"),
            return the opposing color """
        if x == 0:
            return 1
        elif x == 1:
            return 0
        else:
            return "."

    def validMove(self, board, color, pos):
        """ Given a 2D array representing a board, a string
            representing a color, and a tuple representing a
            position, return true if the position is a valid
            move for the color """
        if board[pos[0]][pos[1]] != -1:
            return False

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    if self.canFlip(board, color, pos, (i, j)):
                        return True
        return False

    def valid(self, board, color, move):
        """ Given a 2D array representing a board, a string
            representing a color, and either a tuple representing a
            position or the string "pass", return true if the move
            is a valid for the color """
        if move == "pass":
            for i in range(0, 8):
                for j in range(0, 8):
                    if self.validMove(board, color, (i, j)):
                        return False
            return True
        else:
            return self.validMove(board, color, move)

    def validPos(self, x, y):
        """ Return true of the (x,y) position is within the board """
        return x >= 0 and x < 8 and y >= 0 and y < 8

    def doFlip(self, board, color, pos, direction):
        """ Given a 2D array representing a board, a color, a position
            to move to, and a tuple representing a direction ( (-1,0)
            for up, (-1,1) for up and to the right, (0,1) for to the right,
            and so on), flip all the pieces in the direction until a
            piece of the same color is found """
        currX = pos[0] + direction[0]
        currY = pos[1] + direction[1]

        while board[currX][currY] == self.opponent(color):
            board[currX][currY] = color
            (currX, currY) = (currX + direction[0], currY + direction[1])

        return board

    def doMove(self, board, color, pos):
        """ Given a 2D array representing a board, a color, and a position,
            implement the move on the board.  Note that the move is assumed
            to be valid """

        if pos != "pass":
            if self.validMove(board, color, pos):

                board[pos[0]][pos[1]] = color
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i != 0 or j != 0:
                            if self.canFlip(board, color, pos, (i, j)):
                                board = self.doFlip(board, color, pos, (i, j))

        return board

    def canFlip(self, board, color, pos, direction):
        """ Given a 2D array representing a board, a color, a position
            to move to, and a tuple representing a direction ( (-1,0)
            for up, (-1,1) for up and to the right, (0,1) for to the right,
            and so on), determine if there is a sequence of opponent pieces,
            followed by a color piece, that would allow a flip in this direction
            from this position, if a color piece is placed at pos """

        currX = pos[0] + direction[0]
        currY = pos[1] + direction[1]

        if not self.validPos(currX, currY):
            return False

        if board[currX][currY] != self.opponent(color):
            return False

        while True:
            (currX, currY) = (currX + direction[0], currY + direction[1])
            if not self.validPos(currX, currY):
                return False
            if board[currX][currY] == color:
                return True
            if board[currX][currY] == -1:
                return False

    # For fun, here is a one-line board printer, without the
    # row and column labels
    # print "\n".join(["".join(x) for x in board])

    def gameOver(self, board):
        """ return true if the game is over, that is, no valid moves """
        return self.valid(board, 0, 'pass') and self.valid(board, 1, 'pass')

    def score(self, board):
        """ returns the current score for the board as a tuple
            containing # of black pieces, # of white pieces """
        black = white = 0
        for row in board:
            for square in row:
                if square == 0:
                    black = black + 1

                elif square == 1:
                    white = white + 1

        return (black, white)

    def get_valid_actions(self, player, board):
        moves = []
        for row in range(8):
            for col in range(8):
                if self.valid(board, player, (row, col)):
                    moves.append((row, col))

        return moves

    def printBoard(self, board):

        for row in board:
            print(" ".join([str(x) for x in row]))


# class Controller:
#
#

class AI:

    def __init__(self):
        # 각 구역별 가중치
        # ref https://github.com/hylbyj/Alpha-Beta-Pruning-for-Othello-Game/blob/master/readme_alpha_beta.txt

        # self.adv = [
        #     [100, -10, 10, 3, 3, 10, -10, 100],
        #     [-10, -20, -3, -3, -3, -3, -20, -10],
        #     [10, -3, 8, 1, 1, 8, -3, 10],
        #     [3, -3, 1, 1, 1, 1, -3, 3],
        #     [3, -3, 1, 1, 1, 1, -3, 3],
        #     [10, -3, 8, 1, 1, 8, -3, 10],
        #     [-10, -20, -3, -3, -3, -3, -20, -10],
        #     [100, -10, 10, 3, 3, 10, -10, 100]
        # ]
        self.adv = [[4, -3, 2, 2, 2, 2, -3, 4],
                    [-3, -4, -1, -1, -1, -1, -4, -3],
                    [2, -1, 1, 0, 0, 1, -1, 2],
                    [2, -1, 0, 1, 1, 0, -1, 2],
                    [2, -1, 0, 1, 1, 0, -1, 2],
                    [2, -1, 1, 0, 0, 1, -1, 2],
                    [-3, -4, -1, -1, -1, -1, -4, -3],
                    [4, -3, 2, 2, 2, 2, -3, 4]]

        self.tmp_board = AiBoard()
        self.max_depth = 4
        self.cache = dict()

    def setup(self, player):
        self.player = player
        self.opp = self.tmp_board.opponent(player)


    def to_cache(self, array, score, target,alp,beta):

        array = np.asarray(array).ravel()
        key = "".join(str(x) for x in array) + target+"/"+ str(alp)+"/"+str(beta)

        if key not in self.cache:
            self.cache[key] = score

    def find_cache(self, array, target,alp,beta):
        array = np.asarray(array).ravel()
        key = "".join(str(x) for x in array) + target+"/"+ str(alp)+"/"+str(beta)

        if key in self.cache:
            x = self.cache[key]
            return x

        return False

    # 현재 state를 평가하는 함수
    # ref : https://github.com/yuxuan006/Othello
    # 각 구역에 따라 어드벤티지가 존재하여 외각선을 먹으면 추가 점수
    def eval_fn(self, board):

        point = 0

        for row in range(8):
            for col in range(8):
                if board[row][col] == self.player:
                    point += self.adv[row][col]

        for row in range(8):
            for col in range(8):
                if board[row][col] == self.opp:
                    point -= self.adv[row][col]

        point *= 2
        cnt_player_stone = 0
        for r in board:
            for c in r:
                if c == self.player:
                    cnt_player_stone += 1

        cnt_opp_stone = 0
        for r in board:

            for c in r:

                if c == self.opp:
                    cnt_player_stone += 1

        point += (cnt_player_stone - cnt_opp_stone) * 3

        return point

    def get_action(self, board, can_moves):
        start = time.time()
        # 만약 이동 가능한 공간이 없다면 오류.
        if not can_moves:
            raise NoPlaceableError("get Empty placeable array")

        alp, beta = -INFINITI, INFINITI
        best_score, best_move = -INFINITI, None

        for valid_action in can_moves:

            idx_score = self._min(np.copy(board), valid_action, 1, alp, beta)

            if idx_score > best_score:
                best_score = idx_score
                best_move = valid_action
                
        print(f"ai : {time.time()-start}")
        return best_move

    def _min(self, board, action, depth, alp, beta):

        copyed_board = np.copy(board)
        x = self.find_cache(copyed_board, "min",alp,beta)
        if x:
            return x

        if depth == self.max_depth:
            return self.eval_fn(copyed_board)

        copyed_board = self.tmp_board.doMove(copyed_board, self.player, action)
        lowest_score = INFINITI

        for valid_action in self.tmp_board.get_valid_actions(self.opp, copyed_board):
            idx_score = self._max(copyed_board, valid_action, depth + 1, alp, beta)

            beta = min(beta, idx_score)

            if lowest_score > idx_score:
                lowest_score = idx_score

            if lowest_score <= alp:
                break

        if lowest_score == INFINITI:
            x = self.eval_fn(copyed_board)
            return x

        # self.to_cache(board, lowest_score, "min", alp, beta)
        return lowest_score

    def _max(self, board, action, depth, alp, beta):

        copyed_board = np.copy(board)
        x = self.find_cache(copyed_board, "max", alp, beta)

        if x:
            return x

        if depth == self.max_depth:
            x = self.eval_fn(copyed_board)
            return x

        copyed_board = self.tmp_board.doMove(copyed_board, self.opp, action)

        max_score = -INFINITI

        for valid_action in self.tmp_board.get_valid_actions(self.player, copyed_board):

            idx_score = self._min(copyed_board, valid_action, depth + 1, alp, beta)
            alp = max(alp, idx_score)

            if max_score < idx_score:
                max_score = idx_score

            if max_score >= beta:
                break

        if max_score == -INFINITI:
            x = self.eval_fn(copyed_board)
            return x

        # self.to_cache(board, max_score, "max", alp, beta)
        return max_score