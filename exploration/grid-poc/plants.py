#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Plants

from cells import (
    Cell,
)

class Plant(Cell):
    colour = (0.0, 1.0, 0.0, 1.0)

    def __init__(self):
        super().__init__()
        colour = (0.0, 1.0, 0.0, 1.0)

    def update_water(self):
        pass

    def update_flux(self):
        pass

    def update(self, grid):
        pass

    def apply_flux(self, incoming):
        self.water += incoming


