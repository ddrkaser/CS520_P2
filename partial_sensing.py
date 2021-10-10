#!/usr/bin/env python3

import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt 
import time

# Generates a length * width size gridworld
# Each square has a probability chance of being blocked 0 means unblocked, 1 means blocked
# The start and end squares are set to unblocked
def generate_gridworld(length, width, probability):
    grid = np.random.choice([0,1], length * width, p = [1 - probability, probability]).reshape(length, width)
    grid[0][0] = 0
    grid[-1][-1] = 0
    return grid

# Calculates h(x) using one of a range of heuristics
def hureisticValue(point1, point2):
    x1,y1=point1
    x2,y2=point2
    return abs(x1 - x2) + abs(y1 - y2)

class Cell:
    def __init__(self, row, col, dim):
        self.row=row
        self.col=col
        self.dim=dim
        self.neighbors=[]
        self.visited=False
        self.blocked=9999
        self.c=9999
        self.b=9999
        self.e=9999
        self.h=9999
        self.n=len(self.neighbors)

    def getPos(self):
        return self.col, self.row
    #return a list of neighbors of the current cell
    def findneighbors(self):
        dim = self.dim
        y, x = self.getPos()
        neighbors = [(y2, x2) for x2 in range(x-1, x+2)                     
                              for y2 in range(y-1, y+2)
                              if (-1 < x < dim and
                                  -1 < y < dim and
                                  (x != x2 or y != y2) and
                                  (0 <= x2 < dim) and
                                  (0 <= y2 < dim))]
        return neighbors
    #sense the neigbhors, update current cell's info
    def sensing(self, knowledge):
        neighbors = knowledge[self.row][self.col].findneighbors()
        c = 0
        b = 0
        e = 0
        h = 0
        for cell in neighbors:
            x, y = cell
            if grid[y][x] == 1:
                c += 1
            if knowledge[y][x].blocked == 1:
                b += 1
            if knowledge[y][x].blocked == 0:
                e += 1
            if knowledge[y][x].blocked == 9999:
                h += 1
        self.c = c
        self.b = b
        self.e = e
        self.h = h
        self.n = len(neighbors)
                         
    def __lt__(self, other):
        return False

#generate knowledge embeded with cell class
def generate_knowledge(grid):
    cell_list = []
    rows = len(grid)
    cols = len(grid[0])
    for i in range(rows):
        cell_list.append([])
        for j in range(cols):
            cellOBJ = Cell(i,j,rows)
            #cellOBJ.blocked = grid[i][j]
            cell_list[i].append(cellOBJ)
    return cell_list

#inferencing info of current cell, if updated then propagate to its visited neighbors and so on
def infering(y,x,knowledge):
    queue = [(x,y)]
    queue = check_queue(y,x,knowledge,queue)
    while len(queue) != 0:
        for item in queue:
            queue.remove(item)
            x1, y1 = item
            neighbors = knowledge[y1][x1].findneighbors()
            knowledge[y1][x1].sensing(knowledge)
            if knowledge[y1][x1].c == knowledge[y1][x1].b:
                knowledge[y1][x1].h == 0
                for neighbor in neighbors:
                    x2, y2 = neighbor
                    if knowledge[y2][x2].blocked == 9999:
                        knowledge[y2][x2].blocked = 0
                        #if a neighbor was updated, then add its visited neigbhors to queue
                        queue = check_queue(y2,x2,knowledge,queue)
            if knowledge[y1][x1].n - knowledge[y1][x1].c == knowledge[y1][x1].e:
                knowledge[y1][x1].h == 0
                for neighbor in neighbors:
                    x2, y2 = neighbor
                    if knowledge[y2][x2].blocked == 9999:
                        knowledge[y2][x2].blocked = 1
                        #if a neighbor was updated, then add its visited neigbhors to queue
                        queue = check_queue(y2,x2,knowledge,queue)
    return knowledge

#Add (x,y) neighbors which has been visted and h != 0
def check_queue(y,x,knowledge,queue):
    for neigbor in knowledge[y][x].findneighbors():
        x2, y2 = neigbor
        if knowledge[y2][x2].h != 0 and knowledge[y2][x2].visited == True and neigbor not in queue:
            queue.append(neigbor)
    return queue

