#!/usr/bin/env python3

'''
Adds Mask in netcdf file


Usage:

nc2ts.py  -n=[netcdf file] -ni=[netcdf dimenssion info] .. 
          -s=[shapefile] -sp=[shapefile header info]  ..
          --inplace
          
'''


import fiona
import argparse
import numpy as np
from netCDF4 import Dataset
from pyscissor import scissor
from shapely.geometry import shape
from datetime import datetime as dt



def main():
    
    arg_parser = argparse.ArgumentParser()
    
    arg_parser.add_argument('-n', '--netcdf', dest="nc",required=True,
                            type=str,default=None, help="netcdf file location")

    arg_parser.add_argument('-s', '--shapefile', dest="shp",required=True,
                            type=str,help="shapefile location")

    arg_parser.add_argument('-i', '--inplace', dest="inp",
                            type=bool,default=True, help="netcdf file details")

    arg_parser.add_argument()
   



if __name__ == '__main__':
    main()