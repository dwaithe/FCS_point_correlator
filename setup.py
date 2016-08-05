from distutils.core import setup
from Cython.Build import cythonize
import os
import platform
import numpy

setup(ext_modules = cythonize("fib.pyz"),
	include_dirs=[numpy.get_include()],
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit']


	)