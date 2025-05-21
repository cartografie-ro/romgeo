import unittest

import romgeo as rg
import numpy as np

class TestRomgeo(unittest.TestCase):
    def test_etrs_st70(self):

        print(f"Test ETRS - ST70")

        N = np.array([45.00],    dtype=float)
        E = np.array([25.00],    dtype=float)
        H = np.array([123.0],    dtype=float)

        X = np.full_like(N, 0.0)
        Y = np.full_like(E, 0.0)
        Z = np.full_like(H, 0.0)

        t = rg.transformations.Transform()
        t.etrs_to_st70(N,E,H, X,Y,Z)

        N1 = np.full_like(N, 0.0)
        E1 = np.full_like(E, 0.0)
        H1 = np.full_like(H, 0.0)

        t.st70_to_etrs(X,Y,Z, N1,E1,H1)

        print(f"3844: {X[0]:.3f} {Y[0]:.3f} {Z[0]:.3f}")
        print(f"4326: {N[0]:.3f} - {N1[0]:.3f}")
        print(f"4326: {E[0]:.3f} - {E1[0]:.3f}")

        self.assertAlmostEqual(N[0],N1[0],3)

    def test_grid(self):

        print(f"Grid Info")

        t = rg.transformations.Transform()
        print(f"{t.grid_version=}")
        

if __name__ == '__main__':
    unittest.main()