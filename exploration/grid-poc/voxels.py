from matplotlib import cm
import numpy as np
import pyvista
import pyvistaqt as pvqt

def matrix_toXY(array,mult):
    """
    Converts a 2D numpy array into an XYv coordinate matrix where v is the corresponding element in every x-y coordinate.

    Parameters
    ----------
    array : np.array(int,int)
        The 2D numpy array to be converted to an XYv coordinate matrix.
    mult : int or float
        The multiplication factor to be applied to the elements in the matrix.
    """

    Z  = np.max(array)
    return np.array([ [*i,mult*array[tuple(i)]] for i in np.argwhere(array)])

class Model:

    def __init__(self, array=[],file=''):
        '''Model structure. Calls `3-D` array to process into 3-D model.

        Parameters
        ----------
        array : np.array(int)
            array of the third-order populated with discrete, non-zero integers which may represent a voxel block type
        file : str
            file name and/or path for image file
        hashblocks : dict[int]{str, float }
            a dictionary for which the keys are the integer values on the discrete arrays (above) an the values are the color (str) for the specific key and the alpha for the voxel object (float)
        colormap : < matplotlib.cm object >
            colormap to use for voxel coloring if coloring kwarg in Model.draw method is not voxels. Default: cm.cool
        alphacm : float
            alpha transparency of voxels if colormap option is chosen. default: opaque colormap (alpha=1)
        
        -- FOR FILE PROCESSING --

        file : str
            file name a/or path for goxel txt file

        -- FOR XYZ COORDINATE ARRAY PROCESSING -- 

        XYZ : np.array(float )
            an array containing the x,y,z coordinates of shape `number_voxel-locations` x 3 [for each x y z]
        RGB : list[str] 
            a list for the colors of every voxels in xyz array (length: `number_voxel-locations`)
        sparsity : float
            a factor to separate the relative distance between each voxel (default:10.0 [> 50.0 may have memory limitations])
        '''
        self.array = array   # array of third-order (3-D)

        self.hashblocks = {}        # start with empty voxel-color dictionary
        self.colormap = cm.cool     # default: cool colormap
        self.alphacm = 1            # default: opaque colormap (alpha=1)

        # self.file = 'placeholder.txt'
        self.objfile = 'scene.obj'
        self.XYZ = []
        self.RGB = []
        self.sparsity = 10.0

    def draw(self, coloring='none', geometry = 'voxels', scalars='', background_color='#cccccc', wireframe=False, wireframe_color='k', window_size=[1024, 768],len_voxel=1,show=True):
        '''Draws voxel model after building it with the provided `array` with PyVista library 

        Parameters
        ----------
        coloring: string  
            voxel coloring scheme
                * 'custom'                      --> colors voxel model based on the provided keys to its array integers, defined in the `hashblocks` variable from the `Model` class
                * 'custom: #8599A6'             -->  color all voxel types with the #8599A6 hex color (bluish dark gray) and an alpha transparency of 1.0 (default)
                * 'custom: red, alpha: 0.24'    --> color all voxel types red and with an alpha transparency of 0.24
                * 'cmap : {colormap name}' :        colors voxel model based on a colormap; assigns colors from the chosen colormap to the defined array integers
                * 'cmap : viridis'              --> colormap voxel assignment with the viridis colormap
                * 'cmap : hot', alpha: 0.56     --> voxel assignment with the hot colormap with an alpha transparency of 0.56
                * 'none'   --> no coloring 
                * 'cool'      cool colormap
                * 'fire'      fire colormap
                * and so on...
        geometry: string  
            voxel geometry. Choose voxels to have a box geometry with geometry='voxels' or spherical one with geometry='particles'
        scalars : list
            list of scalars for cmap coloring scheme
        background_color : string / hex
            background color of pyvista plot
        wireframe: bool
            Represent mesh as wireframe instead of solid polyhedron if True (default: False). 
        wireframe_color: string / hex 
            edges or wireframe colors
        window_size : (float,float)
            defines plot window dimensions. Defaults to [1024, 768], unless set differently in the relevant theme’s window_size property [pyvista.Plotter]
        len_voxel : float [for geometry='voxels' or 'particles'] / (float,float,float) [for geometry='voxels']
            The characteristic side length (or lengths) of the voxel. For 'voxels' geometry, the x,y,z side lengths may be set by defining them in a tuple i.e. len_voxel=(x_len,y_len,z_len); if the len_voxel is set to a singular value, it assumes all box side lengths are the same. For 'particles' geometry, len_voxel=radius (default=1) 
        show : bool
            Display Pyvista 3-D render of drawn 3-D model if True (default: True)
        '''

        xx, yy, zz, voxid = matrix_toXY(self.array, 1).T

        centers = np.vstack((xx.ravel(), yy.ravel(), zz.ravel())).T

        pl = pvqt.BackgroundPlotter()

        if background_color != "":
            pl.background_color = background_color

        voxels = []
        for i in range(len(centers)):

            x_len,y_len,z_len = tuple(3*[len_voxel]) if type(len_voxel) == int or float else len_voxel

            # Voxel Geometry
            voxel = pyvista.Cube(center=centers[i],x_length=x_len, y_length=y_len, z_length=z_len)
            smooth= None

            # Mesh creation and coloring
            voxel_color = "#000000"
            voxel_alpha = 0.0
            actor = pl.add_mesh(voxel, color=voxel_color, smooth_shading=smooth, opacity=voxel_alpha,show_edges=True if wireframe else False, edge_color=wireframe_color, render=False)
            voxels.append(actor)


        return pl, voxels

