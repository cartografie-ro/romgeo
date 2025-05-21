#!/usr/bin/env python
# coding: utf-8
# projections class - Perform CRS projections

import numpy as np
import numba as nb
import numba.cuda
import math
import os
import pickle

from romgeo import crs
from romgeo import projections
from romgeo import transformations

class Transform(transformations.Transform):
    
    def load_grids(self, grid_data):
        self.grid_shifts['grid'] = nb.cuda.to_device(grid_data['grids']['geodetic_shifts']['grid'])
        self.geoid_heights['grid'] = nb.cuda.to_device(grid_data['grids']['geoid_heights']['grid'])
        self.gpu = True

    @staticmethod
    @nb.cuda.jit('(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:],f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8)')
    def _bulk_st70_to_etrs(e, n, height, lat, lon, z, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi):
        
        i = nb.cuda.grid(1)
        if i < e.shape[0]:
           lat[i], lon[i], z[i] =  transformations._st70_to_etrs(e[i], n[i], height[i],
                                                              E0, N0, PHI0, LAMBDA0, k0, a, b,
                                                              tE, tN, dm, Rz,
                                                              shifts_grid, mine, minn, stepe, stepn,
                                                              heights_grid, minla, minphi, stepla, stepphi)
                                                              
    @staticmethod
    @nb.cuda.jit('(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:],f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8,f4[:,:,:],f8,f8,f8,f8)')
    def _bulk_etrs_to_st70(lat, lon, z, e, n, height, E0, N0, PHI0, LAMBDA0, k0, a, b, tE, tN, dm, Rz, shifts_grid, mine, minn, stepe, stepn, heights_grid, minla, minphi, stepla, stepphi):

        i = nb.cuda.grid(1)
        if i < lat.shape[0]:
           e[i], n[i], height[i] =  transformations._etrs_to_st70(lat[i], lon[i], z[i],
                                                                 E0, N0, PHI0, LAMBDA0, k0, a, b,
                                                                 tE, tN, dm, Rz,
                                                                 shifts_grid, mine, minn, stepe, stepn,
                                                                 heights_grid, minla, minphi, stepla, stepphi)

    def st70_to_etrs(self, e, n, height, lat, lon, z):
        
        self._bulk_st70_to_etrs.forall(e.shape[0])(e, n, height, lat, lon, z,
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
                                    
        nb.cuda.synchronize()
        
    def etrs_to_st70(self, lat, lon, z, e, n, height):
        self._bulk_etrs_to_st70.forall(lat.shape[0])(lat, lon, z, e, n, height,
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
