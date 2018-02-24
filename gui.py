import tkinter as tk
import colorfight
import multiprocessing
import time
from multiprocessing.managers import BaseManager

queue = []
g = colorfight.Game()

def calculateTimeToTake(x,y):
    cell = g.GetCell(x,y)
    numNeighbors = 0
    neighbors = (g.GetCell(x+1,y),g.GetCell(x,y+1),g.GetCell(x-1,y),g.GetCell(x,y-1))
    for c in neighbors:
        if c is not None and c.owner == g.uid:
            numNeighbors = numNeighbors+1
    
    return cell.takeTime * (1 - 0.25*(numNeighbors - 1))



if(g.JoinGame('cheat')):
	color_list = ['sky blue', 'aquamarine', 'pale green', 'lawn green', 'forest green', 'goldenrod', 'salmon', 'hot pink', 'orange', 'medium purple', 'maroon']
	color_counter = 0
	colors = {g.uid: "red", 0: "white"}

	root = tk.Tk()

	atk_type = tk.IntVar()
	atk_type.set(1)
	atk_options = [
		("Normal", 1),
		("Boost(10)", 2),
		("Bomb Center(40)", 3),
		("Bomb Vert(40)", 4),
		("Bomb Horiz(40)", 5),
		("Build Base(60g)", 6)
	]
	root.geometry("1200x900")
	cells = [None]*900
	cell_labels = [None]*900
	#grid
	for i in range(30):
		for j in range(30):
			if(g.GetCell(i,j).cellType == 'gold'):
				cells[i+j*30] = tk.Frame(root, width = 30, height = 30, bg = "yellow", highlightbackground="black", highlightcolor="black", highlightthickness=1)
			elif(g.GetCell(i,j).cellType == 'energy'):
				cells[i+j*30] = tk.Frame(root, width = 30, height = 30, bg = "blue", highlightbackground="black", highlightcolor="black", highlightthickness=1)
			else:
				cells[i+j*30] = tk.Frame(root, width = 30, height = 30, bg = "gray", highlightbackground="black", highlightcolor="black", highlightthickness=1)
			cells[i+j*30].grid_propagate(0)
			cell_labels[i+j*30] = tk.Label(cells[i+j*30], bg="white", font = ("Calibri", 9), fg = "black", text = str(1))
			cell_labels[i+j*30].place(x=15, y=15, anchor="center")
			cells[i+j*30].place(x=(150+i*30), y=j*30)
	#radiobuttons
	for option in atk_options:
		tk.Radiobutton(root,text=option[0], variable=atk_type, value=option[1], font = ("Calibri", 9)).place(x=0,y=(option[1]-1)*30)
	#info
	energy_label = tk.Label(root, font = ("Calibri", 9), fg = "black", text = "Energy: ")
	gold_label = tk.Label(root, font = ("Calibri", 9), fg = "black", text = "Gold: ")
	energy_label.place(x=0, y = 8*30)
	gold_label.place(x=0, y = 9*30)

	#update and undo buttons
	def update():
		global color_counter
		g.Refresh()
		for i in range(30):
			for j in range(30):
				cell = g.GetCell(i,j)
				if(cell.owner != 0 and cell.owner not in colors.keys()):
					colors[cell.owner] = color_list[color_counter]
					color_counter += 1
				cell_labels[i+j*30].config(bg = colors[cell.owner], text = int(calculateTimeToTake(i,j)))
				if(cell.isBase):
					cell_labels[i+j*30].config(fg = 'white')
				else:
					cell_labels[i+j*30].config(fg = 'black')	
		energy_label.config(text = "Energy: {}".format(int(g.energy)))
		gold_label.config(text = "Gold: {}".format(int(g.gold)))
	def undo():
		if len(queue) > 0:
			queue.pop()
		print(queue)
	tk.Button(root, text = "Update", command = update).place(x = 0, y = 6*30)
	tk.Button(root, text = "Undo", command = undo).place(x = 0, y = 7*30)



	#Click methods
	def getcell(x,y):
		anchorx = root.winfo_rootx()
		anchory = root.winfo_rooty()
		return int((x-anchorx-150)/30), int((y-anchory)/30)
	def format_attack(x,y):
		return((x,y,atk_type.get()))
	def click(eventorigin):
		x = eventorigin.x_root
		y = eventorigin.y_root
		cellx, celly = getcell(x,y)
		if(cellx < 30 and cellx >= 0 and celly < 30 and celly >= 0):
			queue.append(format_attack(cellx,celly))
			print(queue)

	def execute():
		if len(queue) > 0:
			attack = queue[0]
			if(attack[2] == 2):
				status = g.AttackCell(attack[0], attack[1], boost = True)
			elif(attack[2] == 3):
				status = g.Blast(attack[0], attack[1], "square", "attack")
			elif(attack[2] == 4):
				status = g.Blast(attack[0], attack[1], "vertical", "attack")
			elif(attack[2] == 5):
				status = g.Blast(attack[0], attack[1], "horizontal", "attack")
			elif(attack[2] == 6):
				status = g.BuildBase(attack[0], attack[1])
			else:
				status = g.AttackCell(attack[0], attack[1])
			if status[1] != 3:
				queue.pop(0)
			print(queue)
		update()

	root.bind('<Button-1>', click)
	while True:
		execute()
		root.update_idletasks()
		root.update()
else:
	print('rip')
