# You need to import colorfight for all the APIs
import colorfight
import random
directions = [(0,1), (0,-1), (1, 0), (-1,0)]

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
    cell = g.GetCell(x,y)
    time = calculateTimeToTake(g,x,y)
    if cell.cellType == 'gold':
        score = 10
    else:
        score = 1
    if cell.owner != 0:
        owner = [user for user in g.users if user.id == cell.owner]
        owner = owner[0]
        score = score + score*owner.cellNum/900
    E_score = score/time
    return E_score

def find_max(cells):
    m = (-1,-1,-1)
    for cell in cells:
        if cell[2] > m[2]:
            m = cell
    return [cell for cell in cells if cell[2] == m[2]]

if __name__ == '__main__':
    # Instantiate a Game object.
    g = colorfight.Game()
    # You need to join the game using JoinGame(). 'MyAI' is the name of your
    # AI, you can change that to anything you want. This function will generate
    # a token file in the folder which preserves your identity so that you can
    # stop your AI and continue from the last time you quit. 
    # If there's a token and the token is valid, JoinGame() will continue. If
    # not, you will join as a new player.
    if g.JoinGame('Q stands for Q'):
        # Put you logic in a while True loop so it will run forever until you 
        # manually stop the game
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
            max_score_cell = random.choice(find_max(valid_cells))
            print(g.AttackCell(max_score_cell[0],max_score_cell[1]))
            g.Refresh()
						
    else:
        print("Failed to join the game!")
