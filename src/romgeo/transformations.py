"""
This module contains functions for performing various transformations such as CRS projections, spline interpolation, Helmert transformations, and converting between different coordinate systems like ETRS, ST70, UTM, and stereographic.

Functions:
- _spline_params: Calculate the parameters of a bicubic spline surface based on the given x and y coordinates.
- _spline_grid: Calculate the 16 unknown coefficients of the interpolated surface using spline interpolation.
- _doBSInterpolation: Perform bicubic spline interpolation at a given point within a grid.
- _helmert_2d: Compute 4 parameter Helmert transformation (2D).
- _helmert_7: Compute 7 parameter Helmert transformation (3D).
- _etrs_to_st70: Convert ETRS coordinates to ST70 coordinates.
- _etrs_to_st70_en: Convert ETRS coordinates to ST70 coordinates with additional information.
- _st70_to_etrs: Convert ST70 coordinates to ETRS coordinates.
- _st70_to_utm: Convert ST70 coordinates to UTM coordinates.
- Transform: Class for initializing constants and loading grid data from a file.
"""

#!/usr/bin/env python
# coding: utf-8
# projections class - Perform CRS projections

import numpy as np
import numba as nb
import math
import os
import pickle
import glob

from romgeo import crs
from romgeo import projections
from romgeo import transformations
from pathlib import Path

@nb.jit(nopython=True)
def _spline_params(xk:float, yk:float) -> tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float]:
    """
    Calculate the parameters of a bicubic spline surface based on the given x and y coordinates.

    Parameters:
    xk (float): x coordinate
    yk (float): y coordinate

    Returns:
    tuple: Tuple[17] containing one dummy and 16 parameters for the bicubic spline surface.
    """
    return (0.0,                  # Initial dummy parameter
            1.0,                  # Parameter 1
            xk,                   # Parameter 2
            xk**2,                # Parameter 3
            xk**3,                # Parameter 4
            yk,                   # Parameter 5
            xk * yk,              # Parameter 6
            xk**2 * yk,           # Parameter 7
            xk**3 * yk,           # Parameter 8
            yk**2,                # Parameter 9
            xk * yk**2,           # Parameter 10
            xk**2 * yk**2,        # Parameter 11
            xk**3 * yk**2,        # Parameter 12
            yk**3,                # Parameter 13
            xk * yk**3,           # Parameter 14
            xk**2 * yk**3,        # Parameter 15
            xk**3 * yk**3)        # Parameter 16

@nb.jit(nopython=True)
def _spline_grid(grid: np.ndarray, cell_x: int, cell_y: int) -> tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float]:
    """
    Calculate the 16 unknown coefficients of the interpolated surface using spline interpolation.

    Args:
    grid (numpy.ndarray): The input grid of values.
    cell_x (int): The x-coordinate of the cell.
    cell_y (int): The y-coordinate of the cell.

    Returns:
    tuple: A tuple containing the 16 unknown coefficients for the interpolated surface.
    """
    return (0.0,                                  # Dummy parameter
            grid[cell_y - 1, cell_x],             # Parameter 1
            grid[cell_y - 1, cell_x + 1],         # Parameter 2
            grid[cell_y - 1, cell_x + 2],         # Parameter 3
            grid[cell_y - 1, cell_x + 3],         # Parameter 4
            grid[cell_y, cell_x],                 # Parameter 5
            grid[cell_y, cell_x + 1],             # Parameter 6
            grid[cell_y, cell_x + 2],             # Parameter 7
            grid[cell_y, cell_x + 3],             # Parameter 8
            grid[cell_y + 1, cell_x],             # Parameter 9
            grid[cell_y + 1, cell_x + 1],         # Parameter 10
            grid[cell_y + 1, cell_x + 2],         # Parameter 11
            grid[cell_y + 1, cell_x + 3],         # Parameter 12
            grid[cell_y + 2, cell_x],             # Parameter 13
            grid[cell_y + 2, cell_x + 1],         # Parameter 14
            grid[cell_y + 2, cell_x + 2],         # Parameter 15
            grid[cell_y + 2, cell_x + 3])         # Parameter 16

