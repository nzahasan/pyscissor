#!/usr/bin/env python3
'''
    extract timeseries using lat/lon
    interpolation methods, 
        --bilinear
        --nearest-neighbour
'''

from netCDF4 import Dataset,num2date
import numpy as np 
import sys,os
import argparse
import pandas as pd
from pyscissor import pinpoint



def parse_nci(args_nci):

    nci=dict()
    
    for rec in args_nci.split(';'):
        rec_split = rec.split('=')
        
        if len(rec_split)==2 and len(rec_split[1])>0: 
            key,val=rec_split
            nci[key.upper()]=val

    return nci



def main():

    arg_parser=argparse.ArgumentParser(
                description="Extract time series with lat lon ",
                usage='use "%(prog)s --help" for more information',
            )

    arg_parser.add_argument('-nc', '--netcdf', 
                                dest="nc",
                                required=True,
                                type=str,
                                default=None, 
                                help="netcdf file location",
                            )

    arg_parser.add_argument('-nci', '--netcdf-info',
                                dest="nci",
                                required=True,
                                type=str,
                                default=None,
                                help="netcdf file details"
                            )

    arg_parser.add_argument('-x',
                            dest='x',
                            required=True,
                            type=float,
                            help="X/Longitude"
                            )

    arg_parser.add_argument('-y',
                            dest='y',
                            required=True,
                            type=float,
                            help="Y/Latitude"
                            )

    arg_parser.add_argument('-intp',
                                dest='intp',
                                default='nearest',
                                choices=['nearest','bilinear']
                            )

    arg_parser.add_argument('-o', '--output',
                                dest="out", 
                                required=True,
                                type=str,
                                default='ts_xy.csv',
                                help="output file"
                            )

    args = arg_parser.parse_args()

    nci  = parse_nci(args.nci)

    
    # read netcdf file
    nc_file = Dataset(args.nc,'r')
    lats    = nc_file.variables[nci['Y']][:]
    lons    = nc_file.variables[nci['X']][:]
    datavar = nc_file.variables[nci['V']][:]
    timevar = nc_file.variables[nci['T']]

    try:
        times  = num2date(timevar[:],timevar.units)
        times = [ tx.strftime(tx.format) for tx in times  ]
    except:
        print('unable to use units for datetime conversion. using raw time values')
        times=timevar[:]


    # get raster extent

    # check if within extent

    if len(datavar.shape)>3: 
        if nci.get('slicer',None)!=None:
            try:
                datavar = eval(f"datavar{nci['slicer']}")
            except:
                sys.exit('invalid slicing information')
        else:
            sys.exit(f"{nci['V']} has more than 3 dimension,provide slicing information")


    time_series = pd.DataFrame()
    time_series[nci['T']] = times

    # initialize pinpoint and set xy
    pin = pinpoint(lats,lons)
    pin.set_xy(args.y,args.x)
    
    # nearest neighbour
    if args.intp=='nearest':

        values = datavar[:,pin.nn_id[0],pin.nn_id[1]]


    # bilinear interpolation
    if args.intp=='bilinear':
        values = np.empty(len(times),dtype=np.float32)
        for ts in range(len(times)):
            values[ts] = pin.bilinear(datavar[ts])

    time_series[nci['V']] = values

    # write data

    time_series.to_csv(args.out,float_format='%.4f',index=False)



if __name__ == '__main__':
    main()