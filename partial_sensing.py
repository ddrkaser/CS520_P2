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
    def findneighbors(self,grid):
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
    #unfinished
    #now can only update kb.c
    def update_kb(self, knowledge):
        neighbors = knowledge[self.row][self.col].findneighbors(grid)
        c = 0
        for cell in neighbors:
            y, x = cell
            if grid[x][y] == 1:
                c += 1
        knowledge[self.row][self.col].c = c
            
    def __lt__(self, other):
        return False

#generate kb based on the grid
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

#test
#PLEASE BE NOTED use knowledge[row][col] to retraive a cell!!!!
grid = generate_gridworld(10,9,.3)
knowledge = generate_knowledge(grid)
#should return (1,0)
knowledge[0][1].getPos()
#should return 9999
knowledge[0][1].blocked
#should return list of neighbors
neighbors = knowledge[0][1].findneighbors(grid)
#should return correct c
knowledge[1][2].update_kb(knowledge)
knowledge[1][2].c
