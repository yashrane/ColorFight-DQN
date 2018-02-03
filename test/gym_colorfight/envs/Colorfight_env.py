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
#import colorfight
import numpy as np
import torch
import json
import requests


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
		game = Game()
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
		
	def step(self, action):#im going to assume action is a tuple telling me what cell to attack
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
		self.take_action(action)
		reward = self.get_reward()
		ob = self.get_state()
		'''
		
		
		self.take_action(action)
		ob = self.get_state()
		reward = self.get_reward()
		done = self.game.currTime >= self.game.endTime
		
		return ob, reward, done, {}

	def take_action(self, action):
		self.action_episode_memory[self.curr_episode].append(action)
		self.game.AttackCell(action[0], action[1])
		

	def get_reward(self, state):
		score = torch.mul(state[:,:,2],state[:,:,0])
		return score.sum()

		
	def reset(self):
		"""
		Reset the state of the environment and returns an initial observation.

		Returns
		-------
		observation (object): the initial observation of the space.
		"""
		self.curr_episode += 1
		self.action_episode_memory.append([])
		
		headers = {'content-type': 'application/json'}
		r = requests.post(hostUrl + 'startgame', data=json.dumps({"admin_password":'', "last_time":0, "ai_join_time":0, "ai_only":True, "soft":False}), headers = headers)
		
		self.game = Game()
		self.game.JoinGame('MyAI2')
		
		return self.get_state()

	def render(self, mode='human', close=False):
		return

	def get_state(self):
		"""Get the observation."""
		self.game.Refresh()
		tensor = np.empty(shape = (self.game.width, self.game.height, 5), dtype=np.float64)
		for x in range(self.game.width):
			for y in range(self.game.height):
				c = self.game.GetCell(x,y)
				tensor[x,y,0] = (int)(c.owner == self.game.uid) 					#isPlayer
				tensor[x,y,1] = (int)(c.owner != self.game.uid and c.owner != 0)	#isEnemy
				tensor[x,y,2] = (int)(c.cellType == 'gold')*9+1						#score
				tensor[x,y,3] = self.calculateTimeToTake(x,y)						#takeTime
				tensor[x,y,4] = self.calculateTimeToFinish(c)						#finishTime
		return torch.from_numpy(tensor)
		
		
		
	#calculates the adjusted time it takes to capture a cell, 
	#returning the max float if we already own the cell
	def calculateTimeToTake(self,x,y):
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
	def calculateTimeToFinish(self,cell):
		g = self.game
		finish_time = cell.finishTime - g.currTime
		if(finish_time < 0):
			return np.finfo(np.float64).max #CHECK TO SEE IF THIS WORKS OUT OK
		return finish_time

		
		
		
		
		
		
		
		
		
		
		
		
#IGNORE ALL THIS STUFF 
#ITS A TERRIBLE WAY OF DOING THIS
#JUST STOP SCROLLING BEFORE YOU SEE HOW BAD IT IS















		
		
		
		
		
		
		
import requests
import json
import os
import random

hostUrl   = 'https://colorfight.herokuapp.com/'
#hostUrl   = 'http://localhost:8000/'

def CheckToken(token):
    headers = {'content-type': 'application/json'}
    r = requests.post(hostUrl + 'checktoken', data=json.dumps({'token':token}), headers = headers)
    if r.status_code == 200:
        return r.json()
    return None

class Cell:
    def __init__(self, cellData):
        self.owner      = cellData['o']
        self.attacker   = cellData['a']
        self.isTaking   = cellData['c'] == 1
        self.x          = cellData['x']
        self.y          = cellData['y']
        self.occupyTime = cellData['ot']
        self.attackTime = cellData['at']
        self.takeTime   = cellData['t']
        self.finishTime = cellData['f']
        self.cellType   = cellData['ct']
        self.isBase     = cellData['b'] == "base"
        self.isBuilding = cellData['bf'] == False
        self.buildTime  = cellData['bt']

    def __repr__(self):
        s = ""
        s += "({x}, {y}), owner is {owner}\n".format(x = self.x, y = self.y, owner = self.owner)
        if self.isTaking:
            s += "Cell is being attacked\n"
            s += "Attacker is {attacker}\n".format(attacker = self.attacker)
            s += "Attack time is {atkTime}\n".format(atkTime = self.attackTime)
            s += "Finish time is {finishTime}\n".format(finishTime = self.finishTime)
        else:
            s += "Cell is not being attacked\n"
            s += "Cell is occupied at {occupyTime}\n".format(occupyTime = self.occupyTime)
            s += "Take time is {takeTime}\n".format(takeTime = self.takeTime)
        return s

class User:
    def __init__(self, userData):
        self.id         = userData['id']
        self.name       = userData['name']
        self.cdTime     = userData['cd_time']
        self.cellNum    = userData['cell_num']
        if 'energy' in userData:
            self.energy = userData['energy']
        if 'gold' in userData:
            self.gold = userData['gold']
    
    def __repr__(self):
        return "uid: {}\nname: {}\ncd time: {}\ncell number: {}\n".format(self.id, self.name, self.cdTime, self.cellNum)

class Game:
    def __init__(self):
        self.data = None
        self.token = ''
        self.name  = ''
        self.uid   = -1
        self.endTime = 0
        self.users = []
        self.cellNum = 0
        self.cdTime = 0
        self.energy = 0
        self.gold = 0
        self.gameVersion = ''
        self.Refresh()

    def JoinGame(self, name, password = None, force = False):
        if type(name) != str:
            print("Your name has to be a string!")
            return False
        if force == False and os.path.isfile('token'):
            with open('token') as f:
                self.token = f.readline().strip()
                data = CheckToken(self.token)
                if data != None:
                    if name == data['name']:
                        self.name = data['name']
                        self.uid  = data['uid']
                        return True
    
        headers = {'content-type': 'application/json'}
        data = {'name':name}
        if password != None:
            data['password'] = password
        r = requests.post(hostUrl + 'joingame', data=json.dumps(data), headers = headers)
        if r.status_code == 200:
            data = r.json()
            with open('token', 'w') as f:
                f.write(data['token'] + '\n')
            self.token = data['token']
            self.uid   = data['uid']
            self.Refresh()
        else:
            return False

        return True

    def AttackCell(self, x, y, boost = False):
        if self.token != '':
            headers = {'content-type': 'application/json'}
            r = requests.post(hostUrl + 'attack', data=json.dumps({'cellx':x, 'celly':y, 'boost': boost, 'token':self.token}), headers = headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly"
        else:
            return False, None, "You need to join the game first!"

    def BuildBase(self, x, y):
        if self.token != '':
            headers = {'content-type': 'application/json'}
            r = requests.post(hostUrl + 'buildbase', data=json.dumps({'cellx':x, 'celly':y, 'token':self.token}), headers = headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly, status_code ", r.status_code
        else:
            return False, None, "You need to join the game first!"
    
    def Boom(self, x, y, direction, boomType):
        if self.token != '':
            if direction not in ["square", "vertical", "horizontal"]:
                return False, None, "Wrong direction!"
            if boomType not in ["attack", "defense"]:
                return False, None, "Wrong boom type!"
            headers = {'content-type': 'application/json'}
            r = requests.post(hostUrl + 'boom', data=json.dumps({'cellx':x, 'celly':y, 'token':self.token, 'direction':direction, 'boomType':boomType}), headers = headers)
            if r.status_code == 200:
                data = r.json()
                if data['err_code'] == 0:
                    return True, None, None
                else:
                    return False, data['err_code'], data['err_msg']
            else:
                return False, None, "Server did not return correctly, status_code ", r.status_code
        else:
            return False, None, "You need to join the game first!"

    def GetCell(self,x,y):
        if 0 <= x < self.width and 0 <= y < self.height:
            c = Cell(self.data['cells'][x+y*self.width])
            return c
        return None
    def GetTakeTimeEq(self, timeDiff):
        if timeDiff <= 0:
            return 33
        return 30*(2**(-timeDiff/30))+3
    def RefreshUsers(self, usersData):
        self.users = []
        for userData in usersData:
            u = User(userData)
            self.users.append(u)
            if u.id == self.uid:
                self.gold   = u.gold
                self.energy = u.energy
                self.cdTime = u.cdTime
                self.cellNum = u.cellNum
    def Refresh(self):
        headers = {'content-type': 'application/json'}
        if self.data == None:
            r = requests.post(hostUrl + 'getgameinfo', data=json.dumps({"protocol":2}), headers = headers)
            if r.status_code == 200:
                self.data = r.json()
                self.width = self.data['info']['width']
                self.height = self.data['info']['height']
                self.currTime = self.data['info']['time']
                self.endTime = self.data['info']['end_time']
                self.lastUpdate = self.currTime
                self.RefreshUsers(self.data['users'])
            else:
                return False
        else:
            r = requests.post(hostUrl + 'getgameinfo', data=json.dumps({"protocol":1, "timeAfter":self.lastUpdate}), headers = headers)
            if r.status_code == 200:
                d = r.json()
                self.data['info'] = d['info']
                self.data['users'] = d['users']
                self.width = d['info']['width']
                self.height = d['info']['height']
                self.currTime = d['info']['time']
                self.endTime = self.data['info']['end_time']
                self.lastUpdate = self.currTime
                self.RefreshUsers(self.data['users'])
                for c in d['cells']:
                    cid = c['x'] + c['y']*self.width
                    self.data['cells'][cid] = c
                for cell in self.data['cells']:
                    if cell['c'] == 1:
                        cell['t'] = -1
                    else:
                        if cell['o'] == 0:
                            cell['t'] = 2;
                        else:
                            cell['t'] = self.GetTakeTimeEq(self.currTime - cell['ot'])
            else:
                return False
        return True


