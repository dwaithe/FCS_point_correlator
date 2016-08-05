from setuptools import setup, find_packages

setup(name='fcspointcorrelator',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit'],
	packages = ['FCS_point_correlator'],
	entry_points={
        'console_scripts': [
            'fcspointcorrelator=fcspointcorrelator:main',
        ],
    },

	)