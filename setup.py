from setuptools import setup, Extension
import numpy
from Cython.Build import cythonize

ext_modules = cythonize([Extension('focuspoint.fib4', ['focuspoint/fib4.pyx'],
	include_dirs=[numpy.get_include()])], language_level=3)
# Optional: without a C compiler the install still succeeds and the correlator
# uses NumPy instead of the compiled routine (same results). Set after
# cythonize, which does not copy this flag.
for ext in ext_modules:
	ext.optional = True

setup(name='focuspoint',
	version='0.2',
	author='Dominic Waithe',
	python_requires='>=3.9',
	install_requires=['numpy', 'scipy', 'matplotlib', 'lmfit', 'PyQt5', 'pyperclip', 'tables', 'tifffile'],
	# Optional: the About window renders its HTML with Qt WebEngine when it is installed.
	extras_require={'web': ['PyQtWebEngine']},
	include_package_data=True,
	ext_modules=ext_modules,
	packages = ['focuspoint', 'focuspoint.import_methods', 'focuspoint.correlation_methods', 'focuspoint.fitting_methods'],

	package_data={
        'focuspoint': ['fib4.pyx'],
    },
	)
