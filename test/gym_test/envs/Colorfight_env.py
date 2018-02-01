#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simulate colorfight
There are two things that still have to be done:
-figure out what the action and observation spaces are
"""

# core modules
import random
import math

# 3rd party modules
import gym
import numpy as np
from gym import spaces
import colorfight
import numpy as np
import torch
import json
import requests


def get_chance(x):
    """Get probability that a banana will be sold at price x."""
    e = math.exp(1)
    return (1.0 + e) / (1. + math.exp(x + 1))


class ColorfightEnv(gym.Env):
    """
    The environment defines which actions can be taken at which point and
    when the agent receives which reward.
    """

    def __init__(self):
        self.__version__ = "0.1.0"
        print("ColorfightEnv - Version {}".format(self.__version__))

        # Old Variables
		'''
        self.MAX_PRICE = 2.0
        self.TOTAL_TIME_STEPS = 2

        self.curr_step = -1
        self.is_banana_sold = False
		'''
		#Variables that define the environment
		game = colorfight.Game()
		game.JoinGame('MyAI2')
		
		
		#This is the shit i havent been able to figure out yet
		'''
        # Define what the agent can do
        # Sell at 0.00 EUR, 0.10 Euro, ..., 2.00 Euro
        self.action_space = spaces.Discrete(21)

        # Observation is the remaining time
        low = np.array([0.0,  # remaining_tries
                        ])
        high = np.array([self.TOTAL_TIME_STEPS,  # remaining_tries
                         ])
        self.observation_space = spaces.Box(low, high)
		'''
        # Store what the agent tried
        self.curr_episode = -1
        self.action_episode_memory = []

    def _step(self, action):#im going to assume action is a tuple telling me what cell to attack
        """
        The agent takes a step in the environment.

        Parameters
        ----------
        action : int

        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """
		
		
		
		
		
		#old code
		'''
        if self.is_banana_sold:
            raise RuntimeError("Episode is done")
        self.curr_step += 1
        self._take_action(action)
        reward = self._get_reward()
        ob = self._get_state()
		'''
		
		
		self._take_action(action)
		ob = self._get_state()
		reward = self._get_reward()
		done = self.game.currTime >= self.game.endTime
		
        return ob, reward, done, {}

    def _take_action(self, action):
        self.game.AttackCell(action[0], action[1])
		

    def _get_reward(self, state):
        score = torch.mul(state[:,:,2],state[:,:,0])
		return score.sum()

		
    def _reset(self):
        """
        Reset the state of the environment and returns an initial observation.

        Returns
        -------
        observation (object): the initial observation of the space.
        """
		
		headers = {'content-type': 'application/json'}
		r = requests.post(hostUrl + 'startgame', data=json.dumps({"admin_password":'', "last_time":0, "ai_join_time":0, "ai_only":True, "soft":False}), headers = headers)
		
        return self._get_state()

    def _render(self, mode='human', close=False):
        return

    def _get_state(self):
        """Get the observation."""
		self.game.Refresh()
        tensor = np.empty(shape = (self.game.width, self.game.height, 5), dtype=np.float64)
		for x in range(self.game.width):
			for y in range(self.game.height):
				c = self.game.GetCell(x,y)
				tensor[x,y,0] = (int)(c.owner == self.game.uid) 					#isPlayer
				tensor[x,y,1] = (int)(c.owner != self.game.uid and c.owner != 0)	#isEnemy
				tensor[x,y,2] = (int)(c.cellType == 'gold')*9+1						#score
				tensor[x,y,3] = self._calculateTimeToTake(x,y)						#takeTime
				tensor[x,y,4] = self._calculateTimeToFinish(c)						#finishTime
		return torch.from_numpy(tensor)
		
		
		
	#calculates the adjusted time it takes to capture a cell, 
	#returning the max float if we already own the cell
	def _calculateTimeToTake(x,y):
		g = self.game
		cell = g.GetCell(x,y)
		if(cell.owner == g.uid):#if we already own the cell
			return np.finfo(np.float64).max#INSERT SOMETHING HERE

		numNeighbors = 0
		neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
		for c in neighbors:
			if c is not None and c.owner == g.uid:
				numNeighbors = numNeighbors+1
		
		return cell.takeTime * (1 - 0.25*(numNeighbors - 1))

	#Calculate the time left until a cell will be captured, 
	#returning max float if the cell is not being captured right now
	def _calculateTimeToFinish(cell):
		g = self.game
		finish_time = cell.finishTime - g.currTime
		if(finish_time < 0):
			return np.finfo(np.float64).max #CHECK TO SEE IF THIS WORKS OUT OK
		return finish_time
