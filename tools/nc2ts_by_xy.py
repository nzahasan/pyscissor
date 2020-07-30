#!/usr/bin/env python3
'''
    extract timeseries using lat/lon
    interpolation methods, 
        --bilinear, 
        --nearest-neighbour, 
        --cubic

        add point bufr


'''

from netCDF4 import Dataset,num2date
import numpy as np 
import sys,os
import argparse
import pandas as pd
from scipy.interpolate import interp2d



def parse_nci(args_nci):

    nci={}
    
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
    except ValueError as err:
        print('unable to use units for datetime conversion:',err,'using raw time values')
        times=timevar[:]


    # get raster extent

    # check if within extent

    

    if nci.get('slicer',None)!=None:

        try:
            datavar = eval(f"datavar{nci['slicer']}")
        except:
            sys.exit('invalid slicing information')

    if len(datavar.shape)>3:

        sys.exit(f"{nci['V']} has more than 3 dimension,provide slicing information")




    # for nearest neighbour
    time_series = pd.DataFrame()
    time_series[nci['T']] = times

    nn_yi = np.argmin(np.abs(lats-args.y))
    nn_xi = np.argmin(np.abs(lons-args.x))
    # nearest neighbour
    if args.intp=='nearest':

        values = datavar[:,nn_yi,nn_xi]


    '''

      x0,y1                x1,yi
        |                    |
    ----|-------^------------|----
        |       |            |
        |---->xi,yi<---------|
        |       |            |
    ----|-------^------------|----
        |                    |
      x0,y0                x1,y0

      xi,y0 = v10- 

      xi,y1 =
    '''



    # bilinear interpolation
    if args.intp=='bilinear'
        

        intp_arr_2d = np.empty(
            [
                [values[nn_yi,nn_xi],values[nn_yi,nn_xi+1]],
                [values[nn_yi+1,nn_xi],values[nn_yi+!,nn_xi+1]],
            ]
            ,dtype=np.float64)

        intp_fn = interp2d([nn_xi,nn_xi+1],[nn_yi,nn_yi+1],intp_arr_2d)

        # 

        pass

    # import pylab as pl
    # pl.plot(values)
    # pl.show()


    time_series[nci['V']] = values

    # write data

    time_series.to_csv(args.out,float_format='%.4f',index=False)



if __name__ == '__main__':
    main()