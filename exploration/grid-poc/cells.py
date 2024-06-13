#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

from enum import Enum

UNSATURATED_PRESSURE_GRADIENT = 0.5
SATURATED_PRESSURE_GRADIENT = 1.0

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    BELOW = 2
    ABOVE = 3
    FRONT = 4
    BEHIND = 5

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
            # exit()
        pass

def interpolate(col1, col2, s):
    return (
        (col2[0] * s) + (col1[0] * (1 - s)),
        (col2[1] * s) + (col1[1] * (1 - s)),
        (col2[2] * s) + (col1[2] * (1 - s)),
        #(col2[3] * s) + (col1[3] * (1 - s)),
        s if s > 0.2 else 0.2
    )

class Soil(Cell):
    colour = (0.8, 0.3, 0.0, 0.0)

    def __init__(self):
        super().__init__()
        self.water = 0 #random.randint(1, 10)

    def update(self, grid):
        scale = min(self.water, 1.0) / 1.0
        rock = (0.8, 0.3, 0.0, 0.8)
        water = (0.075, 0.416, 0.936, 0.8)

        self.colour = interpolate(rock, water, scale)

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
            # exit()
        pass



