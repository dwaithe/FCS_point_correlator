from setuptools import setup, find_packages, Extension

setup(name='focuspoint',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit','pypng','matplotlib','cython'],
	include_package_data=True,
	
	packages = ['focuspoint'],
	
	package_data={
        'focuspoint': ['fib4.pyx'],
    },
	entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },


	)

import numpy

setup(
	name='cythonmaxima',
	version='0.1',
include_dirs=[numpy.get_include()],
ext_modules=[Extension('focuspoint.fib4', ['focuspoint/fib4.c'])]
	)
