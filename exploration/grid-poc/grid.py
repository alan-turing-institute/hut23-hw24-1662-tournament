#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Example Plants

from time import sleep
import numpy as np
import math
from enum import Enum
import copy
import random
from math import floor
import voxels as vxm
from threading import Thread, Lock

UNSATURATED_PRESSURE_GRADIENT = 0.5
SATURATED_PRESSURE_GRADIENT = 1.0

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
    energy = 0
    # State
    colour = None
    wsat = 128.0
    permeability = (1.0/8.0)
    water_pressure_external = []
    pressure_gradient = []
    flux = []

    def __init__(self):
        super().__init__()
        self.water_pressure_external = [0.0] * len(Direction)
        self.pressure_gradient = [0.0] * len(Direction)
        self.flux = [0] * len(Direction)

    def update_water(self):
        # Calculate the internal water pressure
        if self.water < self.wsat:
            pressure = UNSATURATED_PRESSURE_GRADIENT * self.water
        else:
            pressure = SATURATED_PRESSURE_GRADIENT * self.water

        # Calculate the pressure gradient on each face
        water_pressure = [
            (pressure - self.water_pressure_external[direction]) * self.permeability
            for direction in range(len(Direction))
        ]
        water_pressure[Direction.BELOW.value] += self.water * self.permeability

        for direction in range(len(Direction)):
            self.flux[direction] = (water_pressure[direction])

    def update_flux(self):
        new_flux = [0] * 6
        total = 0
        water_orig = self.water
        while total < water_orig and max(self.flux) > 0:
            pos = self.flux.index(max(self.flux))
            if self.water > self.flux[pos]:
                new_flux[pos] = self.flux[pos]
                total += self.flux[pos]
                self.water -= self.flux[pos]
                self.flux[pos] = 0
            else:
                new_flux[pos] = self.water
                total += self.water
                self.flux[pos] -= self.water
                self.water = 0
        self.flux = new_flux

    def apply_flux(self, incoming):
        self.water += incoming

    def update(self, grid):
        pass

class Air(Cell):
    colour = (0.0, 0.0, 0.0, 0.0)

    def __init__(self):
        super().__init__()
        self.water_pressure_external = [10000.0] * len(Direction)

    def update_water(self):
        pass

    def update_flux(self):
        pass

    def update(self, grid):
        pass

    def apply_flux(self, incoming):
        if incoming > 0:
            print("ERROR: {}".format(incoming))
            exit()
        pass

def interpolate(col1, col2, s):
    return (
        (col2[0] * s) + (col1[0] * (1 - s)),
        (col2[1] * s) + (col1[1] * (1 - s)),
        (col2[2] * s) + (col1[2] * (1 - s)),
        #(col2[3] * s) + (col1[3] * (1 - s)),
        s if s > 0.2 else 0.0
    )

class Soil(Cell):
    colour = (0.0, 0.0, 0.0, 0.0)

    def __init__(self):
        super().__init__()
        self.water = 0 #random.randint(1, 10)

    def update(self, grid):
        scale = min(self.water, 1.0) / 1.0
        rock = (0.0, 0.0, 0.0, 0.8)
        water = (0.075, 0.416, 0.936, 0.8)

        self.colour = interpolate(water, water, scale)

class Rock(Cell):
    colour = (0.6, 0.6, 0.6, 1.0)

    def __init__(self):
        super().__init__()
        self.water_pressure_external = [10000.0] * len(Direction)

    def update_water(self):
        pass

    def update_flux(self):
        pass

    def update(self, grid):
        pass

    def apply_flux(self, incoming):
        if incoming > 0:
            print("ERROR: {}".format(incoming))
            exit()
        pass

