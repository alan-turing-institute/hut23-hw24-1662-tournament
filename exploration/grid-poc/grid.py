#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Example Plants

from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import math
from enum import Enum
import copy

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    BELOW = 2
    ABOVE = 3
    FRONT = 4
    BEHIND = 5

def opposite(direction):
    return [
        Direction.RIGHT,
        Direction.LEFT,
        Direction.ABOVE,
        Direction.BELOW,
        Direction.BEHIND,
        Direction.FRONT
    ][direction]

class State():
    state = {}

class States():
    state = None
    incoming = None
    outgoing = None
    reproduce = None
    fitness = 128

    def __init__(self):
        self.clear()

    def clear(self):
        self.state = State()
        self.incoming = [State() for _ in range(len(Direction))]
        self.outgoing = [State() for _ in range(len(Direction))]
        self.reproduce = [False for _ in range(len(Direction))]

class Cell(States):
    # Resources
    water = 0
    light = 0
    energy = 0
    # State
    colour = None
    solid = False

    def update(self, grid):
        pass

class Air(Cell):
    colour = (0.0, 0.0, 0.0, 0.0)

    def update(self, grid):
        pass

class Soil(Cell):
    colour = (0.3, 0.2, 0.08, 0.5)

    def update(self, grid):
        pass

class Grid():
    width = 16
    depth = 16
    height = 16

    grid = []
    fitnesses = []
    reproduce = []

    ax = None

    def populate(self):
        self.grid = []
        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    xnorm = (x - (self.width / 2.0) / (self.width / 2.0))
                    ynorm = (y - (self.depth / 2.0) / (self.depth / 2.0))
                    znorm = (z - (self.height / 2.0) / (self.height / 2.0))
                    height = 4.0 + (2.0 * math.sin(0.13 * math.pi * xnorm) + math.cos(0.1 * math.pi * ynorm))
                    if znorm < height:
                        column.append(Soil())
                    else:
                        column.append(Air())
                row.append(column)
            self.grid.append(row)

        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    column.append(0)
                row.append(column)
            self.fitnesses.append(row)

        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    column.append(None)
                row.append(column)
            self.reproduce.append(row)

    def cell(self, x, y, z):
        return self.grid[x % self.width][y % self.depth][z % self.height]

    def fitness(self, x, y, z):
        return self.fitnesses[x % self.width][y % self.depth][z % self.height]

    def neighbour(self, x, y, z, direction):
        if direction == Direction.LEFT:
            x = x - 1
        elif direction == Direction.RIGHT:
            x = x + 1
        if direction == Direction.BELOW:
            z = z - 1
        elif direction == Direction.ABOVE:
            z = z + 1
        if direction == Direction.FRONT:
            y = y - 1
        elif direction == Direction.BEHIND:
            y = y + 1
        x = x % self.width
        y = y % self.depth
        z = z % self.height
        return self.grid[x][y][z]

    def fight(self, x, y, z):
        cell = self.cell(x, y, z)
        fitness_max = cell.fitness
        best = None
        for direction in range(len(Direction)):
            reverse = opposite(direction).value
            neighbour = self.neighbour(x, y, z, direction)
            if neighbour.reproduce[reverse] and neighbour.fitness > fitness_max:
                fitness_max = neighbour.fitness
                best = direction

        if best:
            self.reproduce[x][y][z] = best
        else:
            self.reproduce[x][y][z] = None


    def preupdate(self):
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    # Copy outgoing edge state to incoming edge state
                    cell = self.cell(x, y, z)
                    cell.incoming[Direction.LEFT.value] = self.cell(x - 1, y, z).outgoing[Direction.RIGHT.value]
                    cell.incoming[Direction.RIGHT.value] = self.cell(x + 1, y, z).outgoing[Direction.LEFT.value]
                    cell.incoming[Direction.FRONT.value] = self.cell(x, y - 1, z).outgoing[Direction.BEHIND.value]
                    cell.incoming[Direction.BEHIND.value] = self.cell(x, y + 1, z).outgoing[Direction.FRONT.value]
                    cell.incoming[Direction.BELOW.value] = self.cell(x, y, z - 1).outgoing[Direction.ABOVE.value]
                    cell.incoming[Direction.ABOVE.value] = self.cell(x, y, z + 1).outgoing[Direction.BELOW.value]

                    # Allow cells to try to reproduce
                    self.fight(x, y, z)

    def postupdate(self):
        # Reproduce successful cells
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    direction = self.reproduce[x][y][z]
                    if direction != None:
                        self.grid[x][y][z] = self.neightbour(x, y, z, direction).deepcopy()

    def update(self):
        self.preupdate()

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.grid[x][y][z]
                    cell.update(grid)

        self.postupdate()
    
    def display_slice(self, z):
        for x in range(self.width):
            line = ''
            for y in range(self.depth):
                solid = self.grid[x][y][z].solid
                if solid:
                    character = '*'
                else:
                    character = '.'
                line += character
            print(line)
            
    def plot(self):
        voxelarray = np.empty([self.width, self.depth, self.height], dtype=bool)
        colors = np.empty(voxelarray.shape, dtype=object)

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.grid[x][y][z]
                    if cell.colour[3] > 0.0:
                        voxelarray[x, y, z] = True
                        colors[x, y, z] = "Red"
                    else:
                        voxelarray[x, y, z] = False
                    colors[x, y, z] = cell.colour

        self.ax.voxels(voxelarray, facecolors=colors, edgecolor='k')

    def main(self):
        self.populate()

        self.ax = plt.figure().add_subplot(projection='3d')
        #self.plot()
        #plt.ion()
        #plt.show()

        while True:
            print("Start update")
            self.update()
            print("End update")
            self.display_slice(5)
            #self.plot()
            #plt.draw()
            #plt.pause(0.1)
            sleep(0.25)

if __name__ == "__main__":
    grid = Grid()
    grid.main()
    
    
    
    


