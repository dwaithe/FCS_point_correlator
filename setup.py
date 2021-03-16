from setuptools import setup, find_packages, Extension
import numpy
setup(name='focuspoint',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['lmfit','matplotlib','cython'],
	include_package_data=True,
	include_dirs=[numpy.get_include()],
	ext_modules=[Extension('focuspoint.fib4', ['focuspoint/fib4.c'])],
	packages = ['focuspoint', 'focuspoint.import_methods', 'focuspoint.correlation_methods', 'focuspoint.fitting_methods'],
	
	package_data={
        'focuspoint': ['fib4.pyx'],
    },
	entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },


	)