class Grid():
    width = 8
    depth = 8
    height = 8

    grid = []
    energies = []
    reproduce = []

    # Threading
    render_lock = None
    colours = []



    def populate(self):
        self.grid = []
        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    if z == 0:
                        column.append(Rock())
                    else:
                        xnorm = (x - (self.width / 2.0) / (self.width / 2.0))
                        ynorm = (y - (self.depth / 2.0) / (self.depth / 2.0))
                        znorm = (z - (self.height / 2.0) / (self.height / 2.0))
                        height = 0.0 + (2.0 * math.sin(0.13 * math.pi * xnorm) + math.cos(0.1 * math.pi * ynorm))
                        if znorm < height:
                            column.append(Rock())
                        else:
                            column.append(Soil())
                row.append(column)
            self.grid.append(row)
        self.grid[3][3][7].water = 128

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.grid[x][y][z]
                    if type(cell) == Rock:
                        for direction in range(len(Direction)):
                            reverse = opposite(direction).value
                            neighbour = self.neighbour(x, y, z, direction)
                            neighbour.water_pressure_external[reverse] = 10000.0


        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    column.append(0)
                row.append(column)
            self.energies.append(row)

        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    column.append(None)
                row.append(column)
            self.reproduce.append(row)

        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    column.append((0.0, 0.0, 0.0, 0.0))
                row.append(column)
            self.colours.append(row)

    def cell(self, x, y, z):
        return self.grid[x % self.width][y % self.depth][z % self.height]

    def energy(self, x, y, z):
        return self.energies[x % self.width][y % self.depth][z % self.height]

    def neighbour(self, x, y, z, direction):
        if direction == Direction.LEFT.value:
            x = x - 1
        elif direction == Direction.RIGHT.value:
            x = x + 1
        elif direction == Direction.BELOW.value:
            z = z - 1
        elif direction == Direction.ABOVE.value:
            z = z + 1
        elif direction == Direction.FRONT.value:
            y = y - 1
        elif direction == Direction.BEHIND.value:
            y = y + 1
        else:
            print("ERROR: {}".format(direction))
            exit()
        x = x % self.width
        y = y % self.depth
        z = z % self.height
        return self.grid[x][y][z]

    def fight(self, x, y, z):
        cell = self.cell(x, y, z)
        energy_max = cell.energy
        best = None
        for direction in range(len(Direction)):
            reverse = opposite(direction).value
            neighbour = self.neighbour(x, y, z, direction)
            if neighbour.reproduce[reverse] and neighbour.energy > energy_max:
                energy_max = neighbour.energy
                best = direction

        if best:
            self.reproduce[x][y][z] = best
        else:
            self.reproduce[x][y][z] = None


    def preupdate(self):
        # Copy outgoing edge state to incoming edge state
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    cell.incoming[Direction.LEFT.value] = self.cell(x - 1, y, z).outgoing[Direction.RIGHT.value]
                    cell.incoming[Direction.RIGHT.value] = self.cell(x + 1, y, z).outgoing[Direction.LEFT.value]
                    cell.incoming[Direction.FRONT.value] = self.cell(x, y - 1, z).outgoing[Direction.BEHIND.value]
                    cell.incoming[Direction.BEHIND.value] = self.cell(x, y + 1, z).outgoing[Direction.FRONT.value]
                    cell.incoming[Direction.BELOW.value] = self.cell(x, y, z - 1).outgoing[Direction.ABOVE.value]
                    cell.incoming[Direction.ABOVE.value] = self.cell(x, y, z + 1).outgoing[Direction.BELOW.value]
                    
                    cell.update_water()


    def postupdate(self):
        # Transfer the pressures
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    if type(cell) == Soil:
                        for direction in range(len(Direction)):
                            reverse = opposite(direction).value
                            neighbour = self.neighbour(x, y, z, direction)
                            if type(neighbour) == Soil:
                                cell.water_pressure_external[direction] = neighbour.flux[reverse]
                            else:
                                cell.water_pressure_external[direction] = 9999.0

        # Apply the flux constraints
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    cell.update_flux()

        # Move the water
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    incoming = 0
                    for direction in range(len(Direction)):
                        reverse = opposite(direction).value
                        neighbour = self.neighbour(x, y, z, direction)
                        incoming += neighbour.flux[reverse]
                        #cell.water -= cell.flux[direction]
                        #neighbour.flux[reverse] = 0
                    cell.apply_flux(incoming)

        #print(self.cell(3, 0, 1).flux)

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    cell.flux = [0] * len(Direction)
                    cell.pressure_gradient = [0] * len(Direction)

        water = 0
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    water += cell.water
        print("Water: {}".format(water))

        # Allow cells to try to reproduce
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    self.fight(x, y, z)

        # Reproduce successful cells
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    direction = self.reproduce[x][y][z]
                    if direction != None:
                        self.grid[x][y][z] = self.neightbour(x, y, z, direction).deepcopy()

    count = 1

    def update(self):
        self.preupdate()

        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.grid[x][y][z]
                    cell.update(grid)

        self.postupdate()

    def display_slice(self, z):
        for y in range(self.depth):
            line = ''
            for x in range(self.width):
                character = str(self.grid[x][y][z].water)
                line += "{:3} ".format(character)
            print(line)
            
    def grid_update(self):
        while True:
            self.update()
            with self.render_lock:
                for x in range(self.width):
                    for y in range(self.depth):
                        for z in range(self.height):
                            self.colours[x][y][z] = self.grid[x][y][z].colour
            sleep(0.1)

    def start_grid_thread(self):
        self.render_lock = Lock()
        t = Thread(target=lambda : self.grid_update(), args=[])
        t.start()

    def update_colours(self):
        with self.render_lock:
            count = 0
            for x in range(self.width):
                for y in range(self.depth):
                    for z in range(self.height):
                        voxel = self.voxels[count]
                        colour = self.colours[x][y][z]
                        voxel.prop.color = "#{:02x}{:02x}{:02x}".format(
                            int(colour[0] * 256),
                            int(colour[1] * 256),
                            int(colour[2] * 256)
                        )
                        voxel.prop.opacity = colour[3]
                        count += 1

    def main(self):
        print("Preparing grid world...")
        random.seed(1)
        self.populate()

        # Create the scene
        pl, self.voxels = vxm.draw(self.width, self.depth, self.height)
        pl.add_callback(lambda : self.update_colours(), interval=1000)

        print("...Prepared")
        self.start_grid_thread()
        print("...Prepared2")
        input("Press Enter to continue...")

        while True:
            pl.render()
            pl.app.processEvents()
            pl.show()

if __name__ == "__main__":
    grid = Grid()
    grid.main()
    
    
    
    


