#!/usr/bin/env python3

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
        # only search/operate within these bounds
        self.lon_idx_range = np.arange( 
            (min_lon_idx-1) if min_lon_idx>0 else 0,
            (max_lon_idx+1)+1 if (max_lon_idx+1)<self.nlons else max_lon_idx+1
        )

        # lat can be laid in 2 ways:
        #   - lat deceases with index[generel case] / Lat reversed
        #   - lat inceases with index[odd case]  

        # shape bound sample (90.53, 20.74, 92.68, 24.26)

        self.lat_reversed = True

        if self.lats[1]>self.lats[0]:
            self.lat_reversed = False

        # range for iterating grid
        if self.lat_reversed:
            # generel
            self.lat_idx_range = np.arange(
                (max_lat_idx-1) if max_lat_idx>0 else 0,
                (min_lat_idx+1)+1 if (min_lat_idx+1)<self.nlats else min_lat_idx+1
            )
        else:
            self.lat_idx_range = np.arange(
                (min_lat_idx-1) if min_lat_idx>0 else 0,
                (max_lat_idx+1)+1 if (max_lat_idx+1)< self.nlats else max_lat_idx+1
            )

    def __repr__(self):
        return '<pyscissor_instance>'        


    
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


    # using recursive division
    # inspiration by @ https://gist.github.com/perrette/a78f99b76aed54b6babf3597e0b331f8
    def get_masked_weight_recursive(self,lat_ids=None,lon_ids=None,masked_weight=None,root=True):

        '''
                      gy1
                       |
           23 > ----------------- < 22 (0)
                |               |
         gx0<---|               |--->gx1
                |               |
           22 > ----------------- < 23 (-1)
                       |
                      gy0

        '''

        # root func call
        if root==True:
            lat_ids       = self.lat_idx_range.copy()
            lon_ids       = self.lon_idx_range.copy()
            masked_weight = np.ma.masked_array(
                                np.zeros((self.nlats,self.nlons)),
                                mask = np.ones((self.nlats,self.nlons),dtype=np.bool)
                            )

        gx0,gx1= lon_ids[0],lon_ids[-1]
        gy0,gy1= lat_ids[-1],lat_ids[0]

        if gx0==0:
            x0 = self.lons[gx0] - abs( self.lons[gx0+1] - self.lons[gx0])/2
        else:
            x0 = (self.lons[gx0] + self.lons[gx0-1])/2

        if gx1==(self.nlons-1):
            x1 = self.lons[gx1] + abs(self.lons[gx1] - self.lons[gx1-1])/2
        else:
            x1 = (self.lons[gx1] + self.lons[gx1+1])/2

        if gy0==(self.nlats-1):
            if self.lat_reversed:
                y0 = self.lats[gy0] - abs(self.lats[gy0-1]-self.lats[gy0])/2
            else:
                y0 =  self.lats[gy0] + abs(self.lats[gy0]-self.lats[gy0-1])/2
        else:
            y0 = (self.lats[gy0]+self.lats[gy0+1])/2
          
        if gy1==0:
            if self.lat_reversed:
                y1 = self.lats[gy1] + abs(self.lats[gy1] - self.lats[gy1+1])/2
            else:
                y1 = self.lats[gy1] - abs(self.lats[gy1+1] - self.lats[gy1])/2
        else:
            y1 = (self.lats[gy1] + self.lats[gy1-1])/2 

        # grid box corners
        grid00,grid10,grid11,grid01 = (x0,y0),(x1,y0),(x1,y1),(x0,y1)

        grid_box_poly = Polygon((grid00,grid10,grid11,grid01))
        
        intersection_ratio = self.shape_obj.intersection(grid_box_poly).area/grid_box_poly.area

        lt_len = lat_ids.shape[0]
        ln_len = lon_ids.shape[0]


        if intersection_ratio>0:
            # full intersection
            if intersection_ratio==1:
                masked_weight[gy1:gy0+1,gx0:gx1+1] = 1
                masked_weight.mask[gy1:gy0+1,gx0:gx1+1]=False
            
            # partial intersection
            elif intersection_ratio<1:
                
                # single cell
                if lt_len==1 and ln_len==1:

                    if intersection_ratio >0:
                        masked_weight[lat_ids[0],lon_ids[0]]=intersection_ratio
                        masked_weight.mask[lat_ids[0],lon_ids[0]]=False
                
                # single row > subdevide into 2 row
                elif lt_len==1:
                    self.get_masked_weight_recursive(lat_ids,lon_ids[:ln_len//2],masked_weight,False)
                    self.get_masked_weight_recursive(lat_ids,lon_ids[ln_len//2:],masked_weight,False)
                
                # single column > subdevide into 2 column
                elif ln_len==1:
                    self.get_masked_weight_recursive(lat_ids[lt_len//2:],lon_ids,masked_weight,False)
                    self.get_masked_weight_recursive(lat_ids[:lt_len//2],lon_ids,masked_weight,False)

                # block > subdevide into 4 blocks
                else:
                    self.get_masked_weight_recursive(lat_ids[:lt_len//2],lon_ids[:ln_len//2],masked_weight,False)
                    self.get_masked_weight_recursive(lat_ids[:lt_len//2],lon_ids[ln_len//2:],masked_weight,False)
                    self.get_masked_weight_recursive(lat_ids[lt_len//2:],lon_ids[:ln_len//2],masked_weight,False)
                    self.get_masked_weight_recursive(lat_ids[lt_len//2:],lon_ids[ln_len//2:],masked_weight,False)

        # else 0: -> already is zero


        if root==True:
            return masked_weight





