import sys
import csv

if(len(sys.argv) != 2):
		sys.exit()
g = colorfight.Game()


def run():
	name = str(sys.arvs[1])
	
	weights = get_weights(name)
	
	if g.JoinGame(name):
		game_over = False
		while not game_over:
			#finds the best cell to attack
			best_cell = find_best_cell(weights)
			status = g.AttackCell(best_cell[0], best_cell[1])
			
			game_over = status[1] == 4
		
#Finds the best cell to attack using the given weights
def find_best_cell(weights):
	return (0,0)

	
	
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
	
	
run()