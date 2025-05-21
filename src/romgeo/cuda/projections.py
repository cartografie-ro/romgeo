#!/usr/bin/env python
# coding: utf-8
# projections class - Perform CRS projections

import numba as nb
import numba.cuda
from romgeo import projections

class geocentric(projections.geocentric):

    @staticmethod
    @nb.cuda.jit('(f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8, f8)')
    def _bulk_geodetic_to_geocentric(lat, lon, h, x, y, z, a, b):
        i = nb.cuda.grid(1)
        if i < lat.shape[0]:
            x[i], y[i], z[i] =  projections._geodetic_to_geocentric(lat[i], lon[i], h[i], a, b)

    @staticmethod
    @nb.cuda.jit('(f8[:], f8[:], f8[:], f8[:], f8[:], f8[:], f8, f8)')
    def _bulk_geocentric_to_geodetic(x, y, z, lat, lon, h, a, b):
        i = nb.cuda.grid(1)
        if i < x.shape[0]:
            lat[i], lon[i], h[i] =  projections._geocentric_to_geodetic(x[i], y[i], z[i], a, b)

    def geodetic_to_geocentric(self, lat, lon, h, x, y, z):
        self._bulk_geodetic_to_geocentric.forall(lat.shape[0])(lat, lon, h, x, y, z, self.a, self.b)
        nb.cuda.synchronize()

    def geocentric_to_geodetic(self, x, y, z, lat, lon, h):
        self._bulk_geocentric_to_geodetic.forall(x.shape[0])(x, y, z, lat, lon, h, self.a, self.b)
        nb.cuda.synchronize()
        
class stereographic(projections.stereographic):
        
    @staticmethod
    @nb.cuda.jit('(f8[:], f8[:], f8[:], f8[:], f8, f8, f8, f8, f8, f8, f8)')
    def _bulk_geodetic_to_stereographic(lat, lon, e, n, E0, N0, PHI0, LAMBDA0, k0, a, b):
        i = nb.cuda.grid(1)
        if i < lat.shape[0]:
            e[i], n[i] = projections._geodetic_to_stereographic(lat[i], lon[i], E0, N0, PHI0, LAMBDA0, k0, a, b)
            
    @staticmethod
    @nb.cuda.jit('(f8[:], f8[:], f8[:], f8[:], f8, f8, f8, f8, f8, f8, f8)')
    def _bulk_stereographic_to_geodetic(e, n, lat, lon, E0, N0, PHI0, LAMBDA0, k0, a, b):
        i = nb.cuda.grid(1)
        if i < e.shape[0]:
            lat[i], lon[i] = projections._stereographic_to_geodetic(e[i], n[i], E0, N0, PHI0, LAMBDA0, k0, a, b)  
        
    def geodetic_to_stereographic(self, lat, lon, e, n):
        self._bulk_geodetic_to_stereographic.forall(lat.shape[0])(lat, lon, e, n, self.E0, self.N0, self.PHI0, self.LAMBDA0, self.k0, self.a, self.b)
        nb.cuda.synchronize()
        
    def stereographic_to_geodetic(self, e, n, lat, lon):
        self._bulk_stereographic_to_geodetic.forall(e.shape[0])(e, n, lat, lon, self.E0, self.N0, self.PHI0, self.LAMBDA0, self.k0, self.a, self.b)
        nb.cuda.synchronize()
