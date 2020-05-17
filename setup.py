#! /usr/bin/env python3
from setuptools import setup

setup(
    name='pyscissor',
    version='0.1',
    keywords='netcdf crop shapefile',
    url='https://github.com/nzahasan/pyscissor',
    description='A python module for obtaining reduced(min,max,avg) value from netCDF file under a polygon',
    author='nzahasan',
    author_email='nzahasan@gmail.com',
    license='MIT',
    packages=['pyscissor'],
    scripts=['tools/nc2ts.py'],
    include_package_data = True,
    zip_safe=False,
    test_suite='tests',
    install_requires=[
        'numpy',
        'netCDF4',
        'shapely',
        'fiona',
        'pandas',
        'tqdm',
    ]
)