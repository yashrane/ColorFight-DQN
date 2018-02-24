# You need to import colorfight for all the APIs
'''
TODO:
add weight for bases
deprioritize energy if we have a lot of energy cells already
priority for distance from base if we have 2 bases
add base killing
add using energy for base defense
add usage of energy(but only if theres a good reason to/ we have a lot of energy cells)
-calculate the energy cells needed for using energy to be a net gain, cells wise

'''


import colorfight
import random
import math

haveGold = False
directions = [(0,1), (0,-1), (1, 0), (-1,0)]
surround = [(0,1), (0,-1), (1, 0), (-1,0), (1,1), (1,-1), (-1, 1), (-1,-1)]
location_importance = []
for i in range(30):
	location_importance.append([])
	for j in range(30):
		location_importance[i].append(0)
for i in range(15):
	for j in range(15):
		location_importance[i+15][j+15] = round(math.sqrt((i+1)**2 + (j+1)**2))
		location_importance[14-i][j+15] = location_importance[i+15][j+15]
		location_importance[i+15][14-j] = location_importance[i+15][j+15]
		location_importance[14-i][14-j] = location_importance[i+15][j+15]
		
#get the map of weights based on the type of cells
def get_map(g, type):
	weight_setter = []
	for i in range(0,4):
		for j in range(0,4):
			if(i+j < 4 and i+j != 0):
				weight_setter.append((i,j,4-i-j))
				weight_setter.append((-i,j,4-i-j))
				weight_setter.append((i,-j,4-i-j))
				weight_setter.append((-i,-j,4-i-j))
	weight_setter.append((0,0,4))
	map = []
	for i in range(30):
		map.append([])
		for j in range(30):
			map[i].append(0)
	for i in range(30):
		for j in range(30):
			if g.GetCell(i,j).cellType == type:
				for thing in weight_setter:
					if g.GetCell(i-thing[0],j-thing[1]) is not None:
						map[i-thing[0]][j-thing[1]] += thing[2]
	return map
		
energy_map = []
gold_map = []
		
		

def valid(g,x,y):
	if g.GetCell(x,y).isTaking:
		return False
	for direction in directions:
		cell = g.GetCell(x+direction[0], y+direction[1])
		if cell is not None and cell.owner == g.uid:
			return True
	return False

def calculateTimeToTake(g,x,y):
	cell = g.GetCell(x,y)
	numNeighbors = 0
	neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
	for c in neighbors:
		if c is not None and c.owner == g.uid:
			numNeighbors = numNeighbors+1

	return cell.takeTime * (1 - 0.25*(numNeighbors - 1))

def calcExpScore(g,x,y):
	global energy_map
	global gold_map

	cell = g.GetCell(x,y)
	time = calculateTimeToTake(g,x,y)
	if cell.cellType == 'gold':
		score = 10
	else:
		score = 1
	
	score = score*location_importance[x][y]
	score = score*(energy_map[x][y]+1)
	if not haveGold:#only prioritizes gold if we have less than 3
		score = score*(gold_map[x][y]+1)	
	
	if cell.owner != 0:
		owner = [user for user in g.users if user.id == cell.owner]
		owner = owner[0]
		score = score + score*owner.cellNum/900

	E_score = score/(time**2)
	return E_score

def find_max(cells):
	m = (-1,-1,-1)
	for cell in cells:
		if cell[2] > m[2]:
			m = cell
	return [cell for cell in cells if cell[2] == m[2]]
	
#Finds the best base location by summing the distances to non-user cells in cardinal directions
def find_best_base_loc(g):
	best = (-1, -1, -5)
	for i in range(30):
		for j in range(30):
			if(g.GetCell(i,j).owner == g.uid):
				x,y,count = i,j,-4
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					x -= 1
					cell = g.GetCell(x,y)
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					x += 1
					cell = g.GetCell(x,y)
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					y += 1
					cell = g.GetCell(x,y)
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					y -= 1
					cell = g.GetCell(x,y)
				if count > best[2]:
					best = (i,j,count)
	return best[0],best[1]

def num_bases(g):
	n = 0
	for i in range(30):
		for j in range(30):
			cell = g.GetCell(i,j)
			if (cell.isBase or cell.isBuilding )and cell.owner == g.uid:
				n += 1
	return n
	
#returns true if you should use boost on the cell
def shouldBoost(g,c):
	if(g.energy <= 50):#if we're low on energy, then dont boost <- this cutoff should probably be adjusted
		return False
		
	if g.energyCellNum > 1 and g.energy > 90: #if we're at max energy, then might as well use some
		print('Boosting!')
		return True
		
	#if the time we save is greater than the time it takes to regain the energy used
	if(g.energyCellNum >2 and c.takeTime-1 > 20.0/(g.energyCellNum-2)):
		print('Boosting!')
		return True
	return False
	

if __name__ == '__main__':
	# Instantiate a Game object.
	g = colorfight.Game()
	# You need to join the game using JoinGame(). 'MyAI' is the name of your
	# AI, you can change that to anything you want. This function will generate
	# a token file in the folder which preserves your identity so that you can
	# stop your AI and continue from the last time you quit. 
	# If there's a token and the token is valid, JoinGame() will continue. If
	# not, you will join as a new player.
	if g.JoinGame('test1'):
		# Put you logic in a while True loop so it will run forever until you 
		# manually stop the game
		
		energy_map = get_map(g,'energy')
		gold_map = get_map(g,'gold')
		
		while True:
			valid_cells = []
			# Use a nested for loop to iterate through the cells on the map
			for x in range(g.width):
				for y in range(g.height):
					# Get a cell
					c = g.GetCell(x,y)
					# If the cell I got is mine
					if c.owner != g.uid and valid(g,x,y):
						valid_cells.append((x,y,calcExpScore(g,x,y)))
						
			#finds the best cell to build a base
			if(num_bases(g) < 3):
				if(g.gold >= 60):
					cellx,celly = find_best_base_loc(g)
					g.BuildBase(cellx,celly)
					g.Refresh()
			if(g.goldCellNum < 3):
				haveGold = False
			else:
				haveGold = True
			
			max_score_cell = random.choice(find_max(valid_cells))
			max_x = max_score_cell[0]
			max_y = max_score_cell[1]
			print(g.AttackCell(max_x,max_y, shouldBoost(g, g.GetCell(max_x, max_y))))
#			print(str(1000*(energy_map[max_score_cell[0]][max_score_cell[1]]+ 1)) + " " + str(max_score_cell[2]))
			g.Refresh()
						
	else:
		print("Failed to join the game!")
