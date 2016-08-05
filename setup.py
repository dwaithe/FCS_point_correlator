from setuptools import setup

setup(name='fcspointcorrelator',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit'],
	packages = find_packages(),
	entry_points={
        'console_scripts': [
            'fcspointcorrelator=fcspointcorrelator:main',
        ],
    },

	)