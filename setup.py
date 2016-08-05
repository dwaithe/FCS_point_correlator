from setuptools import setup, find_packages

setup(name='focuspoint',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit','matplotlib'],
	include_package_data=True,
	packages = ['focuspoint'],
	entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },

	)