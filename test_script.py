#Tests the main functionality of the correlation without the interface.

from correlation_objects import picoObject


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
pt3file = picoObject("topfluorPE_2_1_1_1.pt3", par_obj, None)

print 'tau: ', pt3file.autotime
print 'normalised correlation', pt3file.autoNorm 