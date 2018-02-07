import csv
import genetic
import sys
import colorfight
import subprocess
import json
import requests
import time

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
	for user in g.users:
		if user.id == userid:
			return user
def run():
	#restart server
	headers = {'content-type': 'application/json'}
	r = requests.post(hostUrl + 'startgame', data=json.dumps({"admin_password":'', "last_time":300, "ai_join_time":60, "ai_only":True, "soft":False}), headers = headers)
	
	g = colorfight.Game()
	if g.JoinGame('control'):
		#start subprocesses
		subprocess.call(['./bots.sh'])
		#lag control
		time.sleep(10)
		#setup scores list in case some die
		scores = {}
		for user in g.users:
			if user.id != g.uid:
				scores[user.name] = 0
		#find cell and defend that cell
		x,y = find_cell(g)
		status = g.AttackCell(x,y)
		while status[1] != 4:
			status = g.AttackCell(x,y)
		#gather scores in dictionary

		for x in range(30):
			for y in range(30):
				cell = g.GetCell(x,y)
				user = find_user(g, cell.owner)
				if user.id != g.uid:
					if cell.cellType == 'gold':
						scores[user.name] += 10
					else:
						scores[user.name] += 1
		#mutate
		genetic.breed(scores)
		#restart
		run()
	else:
		print('something went fucking wrong')
		run()