# pyscissor
![Supported Version](https://img.shields.io/badge/python-3.6|3.7|3.8-blue.svg) 
![Action: Build](https://github.com/nzahasan/pyscissor/workflows/build/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
A Python3 module for extracting data from netcdf file under a shapefile region.  

<img src="data/sample.png" height="500" align="center">


### Installation

pyscissor can be installed using the following commands

```bash
$ git clone https://github.com/nzahasan/pyscissor.git
$ cd pyscissor
$ python3 setup.py install
```
or using pip

```bash
$ pip install pyscissor
```

### Using pyscissor

```python
import numpy as np
from pyscissor import scissor 

'''<code for reading netcdf and shapefile>'''

pys = scissor(polygon,lats,lons)

weight_grid = pys.get_masked_weight() #=> returns a masked array containing weights

# get weighted average
avg = np.average(var,weights=weight_grid)

# if only intersection mask with shape is needed use `weight_grid.mask`
```
A detailed use case can be found in the following notebook <a href="notebooks/example_01.ipynb">example_01.ipynb</a>



### Using nc2ts_by_shp.py
this package contains a `nc2ts_by_shp.py` script. A command line tool that can be used to quickly extract 
reduced(min/max/average/weighted average) time-series form netcdf file with shapefile

```bash
# with 3d array [data/sample_2.nc] generel case
$ nc2ts_by_shp.py -nc=sample_2.nc -nci='Y=lat;X=lon;T=time;V=tmin;' -s=shape_esri.zip \
		-sp='ADM2_EN;ADM3_EN' -r=avg -o=test2.csv

# with 4d array [data/sample_1.nc]
$ nc2ts_by_shp.py -nc=sample_1.nc -nci='Y=lat;X=lon;T=time;V=temperature;slicer=[:,0,:,:]' -sf=shape_esri.zip \
		-sfp='ADM2_EN;ADM3_EN' -r=wavg -o=test1.csv

```
Options:

	-nc  = netcdf file

	-nci = netcdf variable and dimension information
			available options:
			X = x dimension variable name,
			Y = y dimension variable name,
			T = time dimension variable name,
			V = variable name,
			slicer = slicing index for obtaining 3d array [optional]
					
			note: `slicer` is required if variable has more than three dimension

	-sf  = shape file ( can be zipped shapefile, shapefile or geojson )

	-sfp = shapefile properties
			only required when shapefile contains multiple records

	-r   = reducer, default is average
			Available options: min,max,avg,wavg

	-o   = output file name


### Causes of Erroneous output

	- when shapefile and netcdf file have different projection
	- shapefile dosen't fully reside within netcdf bounds 