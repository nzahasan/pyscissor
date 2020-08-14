#!/usr/bin/env python3

'''
Run this script to extract reduced timeseries from a 
netCDF file under polygon regions of a shapefile.


Usage:

nc2ts.py  -n  = [netcdf file] -ni=[netcdf dimenssion info] .. 
          -s  = [shapefile] -sp=[shapefile header info]  ..
          -r  = [reducer to be used min/max/avg/wavg]  ..
          -rs = [use recursive subdidision instead of iteration] ..
          -o  = [output filename]
'''

import sys,fiona,argparse
import numpy as np,pandas as pd
from yaspin import yaspin
from pyscissor import scissor
from shapely.geometry import shape
from netCDF4 import Dataset,num2date


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
                    description="Extract time series under a polygon region ",
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

    arg_parser.add_argument('-sf', '--shapefile',
                                dest="shp",
                                required=True,
                                type=str,
                                help="shapefile location"
                            )

    # only required when shapefile contains multiple record
    arg_parser.add_argument('-sfp', '--shapefile-prop',
                                dest="shpprop", 
                                default=None,
                                type=str,
                                help="csv header if shapefile contains multiple records"
                            )

    arg_parser.add_argument('-r', '--reducer',
                                dest="reducer",
                                type=str,
                                default='avg',
                                choices=['min','max','avg','wavg'],
                                help="reducer to use"
                            )

    arg_parser.add_argument('-rs', '--recursive-subdivision',
                                dest="recursive_division",
                                action="store_true",
                                help="use recrusive subdivision"
                            )

    arg_parser.add_argument('-o', '--output',
                                dest="out", 
                                required=True,
                                type=str,
                                default='ts.csv',
                                help="output file"
                            )

    args = arg_parser.parse_args()

    nci  = parse_nci(args.nci)
    
    # read shapefile
    if args.shp.endswith('.zip'):
        args.shp='zip://'+args.shp


    # read netcdf file
    nc_file = Dataset(args.nc,'r')
    lats    = nc_file.variables[nci['Y']][:]
    lons    = nc_file.variables[nci['X']][:]
    datavar = nc_file.variables[nci['V']][:]
    timevar = nc_file.variables[nci['T']]

    # parse time

    try:
        times  = num2date(timevar[:],timevar.units)
        times = [ tx.strftime(tx.format) for tx in times  ]
    except:
        print('Warning: unable to convert time, using raw time values!')
        times=timevar[:]

    tseries_data = pd.DataFrame()
    tseries_data['date']=times

    # if lat and lon position is reversed transpose
    transpose_weight=False

    dims=nc_file.variables[nci['V']].dimensions

    # check if dimesnions are in desired order
    
    t_pos,y_pos,x_pos = dims.index(nci['T']),dims.index(nci['Y']),dims.index(nci['X'])

    if not ( (t_pos<y_pos<x_pos) or (t_pos<x_pos<y_pos) ):
        sys.exit('invalid time dimension orders')
    
    if y_pos>x_pos:
        transpose_weight=True
        print('weight needs to be transposed')
        # @add transpose func


    if len(datavar.shape)>3: 
        if nci.get('slicer',None)!=None:
            try:
                datavar = eval(f"datavar{nci['slicer']}")
            except:
                sys.exit('invalid slicing information')
        else:
            sys.exit(f"{nci['V']} has more than 3 dimension,provide slicing information")


    # read shapefile

    shp_file = fiona.open(args.shp,'r')

    use_prop_header=False

    shp_rec_count = len(shp_file)

    if shp_rec_count>1:
        use_prop_header=True

        if args.shpprop==None:
            sys.exit(
                'shapefile has more than 1 record.',
                'No shape properties is provided for column header'
            )

    # if datavar is not masked array create masked array

    premasked=np.ma.is_masked(datavar)

    if premasked:
        # explicitly copy this mask otherwise gets 
        # overwriten at every iteration of shape
        root_mask=datavar.mask.copy()

    # extract data
    fmtstr=lambda idx: f'processing shape {idx+1:02d} out of {shp_rec_count}'

    for idx,rec in enumerate(shp_file):

        with yaspin(text=fmtstr(idx), color="yellow") as spinner:
            
            tseries_val=[None]*len(times)
            
            shapely_obj = shape(rec['geometry']) 
            
            # get weighted grid
            pys = scissor(shapely_obj,lats,lons)

            if args.recursive_division==False:
                weight_grid = pys.get_masked_weight()
            elif args.recursive_division==True:
                weight_grid = pys.get_masked_weight_recursive()

            # handle premasked variable[may contain land ocean mask] 
            if premasked:
                # root mask will boradcast if weight_grid.mask is 3d
                datavar.mask=np.bitwise_or(root_mask,weight_grid.mask)
            else:
                datavar.mask=weight_grid.mask
            
            if use_prop_header:
                header=''
                for prop in args.shpprop.split(';'):
                    header += str(rec['properties'].get(prop,''))+','
            else:
                header = nci['V']

            # calculate redused value of each timestep
            for ts in range(len(times)):

                if args.reducer=='min':

                    tseries_val[ts] = datavar[ts].min()

                elif args.reducer=='max':

                    tseries_val[ts] = datavar[ts].max()

                elif args.reducer=='avg':

                    tseries_val[ts] = datavar[ts].mean()

                elif args.reducer=='wavg':

                    tseries_val[ts] = np.average(datavar[ts],weights=weight_grid)

            tseries_data[header] = tseries_val

            spinner.ok("✔")


    # save tseries as csv
    if not args.out.endswith('.csv'):
        args.out+='.csv'

    tseries_data.to_csv(args.out,float_format='%.4f',index=False)


if __name__ == '__main__':
    main()