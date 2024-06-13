#!/bin/python3
# vim: et:ts=4:sts=4:sw=4

# SPDX-License-Identifier: BSD-2-Clause
# Copyright © 2024 The Alan Turing Institute

from matplotlib import cm
import numpy as np
import pyvista
import pyvistaqt as pvqt

# Adapted from Voxelmap
# See https://github.com/andrewrgarcia/voxelmap
# See https://github.com/andrewrgarcia/voxelmap/blob/main/voxelmap/main.py
# MIT license (Copyright (c) 2022 Andrew R. Garcia)

def draw(width, depth, height):
    array = np.empty([width, depth, height], dtype=int)

    for x in range(width):
        for y in range(depth):
            for z in range(height):
                array[x, y, z] = 1

    Z  = np.max(array)
    xx, yy, zz, voxid = np.array([ [*i,1*array[tuple(i)]] for i in np.argwhere(array)]).T
    centres = np.vstack((xx.ravel(), yy.ravel(), zz.ravel())).T

    pl = pvqt.BackgroundPlotter()
    pl.background_color = "#cccccc"
    pl.view_isometric()

    voxels = []
    for pos in range(len(centres)):
        x_len, y_len, z_len = tuple(3*[1.0])

        # Voxel Geometry
        voxel = pyvista.Cube(center=centres[pos], x_length=x_len, y_length=y_len, z_length=z_len)
        smooth= None

        # Mesh creation and coloring
        voxel_color = "#000000"
        voxel_alpha = 0.0
        actor = pl.add_mesh(voxel, color=voxel_color, smooth_shading=smooth, opacity=voxel_alpha,show_edges=True, edge_color="#000000", render=False)
        voxels.append(actor)

    return pl, voxels

