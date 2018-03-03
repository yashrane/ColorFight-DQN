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
	for i in range(0,5):
		for j in range(0,5):
			if(i+j < 5 and i+j != 0):
				weight_setter.append((i,j,5-i-j))
				weight_setter.append((-i,j,5-i-j))
				weight_setter.append((i,-j,5-i-j))
				weight_setter.append((-i,-j,5-i-j))
	if type == 'energy':
		weight_setter.append((0,0,7))
	else:
		weight_setter.append((0,0,5))
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

def calcExpScore(g,x,y, base):
	global energy_map
	global gold_map	
	
	
	cell = g.GetCell(x,y)
	time = calculateTimeToTake(g,x,y)
	score = 1
	
	score = score*location_importance[x][y]/3
	score = score*(energy_map[x][y]+1)*2
	if not haveGold:#only prioritizes gold if we have less than 3
		score = score*(gold_map[x][y]+1)	
	
	if cell.owner != 0:
		owner = [user for user in g.users if user.id == cell.owner]
		owner = owner[0]
		score = score + score*owner.cellNum/900

	if nearEnergy(g, cell):
		score = score*1.5
	
	#priorizing cells near base if there is only one base
	if base is not None:
		distance_to_base = 3 - distance(x,y,base.x, base,y)
		if distance_to_base > 0:
			score = score*distance_to_base
		
	
	
	E_score = score/(time**2)
	return E_score

def find_max(cells):
	m = (-1,-1,-1)
	for cell in cells:
		if cell[2] > m[2]:
			m = cell
	return [cell for cell in cells if cell[2] == m[2]]
	
#Calculates the distance from one point to another
def distance(x1, y1, x2, y2):
	return round(math.sqrt((x1-x2)**2 + (y1-y2)**2))
	
	
	
#Finds the best base location by summing the distances to non-user cells in cardinal directions
def find_best_base_loc(g):
	best = (-1, -1, -999999)
	for i in range(30):
		for j in range(30):
			if(g.GetCell(i,j).owner == g.uid):
				x,y,count = i,j,-1
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					x -= 1
					cell = g.GetCell(x,y)
					if (abs(i-x) < 3):
						if cell is None:
							count += 5
						elif cell.owner != g.uid and cell.owner != 0:
							count -= 20
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					x += 1
					cell = g.GetCell(x,y)
					if (abs(i-x) < 3):
						if cell is None:
							count += 5
						elif cell.owner != g.uid and cell.owner != 0:
							count -= 20
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					y += 1
					cell = g.GetCell(x,y)
					if (abs(j-y) < 3):
						if cell is None:
							count += 5
						elif cell.owner != g.uid and cell.owner != 0:
							count -= 20
				x,y = i,j
				cell = g.GetCell(x,y)
				while(cell is not None and not cell.isBase and (cell.owner == g.uid or cell.owner == 0)):
					count += 1
					y -= 1
					cell = g.GetCell(x,y)
					if (abs(j-y) < 3):
						if cell is None:
							count += 5
						elif cell.owner != g.uid and cell.owner != 0:
							count -= 20
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
	
	
def nearEnergy(g,c):
	if c.cellType == 'energy':
		return True
	for d in directions:
		cell = g.GetCell(c.x + d[0], c.y+d[1])
		if cell is not None and cell.cellType == 'energy':
			return True
	return False
	
	
#Returns the time left until the game ends
def timeLeft(g):
	return g.endTime - g.currTime
	
#returns true if you should use boost on the cell
def shouldBoost(g,c):
	if g.energy > 10 and (nearEnergy(g,c) or timeLeft(g) < 60) and c.owner != 0:
		print('Boosting!')
		return True
		
	if(g.energy <= 50 or c.owner == 0):#if we're low on energy, then dont boost <- this cutoff should probably be adjusted
		return False
		
	if g.energyCellNum > 1 and g.energy > 90: #if we're at max energy, then might as well use some
		print('Boosting!')
		return True
		
	#if the time we save is greater than the time it takes to regain the energy used
	if(g.energyCellNum >2 and c.takeTime-1 > 20.0/(g.energyCellNum-2)):
		print('Boosting!')
		return True
	return False
	
#returns the first player base that it finds
def findBase(g):
	for x in range(30):
		for y in range(30):
			c = g.GetCell(x,y)
			if(c.isBase and c.owner == g.uid):
				return c
#returns the number of enemy cells or edges around a cell
def numEnemyCellsAround(g,c):
	num_enemies = 0
	directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
	for d in directions:
		cell = g.GetCell(c.x + d[0], c.y + d[1]) 
		if cell is not None and cell.owner != g.uid and cell.owner!= 0:
			num_enemies = num_enemies + 1
	return num_enemies
	
#decides whether to use a boom defensively or not
def decideDefenseBoom(g):
	if(g.baseNum > 1 or g.energy < 40):
		return False
		
	base = findBase(g)
	if base is None:
		return
	num_enemies = numEnemyCellsAround(g,base)
	
	enemy_threshold = 6
	if(base.x == 0 or base.x == 29) and (base.y == 0 or base.y == 29):#its on a corner
		enemy_threshold = 2
	elif base.x == 0 or base.x == 29 or base.y == 0 or base.y == 29:#its on an edge
		enemy_threshold = 4
		
	if num_enemies > enemy_threshold:
		print('Booming around a base!')
		g.Blast(base.x, base.y, 'square', 'attack')
	
		
	
	
	
	
	
if __name__ == '__main__':
	# Instantiate a Game object.
	g = colorfight.Game()
	# You need to join the game using JoinGame(). 'MyAI' is the name of your
	# AI, you can change that to anything you want. This function will generate
	# a token file in the folder which preserves your identity so that you can
	# stop your AI and continue from the last time you quit. 
	# If there's a token and the token is valid, JoinGame() will continue. If
	# not, you will join as a new player.
	if g.JoinGame('sendmorehelp'):
		# Put you logic in a while True loop so it will run forever until you 
		# manually stop the game
		
		energy_map = get_map(g,'energy')
		gold_map = get_map(g,'gold')
		
		while True:
			decideDefenseBoom(g)
		
			base=None
			if g.baseNum == 1:
				base = findBase(g)
		
		
			valid_cells = []
			# Use a nested for loop to iterate through the cells on the map
			for x in range(g.width):
				for y in range(g.height):
					# Get a cell
					c = g.GetCell(x,y)
					# If the cell I got is mine
					if c.owner != g.uid and valid(g,x,y):
						valid_cells.append((x,y,calcExpScore(g,x,y, base)))
						
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