@nb.jit(nopython=True)
def _doBSInterpolation(x: float, y: float, minx: float, miny: float, stepx: float, stepy: float, grid: np.ndarray) -> float:
    """
    Perform bicubic spline interpolation at a given point (x, y) within a grid.

    Parameters:
    x (float): x-coordinate of the point to interpolate.
    y (float): y-coordinate of the point to interpolate.
    minx (float): Minimum x-coordinate of the grid.
    miny (float): Minimum y-coordinate of the grid.
    stepx (float): Step size in the x-direction of the grid.
    stepy (float): Step size in the y-direction of the grid.
    grid (numpy.ndarray): 2D grid of values for interpolation.

    Returns:
    float: Interpolated value at the point (x, y) using bicubic spline interpolation.
    """
    offset_x = abs((x - minx) / stepx)
    offset_y = abs((y - miny) / stepy)
    cell_x = int(offset_x)
    cell_y = int(offset_y)

    xk = minx + cell_x * stepx # {lambda of point 6 / East of point 6}
    yk = miny + cell_y * stepy # {phi of point 6 / North of point 6}

    # {relative coordinate of point X:}
    xk = (x - xk) / stepx
    yk = (y - yk) / stepy

    if cell_x < -1 or cell_x + 3 >= grid.shape[1] or cell_y < -1 or cell_y + 3 >= grid.shape[0]:
        return np.nan

    # Slice grid to coordinates
    az = transformations._spline_grid(grid, cell_x-1, cell_y)

    # {Parameters of bicubic spline surface}
    ff = transformations._spline_params(xk, yk)

    # Linear coefficients
    cf_1 = az[6]
    cf_2 = az[7]
    cf_3 = az[10]
    cf_4 = az[11]

    # Derivatives in the East-direction and the North-direction

    cf_5 = (-az[8] + 4 * az[7] - 3 * az[6]) / 2
    cf_6 = (3 * az[7] - 4 * az[6] + az[5]) / 2
    cf_7 = (-az[12] + 4 * az[11] - 3 * az[10]) / 2
    cf_8 = (3 * az[11] - 4 * az[10] + az[9]) / 2
    cf_9 = (-az[14] + 4 * az[10] - 3 * az[6]) / 2
    cf_10 = (-az[15] + 4 * az[11] -3 * az[7]) / 2
    cf_11 = (3 * az[10] - 4 * az[6] + az[2]) / 2
    cf_12 = (3 * az[11] - 4 * az[7] + az[3]) / 2

    # Equations for the cross derivative

    cf_13 = ((az[1] + az[11]) - (az[3] + az[9])) / 4
    cf_14 = ((az[2] + az[12]) - (az[4] + az[10])) / 4
    cf_15 = ((az[5] + az[15]) - (az[7] + az[13])) / 4
    cf_16 = ((az[6] + az[16]) - (az[8] + az[14])) / 4

    # Determining the 16 unknown coefficients of the interpolated surface

    shift_value = cf_1 * ff[1]
    shift_value += cf_5 * ff[2]
    shift_value += (-3 * cf_1 + 3 * cf_2 - 2 * cf_5 -cf_6) * ff[3]
    shift_value += (2 * cf_1 - 2 * cf_2 + cf_5 + cf_6) * ff[4]
    shift_value += cf_9 * ff[5]
    shift_value += cf_13 * ff[6]
    shift_value += (-3 * cf_9 + 3 * cf_10 - 2 * cf_13 - cf_14) * ff[7]
    shift_value += (2 * cf_9 - 2 * cf_10 + cf_13 + cf_14) * ff[8]
    shift_value += (-3 * cf_1 + 3 * cf_3 - 2 * cf_9 - cf_11) * ff[9]
    shift_value += (-3 * cf_5 + 3 *cf_7 - 2 * cf_13 - cf_15) * ff[10]
    shift_value += (9 * cf_1 - 9 * cf_2 - 9 * cf_3 + 9 * cf_4 + 6 * cf_5 + 3 * cf_6 - 6 * cf_7 - 3 * cf_8 +
                    6 * cf_9 - 6 * cf_10 + 3 * cf_11 - 3 * cf_12 + 4 * cf_13 + 2 * cf_14 + 2 * cf_15 + cf_16) * ff[11]
    shift_value += (-6 * cf_1 + 6 * cf_2 + 6 * cf_3 - 6 * cf_4 - 3 * cf_5 - 3 * cf_6 + 3 * cf_7 + 3 * cf_8 -
                    4 * cf_9 + 4 * cf_10 - 2 * cf_11 + 2 * cf_12 - 2 * cf_13 - 2 * cf_14 - cf_15 - cf_16) * ff[12]
    shift_value += (2 * cf_1 - 2 * cf_3 + cf_9 + cf_11) * ff[13]
    shift_value += (2 * cf_5 - 2 * cf_7 + cf_13 + cf_15) * ff[14]
    shift_value += (-6 * cf_1 + 6 * cf_2 + 6 * cf_3 - 6 * cf_4 - 4 * cf_5 - 2 * cf_6 + 4 * cf_7 + 2 * cf_8 -
                    3 * cf_9 + 3 * cf_10 - 3 * cf_11 + 3 * cf_12 - 2 * cf_13 - cf_14 - 2 * cf_15 - cf_16) * ff[15]
    shift_value += (4 * cf_1 - 4 * cf_2 - 4 * cf_3 + 4 * cf_4 + 2 * cf_5 + 2 * cf_6 - 2 * cf_7 - 2 * cf_8 +
                    2 * cf_9 - 2 * cf_10 + 2 * cf_11 - 2 * cf_12 + cf_13 + cf_14 + cf_15 + cf_16) * ff[16]

    return shift_value