def A_star(curr_knowledge, start, end):
    # Initializes the g(x), f(x), and h(x) values for all squares
    g = {(x, y):float("inf") for y, eachRow in enumerate(curr_knowledge) for x, eachcolumn in enumerate(eachRow)}
    g[start] = 0
    f = {(x, y):float("inf") for y, eachRow in enumerate(curr_knowledge) for x, eachcolumn in enumerate(eachRow)}
    f[start] = hureisticValue(start, end)
    h = {(x, y): hureisticValue((x, y), end) for y, eachRow in enumerate(curr_knowledge) for x, eachcolumn in enumerate(eachRow)}
    parent = {}
    visited={start} # it is a set which provide the uniqueness, means it is ensure that not a single cell visit more than onece.
    tiebreaker = 0
	# Creates a priority queue using a Python set, adding start cell and its distance information
    pq = set([ (f[start], tiebreaker, start) ])
    #count cell being processed
    cell_count = 0
    # A* algorithm, based on assignment instructions
    while not len(pq) == 0:
		# Remove the node in the priority queue with the smallest f value
        n = min(pq)
        pq.remove(n)
        cell_count += 1
        successors = []
		# curr_pos is a tuple (x, y) where x represents the column the square is in, and y represents the row
        curr_pos = n[2]
        visited.remove(curr_pos)
		# if goal node removed from priority queue, shortest path found
        if curr_pos == end:
            shortest_path = []
            path_pointer = end
            while path_pointer != start:
                shortest_path.append(path_pointer)
                path_pointer = parent[path_pointer]
            shortest_path.append(start)
            shortest_path = shortest_path[::-1]
            return [shortest_path, cell_count]	
		# Determine which neighbors are valid successors
        #add unblocked cells first, otherwise add unknown cells
        if curr_pos[0] > 0 and curr_knowledge[curr_pos[1]][curr_pos[0] - 1].blocked == 0: # the current node has a neighbor to its left which is unblocked
            left_neighbor = (curr_pos[0] - 1, curr_pos[1])
            if g[left_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(left_neighbor)
        elif curr_pos[0] > 0 and curr_knowledge[curr_pos[1]][curr_pos[0] - 1].blocked == 9999:
            left_neighbor = (curr_pos[0] - 1, curr_pos[1])
            if g[left_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(left_neighbor)
				
        if curr_pos[0] < len(curr_knowledge[0])  - 1 and curr_knowledge[curr_pos[1]][curr_pos[0] + 1].blocked == 0: # the current node has a neighbor to its right which is unblocked
            right_neighbor = (curr_pos[0] + 1, curr_pos[1])
            if g[right_neighbor] > g[curr_pos] + 1:
                #if neighbor is undiscovered
                successors.append(right_neighbor)
        elif curr_pos[0] < len(curr_knowledge[0])  - 1 and curr_knowledge[curr_pos[1]][curr_pos[0] + 1].blocked == 9999: # the current node has a neighbor to its right which is unblocked
            right_neighbor = (curr_pos[0] + 1, curr_pos[1])
            if g[right_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(right_neighbor)
        
        if curr_pos[1] > 0 and curr_knowledge[curr_pos[1] - 1][curr_pos[0]].blocked == 0: # the current node has a neighbor to its top which is unblocked
            top_neighbor = (curr_pos[0], curr_pos[1] - 1)
            if g[top_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(top_neighbor)
        elif curr_pos[1] > 0 and curr_knowledge[curr_pos[1] - 1][curr_pos[0]].blocked == 9999: # the current node has a neighbor to its top which is unblocked
            top_neighbor = (curr_pos[0], curr_pos[1] - 1)
            if g[top_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(top_neighbor)
				
        if curr_pos[1] < len(curr_knowledge) - 1 and curr_knowledge[curr_pos[1] + 1][curr_pos[0]].blocked == 0: # the current node has a neighbor to its bottom which is unblocked
            bottom_neighbor = (curr_pos[0], curr_pos[1] + 1)
            if g[bottom_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(bottom_neighbor)
        elif curr_pos[1] < len(curr_knowledge) - 1 and curr_knowledge[curr_pos[1] + 1][curr_pos[0]].blocked == 9999: # the current node has a neighbor to its bottom which is unblocked
            bottom_neighbor = (curr_pos[0], curr_pos[1] + 1)
            if g[bottom_neighbor] > g[curr_pos] + 1: # if neighbor is undiscovered
                successors.append(bottom_neighbor)				
        # Update shortest paths and parents for each valid successor and add to priority queue, per assignment instructions
        for successor in successors:
            g[successor] = g[curr_pos] + 1
            parent[successor] = curr_pos
            if successor not in visited:
                tiebreaker += 1
                pq.add((g[successor] + h[successor], -tiebreaker, successor))
                visited.add(successor)
		# if priority queue is empty at any point, then unsolvable
        if len(pq) == 0:
            return False

# Handles processing of Repeated A*, restarting that algorithm if a blocked square is found in the determined shortest path
def algorithmA(grid, start, end, has_four_way_vision):
    # The assumed state of the gridworld at any point in time. For some questions, the current knowledge is unknown at the start
    curr_knowledge = generate_knowledge(grid)
    # If the grid is considered known to the robot, operate on that known grid
	# Else, the robot assumes a completely unblocked gridworld and will have to discover it as it moves
    complete_path = [(0,0)]
	# Run A* once on grid as known, returning False if unsolvable
    shortest_path = A_star(curr_knowledge, start, end)
    if not shortest_path:
        return False
    is_broken = False
    cell_count = shortest_path[1]
    while True:
		# Move pointer square by square along path
        for sq in shortest_path[0]:
            x = sq[0]
            y = sq[1]
			# If blocked, rerun A* and restart loop
            if grid[y][x] == 1:
                # If the robot can only see squares in its direction of movement, update its current knowledge of the grid to include this blocked square
                if not has_four_way_vision:
                    curr_knowledge[y][x].blocked = 1
                shortest_path = A_star(curr_knowledge, prev_sq, end)                
                if not shortest_path:
                    return False
                is_broken = True
                cell_count += shortest_path[1]
                break
			# If new square unblocked, update curr_knowledge. Loop will restart and move to next square on presumed shortest path
            else:
                if sq != complete_path[-1]:
                    complete_path.append(sq)
                # If the robot can see in all compass directions, update squares adjacent to its current position
                if has_four_way_vision:
                     if x != 0:
                         curr_knowledge[y][x - 1].blocked = grid[y][x - 1]
                     if x < len(curr_knowledge[0]) - 1:
                         curr_knowledge[y][x + 1].blocked = grid[y][x + 1]
                     if y != 0:
                         curr_knowledge[y - 1][x].blocked = grid[y - 1][x]
                     if y < len(curr_knowledge) - 1:
                         curr_knowledge[y + 1][x].blocked = grid[y + 1][x]
            prev_sq = sq
        if not is_broken:
            break
        is_broken = False
    return [complete_path, cell_count]

def inference(grid, start, end):
    #generate initial shortest path
    shortest_path = A_star(generate_knowledge(grid), start, end)
    curr_knowledge = generate_knowledge(grid)
    complete_path = [(0,0)]
    if not shortest_path:
        return False
    is_broken = False
    cell_count = shortest_path[1]
    while True:
		# Move pointer square by square along path
        for sq in shortest_path[0]:
            x = sq[0]
            y = sq[1]
			# If blocked, rerun A* and restart loop            
            if grid[y][x] == 1:
                curr_knowledge[y][x].blocked = 1
                curr_knowledge = infering(prev_sq[1],prev_sq[0],curr_knowledge)
                shortest_path = A_star(curr_knowledge, prev_sq, end)
                #print(shortest_path)
                if not shortest_path:
                    return False
                is_broken = True
                cell_count += shortest_path[1]
                break
			# If new square unblocked, update curr_knowledge. Loop will restart and move to next square on presumed shortest path
            else:
                if sq != complete_path[-1]:
                    complete_path.append(sq)
                curr_knowledge[y][x].blocked = 0
                curr_knowledge[y][x].visited = True
                if curr_knowledge[y][x].h != 0:
                    curr_knowledge = infering(y,x,curr_knowledge)
                    shortest_path = A_star(curr_knowledge, sq, end)                 
            prev_sq = sq
        if not is_broken:
            break
        is_broken = False
    return [complete_path, cell_count]    
    
"""test 1 try cell class"""
#PLEASE BE NOTED use knowledge[row][col] to retraive a cell!!!!
grid = generate_gridworld(10,10,.3)
knowledge = generate_knowledge(grid)
#should return (1,0)
knowledge[0][1].getPos()
#should return 9999
knowledge[0][1].blocked
#should return list of neighbors
knowledge[0][1].findneighbors()
#should return correct c
knowledge[1][2].sensing(knowledge)
knowledge[1][2].c
knowledge[1][2].n
knowledge[1][2].b
knowledge[1][2].h
"""test 2 searching algo"""
grid = generate_gridworld(101,101,.3)
start = (0,0)
end = (100,100)
agent1 = algorithmA(grid, start, end, has_four_way_vision = False)
agent2 = algorithmA(grid, start, end, has_four_way_vision = True)
agent3 = inference(grid, start, end)
