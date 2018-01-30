import colorfight
import numpy as np
import torch

#Uses a game object g to generate a tensor representing
#the current state of the board
'''
columns:
isPlayer
isEnemy
isGolden
adjusted time to take(if already owned, set to 0?)
timeToFinish(if not being taken, set to 0?)

'''
def getStateTensor(g):
	tensor = np.empty(shape = (g.width, g.height, 5), dtype=np.float64)
	for x in range(g.width):
		for y in range(g.height):
			c = g.GetCell(x,y)
			tensor[x,y,0] = (int)(c.owner == g.uid) 					#isPlayer
			tensor[x,y,1] = (int)(c.owner != g.uid and c.owner != 0)	#isEnemy
			tensor[x,y,2] = (int)(c.cellType == 'gold')					#isGolden
			tensor[x,y,3] = calculateTimeToTake(g,x,y)					#takeTime
			tensor[x,y,4] = calculateTimeToFinish(g,c)					#finishTime
	return torch.from_numpy(tensor)
			
			
			
#calculates the adjusted time it takes to capture a cell, 
#returning the max float if we already own the cell
def calculateTimeToTake(g, x,y):
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
def calculateTimeToFinish(g,cell):
	finish_time = cell.finishTime - g.currTime
	if(finish_time < 0):
		return np.finfo(np.float64).max #CHECK TO SEE IF THIS WORKS OUT OK
	return finish_time
	
	
if __name__ == '__main__':
	# Instantiate a Game object.
	g = colorfight.Game()
	# You need to join the game using JoinGame(). 'MyAI' is the name of your
	# AI, you can change that to anything you want. This function will generate
	# a token file in the folder which preserves your identity so that you can
	# stop your AI and continue from the last time you quit. 
	# If there's a token and the token is valid, JoinGame() will continue. If
	# not, you will join as a new player.
	if g.JoinGame('MyAI'):
		# Put you logic in a while True loop so it will run forever until you 
		# manually stop the game
		while True:
			print(getStateTensor(g))
			g.Refresh()
	else:
		print("Failed to join the game!")
