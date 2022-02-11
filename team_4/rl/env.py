from ai.alpbeta import AiBoard
import numpy as np


PLAYER = {
    1 : 'W',
    0 : 'B',
    'W' : 1,
    'B' : 0
}

class Othello_env:
    def __init__(self):
        self.adv = [[4, -3, 2, 2, 2, 2, -3, 4],
                    [-3, -4, -1, -1, -1, -1, -4, -3],
                    [2, -1, 1, 0, 0, 1, -1, 2],
                    [2, -1, 0, 1, 1, 0, -1, 2],
                    [2, -1, 0, 1, 1, 0, -1, 2],
                    [2, -1, 1, 0, 0, 1, -1, 2],
                    [-3, -4, -1, -1, -1, -1, -4, -3],
                    [4, -3, 2, 2, 2, 2, -3, 4]]

        self.controller = AiBoard()

        self.board = []

        self.done = False

        self.player = None

        self.opp = None

        self.reset(1)


    def reset(self,player):
        #reset player
        self.player = player

        self.opp = self.controller.opponent(self.player)

        #reset map
        result = []
        for i in range(3):
            result = result + [[-1] * 8]

        result = result + [[-1] * 3 + [1, 0] + [-1] * 3]
        result = result + [[-1] * 3 + [0, 1] + [-1] * 3]

        for i in range(3):
            result = result + [[-1] * 8]

        self.board = result
        self.done = False

    def print_board(self):

        self.controller.printBoard(self.board)

    def get_state(self,mode='1D'):
        if mode == '2D':
            return self.board

        elif mode == '1D':
            return np.asarray(self.board).ravel()

    def get_reward(self):
        # 게임이 끝났을 때, 이기면 100, 지면 -100

        # 게임이 끝나지 않았을 때,
        point = 0

        for row in range(8):
            for col in range(8):
                if self.board[row][col] == self.player:
                    point += self.adv[row][col]

                elif self.board[row][col] == self.opp:
                    point -= self.adv[row][col]

        # point = self.tmp_board.score(board)[self.player]
        if self.controller.gameOver(self.board):

            game_score = self.tmp_board.score(self.board)
            player_score = game_score[self.player]
            opp_score = game_score[self.opp]

            if player_score > opp_score:
                point += 50

            elif player_score < opp_score:
                point += -50

        return point

    """
    :return state,score,done,_
    """

    def step(self,action):

        self.controller.doMove(board=self.board,color=self.player,pos=action)

        return self.get_state(mode='1D'),self.get_reward(),self.done

    def step_alp(self,action):

        self.controller.doMove(board=self.board, color=self.player, pos=action)

        return self.get_state(mode='2D')

    def get_valid_action(self):

        return self.controller.get_valid_actions(self.player,self.board)


