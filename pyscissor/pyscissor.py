#! /usr/bin/env python3

import numpy as np
from shapely.geometry import Polygon,MultiPolygon

class scissor():    

    def __init__(self, shape_obj,lattitude_array,longitude_array):
        
        self.lats  = lattitude_array
        self.nlats = self.lats.shape[0]
        

        self.lons  = longitude_array
        self.nlons = self.lons.shape[0]

        
        # check for shapely polygon
        if isinstance(shape_obj,Polygon) or isinstance(shape_obj,MultiPolygon):
            self.shape_obj = shape_obj
        else:
            raise Exception('Invalid object, Must be a shapely Polygon or MultiPolygon.')

        # find nearest neighbours for lat and lons
        min_lon_idx = np.abs(self.lons - self.shape_obj.bounds[0]).argmin()
        max_lon_idx = np.abs(self.lons - self.shape_obj.bounds[2]).argmin()

        min_lat_idx = np.abs(self.lats - self.shape_obj.bounds[1]).argmin()
        max_lat_idx = np.abs(self.lats - self.shape_obj.bounds[3]).argmin()


        # expand lat lon index by 1 cell 
        self.lon_idx_range = np.arange( 
            (min_lon_idx-1) if min_lon_idx>0 else 0,
            (max_lon_idx+1)+1 if (max_lon_idx+1)<self.nlons else max_lon_idx+1
        )

        # lat can be laid in 2 ways:
        #   - lat deceases with index[generel case] / Lat reversed
        #   - lat inceases with index[odd case]  

        # (90.53868604700006, 20.746514391000062, 92.68025738200004, 24.266389881000066)

        self.lat_reversed = True

        if self.lats[1]>self.lats[0]:
            self.lat_reversed = False

        # range for iterating grid
        if self.lat_reversed:
            # generel
            self.lat_idx_range = np.arange(
                (max_lat_idx-1) if max_lat_idx>0 else 0,
                (min_lat_idx+1)+1 if (min_lat_idx+1)<(self.nlats-1) else min_lat_idx+1
            )
        elif not self.lat_reversed:
            self.lat_idx_range = np.arange(
                (min_lat_idx-1) if min_lat_idx>0 else 0,
                (max_lat_idx+1)+1 if (max_lat_idx+1)<(self.nlats-1) else max_lat_idx+1
            )

    def __repr__(self):
        return f'<pyscissor>'        


    
    def get_masked_weight(self):
        
        ''' 
    
        # generel case
                
                                       r-1,c 
                                         |
                                         |
                                         |
                      [1,0]---------[r+(r-1)]/2--------[1,1]
                        |                |               |
                        |                |               |
                        |                |               |
        r,c-1 -----[c+(c-1)]/2 -------- r,c -------- [c+(c-1)]/2 ----- r,c+1
                        |                |               |
                        |                |               |
                        |                |               |
                      [0,0]--------- [r+(r+1)]/2 ------[1,0]
                                         |
                                         |
                                         |
                                       r+1,c

        # edge cases => latitude decreases when `r` increases
        
        @ lat_reversed=true
        -------------------
        
        >>  top edge: r=0              
                        
                    r+[r-(r+1)]/2,c            *|23.5
                           .
                           .
                           .
               r,c-1 ---- r,c ---- r,c+1       0|23 
                           |
                           |
                         r+1,c                 1|22 

        >>  bottom edge: r= nr-1

                         r-1,c                 8|23
                           |
                           |
               r,c-1 ---- r,c ---- r,c+1       9|22
                           .
                           .
                           .
                    r - [(r-1)-r]/2,c          *|21.5

        @ lat_reversed=false  
        --------------------

        >> bottom edge: r=0               
                        
                         r+1,c                 1|23
                           |
                           |
               r,c-1 ---- r,c ---- r,c+1       0|22
                           .
                           .
                           .
                  r - [(r+1)-r]/2,c            *|21.5

        >> top edge: r= rn-1

                    r + [r-(r-1)]/2,c          *|24.5
                           .
                           .
                           .
               r,c-1 ---- r,c ---- r,c+1       9|24
                           |
                           |
                         r-1,c                 8|23

        
        left edge: c=0

                            r-1,c               
                               |
                               |
          r,c-[(c+1)-c]/2 ~~~ r,c ---- r,c+1    
                               |
                               |
                               |
                            r+1,c

        right edge: c= nc-1

                   r-1,c
                     |
                     |
          r,c-1 --- r,c ~~~ r,c + [c - (c-1)]/2
                     |
                     |
                     |
                  r+1,c
        '''


        weight_grid = np.zeros((self.nlats,self.nlons))
        mask_grid   = np.ones((self.nlats,self.nlons),dtype=np.bool)

        for ry in self.lat_idx_range:
            
            for cx in self.lon_idx_range:
            
                # edge cases

                if cx==0:
                    # x0 = x - dx1/2
                    x0 = self.lons[cx] - abs( self.lons[cx+1] - self.lons[cx])/2
                else:
                    x0 = (self.lons[cx] + self.lons[cx-1])/2

                if cx==(self.nlons-1):
                    # x1 = x + dxn/2
                    x1 = self.lons[cx] + abs(self.lons[cx] - self.lons[cx-1])/2
                else:
                    x1 = (self.lons[cx] + self.lons[cx+1])/2

                if ry==0:
                    if self.lat_reversed:
                        y1 = self.lats[ry] + abs(self.lats[ry] - self.lats[ry+1])/2
                    elif not self.lat_reversed:
                        # r - [(r+1)-r]/2,c
                        y1 = self.lats[ry] - abs(self.lats[ry+1] - self.lats[ry])/2
                else:
                    y1 = (self.lats[ry] + self.lats[ry-1])/2

                if ry==(self.nlats-1):

                    if self.lat_reversed:
                        y0 = self.lats[ry] - abs(self.lats[ry-1]-self.lats[ry])/2
                    elif not self.lat_reversed:
                        # r + [r-(r-1)]/2
                        y0 =  self.lats[ry] + abs(self.lats[ry]-self.lats[ry-1])/2
                        
                else:
                    y0 = (self.lats[ry]+self.lats[ry+1])/2

                # grid box corners
                grid00 = (x0,y0)
                grid10 = (x1,y0)
                grid11 = (x1,y1)
                grid01 = (x0,y1)

                # polygon can be defined both clock and anti clock wise way
                
                grid_box_poly = Polygon((grid00,grid10,grid11,grid01))

                # check if area of grid_box_poly=0
                if grid_box_poly.area==0:
                  raise Exception('Invalid grid boundary encountered')

                intersection_area = self.shape_obj.intersection(grid_box_poly).area

                weight_grid[ry,cx] =  intersection_area / grid_box_poly.area

                if intersection_area >0:
                    mask_grid[ry,cx]=False


        # return a musked array, if only mask is neded use arr.mask
        return np.ma.masked_array(weight_grid,mask=mask_grid)

