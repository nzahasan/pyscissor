import fiona
import unittest
import numpy as np
from pyscissor import scissor
from shapely.geometry import Polygon,shape

class test_scissor(unittest.TestCase):

    # all edge + lat reversed
    def test_generel_lr(self):
        poly = Polygon([(1,1),(2,1),(2,2),(1,2)])
        x = np.array([1,2])
        y = np.array([2,1])
        pys=scissor(poly,y,x)
        wg = pys.get_masked_weight()
        total_intersect = wg[wg>0].shape[0]

        self.assertEqual(total_intersect,4)
        self.assertEqual(wg.sum(),1)

    # all edge + lat not reversed
    def test_generel_lnr(self):
        poly = Polygon([(1,1),(2,1),(2,2),(1,2)])
        x = np.array([1,2])
        y = np.array([1,2])
        pys=scissor(poly,y,x)
        wg = pys.get_masked_weight()
        total_intersect = wg[wg>0].shape[0]

        self.assertEqual(total_intersect,4)
        self.assertEqual(wg.sum(),1)

    # contained + lat reversed
    def test_contained_lr(self):
        poly = Polygon([(2,2),(3,2),(3,3),(2,3)])
        x = np.array([1,2,3,4])
        y = np.array([4,3,2,1])
        pys=scissor(poly,y,x)
        wg = pys.get_masked_weight()
        total_intersect = wg[wg>0].shape[0]

        self.assertEqual(total_intersect,4)
        self.assertEqual(wg.sum(),1)

    # contained + lat not reversed
    def test_contained_lnr(self):
        poly = Polygon([(2,2),(3,2),(3,3),(2,3)])
        x = np.array([1,2,3,4])
        y = np.array([1,2,3,4])
        pys=scissor(poly,y,x)
        wg = pys.get_masked_weight()
        total_intersect = wg[wg>0].shape[0]

        self.assertEqual(total_intersect,4)
        self.assertEqual(wg.sum(),1)


    def test_contained_lnr_recursive(self):
        poly = Polygon([(2,2),(3,2),(3,3),(2,3)])
        x = np.array([1,2,3,4])
        y = np.array([1,2,3,4])
        pys=scissor(poly,y,x)
        wg = pys.get_masked_weight_recursive()
        total_intersect = wg[wg>0].shape[0]

        self.assertEqual(total_intersect,4)
        self.assertEqual(wg.sum(),1)


    def test_contained_shp2_recursive(self):
        
        sf = fiona.open("data/shape_2.geojson",'r')
        rec = next(iter(sf))

        shapely_poly = shape(rec['geometry'])
        lons=np.arange(71.5,110.5)
        lats=np.arange(19.5,35.5)
        pys = scissor(shapely_poly,lats,lons)
        wg = pys.get_masked_weight_recursive()

        self.assertEqual(shapely_poly.area,wg.sum())



if __name__ == '__main__':
    unittest.main()