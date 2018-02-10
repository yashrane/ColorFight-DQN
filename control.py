import csv
import genetic
import sys
import colorfight
import subprocess
import json
import requests
import time
import os


hostUrl   = 'https://colorfight-dqn.herokuapp.com/'

#command line with anything to start from scratch
#python3 control.py to start with current csv
if 'start' in sys.argv:
	genetic.randomize_bots()
def find_cell(g):
	for x in range(30):
		for y in range(30):
			if g.GetCell(x,y).owner == g.uid:
				return x,y

def find_user(g, userid):
	if userid == 0:
		return
	for user in g.users:
		if user.id == userid:
			return user
def run():
	#restart server
	headers = {'content-type': 'application/json'}
	r = requests.post(hostUrl + 'startgame', data=json.dumps({"admin_password":'', "last_time":320, "ai_join_time":80, "ai_only":True, "soft":False}), headers = headers)
	time.sleep(5)
	g = colorfight.Game()
	if g.JoinGame('control'):
		#start subprocesses
		subprocess.call(['./bots.sh'])
		#lag control
		time.sleep(15)
		#setup scores list in case some die
		scores = {}
		g.Refresh()
		for user in g.users:
			if user.id != g.uid:
				scores[user.name] = 0
		#find cell and defend that cell
		x,y = find_cell(g)
		status = g.AttackCell(x,y)
		while g.endTime - g.currTime > 1.5:
			g.Refresh()
		#gather scores in dictionary
		for x in range(30):
			for y in range(30):
				cell = g.GetCell(x,y)
				user = find_user(g, cell.owner)
				if user is not None and user.id != g.uid:
					if cell.cellType == 'gold':
						scores[user.name] += 10
					else:
						scores[user.name] += 1
		#mutate
		genetic.breed(scores)
		time.sleep(3)
		#restart
		run()
	else:
		print('something went fucking wrong')
		run()
		
run()