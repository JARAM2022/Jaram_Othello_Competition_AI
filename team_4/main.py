from api import Othello_api
from rl.env import Othello_env
from ai.alpbeta import AI
import random
from tqdm import tqdm
import orjson
import time
PLAYER = {
    1: 'W',
    0: 'B',
    'W': 1,
    'B': 0
}

def test_env(auto=False,cnt = 1):
    env = Othello_env()
    env.reset(1)
    print(env.controller.gameOver(env.board))
    ai = AI()
    with open("./c.json", 'r') as f:
        ai.cache = orjson.loads(f.read())
    print(f"{len(ai.cache)}")
    # try:
    #     with open("./1.json",'r') as f:
    #         ai.cache = orjson.loads(f.read())
    #     print(f"{len(ai.cache)}")
    #
    # except Exception as e:
    #     print(e)
    #     print("캐시 파일을 찾을 수 없습니다.")

    ai_w = 0
    turn = [0,1]
    player = ['player','ai']
    for i in tqdm(range(cnt)):
        for _ in range(2):
            t = 0
            while not env.controller.gameOver(env.board):

                if player[t] == 'player':
                    can = env.controller.get_valid_actions(turn[t], env.board)
                    if not can:
                        pass
                    else:
                        if not auto:
                            action_x,action_y = map(int,input().split())
                            env.board = env.controller.doMove(env.board,turn[t],(action_x,action_y))

                        else:

                            action = random.choice(can)
                            # action = can[0]

                            env.controller.doMove(env.board, turn[t], action)


                else:
                    can = env.controller.get_valid_actions(turn[t], env.board)
                    if not can:
                        pass

                    else:
                        ai.setup(turn[t])
                        action = ai.get_action(env.board, can)
                        env.board = env.controller.doMove(env.board, turn[t], action)

                t = 1 if not t else 0

            score = env.controller.score(env.board)

            if score[0] > score[1]:

                if player[0] == 'ai':
                    ai_w += 1

            elif score[0] < score[1]:

                if player[1] == 'ai':
                    ai_w += 1

            env.reset(1)
            player.reverse()
            # if i > 5 and i % 5:
            #     with open("cache.json","wb") as f:
            #         f.write(orjson.dumps(ai.cache,option=orjson.OPT_APPEND_NEWLINE|orjson.OPT_NON_STR_KEYS))
            #         print("save")

    print(f"{ai_w} / {cnt*2}")

if __name__ == '__main__':
    api = Othello_api()
    api.run()
    # test_env(True)