@nb.jit
def _helmert_2d(east: float, north: float, tE: float, tN: float, dm: float, Rz: float) -> tuple[float, float]:
    """
    Compute 4 parameter Helmert transformation (2D).

    Parameters:
    east (float): Easting coordinate.
    north (float): Northing coordinate.
    tE (float): Translation in the East direction.
    tN (float): Translation in the North direction.
    dm (float): Scale factor.
    Rz (float): Rotation angle in seconds.

    Returns:
    tuple: Transformed easting and northing coordinates after Helmert transformation.
    """
    m = 1 + dm * 1e-6
    rz = math.radians(Rz/3600)  # Convert seconds to radians
    eastt = east * m * math.cos(rz) - north * m * math.sin(rz) + tE
    northt = north * m * math.cos(rz) + east * m * math.sin(rz) + tN

    return eastt, northt

@nb.jit
def _helmert_7(x: float, y: float, z: float, cx: float, cy: float, cz: float, scale: float, rx: float, ry: float, rz: float) -> tuple[float, float, float]:
    """
    Compute 7 parameter Helmert transformation (3D).

    Parameters:
    x (float): X-coordinate.
    y (float): Y-coordinate.
    z (float): Z-coordinate.
    cx (float): Translation in the X direction.
    cy (float): Translation in the Y direction.
    cz (float): Translation in the Z direction.
    scale (float): Scale factor.
    rx (float): Rotation angle around X-axis.
    ry (float): Rotation angle around Y-axis.
    rz (float): Rotation angle around Z-axis.

    Returns:
    tuple: Transformed X, Y, Z coordinates after Helmert transformation.
    """
    x1 = cx + scale * (x + rz * y - ry * z)
    y1 = cy + scale * (-rz * x + y + rx * z)
    z1 = cz + scale * (ry * x - rx * y + z)

    return x1, y1, z1

@nb.jit
def _etrs_to_st70(lat: float, lon: float, z: float, E0: float, N0: float, PHI0: float, LAMBDA0: float, k0: float, a: float, b: float, tE: float, tN: float, dm: float, Rz: float, shifts_grid: np.ndarray, mine: float, minn: float, stepe: float, stepn: float, heights_grid: np.ndarray, minla: float, minphi: float, stepla: float, stepphi: float) -> tuple[float, float, float]:
    """
    Perform ETRS to ST70 transformation.

    Parameters:
    lat (float): Latitude coordinate.
    lon (float): Longitude coordinate.
    z (float): Height coordinate.
    E0 (float): Reference Easting coordinate.
    N0 (float): Reference Northing coordinate.
    PHI0 (float): Reference Latitude.
    LAMBDA0 (float): Reference Longitude.
    k0 (float): Scale factor.
    a (float): Semi-major axis of ellipsoid.
    b (float): Semi-minor axis of ellipsoid.
    tE (float): Translation in the East direction.
    tN (float): Translation in the North direction.
    dm (float): Scale factor.
    Rz (float): Rotation angle in seconds.
    shifts_grid (np.ndarray): Grid of shifts.
    mine (float): Minimum Easting coordinate.
    minn (float): Minimum Northing coordinate.
    stepe (float): Step in East direction.
    stepn (float): Step in North direction.
    heights_grid (np.ndarray): Grid of heights.
    minla (float): Minimum Latitude coordinate.
    minphi (float): Minimum Longitude coordinate.
    stepla (float): Step in Latitude direction.
    stepphi (float): Step in Longitude direction.

    Returns:
    tuple: Transformed Easting, Northing, and Height coordinates after ETRS to ST70 transformation.
    """
    en = projections._geodetic_to_stereographic(lat, lon, E0, N0, PHI0, LAMBDA0, k0, a, b)
    h = transformations._helmert_2d(en[0], en[1], tE, tN, dm, Rz)

    e_shift = transformations._doBSInterpolation(h[0], h[1], mine, minn, stepe, stepn, shifts_grid[0])
    n_shift = transformations._doBSInterpolation(h[0], h[1], mine, minn, stepe, stepn, shifts_grid[1])
    h_shift = transformations._doBSInterpolation(lon, lat, minla, minphi, stepla, stepphi, heights_grid[0])

    return h[0] + e_shift, h[1] + n_shift, z - h_shift

