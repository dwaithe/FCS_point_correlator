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


	)
from distutils.command.sdist import sdist as _sdist
cmdclass = { }
class sdist(_sdist):
    def run(self):
        # Make sure the compiled Cython files in the distribution are up-to-date
        from Cython.Build import cythonize
        cythonize(['fib4.pyx'])
        _sdist.run(self)
        print 'ccccccchhhuuuubahhh'
cmdclass['sdist'] = sdist