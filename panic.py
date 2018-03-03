import colorfight

g = colorfight.Game()

if g.JoinGame('Creative Nickname'):
	for i in range(30):
		for j in range(30):
			if g.GetCell(i,j).isBase and g.GetCell(i,j).owner == g.uid:
				while True:
					print(g.AttackCell(i,j))
else:
	print("failed to reload")