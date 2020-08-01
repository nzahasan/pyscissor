import numpy as np
from collections import namedtuple

class pinpoint():

	def __init__(self, lattitude_array, longitude_array):

		self.lat_arr  = lattitude_array
		# self.nlats = self.lat_arr.shape[0]

		self.lon_arr  = longitude_array
		# self.nlons = self.lons.shape[0]

		self.nn_xy_id = None
		self.surr_id   = None

		# check lat reversed or not
		if self.lat_arr[1]>self.lat_arr[0]:
			self.lat_reversed = True 
		else:
			self.lat_reversed = False

	def check_set_xy(self):
		if self.nn_xy_id==None or self.surr_id==None:
				raise ValueError('set_ltln() has not been not called')
	
	def set_xy(self,lat,lon):
	
		self.nn_xy_id= [ 
						 np.argmin(np.abs(self.lat_arr-lat)),
						 np.argmin(np.abs(self.lon_arr-lon))
					 ]
		'''
		      x0,y1                x1,yi
		        |      x_m1          |
		    ----|-------^------------|----y1    |5
		        |       |            |
		        |----->m,n<----------|----> xmn |5.5
		        |       |            |
		    ----|-------^------------|----y0    |6
		        |      x_m0          |
		      x0,y0                x1,y0

		'''
		# check for raster bound
		# get surrounding index 
		# need to consider boundary condition
		x1_id= (self.lon_arr>=lon).argmax()
		x0_id=x1_id-1

		if self.lat_reversed==False: 
			y0_id = (self.lat_arr<=lat).argmax()
			y1_id = y0_id-1
		if self.lat_reversed==True: 
			y0_id = (self.lat_arr>=lat).argmax()
			y1_id = y0_id-1

		
		self.surr_id={ 'x':(x0_id,x1_id), 'y':(y0_id,y1_id) }
		
		# 
		x0,x1=self.lon_arr[x0_id],self.lon_arr[x1_id]
		y0,y1=self.lat_arr[y0_id],self.lat_arr[y1_id]

		# @wikipedia
		mat = np.array([
				[1,x0,y0,x0*y0],
				[1,x0,y1,x0*y1],
				[1,x1,y0,x1*y0],
				[1,x1,y1,x1*y1],
			])
		m2=np.array([1,lon,lat,lon*lat])

		self.b_coeff = np.matmul(np.linalg.inv(mat).T,m2)
		


	def bilinear(self,grid_2d):

		# self.check_set_xy()

		# surr vals
		v00 = grid_2d[ self.surr_id['y'][0], self.surr_id['x'][0] ]
		v01 = grid_2d[ self.surr_id['y'][1], self.surr_id['x'][0] ]
		v10 = grid_2d[ self.surr_id['y'][0], self.surr_id['x'][1] ]
		v11 = grid_2d[ self.surr_id['y'][1], self.surr_id['x'][1] ]

		
		return self.b_coeff[0]*v00+self.b_coeff[1]*v01+self.b_coeff[1]*v10+self.b_coeff[1]*v11 


