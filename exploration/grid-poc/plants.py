#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Plants

import copy
from cells import (
    Direction,
    Cell,
    CellType,
)

SATURATED_PRESSURE_GRADIENT = 2.0
PRESSURE_UNSATURATED = -16
PRESSURE_SATURATED = -32


class Plant(Cell):
    cell_type = CellType.PLANT
    colour = (0.0, 1.0, 0.0, 1.0)
    wsat = 16
    permeability = (1.0/1.8)

    def __init__(self):
        super().__init__()

    def update_sunlight(self):
        for direction in range(len(Direction)):
            if self.get_neighbour(direction) == CellType.AIR:
                if direction == Direction.ABOVE.value:
                    self.energy += 8
                else:
                    self.energy += 1

    def update_water(self):
        # Calculate the internal water pressure
        if self.water < self.wsat:
            pressure = PRESSURE_UNSATURATED
        else:
            pressure = PRESSURE_SATURATED + ((self.water - self.wsat) * SATURATED_PRESSURE_GRADIENT)

        # Calculate the pressure gradient on each face
        water_pressure = [
            (pressure + self.pressure_gradient[direction] - self.water_pressure_external[direction]) * self.permeability
            for direction in range(len(Direction))
        ]
        water_pressure[Direction.BELOW.value] += self.water * self.permeability

        for direction in range(len(Direction)):
            self.flux[direction] = (water_pressure[direction])
            self.pressure_gradient[direction] = 0.0

    def update(self, grid):
        earth_contact = (
            (self.get_neighbour(Direction.LEFT.value) == CellType.SOIL)
            or (self.get_neighbour(Direction.RIGHT.value) == CellType.SOIL)
            or (self.get_neighbour(Direction.FRONT.value) == CellType.SOIL)
            or (self.get_neighbour(Direction.BEHIND.value) == CellType.SOIL)
            or (self.get_neighbour(Direction.BELOW.value) == CellType.SOIL)
            or True
        )

        if self.get_neighbour(Direction.ABOVE.value) == CellType.AIR:
            # We're a leaf!
            self.colour = (0.7, max(0.4 - 0.4 * (self.water / 7), 0.0), 0,4, 1.0)
            #print("Water leaf: {}, {}".format(self.water, self.energy))
            if self.energy > 5 and self.get_neighbour(Direction.BELOW.value) == CellType.PLANT:
                self.action_send_energy(min(self.energy - 5, 5), Direction.BELOW)
            if self.get_neighbour(Direction.BELOW.value) == CellType.SOIL and self.energy > 30 and self.water > 5:
                self.action_reproduce(Direction.BELOW)
            if earth_contact and self.energy > 30 and self.water > 7:
                self.action_reproduce(Direction.ABOVE)
            if self.energy > 40:
                self.action_pump(Direction.BELOW.value, -8)
        elif self.get_neighbour(Direction.ABOVE.value) == CellType.PLANT and self.get_neighbour(Direction.BELOW.value) == CellType.PLANT:
            # We're a shoot!
            self.colour = (0.2, 0.8, 0,4, 1.0)
            #print("Water shoot: {}, {}".format(self.water, self.energy))
            if self.energy > 10:
                self.action_pump(Direction.ABOVE.value, 8)
                self.action_pump(Direction.BELOW.value, -8)
        elif self.get_neighbour(Direction.ABOVE.value) == CellType.PLANT and self.get_neighbour(Direction.BELOW.value) != CellType.PLANT:
            # We're a root!
            self.colour = (0.4, 0.8, 0,4, 1.0)
            #print("Water root: {}, {}".format(self.water, self.energy))
            if self.get_neighbour(Direction.BELOW.value) == CellType.SOIL and self.energy > 30 and self.water > 5:
                self.action_reproduce(Direction.BELOW)
            if self.get_neighbour(Direction.ABOVE.value) != CellType.PLANT and self.energy > 30 and self.water > 7:
                self.action_reproduce(Direction.ABOVE)
            if self.energy > 10:
                self.action_pump(Direction.ABOVE.value, 8)


