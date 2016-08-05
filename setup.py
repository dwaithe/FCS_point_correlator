from setuptools import setup, find_packages, Extension

setup(name='focuspoint',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit','pypng','matplotlib','cython'],
	include_package_data=True,
	packages = ['focuspoint'],
	ext_modules=[Extension('focuspoint.fib4', ['focuspoint.fib4/focuspoint.c'])],
	package_data={
        'focuspoint': ['fib4.pyx'],
    },
	entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },


	)
