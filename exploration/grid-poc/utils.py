#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

# Utilities

from cells import (
    Direction,
)

def opposite(direction):
    return [
        Direction.RIGHT,
        Direction.LEFT,
        Direction.ABOVE,
        Direction.BELOW,
        Direction.BEHIND,
        Direction.FRONT
    ][direction]