@nb.jit
def _etrs_to_st70_en(e: float, n: float, height: float, E0: float, N0: float, PHI0: float, LAMBDA0: float, k0: float, a: float, b: float, tE: float, tN: float, dm: float, Rz: float, shifts_grid: np.ndarray, mine: float, minn: float, stepe: float, stepn: float, heights_grid: np.ndarray, minla: float, minphi: float, stepla: float, stepphi: float) -> tuple[float, float, float, float, float, float, float, float]:
    """
    Perform ETRS to ST70 transformation for Easting and Northing coordinates.

    Parameters:
    e (float): Easting coordinate.
    n (float): Northing coordinate.
    height (float): Height coordinate.
    E0 (float): Reference Easting coordinate.
    N0 (float): Reference Northing coordinate.
    PHI0 (float): Reference Latitude.
    LAMBDA0 (float): Reference Longitude.
    k0 (float): Scale factor.
    a (float): Semi-major axis of ellipsoid.
    b (float): Semi-minor axis of ellipsoid.
    tE (float): Translation in the East direction.
    tN (float): Translation in the North direction.
    dm (float): Scale factor.
    Rz (float): Rotation angle in seconds.
    shifts_grid (np.ndarray): Grid of shifts.
    mine (float): Minimum Easting coordinate.
    minn (float): Minimum Northing coordinate.
    stepe (float): Step in East direction.
    stepn (float): Step in North direction.
    heights_grid (np.ndarray): Grid of heights.
    minla (float): Minimum Latitude coordinate.
    minphi (float): Minimum Longitude coordinate.
    stepla (float): Step in Latitude direction.
    stepphi (float): Step in Longitude direction.

    Returns:
    tuple: Transformed Latitude, Longitude, Height, Northing, Easting, Easting Shift, Northing Shift after ETRS to ST70 transformation.
    """
    latlon = projections._stereographic_to_geodetic(e, n, E0, N0, PHI0, LAMBDA0, k0, a, b)
    h = transformations._helmert_2d(e, n, tE, tN, dm, Rz)

    e_shift = transformations._doBSInterpolation(h[0], h[1], mine, minn, stepe, stepn, shifts_grid[0])
    n_shift = transformations._doBSInterpolation(h[0], h[1], mine, minn, stepe, stepn, shifts_grid[1])
    h_shift = transformations._doBSInterpolation(latlon[1], latlon[0], minla, minphi, stepla, stepphi, heights_grid[0])

    return latlon[0], latlon[1], height + h_shift, h[1] + n_shift, h[0] + e_shift, e_shift, n_shift

