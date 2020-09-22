import numpy as np
import os, sys
from focuspoint.correlation_methods.correlation_methods import *
from focuspoint.import_methods.import_methods import *
import time
from focuspoint.fitting_methods import fitting_methods_SE as SE
from focuspoint.fitting_methods import fitting_methods_GS as GS
from focuspoint.fitting_methods import fitting_methods_VD as VD
from focuspoint.fitting_methods import fitting_methods_PB as PB
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
import csv
import copy


"""FCS Bulk Correlation Software

	Copyright (C) 2015  Dominic Waithe

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License along
	with this program; if not, write to the Free Software Foundation, Inc.,
	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

class picoObject():
	#This is the class which holds the .pt3 data and parameters
	def __init__(self,filepath, par_obj,fit_obj):
	
		#parameter object and fit object. If 
		self.par_obj = par_obj
		self.fit_obj = fit_obj
		self.type = 'mainObject'
		
		#self.PIE = 0
		self.filepath = str(filepath)
		self.nameAndExt = os.path.basename(self.filepath).split('.')
		self.name = self.nameAndExt[0]
		self.ext = self.nameAndExt[-1]

		self.par_obj.data.append(filepath);
		self.par_obj.objectRef.append(self)
		
		#Imports pt3 file format to object.
		self.unqID = self.par_obj.numOfLoaded
		
		#For fitting.
		self.objId1 = None
		self.objId2 = None
		self.objId3 = None
		self.objId4 = None
		self.processData();
		
		self.plotOn = True;


	def processData(self):

		self.NcascStart = self.par_obj.NcascStart
		self.NcascEnd = self.par_obj.NcascEnd
		self.Nsub = self.par_obj.Nsub
		self.winInt = self.par_obj.winInt
		self.photonCountBin = 25#self.par_obj.photonCountBin
		
		#File import
		if self.ext == 'spc':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = spc_file_import(self.filepath)
		elif self.ext == 'asc':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = asc_file_import(self.filepath)
		elif self.ext == 'pt2':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt2import(self.filepath)
		elif self.ext == 'pt3':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt3import(self.filepath)
		elif self.ext == 'ptu':
			out = ptuimport(self.filepath)
			
			if out != False:
				self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = out
			else:
				self.par_obj.data.pop(-1)
				self.par_obj.objectRef.pop(-1)
				self.exit = True
				
				return
		elif self.ext == 'csv':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = csvimport(self.filepath)
			#If the file is empty.
			if self.subChanArr == None:
				#Undoes any preparation of resource.
				self.par_obj.data.pop(-1);
				self.par_obj.objectRef.pop(-1)
				self.exit = True
				
				return
		else:
			self.exit = True
			return 

					
		
		#Colour assigned to file.
		self.color = self.par_obj.colors[self.unqID % len(self.par_obj.colors)]

		#How many channels there are in the files.
		
		self.ch_present = np.sort(np.unique(np.array(self.subChanArr)))
		if self.ext == 'pt3' or self.ext == 'ptu'or self.ext == 'pt2':
			self.numOfCH =  self.ch_present.__len__()-1 #Minus 1 because not interested in channel 15.
		else:
			self.numOfCH =  self.ch_present.__len__()
		
		#Finds the numbers which address the channels.
		
		#Calculates decay function for both channels.
		self.photonDecayCh1,self.decayScale1 = delayTime2bin(np.array(self.dTimeArr),np.array(self.subChanArr),self.ch_present[0],self.winInt)
		
		if self.numOfCH ==  2:
			self.photonDecayCh2,self.decayScale2 = delayTime2bin(np.array(self.dTimeArr),np.array(self.subChanArr),self.ch_present[1],self.winInt)

		#Time series of photon counts. For visualisation.
		

		self.timeSeries1,self.timeSeriesScale1 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[0],self.photonCountBin)
	
		
		unit = self.timeSeriesScale1[-1]/self.timeSeriesScale1.__len__()
		
		
		#Converts to counts per 
		self.kcount_CH1 = np.average(self.timeSeries1)

		raw_count = np.average(self.timeSeries1) #This is the unnormalised intensity count for int_time duration (the first moment)
		var_count = np.var(self.timeSeries1)

		self.brightnessNandBCH0=(((var_count -raw_count)/(raw_count))/(float(unit)))
		if (var_count-raw_count) == 0:
			self.numberNandBCH0 =0
		else:
			self.numberNandBCH0 = (raw_count**2/(var_count-raw_count))
		


		if self.numOfCH ==  2:

			self.timeSeries2,self.timeSeriesScale2 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[1],self.photonCountBin)
			unit = self.timeSeriesScale2[-1]/self.timeSeriesScale2.__len__()
			self.kcount_CH2 = np.average(self.timeSeries2)
			raw_count = np.average(self.timeSeries2) #This is the unnormalised intensity count for int_time duration (the first moment)
			var_count = np.var(self.timeSeries2)
			self.brightnessNandBCH1= (((var_count -raw_count)/(raw_count))/(float(unit)))
			if (var_count-raw_count) == 0:
				self.numberNandBCH1 =0
			else:
				self.numberNandBCH1 = (raw_count**2/(var_count-raw_count))
			self.CV = calc_coincidence_value(self)
			


		
		#Calculates the Auto and Cross-correlation functions.
		self.crossAndAuto(np.array(self.trueTimeArr),np.array(self.subChanArr))
		
		if self.fit_obj != None:
			#If fit object provided then creates fit objects.
			if self.objId1 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId1 = corrObj.objId
				self.objId1.parent_name = 'point FCS'
				self.objId1.parent_uqid = 'point FCS'
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId1.name = self.name+'_CH0_Auto_Corr'
				self.objId1.ch_type = 0 #channel 0 Auto
				self.objId1.siblings = None
				self.objId1.prepare_for_fit()
				self.objId1.kcount = self.kcount_CH1
				self.objId1.item_in_list = False
				
			self.objId1.autoNorm = np.array(self.autoNorm[:,0,0]).reshape(-1)
			self.objId1.autotime = np.array(self.autotime).reshape(-1)
			self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
			self.objId1.max = np.max(self.objId1.autoNorm)
			self.objId1.min = np.min(self.objId1.autoNorm)
			self.objId1.tmax = np.max(self.objId1.autotime)
			self.objId1.tmin = np.min(self.objId1.autotime)

			
			
			if self.numOfCH ==  2:
				self.objId1.CV = self.CV
				

				if self.objId3 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId3 = corrObj.objId
					self.objId3.parent_name = 'point FCS'
					self.objId3.parent_uqid = 'point FCS'
					self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId3.name = self.name+'_CH1_Auto_Corr'
					self.objId3.ch_type = 1 #channel 1 Auto
					self.objId3.siblings = None
					self.objId3.prepare_for_fit()
					self.objId3.kcount = self.kcount_CH2
					self.objId3.item_in_list = False
					
				self.objId3.autoNorm = np.array(self.autoNorm[:,1,1]).reshape(-1)
				self.objId3.autotime = np.array(self.autotime).reshape(-1)
				self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId3.max = np.max(self.objId3.autoNorm)
				self.objId3.min = np.min(self.objId3.autoNorm)
				self.objId3.tmax = np.max(self.objId3.autotime)
				self.objId3.tmin = np.min(self.objId3.autotime)


				self.objId3.CV = self.CV
				if self.objId2 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId2 = corrObj.objId
					self.objId2.parent_name = 'point FCS'
					self.objId2.parent_uqid = 'point FCS'
					self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId2.name = self.name+'_CH01_Cross_Corr'
					self.objId2.ch_type = 2 #01cross
					self.objId2.siblings = None
					self.objId2.prepare_for_fit()
					self.objId2.item_in_list = False
					
				self.objId2.autoNorm = np.array(self.autoNorm[:,0,1]).reshape(-1)
				self.objId2.autotime = np.array(self.autotime).reshape(-1)
				self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId2.max = np.max(self.objId2.autoNorm)
				self.objId2.min = np.min(self.objId2.autoNorm)
				self.objId2.tmax = np.max(self.objId2.autotime)
				self.objId2.tmin = np.min(self.objId2.autotime)
				self.objId2.CV =self.CV

				if self.objId4 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId4 = corrObj.objId
					self.objId4.parent_name = 'point FCS'
					self.objId4.parent_uqid = 'point FCS'
					self.objId4.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId4.name = self.name+'_CH10_Cross_Corr'
					self.objId4.ch_type = 3 #10cross
					self.objId4.siblings = None
					self.objId4.prepare_for_fit()
					self.objId4.item_in_list = False

				self.objId4.autoNorm = np.array(self.autoNorm[:,1,0]).reshape(-1)
				self.objId4.autotime = np.array(self.autotime).reshape(-1)
				self.objId4.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId4.max = np.max(self.objId4.autoNorm)
				self.objId4.min = np.min(self.objId4.autoNorm)
				self.objId4.tmax = np.max(self.objId4.autotime)
				self.objId4.tmin = np.min(self.objId4.autotime)
				self.objId4.CV = self.CV
			self.fit_obj.fill_series_list()
		self.dTimeMin = 0
		self.dTimeMax = np.max(self.dTimeArr)
		self.subDTimeMin = self.dTimeMin
		self.subDTimeMax = self.dTimeMax
		self.exit = False
		#del self.subChanArr 
		#del self.trueTimeArr 
		del self.dTimeArr
	def crossAndAuto(self,trueTimeArr,subChanArr):
		#For each channel we loop through and find only those in the correct time gate.
		#We only want photons in channel 1 or two.
		y = trueTimeArr[subChanArr < 3]
		validPhotons = subChanArr[subChanArr < 3 ]


		#Creates boolean for photon events in either channel.
		num = np.zeros((validPhotons.shape[0],2))
		num[:,0] = (np.array([np.array(validPhotons) ==self.ch_present[0]])).astype(np.int32)
		if self.numOfCH ==2:
			num[:,1] = (np.array([np.array(validPhotons) ==self.ch_present[1]])).astype(np.int32)


		self.count0 = np.sum(num[:,0]) 
		self.count1 = np.sum(num[:,1])

		t1 = time.time()
		auto, self.autotime = tttr2xfcs(y,num,self.NcascStart,self.NcascEnd, self.Nsub)
		t2 = time.time()
		
		

		#Normalisation of the TCSPC data:
		maxY = np.ceil(max(self.trueTimeArr))
		self.autoNorm = np.zeros((auto.shape))
		self.autoNorm[:,0,0] = ((auto[:,0,0]*maxY)/(self.count0*self.count0))-1
		
		if self.numOfCH ==  2:
			self.autoNorm[:,1,1] = ((auto[:,1,1]*maxY)/(self.count1*self.count1))-1
			self.autoNorm[:,1,0] = ((auto[:,1,0]*maxY)/(self.count1*self.count0))-1
			self.autoNorm[:,0,1] = ((auto[:,0,1]*maxY)/(self.count0*self.count1))-1
			

		#Normalisaation of the decay functions.
		if np.sum(self.photonDecayCh1) > 0:
			self.photonDecayCh1Min = self.photonDecayCh1-np.min(self.photonDecayCh1)
			self.photonDecayCh1Norm = self.photonDecayCh1Min/np.max(self.photonDecayCh1Min)
			
			
			if self.numOfCH ==  2:
				self.photonDecayCh2Min = self.photonDecayCh2-np.min(self.photonDecayCh2)
				self.photonDecayCh2Norm = self.photonDecayCh2Min/np.max(self.photonDecayCh2Min)
		else:
			self.photonDecayCh1Min = 0
			self.photonDecayCh1Norm = 0
			self.photonDecayCh2Min = 0
			self.photonDecayCh2Norm = 0

		
		return 
   

	
	
class subPicoObject():
	def __init__(self,parentId,xmin,xmax,TGid,par_obj):
		#Binning window for decay function
		self.TGid = TGid
		#Parameters for auto-correlation and cross-correlation.
		self.parentId = parentId
		self.par_obj = par_obj
		self.NcascStart = self.parentId.NcascStart
		self.NcascEnd = self.parentId.NcascEnd
		self.Nsub = self.parentId.Nsub
		self.fit_obj = self.parentId.fit_obj
		self.ext = self.parentId.ext
		
		self.type = 'subObject'
		#Appends the object to the subObject register.
		self.par_obj.subObjectRef.append(self)
		self.unqID = self.par_obj.subNum
		self.parentUnqID = self.parentId.unqID
		#self.chanArr = parentObj.chanArr
		#self.trueTimeArr = self.parentId.trueTimeArr
		#self.dTimeArr = self.parentId.dTimeArr
		self.color = self.parentId.color
		self.numOfCH = self.parentId.numOfCH
		self.ch_present = self.parentId.ch_present
		self.photonCountBin = 25#self.par_obj.photonCountBin

		self.filepath = str(self.parentId.filepath)
		self.xmin = xmin
		self.xmax = xmax

		self.nameAndExt = os.path.basename(self.filepath).split('.')
		self.name = self.nameAndExt[0]+'-TG-'+str(self.unqID)+'-xmin_'+str(round(xmin,0))+'-xmax_'+str(round(xmax,0))

		self.objId1 = None
		self.objId2 = None
		self.objId3 = None
		self.objId4 = None
		self.processData();
		self.plotOn = True
		
		
	def processData(self):
		self.NcascStart= self.par_obj.NcascStart
		self.NcascEnd= self.par_obj.NcascEnd
		self.Nsub = self.par_obj.Nsub
		self.winInt = self.par_obj.winInt
		
		
		#self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt3import(self.filepath)
		if self.ext == 'pt2':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt2import(self.filepath)
		if self.ext == 'pt3':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt3import(self.filepath)
		if self.ext == 'csv':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = csvimport(self.filepath)
		if self.ext == 'spc':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = spc_file_import(self.filepath)
		if self.ext == 'asc':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = asc_file_import(self.filepath)


		self.subArrayGeneration(self.xmin,self.xmax)
		
		self.dTimeMin = self.parentId.dTimeMin
		self.dTimeMax = self.parentId.dTimeMax
		self.subDTimeMin = self.dTimeMin
		self.subDTimeMax = self.dTimeMax

	   #Time series of photon counts. For visualisation.
		self.timeSeries1,self.timeSeriesScale1 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[0],self.photonCountBin)
		
		unit = self.timeSeriesScale1[-1]/self.timeSeriesScale1.__len__()
		self.kcount_CH1 = np.average(self.timeSeries1)

		raw_count = np.average(self.timeSeries1) #This is the unnormalised intensity count for int_time duration (the first moment)
		var_count = np.var(self.timeSeries1)

		self.brightnessNandBCH0=(((var_count -raw_count)/(raw_count))/(float(unit)))
		if (var_count-raw_count) == 0:
			self.numberNandBCH0 =0
		else:
			self.numberNandBCH0 = (raw_count**2/(var_count-raw_count))

		if self.numOfCH ==  2:

			self.timeSeries2,self.timeSeriesScale2 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[1],self.photonCountBin)
			unit = self.timeSeriesScale2[-1]/self.timeSeriesScale2.__len__()
			self.kcount_CH2 = np.average(self.timeSeries2)
			raw_count = np.average(self.timeSeries2) #This is the unnormalised intensity count for int_time duration (the first moment)
			var_count = np.var(self.timeSeries2)
			self.brightnessNandBCH1= (((var_count -raw_count)/(raw_count))/(float(unit)))
			if (var_count-raw_count) == 0:
				self.numberNandBCH1 =0
			else:
				self.numberNandBCH1 = (raw_count**2/(var_count-raw_count))

			self.CV = calc_coincidence_value(self)

			
		

		
		#Adds names to the fit function for later fitting.
		if self.objId1 == None:
			corrObj= corrObject(self.filepath,self.fit_obj);
			self.objId1 = corrObj.objId
			self.objId1.parent_name = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
			self.objId1.parent_uqid = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
			self.fit_obj.objIdArr.append(corrObj.objId)
			self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
			self.objId1.name = self.name+'_CH0_Auto_Corr'
			self.objId1.ch_type = 0 #channel 0 Auto
			self.objId1.siblings = None
			self.objId1.prepare_for_fit()
			
			self.objId1.kcount = self.kcount_CH1
		self.objId1.autoNorm = np.array(self.autoNorm[:,0,0]).reshape(-1)
		self.objId1.autotime = np.array(self.autotime).reshape(-1)
		self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
		
		
		if self.numOfCH == 2:
			self.objId1.CV = self.CV
			if self.objId3 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId3 = corrObj.objId
				self.objId3.parent_name = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.objId3.parent_uqid = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId3.name = self.name+'_CH1_Auto_Corr'
				self.objId3.ch_type = 1 #channel 1 Auto
				self.objId3.siblings = None
				self.objId3.prepare_for_fit()
				self.objId3.kcount = self.kcount_CH2
				
				
			self.objId3.autoNorm = np.array(self.autoNorm[:,1,1]).reshape(-1)
			self.objId3.autotime = np.array(self.autotime).reshape(-1)
			self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
			self.objId3.CV = self.CV
			if self.objId2 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId2 = corrObj.objId
				self.objId2.parent_name = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.objId2.parent_uqid = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId2.name = self.name+'_CH01_Cross_Corr'
				self.objId2.ch_type = 2 #channel 01 Cross
				self.objId2.siblings = None
				self.objId2.prepare_for_fit()

				
			self.objId2.autoNorm = np.array(self.autoNorm[:,0,1]).reshape(-1)
			self.objId2.autotime = np.array(self.autotime).reshape(-1)
			self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
			self.objId2.CV = self.CV
			if self.objId4 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId4 = corrObj.objId
				
				self.objId4.parent_name = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.objId4.parent_uqid = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
				self.objId4.param = copy.deepcopy(self.fit_obj.def_param)
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId4.name = self.name+'_CH10_Cross_Corr'
				self.objId4.ch_type = 3 #channel 10 Cross
				self.objId4.siblings = None
				self.objId4.prepare_for_fit()
				
			self.objId4.autoNorm = np.array(self.autoNorm[:,1,0]).reshape(-1)
			self.objId4.autotime = np.array(self.autotime).reshape(-1)
			self.objId4.CV = self.CV
			
			
		
		self.fit_obj.fill_series_list()  
		#del self.subChanArr 
		#self.trueTimeArr 
		del self.dTimeArr 
	


	def subArrayGeneration(self,xmin,xmax):
		if(xmax<xmin):
			xmin1 = xmin
			xmin = xmax
			xmax = xmin1
		#self.subChanArr = np.array(self.chanArr)
		#Finds those photons which arrive above certain time or below certain time.
		photonInd = np.logical_and(self.dTimeArr>=xmin, self.dTimeArr<=xmax).astype(np.bool)
		
		self.subChanArr[np.invert(photonInd).astype(np.bool)] = 16
		
		self.crossAndAuto()

		return
	def crossAndAuto(self):
		#We only want photons in channel 1 or two.
		validPhotons = self.subChanArr[self.subChanArr < 3]
		y = self.trueTimeArr[self.subChanArr < 3]
		#Creates boolean for photon events in either channel.
		num = np.zeros((validPhotons.shape[0],2))
		num[:,0] = (np.array([np.array(validPhotons) ==self.ch_present[0]])).astype(np.int)
		if self.numOfCH == 2:
			num[:,1] = (np.array([np.array(validPhotons) ==self.ch_present[1]])).astype(np.int)

		self.count0 = np.sum(num[:,0]) 
		self.count1 = np.sum(num[:,1]) 
		#Function which calculates auto-correlation and cross-correlation.



		auto, self.autotime = tttr2xfcs(y,num,self.NcascStart,self.NcascEnd, self.Nsub)

		maxY = np.ceil(max(self.trueTimeArr))
		self.autoNorm = np.zeros((auto.shape))
		self.autoNorm[:,0,0] = ((auto[:,0,0]*maxY)/(self.count0*self.count0))-1
		if self.numOfCH ==2:
			self.autoNorm[:,1,1] = ((auto[:,1,1]*maxY)/(self.count1*self.count1))-1
			self.autoNorm[:,1,0] = ((auto[:,1,0]*maxY)/(self.count1*self.count0))-1
			self.autoNorm[:,0,1] = ((auto[:,0,1]*maxY)/(self.count0*self.count1))-1

		return 
def calc_coincidence_value(self):
	N1 = np.bincount((np.array(self.timeSeries1)).astype(np.int64))
	N2 = np.bincount((np.array(self.timeSeries2)).astype(np.int64))
	
	n = max(N1.shape[0],N2.shape[0])
	NN1 = np.zeros(n)
	NN2 = np.zeros(n)
	NN1[:N1.shape[0]] = N1 
	NN2[:N2.shape[0]] = N2 
	N1 = NN1
	N2 = NN2
	
	CV = (np.sum(N1*N2)/(np.sum(N1)*np.sum(N2)))*n
	return CV
class corrObject():
	def __init__(self,filepath,parentFn):
		#the container for the object.
		self.parentFn = parentFn
		self.type = 'corrObject'
		self.filepath = str(filepath)
		self.nameAndExt = os.path.basename(self.filepath).split('.')
		self.name = self.nameAndExt[0]
		self.ext = self.nameAndExt[-1]
		self.autoNorm=[]
		self.autotime=[]
		self.model_autoNorm =[]
		self.model_autotime = []
		self.parent_name = 'Not known'
		self.file_name = 'Not known'
		self.datalen= []
		self.objId = self;
		self.param = []
		self.goodFit = True
		self.fitted = False
		self.checked = False
		self.clicked = False
		self.toFit = False
		self.kcount = None
		self.filter = False
		self.series_list_id = None
	   
	def prepare_for_fit(self):
		if self.parentFn.ch_check_ch0.isChecked() == True and self.ch_type == 0:
			self.toFit = True
		if self.parentFn.ch_check_ch1.isChecked() == True and self.ch_type == 1:
			self.toFit = True
			
		if self.parentFn.ch_check_ch01.isChecked() == True and self.ch_type == 2:
			self.toFit = True
		if self.parentFn.ch_check_ch10.isChecked() == True and self.ch_type == 3:
			self.toFit = True
		#self.parentFn.modelFitSel.clear()
		#for objId in self.parentFn.objIdArr:
		 #   if objId.toFit == True:
		  #      self.parentFn.modelFitSel.addItem(objId.name)
		#self.parentFn.updateFitList()
	def calculate_suitability(self):

		size_of_sequence = float(self.autoNorm.__len__())
		sum_below_origin = float(np.sum(self.autoNorm<0))
		self.above_zero =  (size_of_sequence - sum_below_origin)/size_of_sequence

	def residual(self, param, x, data,options):
		if self.parentFn.def_options['Diff_eq'] == 5:
			A = PB.equation_(param, x,options)
		elif self.parentFn.def_options['Diff_eq'] == 4:
			A = VD.equation_(param, x,options)
		elif self.parentFn.def_options['Diff_eq'] == 3:
			A = GS.equation_(param, x,options)
		else:
			A = SE.equation_(param, x,options)
		residuals = np.array(data)-np.array(A)
		return np.array(residuals).astype(np.float64)
	def fitToParameters(self):
		

		#Populate param for lmfit.
		param = Parameters()
		#self.def_param.add('A1', value=1.0, min=0,max=1.0, vary=False)
		for art in self.param:
			
			if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:
				
				param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']), max=float(self.param[art]['maxv']), vary=self.param[art]['vary']);
				
		


		
		#Find the index of the nearest point in the scale.
		
		data = np.array(self.autoNorm).astype(np.float64).reshape(-1)
		
		scale = np.array(self.autotime).astype(np.float64).reshape(-1)
		self.indx_L = int(np.argmin(np.abs(scale -  self.parentFn.dr.xpos)))
		self.indx_R = int(np.argmin(np.abs(scale -  self.parentFn.dr1.xpos)))

		
		
		if  self.parentFn.bootstrap_enable_toggle == True:
			num_of_straps = self.parentFn.bootstrap_samples.value()
			aver_data = {}

			lim_scale = scale[self.indx_L:self.indx_R+1].astype(np.float64)
			lim_data  = data[self.indx_L:self.indx_R+1].astype(np.float64)

			
			#Populate a container which will store our output variables from the bootstrap.
			for art in self.param:
					if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:
						aver_data[art] = []


			for i in range(0,num_of_straps):
				#Bootstrap our sample, but remove duplicates.
				boot_ind = np.random.choice(np.arange(0,lim_data.shape[0]),size=lim_data.shape[0],replace=True);


				#boot_ind = np.arange(0,lim_data.shape[0])#np.sort(boot_ind)
				boot_scale = lim_scale[boot_ind]
				boot_data = lim_data[boot_ind]
				
				res = minimize(self.residual, param, args=(boot_scale,boot_data, self.parentFn.def_options))
				for art in self.param:

					if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:
						aver_data[art].append(res.params[art].value)
						
				
			for art in self.param:
					
						

					if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:
						self.param[art]['value'] = np.average(aver_data[art])
						self.param[art]['stderr'] = np.std(aver_data[art])
		
		#Run the fitting.
		if  self.parentFn.bootstrap_enable_toggle == False:
			
			res = minimize(self.residual, param, args=(scale[self.indx_L:self.indx_R+1],data[self.indx_L:self.indx_R+1], self.parentFn.def_options))
			#Repopulate the parameter object.
			
			

			for art in self.param:
				
				if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:

					self.param[art]['value'] = res.params[art].value
					
					self.param[art]['stderr'] = res.params[art].stderr
					
					



		
				
		#Extra parameters, which are not fit or inherited.
		#self.param['N_FCS']['value'] = np.round(1/self.param['GN0']['value'],4)

		#Populate param for the plotting. Would like to use same method as 
		plot_param = Parameters()
		#self.def_param.add('A1', value=1.0, min=0,max=1.0, vary=False)
		for art in self.param:
			
			if self.param[art]['to_show'] == True and self.param[art]['calc'] == False:
				
				plot_param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']), max=float(self.param[art]['maxv']), vary=self.param[art]['vary']);
				

		
		
		
		#Display fitted equation.
		
		if self.parentFn.def_options['Diff_eq'] == 5:
			self.model_autoNorm = PB.equation_(plot_param, scale[self.indx_L:self.indx_R+1],self.parentFn.def_options)
		elif self.parentFn.def_options['Diff_eq'] == 4:
			self.model_autoNorm = VD.equation_(plot_param, scale[self.indx_L:self.indx_R+1],self.parentFn.def_options)
		elif self.parentFn.def_options['Diff_eq'] == 3:
			self.model_autoNorm = GS.equation_(plot_param, scale[self.indx_L:self.indx_R+1],self.parentFn.def_options)
		else:
			self.model_autoNorm = SE.equation_(plot_param, scale[self.indx_L:self.indx_R+1],self.parentFn.def_options)
		self.model_autotime = scale[self.indx_L:self.indx_R+1]


		if  self.parentFn.bootstrap_enable_toggle == False:
			self.residualVar = res.residual
		else:
			self.residualVar = self.model_autoNorm - data[self.indx_L:self.indx_R+1].astype(np.float64)


		output = fit_report(res.params)
		
		if(res.chisqr>self.parentFn.chisqr):
			print('CAUTION DATA DID NOT FIT WELL CHI^2 >',self.parentFn.chisqr,' ',res.chisqr)
			self.goodFit = False
		else:
			self.goodFit = True
		self.fitted = True
		self.chisqr = res.chisqr
		
		self.localTime =  time.asctime( time.localtime(time.time()) )
		

		#Update the displayed options.

		if self.parentFn.def_options['Diff_eq'] == 5:
			PB.calc_param_fcs(self.parentFn,self)
		elif self.parentFn.def_options['Diff_eq'] == 4:
			VD.calc_param_fcs(self.parentFn,self)
		elif self.parentFn.def_options['Diff_eq'] == 3:
			GS.calc_param_fcs(self.parentFn,self)
		else:
			SE.calc_param_fcs(self.parentFn,self)

		
		