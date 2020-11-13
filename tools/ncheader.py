#!/usr/bin/env python3
import argparse
from netCDF4 import Dataset

def main():

    arg_parser=argparse.ArgumentParser(
        description="Read header of netcdf file ",
        usage='use "%(prog)s --help" for more information',
    )

    arg_parser.add_argument(
        '-nc', '--netcdf', 
        dest="nc",
        required=True,
        type=str,
        default=None, 
        help="netcdf file ",
    )

    args = arg_parser.parse_args()


    nf = Dataset(args.nc,'r')

    # parse dimension info
    nc_info = 'Dimensions:\n\n'
    for dim in nf.dimensions:
        nc_info += f'\t{dim}\t({nf.dimensions[dim].size})'
        if nf.dimensions[dim].isunlimited():
            nc_info += '\t&unlimited\n'
        else:
            nc_info += '\n'

    nc_info += '\nvariables:\n\n'

    for var in nf.variables:
        nc_info += f'\t{var}:{nf.variables[var].dimensions}:\n'
        
        try: nc_info += f'\t\t standard_name: {nf.variables[var].getncattr("standard_name")}\n'
        except: pass

        try: nc_info += f'\t\t full_name: {nf.variables[var].long_name}\n'
        except: pass

        try: nc_info += f'\t\t units: {nf.variables[var].units}\n'
        except: pass

        try: nc_info += f'\t\t calendar: {nf.variables[var].calendar}\n'
        except: pass

        try: nc_info += f'\t\t axis: {nf.variables[var].axis}\n'
        except: pass

        try: nc_info += f'\t\t cell_methods: {nf.variables[var].getncattr("cell_methods")}\n'
        except: pass

        try: nc_info += f'\t\t comment: {nf.variables[var].comment}\n'
        except: pass
        nc_info += '\n'

    print(nc_info)


if __name__ == '__main__':
    main()