@nb.jit
def _st70_to_etrs(e: float, n: float, height: float, E0: float, N0: float, PHI0: float, LAMBDA0: float, k0: float, a: float, b: float, tE: float, tN: float, dm: float, Rz: float, shifts_grid: np.ndarray, mine: float, minn: float, stepe: float, stepn: float, heights_grid: np.ndarray, minla: float, minphi: float, stepla: float, stepphi: float) -> tuple[float, float, float]:
    """
    Perform ST70 to ETRS transformation for Easting and Northing coordinates.

    Parameters:
    e (float): Easting coordinate.
    n (float): Northing coordinate.
    height (float): Height coordinate.
    E0 (float): Reference Easting coordinate.
    N0 (float): Reference Northing coordinate.
    PHI0 (float): Reference Latitude.
    LAMBDA0 (float): Reference Longitude.
    k0 (float): Scale factor.
    a (float): Semi-major axis of ellipsoid.
    b (float): Semi-minor axis of ellipsoid.
    tE (float): Translation in the East direction.
    tN (float): Translation in the North direction.
    dm (float): Scale factor.
    Rz (float): Rotation angle in seconds.
    shifts_grid (np.ndarray): Grid of shifts.
    mine (float): Minimum Easting coordinate.
    minn (float): Minimum Northing coordinate.
    stepe (float): Step in East direction.
    stepn (float): Step in North direction.
    heights_grid (np.ndarray): Grid of heights.
    minla (float): Minimum Latitude coordinate.
    minphi (float): Minimum Longitude coordinate.
    stepla (float): Step in Latitude direction.
    stepphi (float): Step in Longitude direction.

    Returns:
    tuple: Transformed Latitude, Longitude, Height after ST70 to ETRS transformation.
    """
    e_shift = transformations._doBSInterpolation(e, n, mine, minn, stepe, stepn, shifts_grid[0])
    n_shift = transformations._doBSInterpolation(e, n, mine, minn, stepe, stepn, shifts_grid[1])

    h = transformations._helmert_2d(e - e_shift, n - n_shift, tE, tN, dm, Rz)

    latlon = projections._stereographic_to_geodetic(h[0], h[1], E0, N0, PHI0, LAMBDA0, k0, a, b)

    h_shift = transformations._doBSInterpolation(latlon[1], latlon[0], minla, minphi, stepla, stepphi, heights_grid[0])

    return latlon[0], latlon[1], height + h_shift

@nb.jit
def _st70_to_utm(e: float, n: float, height: float, E0: float, N0: float, PHI0: float, LAMBDA0: float, k0: float, a: float, b: float, tE: float, tN: float, dm: float, Rz: float, shifts_grid: np.ndarray, mine: float, minn: float, stepe: float, stepn: float, heights_grid: np.ndarray, minla: float, minphi: float, stepla: float, stepphi: float, zone: int) -> tuple[float, float, float]:
    """
    Perform ST70 to UTM transformation for Easting, Northing, and Height coordinates.

    Parameters:
    e (float): Easting coordinate.
    n (float): Northing coordinate.
    height (float): Height coordinate.
    E0 (float): Reference Easting coordinate.
    N0 (float): Reference Northing coordinate.
    PHI0 (float): Reference Latitude.
    LAMBDA0 (float): Reference Longitude.
    k0 (float): Scale factor.
    a (float): Semi-major axis of ellipsoid.
    b (float): Semi-minor axis of ellipsoid.
    tE (float): Translation in the East direction.
    tN (float): Translation in the North direction.
    dm (float): Scale factor.
    Rz (float): Rotation angle in seconds.
    shifts_grid (np.ndarray): Grid of shifts.
    mine (float): Minimum Easting coordinate.
    minn (float): Minimum Northing coordinate.
    stepe (float): Step in East direction.
    stepn (float): Step in North direction.
    heights_grid (np.ndarray): Grid of heights.
    minla (float): Minimum Latitude coordinate.
    minphi (float): Minimum Longitude coordinate.
    stepla (float): Step in Latitude direction.
    stepphi (float): Step in Longitude direction.
    zone (int): UTM zone.

    Returns:
    tuple: Transformed Easting, Northing, and Height coordinates after ST70 to UTM transformation.
    """
    lat, lon, height = transformations._st70_to_etrs(e, n, height, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi)

    utm = projections._tm_latlon2en(lat, lon, 500000.0, 0.0, 0.0, math.radians(zone * 6.0 - 183.0), 0.9996, a, b)

    return utm[0], utm[1], height

