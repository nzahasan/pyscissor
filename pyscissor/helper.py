#!/usr/bin/env python3
# healper class for reading shapefile

import fiona 
from shapely.geometry import shape

class shape_container():

    def __init__(self,shape,properties):
        self.shape=shape 
        self.properties=properties

class shapereader():

    def __init__(self,filename):
              
        self.sd = list(fiona.open(filename,'r'))
        
    def __getitem__(self,idx):

        return shape_container( 
            shape(self.sd[idx]['geometry']),
            self.sd[idx]['properties'] 
        )

