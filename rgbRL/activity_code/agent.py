"""
File: agent.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original activity code by Tanushree Burman
Purpose: Handles all user interface aspects of activity
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

import urandom

class QLearningAgent:
    # can change alpha, gamma, and epsilon values based on type of learning
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qtable = self.initialize_qtable()
        self.actions = ["LEFT", "RIGHT"]

    def initialize_qtable(self):
        table = {}
        for key, val in enumerate(self.env.states):
            qvalue = [0] * 2
            table[val] = qvalue
        return table
    
    # determine which action to do (in this case, go left or right)
    def choose_action(self, state):
        k = urandom.uniform(0, 1)
        if self.epsilon > k:
            print("Random action chosen")
            action = urandom.choice(self.actions)
        else:
            actions = self.qtable[state]
            max_val = max(actions)
            indices = [i for i, val in enumerate(actions) if val == max_val]
            action = self.actions[urandom.choice(indices)]
        self.last_state = state
        self.last_action = self.actions.index(action)
        return action
    
    # populating the q-table and calculating the reward
    def learn(self, reward, next_state):
        predict = self.qtable[self.last_state][self.last_action]
        target = reward + self.gamma * max(self.qtable[next_state])
        self.qtable[self.last_state][self.last_action] += self.alpha * (target - predict)
        print(f'Reward: {reward}, Q-table: {self.qtable}')
