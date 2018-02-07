import csv


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
	with open("bots.csv", 'w') as file:
		bots_csv = csv.writer(file)
		for bot_id in bots.keys():
			bots_csv.writerow(bot_id, bots[bot_id])

def breed(scores):
	#format of scores is dictionary {id: score}
	#sort bots by score
	sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse = True)
	#kill bots
	dead = []
	for kill_index in kill:
		dead.append(sorted_scores[kill_index-1][0])
	for dead_index in dead:
		bots[dead_index] = []
	#replace dead bots with child bots
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
			if mutate >= 9:
				bots[d][i] = bots[d][i] + random.uniform(-.2,.2)
	#write updated genes to file
	with open("bots.csv", 'w') as file:
		bots_csv = csv.writer(file)
		for bot_id in bots.keys():
			bots_csv.writerow(bot_id, bots[bot_id])