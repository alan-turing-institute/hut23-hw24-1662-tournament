from typing import Tuple
import numpy as np

def gaussian_surface_3d(grid_size: int = 24, A: float = 24, x0: float = 12, y0: float = 12, 
                        sigma_x: float = 5, sigma_y: float = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    
    return x, y, z

# Example usage
# (x,y,z)=gaussian_surface_3d()

# print("X coordinates:\n", x)
# print("Y coordinates:\n", y)
# print("Z coordinates (Gaussian surface):\n", z)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

surface = gaussian_surface_3d(grid_size=24, A=18, x0=20, y0=20)
# print("X coordinates:\n", x)
# print("Y coordinates:\n", y)
# print("Z coordinates (Gaussian surface):\n", z)

def plot_gaussian_surface(surface: Tuple[np.ndarray, np.ndarray, np.ndarray]) -> None:
    """
    Plots a 3D Gaussian surface using Matplotlib.

    Args:
        surface (Tuple[np.ndarray, np.ndarray, np.ndarray]): A tuple containing the x, y, and z coordinates.
    """
    x, y, z = surface

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z, cmap='viridis')

    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')

    # print(y[0:5])
    print(np.shape(z))

    plt.show()

plot_gaussian_surface(surface)
# plt.show()