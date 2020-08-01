import unittest
import numpy as np
from pyscissor import pinpoint

class test_scissor(unittest.TestCase):

    # generel + lat not reversed
    def test_generel_lnr(self):

        lats = np.array([24,23])
        lons = np.array([88,89])
        vals = np.array([[1,2],[3,4]])
        

        t = pinpoint(lats,lons)
        t.set_xy(23.5,88.5)
        self.assertEqual(0.25*vals.sum(),t.bilinear(vals))


    # generel + lat reversed
    def test_generel_lnr(self):

        lats = np.array([23,24])
        lons = np.array([88,89])
        vals = np.array([[1,2],[3,4]])
        

        t = pinpoint(lats,lons)
        t.set_xy(23.5,88.5)
        self.assertEqual(0.25*vals.sum(),t.bilinear(vals))



if __name__ == '__main__':
    unittest.main()