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

class CellType(Enum):
    NONE = 0
    AIR = 0
    ROCK = 1
    SOIL = 2
    PLANT = 3

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
    cell_type = CellType.NONE
    # Resources
    water = 0
    energy = 0
    # State
    colour = None
    wsat = 128.0
    permeability = (1.0/32.0)
    water_pressure_external = []
    pressure_gradient = []
    flux = []
    energy_outgoing = []
    neighbour_type = []

    def __init__(self):
        super().__init__()
        self.water_pressure_external = [0.0] * len(Direction)
        self.pressure_gradient = [0.0] * len(Direction)
        self.flux = [0] * len(Direction)
        self.energy_outgoing = [0] * len(Direction)
        self.neighbour_type = [CellType.AIR] * len(Direction)

    def get_neighbour(self, direction):
        return self.neighbour_type[direction]

    def action_send_energy(self, energy, direction):
        if energy > self.energy:
            energy = self.energy
        self.energy_outgoing[direction.value] += energy
        self.energy -= energy

    def action_reproduce(self, direction):
        self.reproduce[direction.value] = True

    def action_pump(self, direction, force):
        sign = 1 if force >= 0 else -1
        energy_required = abs(self.energy * 1.0)
        if energy_required > self.energy:
            force = sign * self.energy
        self.pressure_gradient[direction] += force
        self.energy -= energy_required

    def update_sunlight(self):
        pass

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
        self.flux = [max(flux, 0) for flux in self.flux]
        new_flux = [0] * 6
        total = 0
        water_orig = self.water
        while total < water_orig and max(self.flux) > 0 and self.water > 0:
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

    def apply_flux(self, water_incoming, energy_incoming):
        self.water += water_incoming
        self.energy += energy_incoming

    def update(self, grid):
        pass

class Air(Cell):
    cell_type = CellType.AIR
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

    def apply_flux(self, water_incoming, energy_incoming):
        if water_incoming > 0:
            print("ERROR: {}".format(water_incoming))
            #exit()
        self.energy += energy_incoming

def interpolate(col1, col2, s):
    return (
        (col2[0] * s) + (col1[0] * (1 - s)),
        (col2[1] * s) + (col1[1] * (1 - s)),
        (col2[2] * s) + (col1[2] * (1 - s)),
        min(s, 0.8) if s > 0.2 else 0.2
    )

class Soil(Cell):
    cell_type = CellType.SOIL
    colour = (0.8, 0.3, 0.0, 0.0)

    def __init__(self):
        super().__init__()
        self.water = 0

    def update(self, grid):
        scale = min(self.water / 16.0, 1.0) / 1.0
        rock = (0.8, 0.3, 0.0, 0.8)
        water = (0.075, 0.416, 0.636, 0.8)

        self.colour = interpolate(rock, water, scale)

class Rock(Cell):
    cell_type = CellType.ROCK
    colour = (0.6, 0.6, 0.6, 1.0)
    energy = 1000

    def __init__(self):
        super().__init__()
        self.water_pressure_external = [10000.0] * len(Direction)

    def update_water(self):
        pass

    def update_flux(self):
        pass

    def update(self, grid):
        pass

    def apply_flux(self, water_incoming, energy_incoming):
        if water_incoming > 0:
            print("ERROR: {}".format(water_incoming))
            #exit()
        self.energy += energy_incoming



