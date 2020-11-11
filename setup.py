#! /usr/bin/env python3
import sys
from setuptools import setup
from pyscissor import __version__


readme_contents = open('readme.md','r').read()

scritps_list = [
    'tools/nc2ts_by_shp.py','tools/nc2ts_by_xy.py',
    'tools/nc2ts_by_shp.cmd','tools/nc2ts_by_xy.cmd',
]

setup(
    name = 'pyscissor',
    version = __version__,
    python_requires = '>=3.6',
    keywords = ['netcdf', 'crop','shapefile'],
    url = 'https://github.com/nzahasan/pyscissor',
    description = 'A python module for obtaining reduced(min,max,avg) value from netCDF file under a polygon region',
    long_description = readme_contents,
    long_description_content_type = 'text/markdown',
    author = 'nzahasan',
    author_email = 'nzahasan@gmail.com',
    license = 'MIT',
    packages = ['pyscissor'],
    scripts = scritps_list,
    include_package_data = True,
    zip_safe = False,
    test_suite = 'tests',
    install_requires=[
        'numpy',
        'netCDF4',
        'shapely',
        'fiona',
        'pandas',
        'yaspin'
    ]
)