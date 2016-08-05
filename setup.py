from setuptools import setup, find_packages

setup(name='focuspoint',
	version='0.1',
	author='Dominic Waithe',
	install_requires=['numpy','scipy','lmfit','pypng','matplotlib','cython'],
	include_package_data=True,
	packages = ['focuspoint'],
	entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
    ext_modules=['fib4.pyx']

	)
from distutils.command.sdist import sdist as _sdist

class sdist(_sdist):
    def run(self):
        # Make sure the compiled Cython files in the distribution are up-to-date
        from Cython.Build import cythonize
        cythonize(['fib4.pyx'])
        _sdist.run(self)
cmdclass['sdist'] = sdist