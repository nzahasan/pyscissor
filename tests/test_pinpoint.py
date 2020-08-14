import unittest
import numpy as np
from pyscissor import pinpoint
import pytest

class test_scissor(unittest.TestCase):

    # generel + lat not reversed
    def test_generel_lnr(self):

        lats = np.array([24,23])
        lons = np.array([88,89])
        vals = np.array([[1,2],[3,4]])
        
        t = pinpoint(lats,lons)
        t.set_xy(23.6,88.6)

        self.assertLess( abs( ( 3.6+ 0.6* (1.6-3.6) ) - t.bilinear(vals) ), 0.00001)


    # generel + lat reversed
    def test_generel_lr(self):

        lats = np.array([23,24])
        lons = np.array([88,89])
        vals = np.array([[1,2],[3,4]])
        
        t = pinpoint(lats,lons)
        t.set_xy(23.6,88.6)
        self.assertLess(abs( ( 1.6 + 0.6* (3.6-1.6) ) - t.bilinear(vals) ), 0.00001)



if __name__ == '__main__':
    unittest.main()