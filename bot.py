import sys
import csv
import colorfight
import random
import queue
import math

'''
TODO: 
* finish expected_value()
* Change loading so it goes into the dictionary
'''
'''
----------------------------------------------------------------
	Explanation of Weights:
	dist_base_t: threat that a cell feels based on enemy distance to own base
	dist_gold_t: threat that a cell feels based on enemy distance to own gold
	location_t: threat that a cell feels based on location and distance to enemy
	time_t: time weight for threat
	
	dist_gold_a: value of cell based on distance to gold
	time_a: time weight for attacking
	dist_base_a: value of cells surrounding enemy base based on distance
	base_a: value of enemy base based on number of surrounding enemy cells
	location_a: value of location importance of a cell
	enemy_cells_a: value of attacking an enemy based on number of cells they own
	
----------------------------------------------------------------
	formula for calculating "score" of attacking cell

	a is a value that has an a after it (not including time)
	t stands for time

	sum(w_a*f(a))/(time**w_t_a)
----------------------------------------------------------------
	formula for calculating "threat" of owned cell

	for th is a value with t after it (not including time)
	t stands for time

	sum(w_th*f(th))/(time**w_t_th)
----------------------------------------------------------------
'''
weights = {
	"dist_base_t": 0,
	"dist_gold_t": 0,
	"location_t": 0,
	"time_t": 0,
	"dist_gold_a": 0,
	"time_a": 0,
	"dist_base_a": 0,
	"base_a": 0,
	"location_a": 0,
	"enemy_cells_a": 0
}
#get the map of weights based on gold cells
def get_gold_map(g):
	gold_weight_setter = []
	for i in range(0,4):
		for j in range(0,4):
			if(i+j < 4 and i+j != 0):
				gold_weight_setter.append((i,j,4-i-j))
				gold_weight_setter.append((-i,j,4-i-j))
				gold_weight_setter.append((i,-j,4-i-j))
				gold_weight_setter.append((-i,-j,4-i-j))
	gold_weight_setter.append((0,0,4))
	map = []
	for i in range(30):
		map.append([])
		for j in range(30):
			map[i].append(0)
	for i in range(30):
		for j in range(30):
			if g.GetCell(i,j).cellType == 'gold':
				for thing in gold_weight_setter:
					if g.GetCell(i-thing[0],j-thing[1]) is not None:
						map[i-thing[0]][j-thing[1]] += thing[2]
	return map
#cellwise weights of cells surrounding bases
base_weight_setter = []
for i in range(0,4):
	for j in range(0,4):
		if(i+j < 4 and i+j != 0):
			base_weight_setter.append((i,j,4-i-j))
			base_weight_setter.append((-i,j,4-i-j))
			base_weight_setter.append((i,-j,4-i-j))
			base_weight_setter.append((-i,-j,4-i-j))
#own bases weights for threat
def get_own_base_map(g):
	map = []
	for i in range(30):
		map.append([])
		for j in range(30):
			map[i].append(0)
	for i in range(30):
		for j in range(30):
			cell = g.GetCell(i,j)
			if cell.isBase and cell.owner == g.uid:
				for thing in base_weight_setter:
					if g.GetCell(i-thing[0],j-thing[1]) is not None:
						map[i-thing[0]][j-thing[1]] += thing[2]
	return map
#enemy bases for attack
def get_enemy_base_map(g):
	map = []
	for i in range(30):
		map.append([])
		for j in range(30):
			map[i].append(0)
	for i in range(30):
		for j in range(30):
			cell = g.GetCell(i,j)
			if cell.isBase and cell.owner != g.uid:
				for thing in base_weight_setter:
					if g.GetCell(i-thing[0],j-thing[1]) is not None:
						if not g.GetCell(i-thing[0], j-thing[1]).isBase:
							map[i-thing[0]][j-thing[1]] += thing[2]
	return map

