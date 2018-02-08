import sys
import csv
import colorfight
import random

'''
TODO: 
* finish expected_value()

* Create the following weights:
	-distance to base surroundings
	-distance to gold
	-distance to own base
	-number of cells the enemy owns
	+anything else that you can think of
'''

if(len(sys.argv) != 2):
		sys.exit()
g = colorfight.Game()


def run():
	name = str(sys.argv[1])
	
	weights = get_weights(name)
	print(name + " joined")
	if g.JoinGame(name):#this line throws an exception for whatever reason
		game_over = False
		while not game_over:
			#finds the best cell to attack
			best_cell = find_best_cell(weights)
			status = g.AttackCell(best_cell[0], best_cell[1])
			
			game_over = (status[1] == 4)
			g.Refresh()
			
			
			
#Finds the weights in bots.csv for a given bot id
#Raises a lookup error if it cannot be found
def get_weights(id):
	with open('bots.csv', 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			#if we find the correct id, then return the corresponding weights
			if(row[0] == id):
				return row[1]
	raise LookupError('The bot id could not be found.')
			
			
			
#Finds the best cell to attack using the given weights
def find_best_cell(weights):

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
	
	inputs = []
	inputs.append(isGold(cell))
	inputs.append(calculateTimeToTake(x,y))
	inputs.append(distanceToEdge(x,y))
	inputs.append(timeLeft())
	
	
	#add more inputs here
	
	
	if len(inputs) is not len(weights):
		print("Input length(" + str(len(inputs)) + ") does not match weights length(" + str(len(weights)))
		return -1
		
	expected_value = 0
	for i in range(len(inputs)):
		expected_value+=(inputs[i]*weights[i])
	return expected_value
	
	
def timeLeft():
	return g.endTime - g.currTime
	
def distanceToEdge(x,y):
	if(x > g.width/2):
		x = x - g.width/2
	if(y > g.height/2):
		x = x - g.height/2
	return round(math.sqrt((x+1)**2 + (y+1)**2))
	
	
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
			# If the cell I got is mine
			if c.owner != g.uid and valid(x,y):
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