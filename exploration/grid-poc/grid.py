#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Example Plants

from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import math

class Cell():
    # Resources
    water = 0
    light = 0
    energy = 0
    # State
    state = {}
    colour = None
    solid = False

    def get_state(x, y, z):
        pass

    def update(self, grid):
        pass

class Air(Cell):
    colour = (0.0, 0.0, 0.0, 0.0)

    def update(self, grid):
        pass

class Soil(Cell):
    colour = (0.3, 0.2, 0.08, 1.0)

    def update(self, grid):
        pass

class Grid():
    width = 16
    depth = 16
    height = 16

    grid = []

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

    def get_cell(self, x, y, z):
        return self.grid[x][y][z]

    def update(self):
        grid = self.grid

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.grid[x][y][z]
                    cell.update(grid)
    
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
        self.plot()
        plt.ion()
        plt.show()

        while True:
            print("Start update")
            self.update()
            print("End update")
            self.display_slice(5)
            self.plot()
            plt.draw()
            plt.pause(0.1)

if __name__ == "__main__":
    grid = Grid()
    grid.main()
    
    
    
    


