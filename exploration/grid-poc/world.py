#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# World

from time import sleep
import numpy as np
import math
import copy
import random
from math import floor
from threading import Thread, Lock
from typing import Tuple

import src.voxels as vxm

from src.cells import (
    Direction,
    State,
    States,
    Cell,
    Air,
    Soil,
    Rock,
    CellType,
)

from src.plants import (
    Plant,
)

from src.utils import (
    opposite,
)

class Grid():
    width = 16
    depth = 16
    height = 8

    """ Holds the data for the cells in the world"""
    grid = []
    energies = []
    reproduce = []

    # Threading
    render_lock = None
    colours = []

    def fill(self, where, what):
        """
        Create a three dimensional array of 'what's and store them in 'where'

        Args:
            where a variable to store the resulting three dimensional list
            what a function to call that returns the item to store in each cell
        """
        for x in range(self.width):
            row = []
            for y in range(self.depth):
                column = []
                for z in range(self.height):
                    item = what(x, y, z)
                    column.append(item)
                row.append(column)
            where.append(row)

    def apply(self, what):
        """
        Apply a function to every cell in the three dimensional grid

        The function must accept four parameters: cell, x, y, z.

        Args:
            what function to apply to every cell in the grid
        """
        for x in range(self.width):
            for y in range(self.depth):
                for z in range(self.height):
                    cell = self.cell(x, y, z)
                    what(cell, x, y, z)

    def fill_land(self, fertile, gauss_z, x, y, z):
        """
        The function used to fill the land

        Returns an object to store in each cell of the grid.

        Args:
            fertile array to store locations of fertile soil
            gauss_z height of the guassian curve at this point
            x, y, z position in the grid
        """
        if z == 0:
            item = Rock()
        else:
            # xnorm = (x - (self.width / 2.0) / (self.width / 2.0))
            # ynorm = (y - (self.depth / 2.0) / (self.depth / 2.0))
            znorm = (z - (self.height / 2.0) / (self.height / 2.0))
            height = gauss_z[x][y] - 1
            # height = 0.0 + (2.0 * math.sin(0.13 * math.pi * xnorm) + math.cos(0.1 * math.pi * ynorm))
            if znorm < height:
                item = Rock()
            elif znorm < height + 2:
                item = Soil()
                fertile.append((x, y, z))
            else:
                item = Air()
        return item

    def init_pressure(self, cell, x, y, z):
        """
        Initialise the pressur values in teh grid

        Args:
            cell to apply the pressure values to
            x, y, z position in the grid
        """
        if cell.cell_type == CellType.ROCK:
            for direction in range(len(Direction)):
                reverse = opposite(direction).value
                neighbour = self.neighbour(x, y, z, direction)
                neighbour.water_pressure_external[reverse] = 10000.0

    def populate(self):
        """
        Populate the world grid with suitable content.

        Args:
            None

        Returns:
            None
        """

        self.grid = []

        def gaussian_surface_3d(grid_size: int = self.width, A: float = self.height, x0: float = 0, y0: float = 0, 
                        sigma_x: float = 2.5, sigma_y: float = 2.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
            """
            Generates a 3D Gaussian surface.

            Args:
                grid_size (int): The size of the grid (default is 24).
                A (float): Amplitude of the Gaussian (default is 1).
                x0 (float): X-coordinate of the Gaussian center (default is 12).
                y0 (float): Y-coordinate of the Gaussian center (default is 12).
                sigma_x (float): Standard deviation along the X-axis (default is 5).
                sigma_y (float): Standard deviation along the Y-axis (default is 5).

            Returns:
                Tuple[np.ndarray, np.ndarray, np.ndarray]: X, Y, and Z coordinates of the Gaussian surface.
            """
            x = np.linspace(0, grid_size - 1, grid_size)
            y = np.linspace(0, grid_size - 1, grid_size)
            x, y = np.meshgrid(x, y)

            z = A * np.exp(-((x - x0) ** 2 / (2 * sigma_x ** 2) + (y - y0) ** 2 / (2 * sigma_y ** 2)))

            return (x, y, z)

        gauss_x, gauss_y, gauss_z = gaussian_surface_3d(grid_size=int(self.width * 2), A=(2.5 * self.height) / 4, x0=5, y0=5)
        fertile = []
        self.fill(self.grid, lambda x, y, z: self.fill_land(fertile, gauss_z, x, y, z))

        def find_highest_point(fertile):
            """
            Find the highest point in the list of fertile locations
            """
            (highest_x, highest_y, highest_z) = (0,0,0)
            for cell in fertile:
                (cell_x, cell_y, cell_z) = cell
                if cell_z > highest_z:
                    (highest_x, highest_y, highest_z) = cell
            return (highest_x, highest_y, highest_z)

        # cloud_seed = random.randint(0,len(fertile))
        # (cloud_x, cloud_y, cloud_z) = fertile[cloud_seed]

        (highest_x,highest_y,highest_z) = find_highest_point(fertile)
        self.grid[highest_x][highest_y][highest_z].water = 8192

        def find_topsoil(fertile, x, y):
            """
            Find the highest point on the map that's also soil
            """
            (highest_x, highest_y, highest_z) = (0, 0, 0)
            for cell in fertile:
                (cell_x, cell_y, cell_z) = cell
                if (cell_x == x) and (cell_y == y):
                    if cell_z > highest_z:
                        (highest_x, highest_y, highest_z) = cell
            return (highest_x, highest_y, highest_z)

        # Place seeds on the map
        for _ in range(16):
            plant_seed = random.randint(0, len(fertile))
            (seed_x, seed_y, seed_z) = fertile[plant_seed]
            (topsoil_x, topsoil_y, topsoil_z) = find_topsoil(fertile, seed_x, seed_y)
            self.grid[topsoil_x][topsoil_y][topsoil_z] = Plant()


        # Set rock to have "infinite" water pressure
        self.apply(lambda cell, x, y, z: self.init_pressure(cell, x, y, z))

        # Create a grid to store energy values
        self.fill(self.energies, lambda x, y, z: 0)

        # Create a grid to store reproduction intention
        self.fill(self.reproduce, lambda x, y, z: None)

        # Create a grid to store cell colours
        self.fill(self.colours, lambda x, y, z: (0.0, 0.0, 0.0, 0.0))

    def cell(self, x, y, z):
        """
        Returns the data structure for a cell

        Returns a reference to the Cell object for the given grid location. The
        co-ordinates wrap in all directions.

        Args:
            x, y, z: the co-ordinate of the cell

        Returns:
            Cell data structure
        """
        return self.grid[x % self.width][y % self.depth][z % self.height]

    def energy(self, x, y, z):
        """
        Returns the energy for a cell

        Returns the quantity of energy stored in a cell. The co-ordinates wrap
        in all directions.

        Args:
            x, y, z: the co-ordinate of the cell

        Returns:
            The energy stored in the cell
        """
        return self.energies[x % self.width][y % self.depth][z % self.height]

    def neighbour(self, x, y, z, direction):
        """
        Returns the neighbour of a cell in a given direction.

        Provided a cell and a direction, returns the neighbour of that cell in
        the given direction.

        Args:
            x, y, z: the co-ordinate of the cell
            direction: an instance of the Direction enum

        Returns:
            Neighbouring Cell data structure
        """
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
        """
        Returns the result of a Plant cell's reproduction action.

        In the event that a Cell wants to reproduce it aims to copy itself into
        an adjacent cell the reproducing cell must fight the incumbant cell
        and any other Plants simultaneously aiming to reproduce into the same
        cell.

        This method returns the result of that fight, in other words, tells us
        which if the cells succeeds in reproducing into the cell.

        The reproducing cells will have already indicated their intention to
        reproduce by recording the fact in their respective self.reproduce[]
        arrays.

        Args:
            x, y, z: the cell into which the reproducting is to occur

        Returns:
            The direction from which the reproduction can occur, or None
        """
        cell = self.cell(x, y, z)
        energy_max = cell.energy
        best = None
        for direction in range(len(Direction)):
            reverse = opposite(direction).value
            neighbour = self.neighbour(x, y, z, direction)
            #print(neighbour.energy, energy_max)
            if neighbour.reproduce[reverse] and neighbour.energy > energy_max:
                energy_max = neighbour.energy
                best = direction
            neighbour.reproduce[reverse] = None

        if best:
            self.reproduce[x][y][z] = best
        else:
            self.reproduce[x][y][z] = None


    def apply_message_pass(self, cell, x, y, z):
        """
        Pass messages between cells

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        cell.incoming[Direction.LEFT.value] = self.cell(x - 1, y, z).outgoing[Direction.RIGHT.value]
        cell.incoming[Direction.RIGHT.value] = self.cell(x + 1, y, z).outgoing[Direction.LEFT.value]
        cell.incoming[Direction.FRONT.value] = self.cell(x, y - 1, z).outgoing[Direction.BEHIND.value]
        cell.incoming[Direction.BEHIND.value] = self.cell(x, y + 1, z).outgoing[Direction.FRONT.value]
        cell.incoming[Direction.BELOW.value] = self.cell(x, y, z - 1).outgoing[Direction.ABOVE.value]
        cell.incoming[Direction.ABOVE.value] = self.cell(x, y, z + 1).outgoing[Direction.BELOW.value]
        cell.neighbour_type[Direction.LEFT.value] = self.cell(x - 1, y, z).cell_type
        cell.neighbour_type[Direction.RIGHT.value] = self.cell(x + 1, y, z).cell_type
        cell.neighbour_type[Direction.FRONT.value] = self.cell(x, y - 1, z).cell_type
        cell.neighbour_type[Direction.BEHIND.value] = self.cell(x, y + 1, z).cell_type
        cell.neighbour_type[Direction.BELOW.value] = self.cell(x, y, z - 1).cell_type
        cell.neighbour_type[Direction.ABOVE.value] = self.cell(x, y, z + 1).cell_type
        cell.update_water()
        cell.update_sunlight()

    def apply_pressure(self, cell, x, y, z):
        """
        update the pressure values for a cell

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        if cell.cell_type == CellType.SOIL or cell.cell_type == CellType.PLANT:
            for direction in range(len(Direction)):
                reverse = opposite(direction).value
                neighbour = self.neighbour(x, y, z, direction)
                if neighbour.cell_type == CellType.SOIL or neighbour.cell_type == CellType.PLANT:
                    cell.water_pressure_external[direction] = neighbour.flux[reverse]
                else:
                    cell.water_pressure_external[direction] = 9999.0

    def apply_resources(self, cell, x, y, z):
        """
        Update the resources for a cell

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        water_incoming = 0
        energy_incoming = 0
        for direction in range(len(Direction)):
            reverse = opposite(direction).value
            neighbour = self.neighbour(x, y, z, direction)
            water_incoming += neighbour.flux[reverse]
            energy_incoming += neighbour.energy_outgoing[reverse]
            neighbour.energy_outgoing[reverse] = 0
            #cell.water -= cell.flux[direction]
            #neighbour.flux[reverse] = 0
        cell.apply_flux(water_incoming, energy_incoming)

    def apply_reproduce(self, cell, x, y, z):
        """
        Update the reproduction status of a cell

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        direction = self.reproduce[x][y][z]
        if direction != None:
            child = copy.deepcopy(self.neighbour(x, y, z, direction))
            self.grid[x][y][z] = child
            child.water = 0
            child.energy = 0
        self.reproduce[x][y][z] = False

    def apply_flux_reset(self, cell):
        """
        Reset the flux of a cell

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        cell.flux = [0] * len(Direction)

    def apply_colour(self, x, y, z):
        """
        Record the colour of a cell for use by the renderer

        This is applied to every cell every tick of the clock.

        Args:
            cell to apply to
            x, y, z position in the grid
        """
        self.colours[x][y][z] = self.grid[x][y][z].colour

    def preupdate(self):
        """
        All updates that must happen before the main Cell update
        """

        # Copy outgoing edge state to incoming edge state
        self.apply(lambda cell, x, y, z: self.apply_message_pass(cell, x, y, z))

    def postupdate(self):
        """
        All updates that must happen after the main Cell update
        """

        # Transfer the pressures
        self.apply(lambda cell, x, y, z: self.apply_pressure(cell, x, y, z))

        # Apply the flux constraints
        self.apply(lambda cell, x, y, z: cell.update_flux())

        # Move the water and energy
        self.apply(lambda cell, x, y, z: self.apply_resources(cell, x, y, z))

        # Reset the flux values
        self.apply(lambda cell, x, y, z: self.apply_flux_reset(cell))

        # Allow cells to try to reproduce
        self.apply(lambda cell, x, y, z: self.fight(x, y, z))

        # Reproduce successful cells
        self.apply(lambda cell, x, y, z: self.apply_reproduce(cell, x, y, z))

    def update(self):
        """
        The main update calls

        Calls the pre update, then the main update, then the post update cycle.
        """
        self.preupdate()

        # Perform the main Cell update cycle
        self.apply(lambda cell, x, y, z: cell.update())

        self.postupdate()

    def display_slice(self, z):
        """
        Output a slice of the world to the console.

        Prints the specified horizontal slice of the world to the console
        using ASCII characters.

        Useful for debugging.
        """
        for y in range(self.depth):
            line = ''
            for x in range(self.width):
                character = str(self.grid[x][y][z].water)
                line += "{:3} ".format(character)
            print(line)

    def grid_update(self):
        """
        Perform the main update loop for the GridWorld

        This is separate from the rendering and user intear
        """
        input("Press Enter to continue...")
        while True:
            self.update()
            with self.render_lock:
                for x in range(self.width):
                    for y in range(self.depth):
                        for z in range(self.height):
                            self.colours[x][y][z] = self.grid[x][y][z].colour
            #sleep(0.1)

    def start_grid_thread(self):
        """
        Start the world update thread.

        Starts the thread used for updating the world based on the Gridworld
        physics rules.
        """
        self.render_lock = Lock()
        t = Thread(target=lambda : self.grid_update(), args=[])
        t.start()

    def update_colours(self):
        """
        Updates the colours in the render grid.

        Transfers the colours from the cells over to the mesh grid for
        rendering.

        This is threadsafe, but will potentially block the render thread so
        should be kept as fast as possible.
        """
        with self.render_lock:
            count = 0
            for x in range(self.width):
                for y in range(self.depth):
                    for z in range(self.height):
                        voxel = self.voxels[count]
                        colour = self.colours[x][y][z]
                        voxel.prop.color = "#{:02x}{:02x}{:02x}".format(
                            int(colour[0] * 255),
                            int(colour[1] * 255),
                            int(colour[2] * 255)
                        )
                        voxel.prop.opacity = colour[3]
                        count += 1

    def main(self):
        """
        Main execution thread.

        Spawns a thread to perform the update. The main thread is used to
        manage the user interface and rendering.
        """
        print("Preparing grid world...")
        random.seed(4)
        self.populate()

        # Create the scene
        pl, self.voxels = vxm.draw(self.width, self.depth, self.height)
        pl.add_callback(lambda : self.update_colours(), interval=50)
        print("...Prepared")

        self.start_grid_thread()
        pl.show()

        while True:
            pl.render()
            pl.app.processEvents()

if __name__ == "__main__":
    """
    Gridworld entry point
    """
    grid = Grid()
    grid.main()







