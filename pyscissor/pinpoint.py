import numpy as np

class pinpoint():
    '''
        healper class for extracting interpolated
        time series for point from netcdf
    '''

    def __init__(self, lattitude_array, longitude_array):

        self.lat_arr  = lattitude_array
        self.lon_arr  = longitude_array
    
        self.nn_id   = None
        self.bilcf   = None
        self.surr_id = None

        # check lat reversed or not
        if self.lat_arr[1]>self.lat_arr[0]:
            self.lat_reversed = True 
        else:
            self.lat_reversed = False

    def check_set_xy(self):
        if self.nn_id is None or self.surr_id is None or self.bilcf is None:
            raise ValueError('set_ltln() has not been not called')
    
    def set_xy(self,lat,lon):
    
        self.nn_id= [ 
                         np.argmin(np.abs(self.lat_arr-lat)),
                         np.argmin(np.abs(self.lon_arr-lon))
                     ]
        '''
              x0,y1                x1,yi
                |      Vx1           |
            ----|-------^------------|----y1    |5  |6
                |       |            |
                |----->Vxy<----------|----> xmn |5.5|5.5
                |       |            |
            ----|-------^------------|----y0    |6  |5
                |      Vx0           |
              x0,y0                x1,y0

        '''
        # check
        # - if within raster bound
        
        # get surrounding index // need to consider edge cases
        
        x1_id= (self.lon_arr>=lon).argmax()
        x0_id=x1_id-1

        if self.lat_reversed==False: 
            y0_id = (self.lat_arr<=lat).argmax()
            y1_id = y0_id-1
        if self.lat_reversed==True: 
            y0_id = (self.lat_arr>=lat).argmax()
            y1_id = y0_id-1

        
        self.surr_id= dict( x=(x0_id,x1_id), y=(y0_id,y1_id) )

        '''
        ** bilinear calculations **

        simplified calc:

        vx0 = v00 + (v10 - v00) * [ (x-x0)/(x1-x0) ] 
        vx1 = v01 + (v10 - v00) * [ (x-x0)/(x1-x0) ] 

        @ interpolated 
        vxy = vx0 + (vx1 - vx0) * [ (y-y0)/(y1-y0) ] 

        express this equation ^ in terms of coefficients of v00,v10,v11,v01
        
        ref@ https://en.wikipedia.org/wiki/Bilinear_interpolation
        '''

        # get lat lon cords
        x0,x1=self.lon_arr[x0_id],self.lon_arr[x1_id]
        y0,y1=self.lat_arr[y0_id],self.lat_arr[y1_id]
        cfm_0 = np.array([
                [1, x0, y0, x0*y0],
                [1, x0, y1, x0*y1],
                [1, x1, y0, x1*y0],
                [1, x1, y1, x1*y1],
            ],dtype=np.float64)
        cfm_1=np.array([1, lon, lat, lon*lat],dtype=np.float64)

        # b=>x.y: order b00,b01,b10,b11
        self.bilcf = np.matmul(np.linalg.inv(cfm_0).T, cfm_1)


    def bilinear(self,grid_2d):

        self.check_set_xy()
        # check if grid 2d is of same shape of lat.shape,lon.shape

        # surr vals v=>x.y
        v00 = grid_2d[ self.surr_id['y'][0], self.surr_id['x'][0] ]
        v01 = grid_2d[ self.surr_id['y'][1], self.surr_id['x'][0] ]
        v10 = grid_2d[ self.surr_id['y'][0], self.surr_id['x'][1] ]
        v11 = grid_2d[ self.surr_id['y'][1], self.surr_id['x'][1] ]

        return self.bilcf[0]*v00+self.bilcf[1]*v01+self.bilcf[2]*v10+self.bilcf[3]*v11 

