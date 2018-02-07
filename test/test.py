import gym
import gym_colorfight

def valid(state,x,y):
#    if state[x,y].isTaking: <- not currently represented in teh tensor! TODO
#        return False
	directions = [(0,1), (0,-1), (1, 0), (-1,0)]
    for direction in directions:
		if x+direction[0] <30 and x+direction[0] >= 0 and y+direction[1] <30 and y+direction[1] >= 0:
          if cell is not None and cell.owner == g.uid:
            return True
    return False

env = gym.make('Colorfight-v0')
state = env.reset()
print(state)
