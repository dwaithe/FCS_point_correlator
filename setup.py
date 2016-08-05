from setuptools import setup

setup(name='fcspointcorrelator',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit'],
	entry_points={
        'console_scripts': [
            'fcspointcorrelator=fcspointcorrelator:main',
        ],
    },

	)