directions = [(0,1),(1,0),(-1,0),(0,-1)]
#returns a dictionary of the scores of the enemy bases NOT a list
def enemy_base_surround(g):
	enemy_bases = []
	for i in range(30):
		for j in range(30):
			cell = g.GetCell(i,j)
			if cell.isBase and cell.owner != g.uid:
				enemy_bases.append((i,j))
	base_score = {}
	for base in enemy_bases:
		count = 0
		num = 0
		for direction in directions:
			if g.GetCell(base[0]+direction[0], base[1]+direction[1]) is not None:
				num += 1
				if g.GetCell(base[0],base[1]).owner == g.GetCell(base[0]+direction[0], base[1]+direction[1]):
					count += 1
		base_score[(i,j)] = num - count
	return base_score


if(len(sys.argv) != 2):
	print("Incorrect Number of Arguments.")
	print("Correct Usage: python3 bot.py [botname]")
	sys.exit()
g = colorfight.Game()

gold_map = get_gold_map(g)
own_base_map = []
enemy_base_map = []
base_surround = {}

def run():
	name = str(sys.argv[1])
	
	weights = get_weights(name)
	print(name + " joined")
	if g.JoinGame(name):
	
		game_over = False
		while not game_over:
			
			#finds the best cell to attack			
			best_cell = find_best_cell(weights)
			status = g.AttackCell(best_cell[0], best_cell[1])
			
			game_over = (status[1] == 4)
			g.Refresh()
	else:
		print(name + " Could not join game!")
			
			
			
