import os
from datetime import datetime
import pandas as pd
import agent
import numpy as np

class train_sys:
    def __init__(self):
        self.env = env.Env()

        self.action_size = 3
        self.state_shape = self.env.state_shape

        self.agent = agent.PPO_Agent(self.state_shape,self.action_size,'train')

        dummy = np.ones((1,66,166,4))
        _,_,_ = self.agent.get_act(dummy)

        self.end_epi = 100000
        self.epi = 0

        self.end_count = 5
        self.goal_score = 1

        self.tot_rewards = []

        self.state = []
        self.action = []
        self.reward = 0
        self.next_state = []
        self.act_prob = []
        self.done = False

    #state, action, reward, next_state, act_prob, done
    def run(self):

        self.env.run()

        for epi in range(self.end_epi):
            self.done = False
            self.env.reset()
            self.env.play()
            self.state = self.env.get_img()
            print(f"epi {epi} >> start ")
            while(self.done != True):

                _,self.action,self.act_prob = self.agent.get_act(self.state[np.newaxis])
                self.env.step(self.action)

                self.next_state, self.reward, self.done = self.env.get_state(epi)
                self.agent.add_buffer(self.state,self.action,self.reward,self.next_state,self.act_prob,self.done)
                self.state = self.next_state

                if (len(self.agent.s) == 500):
                    self.agent.train(self.env)

            self.env.stay()
            self.tot_rewards.append(self.env.tot_score)


            if(self.env.tot_score > self.goal_score):
                self.end_count += 1
            else:
                self.end_count = 0

            if(self.end_count >= 5):
                print(f"train finish!")
                break

            try:
                os.remove('reward.csv')
            except:
                pass
            reward_data = pd.DataFrame(self.tot_rewards)
            reward_data.to_csv("reward.csv")

        self.env.exit()

        now = datetime.now()
        print(now)