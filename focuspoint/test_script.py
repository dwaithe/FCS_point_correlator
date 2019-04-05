#Tests the main functionality of the correlation without the interface.

from correlation_objects import picoObject
import numpy as np

import pylab as plt


class ParameterClass():
	"""Stores parameters for correlation """
	def __init__(self):
		
		#Where the data is stored.
		self.data = []
		self.objectRef =[]
		self.subObjectRef =[]
		self.colors = ['blue','green','red','cyan','magenta','yellow','black']
		self.numOfLoaded = 0
		self.NcascStart = 0
		self.NcascEnd = 25
		self.Nsub = 6
		self.winInt = 10
		self.photonCountBin = 25

par_obj = ParameterClass()

#Runs correlation on the path/to/filename.
pt3file = picoObject("TopFluo488-PE_8_0_7_1_1_2.pt3", par_obj, None)
plt.figure()
plt.semilogx(pt3file.autotime, pt3file.autoNorm[:,0,0])
plt.show()
print('tau: ', pt3file.autotime)
print('normalised correlation', pt3file.autoNorm )



#Small basic example.

from correlation_methods import tttr2xfcs

y = np.cumsum(10000.+(10000.0*np.cos(np.arange(0,1000.,0.01))))
num = np.zeros((100000,2))

#All photons collected were in channel 0.
num[:,0] = 1.0
#Correlate
auto, autotime = tttr2xfcs(y,num,0,5, par_obj.Nsub)

plt.figure()
#Show output from channel 0 correlation.
plt.semilogx(autotime, auto[:,0,0])
plt.show()

