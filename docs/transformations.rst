Transformations Module
======================

This module provides functions and classes for coordinate transformations, including ETRS, Stereo70, and UTM projections.

Classes
-------

.. class:: Transform
   :members:

   Transform is responsible for handling transformations between different
   coordinate reference systems, specifically for Romanian spatial data.

   Attributes:
       - params (dict): Parameters for the transformations.
       - grid_version (str): Version of the grid data.
       - grid (dict): Information about the geodetic shifts grid.
       - geoid (dict): Information about the geoid heights grid.
       - grid_shifts (dict): Data for geodetic shifts.
       - geoid_heights (dict): Data for geoid heights.
       - helmert (dict): Helmert transformation parameters.
       - source (str): Source CRS.
       - source_epsg (int): EPSG code for the source CRS.
       - dest (str): Destination CRS.
       - dest_epsg (int): EPSG code for the destination CRS.
       - crs (object): CRS projection object.
       - projection (object): Projection parameters.
       - a (float): Semi-major axis of the ellipsoid.
       - b (float): Semi-minor axis of the ellipsoid.
       - f (float): Flattening of the ellipsoid.
       - k0 (float): Scale factor.
       - E0 (float): False easting.
       - N0 (float): False northing.
       - PHI0 (float): Latitude of origin.
       - LAMBDA0 (float): Longitude of origin.

.. method:: __init__(filename=None)
   
   Initialize the Transform class with optional grid data file.

   :param filename: Path to the grid data file, defaults to None.
   :type filename: str, optional

.. method:: load_grids(grid_data)
   
   Load the grids data into the object.

   :param grid_data: Grid data containing geodetic shifts and geoid heights.
   :type grid_data: dict

.. method:: set_ellipsoid_param()
   
   Set the ellipsoid parameters based on the CRS projection.

.. method:: helmert_2d(east, north, transform='etrs2stereo')
   
   Apply Helmert transformation to 2D coordinates.

   :param east: Easting coordinate.
   :type east: float
   :param north: Northing coordinate.
   :type north: float
   :param transform: Type of Helmert transformation, defaults to 'etrs2stereo'.
   :type transform: str, optional
   :returns: Transformed coordinates.
   :rtype: tuple

.. method:: etrs_to_st70(lat, lon, z, e, n, height)
   
   Transform coordinates from ETRS to Stereo70.

   :param lat: Latitude.
   :type lat: float
   :param lon: Longitude.
   :type lon: float
   :param z: Height.
   :type z: float
   :param e: Easting.
   :type e: float
   :param n: Northing.
   :type n: float
   :param height: Height.
   :type height: float

.. method:: st70_to_etrs(e, n, height, lat, lon, z)
   
   Transform coordinates from Stereo70 to ETRS.

   :param e: Easting.
   :type e: float
   :param n: Northing.
   :type n: float
   :param height: Height.
   :type height: float
   :param lat: Latitude.
   :type lat: float
   :param lon: Longitude.
   :type lon: float
   :param z: Height.
   :type z: float

.. method:: st70_to_utm(e, n, height, utm_e, utm_n, z, zone)
   
   Transform coordinates from Stereo70 to UTM.

   :param e: Easting.
   :type e: float
   :param n: Northing.
   :type n: float
   :param height: Height.
   :type height: float
   :param utm_e: UTM Easting.
   :type utm_e: float
   :param utm_n: UTM Northing.
   :type utm_n: float
   :param z: Height.
   :type z: float
   :param zone: UTM zone.
   :type zone: int

Examples
--------

Here is an example of how to use the `Transform` class:

.. code:: python

   import romgeo as rg
   
   # Initialize the Transform class
   t = rg.transform.Transform(filename=None)
   
   # Example usage for transforming coordinates
   lat, lon, z = 45.7489, 25.2087, 100  # ETRS coordinates
   e, n, height = 0.0, 0.0, 0.0        # Initialize variables for Stereo70 coordinates
   
   # Transform ETRS to Stereo70
   t.etrs_to_st70([lat], [lon], [z], [e], [n], [height])
   print(f"Stereo70 coordinates: Easting: {{e}}, Northing: {{n}}, Height: {{height}}")

   # Transform Stereo70 to ETRS
   t.st70_to_etrs([e], [n], [height], [lat], [lon], [z])
   print(f"ETRS coordinates: Latitude: {{lat}}, Longitude: {{lon}}, Height: {{z}}")

Functions
---------

.. function:: _spline_params(xk, yk)

   Return parameters of bicubic spline surface.

   :param xk: X-coordinate.
   :type xk: float
   :param yk: Y-coordinate.
   :type yk: float
   :returns: Parameters of the bicubic spline.
   :rtype: tuple

.. function:: _spline_grid(grid, cell_x, cell_y)

   Return the 16 unknown coefficients of the interpolated surface.

   :param grid: Grid data.
   :type grid: ndarray
   :param cell_x: X-index of the cell.
   :type cell_x: int
   :param cell_y: Y-index of the cell.
   :type cell_y: int
   :returns: Coefficients of the interpolated surface.
   :rtype: tuple

.. function:: _doBSInterpolation(x, y, minx, miny, stepx, stepy, grid)

   Perform bicubic spline interpolation on the given grid.

   :param x: X-coordinate.
   :type x: float
   :param y: Y-coordinate.
   :type y: float
   :param minx: Minimum X value of the grid.
   :type minx: float
   :param miny: Minimum Y value of the grid.
   :type miny: float
   :param stepx: Step size in X direction.
   :type stepx: float
   :param stepy: Step size in Y direction.
   :type stepy: float
   :param grid: Grid data.
   :type grid: ndarray
   :returns: Interpolated value.
   :rtype: float

.. function:: _helmert_2d(e, n, tE, tN, dm, Rz)

   Apply 2D Helmert transformation.

   :param e: Easting coordinate.
   :type e: float
   :param n: Northing coordinate.
   :type n: float
   :param tE: Translation in Easting.
   :type tE: float
   :param tN: Translation in Northing.
   :type tN: float
   :param dm: Scale difference.
   :type dm: float
   :param Rz: Rotation angle.
   :type Rz: float
   :returns: Transformed coordinates.
   :rtype: tuple

.. function:: _etrs_to_st70(lat, lon, z, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi)

   Transform coordinates from ETRS to Stereo70 using interpolation and Helmert transformation.

   :param lat: Latitude.
   :type lat: float
   :param lon: Longitude.
   :type lon: float
   :param z: Height.
   :type z: float
   :param E0: False easting.
   :type E0: float
   :param N0: False northing.
   :type N0: float
   :param PHI0: Latitude of origin.
   :type PHI0: float
   :param LAMBDA0: Longitude of origin.
   :type LAMBDA0: float
   :param k0: Scale factor.
   :type k0: float
   :param a: Semi-major axis of the ellipsoid.
   :type a: float
   :param b: Semi-minor axis of the ellipsoid.
   :type b: float
   :param tE: Translation in Easting.
   :type tE: float
   :param tN: Translation in Northing.
   :type tN: float
   :param dm: Scale difference.
   :type dm: float
   :param Rz: Rotation angle.
   :type Rz: float
   :returns: Transformed coordinates and height.
   :rtype: tuple