class Transform:
    """
    Class representing a transformation object.

    Attributes:
    - params (dict): Parameters for the transformation.
    - grid_version (str): Version of the grid.
    - grid (dict): Information about the grid.
    - geoid (dict): Information about the geoid.
    - grid_shifts (dict): Grid of geodetic shifts.
    - geoid_heights (dict): Grid of geoid heights.
    - helmert (dict): Helmert transformation parameters.
    - source (str): Source of the transformation.
    - source_epsg (int): EPSG code for the source CRS.
    - dest (str): Destination CRS.
    - dest_epsg (int): EPSG code for the destination CRS.
    - crs (object): Coordinate reference system object.
    - projection (str): Projection information.
    - a (float): Semi-major axis of the ellipsoid.
    - b (float): Semi-minor axis of the ellipsoid.
    - f (float): Flattening of the ellipsoid.
    - k0 (float): Scale factor.
    - E0 (float): Reference easting value.
    - N0 (float): Reference northing value.
    - PHI0 (float): Reference latitude value.
    - LAMBDA0 (float): Reference longitude value.
    
    Methods:
    - etrs_to_st70: Convert ETRS coordinates to ST70 coordinates.
    - st70_to_etrs: Convert ST70 coordinates to ETRS coordinates.
    - st70_to_utm: Convert ST70 coordinates to UTM coordinates. Not implemented yet.
    - utm_to_st70: Convert UTM coordinates to ST70 coordinates. Not implemented yet.

    Example:
    transform = Transform(filename='example_grid_file.spg')
    """    

    def __init__(self, filename:str=None):    # intialise constants

        if filename is None:
            filename = sorted(Path(__file__).parent.joinpath('data').glob('rom_grid3d_*.spg'))[-1]

        if not filename or not Path(filename).exists():
            raise FileNotFoundError('Grid file not found.')

        with open(filename, 'rb') as f:
            grid_data = pickle.load(f)

        self.params = grid_data['params']
        self.grid_version = grid_data['params']['version']

        self.grid = {}
        self.grid['name'] = grid_data['grids']['geodetic_shifts']['name']
        self.grid['source'] = grid_data['grids']['geodetic_shifts']['source']
        self.grid['target'] = grid_data['grids']['geodetic_shifts']['target']

        self.geoid = {}
        self.geoid['name'] = grid_data['grids']['geoid_heights']['name']
        self.geoid['source'] = grid_data['grids']['geoid_heights']['source']
        self.geoid['target'] = grid_data['grids']['geoid_heights']['target']

        self.grid_shifts = grid_data['grids']['geodetic_shifts']
        self.geoid_heights = grid_data['grids']['geoid_heights']
        self.load_grids(grid_data)

        self.helmert = {}

        self.source = grid_data['grids']['geodetic_shifts']['source']
        self.source_epsg = 4258

        if 'krasov' in self.grid['name']:
            self.dest = 'st70'
            self.dest_epsg = 3844
        else:
            raise NotImplementedError(f'Target CRS {self.grid["target"]} unsupported')

        self.helmert['etrs2stereo'] = grid_data['params']['helmert']['os_' + self.dest]
        self.helmert['stereo2etrs'] = grid_data['params']['helmert'][self.dest + '_os']

        self.crs = crs.crs(self.dest_epsg, self.source_epsg)
        self.projection = self.crs.projection

        self.set_ellipsoid_param()

    def load_grids(self, grid_data):
        self.gpu = False

    def set_ellipsoid_param(self):

        self.a = float(self.crs.projection['a'])
        self.b = float(self.crs.projection['b'])
        self.f = float(self.crs.projection['f'])
        self.k0 = float(self.crs.projection['k'])

        for axis in self.crs.axes:
            axis_direction = axis.abbrev[0].lower()

            if axis_direction in ('x', 'y'):

                if axis.name[0].lower() == 'e':
                    self.E0 = float(self.crs.projection[f'{axis_direction}_0'])
                elif axis.name[0].lower() == 'n':
                    self.N0 = float(self.crs.projection[f'{axis_direction}_0'])

        self.PHI0 = math.radians(self.crs.projection['lat_0'])
        self.LAMBDA0 = math.radians(self.crs.projection['lon_0'])

    def helmert_2d(self, east, north, transform='etrs2stereo'):
        return _helmert_2d(east, north, **self.helmert[transform])

    @staticmethod
    @nb.jit('(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:],f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8)', nopython=True, parallel=True)
    def _bulk_etrs_to_st70(lat, lon, z, e, n, height, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi):

        for i in nb.prange(e.shape[0]):
           e[i], n[i], height[i] =  transformations._etrs_to_st70(lat[i], lon[i], z[i],
                                                                 E0, N0, PHI0, LAMBDA0, k0, a, b,
                                                                 tE, tN, dm, Rz,
                                                                 shifts_grid, mine, minn, stepe, stepn,
                                                                 heights_grid, minla, minphi, stepla, stepphi)

    @staticmethod
    @nb.jit('(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:],f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8)', nopython=True, parallel=True)
    def _bulk_st70_to_etrs(e, n, height, lat, lon, z, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi):
        """
        Helper function to bulk convert coordinates from Stereo 70 to ETRS89.

        Parameters:
        e (array): Array of easting coordinates in Stereo 70.
        n (array): Array of northing coordinates in Stereo 70.
        height (array): Array of heights in Stereo 70.
        lat (array): Array to store latitude coordinates in ETRS89.
        lon (array): Array to store longitude coordinates in ETRS89.
        z (array): Array to store heights in ETRS89.
        E0 (float): Reference easting value.
        N0 (float): Reference northing value.
        PHI0 (float): Reference latitude value.
        LAMBDA0 (float): Reference longitude value.
        k0 (float): Scale factor.
        a (float): Semi-major axis of the ellipsoid.
        b (float): Semi-minor axis of the ellipsoid.
        tE (float): Translation in east direction.
        tN (float): Translation in north direction.
        dm (float): Molodensky-Badekas parameter.
        Rz (float): Rotation parameter.
        shifts_grid (array): Grid of shifts.
        mine (float): Minimum easting value in the grid.
        minn (float): Minimum northing value in the grid.
        stepe (float): Step size in east direction.
        stepn (float): Step size in north direction.
        heights_grid (array): Grid of heights.
        minla (float): Minimum latitude value in the grid.
        minphi (float): Minimum longitude value in the grid.
        stepla (float): Step size in latitude direction.
        stepphi (float): Step size in longitude direction.
        """
        for i in nb.prange(e.shape[0]):
            lat[i], lon[i], z[i] = transformations._st70_to_etrs(e[i], n[i], height[i],
                                                                 E0, N0, PHI0, LAMBDA0, k0, a, b,
                                                                 tE, tN, dm, Rz,
                                                                 shifts_grid, mine, minn, stepe, stepn,
                                                                 heights_grid, minla, minphi, stepla, stepphi)
    
    @staticmethod
    @nb.jit('(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:],f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,i8)', nopython=True, parallel=True)
    def _bulk_st70_to_utm(e, n, height, utm_e, utm_n, z, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi, zone):
        """
        Helper function to bulk convert coordinates from Stereo 70 to UTM.

        Parameters:
        e (array): Array of easting coordinates in Stereo 70.
        n (array): Array of northing coordinates in Stereo 70.
        height (array): Array of heights in Stereo 70.
        utm_e (array): Array to store UTM easting coordinates.
        utm_n (array): Array to store UTM northing coordinates.
        z (array): Array to store heights in UTM.
        E0 (float): Reference easting value.
        N0 (float): Reference northing value.
        PHI0 (float): Reference latitude value.
        LAMBDA0 (float): Reference longitude value.
        k0 (float): Scale factor.
        a (float): Semi-major axis of the ellipsoid.
        b (float): Semi-minor axis of the ellipsoid.
        tE (float): Translation in east direction.
        tN (float): Translation in north direction.
        dm (float): Molodensky-Badekas parameter.
        Rz (float): Rotation parameter.
        shifts_grid (array): Grid of shifts.
        mine (float): Minimum easting value in the grid.
        minn (float): Minimum northing value in the grid.
        stepe (float): Step size in east direction.
        stepn (float): Step size in north direction.
        heights_grid (array): Grid of heights.
        minla (float): Minimum latitude value in the grid.
        minphi (float): Minimum longitude value in the grid.
        stepla (float): Step size in latitude direction.
        stepphi (float): Step size in longitude direction.
        zone (int): UTM zone.
        """
        raise NotImplementedError('ST70 to UTM transformation not implemented yet.')    
        # for i in nb.prange(e.shape[0]):
        #    utm_e[i], utm_n[i], z[i] =  transformations._st70_to_utm(e[i], n[i], height[i],
        #                                                             E0, N0, PHI0, LAMBDA0, k0, a, b,
        #                                                             tE, tN, dm, Rz,
        #                                                             shifts_grid, mine, minn, stepe, stepn,
        #                                                             heights_grid, minla, minphi, stepla, stepphi, zone)

    def etrs_to_st70(self, lat: np.array, lon: np.array, z: np.array, e: np.array, n: np.array, height: np.array) -> None:
        """
        Function to bulk convert coordinates from ETRS89 to Stereo 70.

        Parameters:
        lat (array): Array of latitude coordinates in ETRS89.
        lon (array): Array of longitude coordinates in ETRS89.
        z (array): Array of heights in ETRS89.
        e (array): Array to store easting coordinates in Stereo 70.
        n (array): Array to store northing coordinates in Stereo 70.
        height (array): Array to store heights in Stereo 70.
        """
        self._bulk_etrs_to_st70(lat, lon, z, e, n, height,
                             self.E0, self.N0, self.PHI0, self.LAMBDA0, self.k0, self.a, self.b,
                             self.helmert['etrs2stereo']['tE'], self.helmert['etrs2stereo']['tN'], self.helmert['etrs2stereo']['dm'], self.helmert['etrs2stereo']['Rz'],
                             self.grid_shifts['grid'],
                             self.grid_shifts['metadata']['mine'],
                             self.grid_shifts['metadata']['minn'],
                             self.grid_shifts['metadata']['stepe'],
                             self.grid_shifts['metadata']['stepn'],
                             self.geoid_heights['grid'],
                             self.geoid_heights['metadata']['minla'],
                             self.geoid_heights['metadata']['minphi'],
                             self.geoid_heights['metadata']['stepla'],
                             self.geoid_heights['metadata']['stepphi'])

    def st70_to_etrs(self, e: np.array, n: np.array, height: np.array, lat: np.array, lon: np.array, z: np.array) -> None:
        """
        Function to bulk convert coordinates from Stereo 70 to ETRS89.

        Parameters:
        e (array): Array of easting coordinates in Stereo 70.
        n (array): Array of northing coordinates in Stereo 70.
        height (array): Array of heights in Stereo 70.
        lat (array): Array to store latitude coordinates in ETRS89.
        lon (array): Array to store longitude coordinates in ETRS89.
        z (array): Array to store heights in ETRS89.
        """
        self._bulk_st70_to_etrs(e, n, height, lat, lon, z,
                             self.E0, self.N0, self.PHI0, self.LAMBDA0, self.k0, self.a, self.b,
                             self.helmert['stereo2etrs']['tE'], self.helmert['stereo2etrs']['tN'], self.helmert['stereo2etrs']['dm'], self.helmert['stereo2etrs']['Rz'],
                             self.grid_shifts['grid'],
                             self.grid_shifts['metadata']['mine'],
                             self.grid_shifts['metadata']['minn'],
                             self.grid_shifts['metadata']['stepe'],
                             self.grid_shifts['metadata']['stepn'],
                             self.geoid_heights['grid'],
                             self.geoid_heights['metadata']['minla'],
                             self.geoid_heights['metadata']['minphi'],
                             self.geoid_heights['metadata']['stepla'],
                             self.geoid_heights['metadata']['stepphi'])

    def st70_to_utm(self, e: np.array, n: np.array, height: np.array, utm_e: np.array, utm_n: np.array, z: np.array, zone: int) -> None:
        """
        Function to bulk convert coordinates from Stereo 70 to UTM.

        Parameters:
        e (array): Array of easting coordinates in Stereo 70.
        n (array): Array of northing coordinates in Stereo 70.
        height (array): Array of heights in Stereo 70.
        utm_e (array): Array to store UTM easting coordinates.
        utm_n (array): Array to store UTM northing coordinates.
        z (array): Array to store heights in UTM.
        zone (int): UTM zone.
        """
        
        raise NotImplementedError('ST70 to UTM transformation not implemented yet.')
    
        # self._bulk_st70_to_utm(e, n, height, utm_e, utm_n, z,
        #                      self.E0, self.N0, self.PHI0, self.LAMBDA0, self.k0, self.a, self.b,
        #                      self.helmert['stereo2etrs']['tE'], self.helmert['stereo2etrs']['tN'], self.helmert['stereo2etrs']['dm'], self.helmert['stereo2etrs']['Rz'],
        #                      self.grid_shifts['grid'],
        #                      self.grid_shifts['metadata']['mine'],
        #                      self.grid_shifts['metadata']['minn'],
        #                      self.grid_shifts['metadata']['stepe'],
        #                      self.grid_shifts['metadata']['stepn'],
        #                      self.geoid_heights['grid'],
        #                      self.geoid_heights['metadata']['minla'],
        #                      self.geoid_heights['metadata']['minphi'],
        #                      self.geoid_heights['metadata']['stepla'],
        #                      self.geoid_heights['metadata']['stepphi'],
        #                      zone)