#Finds the weights in bots.csv for a given bot id
#Raises a lookup error if it cannot be found
def get_weights(id):
	with open('bots.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			#if we find the correct id, then return the corresponding weights
			if(row[0] == id):
				weights["dist_base_t"] = float(row[1])
				weights["dist_gold_t"] = float(row[2])
				weights["location_t"] = float(row[3])
				weights["time_t"] = float(row[4])
				weights["dist_gold_a"] = float(row[5])
				weights["time_a"] = float(row[6])
				weights["dist_base_a"] = float(row[7])
				weights["base_a"] = float(row[8])
				weights["location_a"] = float(row[9])
				weights["enemy_cells_a"] = float(row[10])
				return weights
				
	raise LookupError('The bot id could not be found.')
			
			
			
#Finds the best cell to attack using the given weights
def find_best_cell(weights):
	global own_base_map
	global enemy_base_map
	global base_surround

	#Creates score maps to make calculating expected score easier
	own_base_map = get_own_base_map(g)
	enemy_base_map = get_enemy_base_map(g)
	base_surround = enemy_base_surround(g)

	#finds all cells that we can attack
	valid_cells = get_all_valid_cells()
	for cell in valid_cells:
		cell.append(expected_value(cell, weights))
		
	#chooses the cell with the maximum expected_value, 
	#picking one randomly in case of ties
	best_cell = random.choice(find_max(valid_cells))
	return (best_cell[0],best_cell[1])

	
	
#Return a list of all cells with the largest value
def find_max(cells):
    m = (-1,-1,-1)
    for cell in cells:
        if cell[2] > m[2]:
            m = cell
    return [cell for cell in cells if cell[2] == m[2]]
	
	
	
	
#TODO: Returns the expected value for a cell based on the given weights
def expected_value(coordinates, weights):
	x = coordinates[0]
	y = coordinates[1]
	cell = g.GetCell(x,y)
	
	inputs = {
		"dist_base_t": 0,
		"dist_gold_t": 0,
		"location_t": 0,
		"time_t": 0,
		
		"dist_gold_a": 0,
		"time_a": 0,
		"dist_base_a": 0,
		"base_a": 0,
		"location_a": 0,
		"enemy_cells_a": 0
	}
	
	nearest_enemy = findNearestEnemy(x,y)
	
	
	#might have to screw with the scaling bc distance to edge will be bigger than distance to enemy
	inputs['location_t'] = distanceToEdge(x,y) - distance(x,y,nearest_enemy.x, nearest_enemy.y) 
	inputs['time_t'] = calculateTimeToTake(x,y)
	inputs['dist_base_t'] = own_base_map[nearest_enemy.x][nearest_enemy.y]
	inputs['dist_gold_t'] = gold_map[nearest_enemy.x][nearest_enemy.y]
	
	inputs['location_a'] = distanceToEdge(x,y)
	inputs['time_a'] = calculateTimeToTake(x,y)
	inputs['dist_gold_a'] = gold_map[x][y]
	if cell.owner != 0:
		inputs['enemy_cells_a'] = cellsOwned(cell)
	inputs['dist_base_a'] = enemy_base_map[x][y]
	
	
	if cell.isBase:
		inputs['base_a'] = base_surround[(x,y)]
	
#	inputs.append(timeLeft())
	
	
	
	if inputs.keys() != weights.keys():
		print("Input length(" + str(len(inputs)) + ") does not match weights length(" + str(len(weights)))
		return -1
	
	expected_value = 0	
	time = 0
	if cell.owner == g.uid:
		keys = [key for key in weights.keys() if key[-1] == 't']#all the threat keys
	else:
		keys = [key for key in weights.keys() if key[-1] == 'a']#all the threat keys#all the attacking keys
		
	for key in keys:
		if key[:4] == "time":
			time = inputs[key]**weights[key]
		else:
			expected_value+=(inputs[key]*weights[key])
			
	return expected_value/time
	
	
def scoreOf(cell):
	if cell.cellType == "gold":
		return 10
	return 1
	
def cellsOwned(cell):
	owner = [user for user in g.users if user.id == cell.owner]
	owner = owner[0]
	return owner.cellNum

#Finds the nearest enemy using a breadth first search	
def findNearestEnemy(x,y):	
	cells = queue.Queue()
	cells.put(g.GetCell(x,y))
	while(not cells.empty()):
		cell = cells.get()
		if(cell.owner != g.uid):
			return cell
		else:
			neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
			for n in neighbors:
				if(n is not None):
					cells.put(n)
	return None
	
#Finds the nearest gold using a breadth first search
def distanceToNearestGold(x,y):
	cells = queue.Queue()
	cells.put(g.GetCell(x,y))
	while(not cells.empty()):
		cell = cells.get()
		if(isGold(cell)):
			return distance(x,y,cell.x, cell.y)
		else:
			neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
			for n in neighbors:
				if(n is not None):
					cells.put(n)
	return -1
	
#Returns the time left until the game ends
def timeLeft():
	return g.endTime - g.currTime
	
#Calculates the distance from one point to another
def distance(x1, y1, x2, y2):
	return round(math.sqrt((x1-x2)**2 + (y1-y2)**2))
	
#Calculates the distance to an edge
def distanceToEdge(x,y):
	if(x > g.width/2):
		x = x - g.width/2
	if(y > g.height/2):
		x = x - g.height/2
	return round(math.sqrt((x+1)**2 + (y+1)**2))
	

#Calculates the time needed to take a cell	
def calculateTimeToTake(x,y):
    cell = g.GetCell(x,y)
    numNeighbors = 0
    neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
    for c in neighbors:
        if c is not None and c.owner == g.uid:
            numNeighbors = numNeighbors+1
    
    return cell.takeTime * (1 - 0.25*(numNeighbors - 1))
	
def isGold(cell):
	return int(cell.cellType == 'gold')
	
	
#Returns the coordinates of all cells that can be attacked
def get_all_valid_cells():
	valid_cells = []
	# Use a nested for loop to iterate through the cells on the map
	for x in range(g.width):
		for y in range(g.height):
			# Get a cell
			c = g.GetCell(x,y)
			
			if valid(x,y):
				valid_cells.append([x,y])
	return valid_cells
	
	
	
#Returns True if you can attack the cell at x,y.
def valid(x,y):
	directions = [(0,1), (0,-1), (1, 0), (-1,0)]
	if g.GetCell(x,y).isTaking:
		return False
	for direction in directions:
		cell = g.GetCell(x+direction[0], y+direction[1])
		if cell is not None and cell.owner == g.uid:
			return True
	return False
	
	
run()
