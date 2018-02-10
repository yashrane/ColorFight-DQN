import csv
import random
import operator

num_weights = 11
num_bots = 10
bots = {}
kill = [4,6,8,9,10]
breed_pairs = [(1,2),(1,3),(2,3),(1,5),(5,7)]

def randomize_bots():
	for i in range(num_bots):
		bots[str(i+1)] = []
		for j in range(num_weights):
			bots[str(i+1)].append(random.uniform(.1,3.0))
		bots[str(i+1)][num_weights-1] = random.uniform(10,50)
	with open("bots.csv", 'w') as file:
		bots_csv = csv.writer(file)
		for bot_id in bots.keys():
			row = [bot_id]
			row.extend(bots[bot_id])
			bots_csv.writerow(row)

def breed(scores):
	print('starting breeding')
	#format of scores is dictionary {id: score}
	if bots == {}:
		with open('bots.csv','r') as file:
			bots_csv = csv.reader(file)
			for row in bots_csv:
				bots[row[0]] = row[1:]
	#sort bots by score
	sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse = True)
	#kill bots
	print('killing')
	dead = []
	for kill_index in kill:
		dead.append(sorted_scores[kill_index-1][0])
	for dead_index in dead:
		bots[dead_index] = []
	#replace dead bots with child bots
	print('sex')
	for pair,d in zip(breed_pairs,dead):
		id0 = str(sorted_scores[pair[0]][0])
		id1 = str(sorted_scores[pair[1]][0])
		for i in range(num_weights):
			#50-50 chance of getting gene from each parent
			parent = random.randint(0,1)
			if parent == 0:
				bots[d].append(bots[id0][i])
			else:
				bots[d].append(bots[id1][i])
			#20% mutate chance per gene
			mutate = random.randint(1,10)
			if mutate >= 10:
				bots[d][i] = float(bots[d][i]) + random.uniform(-.2,.2)
			if(float(bots[d][i]) < 0):
				bots[d][i] = 0
	#write updated genes to file
	with open("bots.csv", 'w') as file:
		bots_csv = csv.writer(file)
		for bot_id in bots.keys():
			row = [bot_id]
			row.extend(bots[bot_id])
			bots_csv.writerow(row)
