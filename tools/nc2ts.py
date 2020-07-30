#!/usr/bin/env python3

# A placeholder for nc2ts.py, renamed to nc2ts_by_shp.py
import sys
import subprocess as sp


print("#: This tool is renamed to nc2ts_by_shp.py :#\n")

if __name__ == '__main__':
    
    try:
        sp.call(['nc2ts_by_shp.py',*sys.argv[1:]])
    except:
        try: 
            sp.call(['./nc2ts_by_shp.py',*sys.argv[1:]])
        except:
            try: 
                sp.call(['./tools/nc2ts_by_shp.py',*sys.argv[1:]])
            except:
                print('cant execute nc2ts_by_shp.py')


