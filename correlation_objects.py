import numpy as np
import os, sys
from correlation_methods import *
from import_methods import *
import time
from fitting_methods import equation_
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
		self.photonCountBin = self.par_obj.photonCountBin
		
		#File import
		
		if self.ext == 'pt3':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt3import(self.filepath)
		if self.ext == 'csv':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = csvimport(self.filepath)
			#If the file is empty.
			if self.subChanArr == None:
				#Undoes any preparation of resource.
				self.par_obj.data.pop(-1);
				self.par_obj.objectRef.pop(-1)
				self.exit = True
				print 'Your file is not in the correct format.'
				return

		#print 'shape of self.subChanArr',self.subChanArr.shape
		#print 'shape of self.trueTimeArr',self.trueTimeArr.shape
		#print 'shape of self.dTimeArr',self.dTimeArr.shape
		
		#f = open('test_uncorreled.csv', 'w')
		#f.write('version,'+str(2)+'\n')
		#f.write('type,pt uncorrelated\n')
		#f.write('resolution,'+str(self.resolution)+str('\n'))
		#for i in range(self.subChanArr.shape[0]):

		#     f.write(str(self.subChanArr[i])+','+"%.3f"%self.trueTimeArr[i]+','+str(self.dTimeArr[i])+'\n')
		#f.write('end'+str('\n'))
		#f.close()
					
		
		#Colour assigned to file.
		self.color = self.par_obj.colors[self.unqID % len(self.par_obj.colors)]

		#How many channels there are in the files.
		self.numOfCH =  np.unique(np.array(self.subChanArr)).__len__()-1 #Minus 1 because not interested in channel 15.
		
		#Finds the numbers which address the channels.
		self.ch_present = np.unique(np.array(self.subChanArr[0:100]))

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


		
		#Calculates the Auto and Cross-correlation functions.
		self.crossAndAuto(np.array(self.trueTimeArr),np.array(self.subChanArr))
		
		if self.fit_obj != None:
			#If fit object provided then creates fit objects.
			if self.objId1 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId1 = corrObj.objId
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId1.name = self.name+'_CH0_Auto_Corr'
				self.objId1.ch_type = 0 #channel 0 Auto
				self.objId1.siblings = None
				self.objId1.prepare_for_fit()
				self.objId1.kcount = self.kcount_CH1
				
			self.objId1.autoNorm = np.array(self.autoNorm[:,0,0]).reshape(-1)
			self.objId1.autotime = np.array(self.autotime).reshape(-1)
			self.objId1.param = self.fit_obj.def_param
			
			
			if self.numOfCH ==  2:
				if self.objId3 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId3 = corrObj.objId
					self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId3.name = self.name+'_CH1_Auto_Corr'
					self.objId3.ch_type = 1 #channel 1 Auto
					self.objId3.siblings = None
					self.objId3.prepare_for_fit()
					self.objId3.kcount = self.kcount_CH2
					
				self.objId3.autoNorm = np.array(self.autoNorm[:,1,1]).reshape(-1)
				self.objId3.autotime = np.array(self.autotime).reshape(-1)
				self.objId3.param = self.fit_obj.def_param
				
				if self.objId2 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId2 = corrObj.objId
					self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId2.name = self.name+'_CH01_Cross_Corr'
					self.objId2.ch_type = 2 #01cross
					self.objId2.siblings = None
					self.objId2.prepare_for_fit()
					
				self.objId2.autoNorm = np.array(self.autoNorm[:,0,1]).reshape(-1)
				self.objId2.autotime = np.array(self.autotime).reshape(-1)
				self.objId2.param = self.fit_obj.def_param
				

				if self.objId4 == None:
					corrObj= corrObject(self.filepath,self.fit_obj);
					self.objId4 = corrObj.objId
					self.objId4.param = copy.deepcopy(self.fit_obj.def_param)
					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId4.name = self.name+'_CH10_Cross_Corr'
					self.objId4.ch_type = 3 #10cross
					self.objId4.siblings = None
					self.objId4.prepare_for_fit()
					
				self.objId4.autoNorm = np.array(self.autoNorm[:,1,0]).reshape(-1)
				self.objId4.autotime = np.array(self.autotime).reshape(-1)
				self.objId4.param = self.fit_obj.def_param
				
			self.fit_obj.fill_series_list()
		self.dTimeMin = 0
		self.dTimeMax = np.max(self.dTimeArr)
		self.subDTimeMin = self.dTimeMin
		self.subDTimeMax = self.dTimeMax
		self.exit = False
		del self.subChanArr 
		del self.trueTimeArr 
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
		self.photonDecayCh1Min = self.photonDecayCh1-np.min(self.photonDecayCh1)
		self.photonDecayCh1Norm = self.photonDecayCh1Min/np.max(self.photonDecayCh1Min)
		
		
		if self.numOfCH ==  2:
			self.photonDecayCh2Min = self.photonDecayCh2-np.min(self.photonDecayCh2)
			self.photonDecayCh2Norm = self.photonDecayCh2Min/np.max(self.photonDecayCh2Min)
		
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
		self.photonCountBin = self.par_obj.photonCountBin

		self.filepath = str(self.parentId.filepath)
		self.xmin = xmin
		self.xmax = xmax

		self.nameAndExt = os.path.basename(self.filepath).split('.')
		self.name = 'TG-'+str(self.unqID)+'-xmin_'+str(round(xmin,0))+'-xmax_'+str(round(xmax,0))+'-'+self.nameAndExt[0]

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
		if self.ext == 'pt3':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = pt3import(self.filepath)
		if self.ext == 'csv':
			self.subChanArr, self.trueTimeArr, self.dTimeArr,self.resolution = csvimport(self.filepath)
			#If the file is empty.
			#if self.subChanArr == None:
				#Undoes any preparation of resource.
			#    self.par_obj.subObjectRef.pop(-1)
				#self.exit = True
			#    return


		self.subArrayGeneration(self.xmin,self.xmax)
		
		self.dTimeMin = self.parentId.dTimeMin
		self.dTimeMax = self.parentId.dTimeMax
		self.subDTimeMin = self.dTimeMin
		self.subDTimeMax = self.dTimeMax

	   #Time series of photon counts. For visualisation.
		self.timeSeries1,self.timeSeriesScale1 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[0],self.photonCountBin)
		
		unit = self.timeSeriesScale1[-1]/self.timeSeriesScale1.__len__()
		self.kcount_CH1 = np.average(self.timeSeries1)
		if self.numOfCH ==  2:

			self.timeSeries2,self.timeSeriesScale2 = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[1],self.photonCountBin)
			unit = self.timeSeriesScale2[-1]/self.timeSeriesScale2.__len__()
			self.kcount_CH2 = np.average(self.timeSeries2)
		

		
		#Adds names to the fit function for later fitting.
		if self.objId1 == None:
			corrObj= corrObject(self.filepath,self.fit_obj);
			self.objId1 = corrObj.objId
			self.fit_obj.objIdArr.append(corrObj.objId)
			self.objId1.param = copy.deepcopy(self.fit_obj.def_param)
			self.objId1.name = self.name+'_CH0_Auto_Corr'
			self.objId1.ch_type = 0 #channel 0 Auto
			self.objId1.siblings = None
			self.objId1.prepare_for_fit()
			
			self.objId1.kcount = self.kcount_CH1
		self.objId1.autoNorm = np.array(self.autoNorm[:,0,0]).reshape(-1)
		self.objId1.autotime = np.array(self.autotime).reshape(-1)
		self.objId1.param = self.fit_obj.def_param
		
		
		if self.numOfCH ==2:
			if self.objId3 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId3 = corrObj.objId
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId3.param = copy.deepcopy(self.fit_obj.def_param)
				self.objId3.name = self.name+'_CH1_Auto_Corr'
				self.objId3.ch_type = 1 #channel 1 Auto
				self.objId3.siblings = None
				self.objId3.prepare_for_fit()
				self.objId3.kcount = self.kcount_CH2
				
			self.objId3.autoNorm = np.array(self.autoNorm[:,1,1]).reshape(-1)
			self.objId3.autotime = np.array(self.autotime).reshape(-1)
			self.objId3.param = self.fit_obj.def_param
			if self.objId2 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId2 = corrObj.objId
				self.objId2.param = copy.deepcopy(self.fit_obj.def_param)
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId2.name = self.name+'_CH01_Cross_Corr'
				self.objId2.ch_type = 2 #channel 01 Cross
				self.objId2.siblings = None
				self.objId2.prepare_for_fit()
				
			self.objId2.autoNorm = np.array(self.autoNorm[:,0,1]).reshape(-1)
			self.objId2.autotime = np.array(self.autotime).reshape(-1)
			self.objId2.param = self.fit_obj.def_param
			if self.objId4 == None:
				corrObj= corrObject(self.filepath,self.fit_obj);
				self.objId4 = corrObj.objId
				self.objId4.param = copy.deepcopy(self.fit_obj.def_param)
				self.fit_obj.objIdArr.append(corrObj.objId)
				self.objId4.name = self.name+'_CH10_Cross_Corr'
				self.objId4.ch_type = 3 #channel 10 Cross
				self.objId4.siblings = None
				self.objId4.prepare_for_fit()
				
			self.objId4.autoNorm = np.array(self.autoNorm[:,1,0]).reshape(-1)
			self.objId4.autotime = np.array(self.autotime).reshape(-1)
			
			
		
		self.fit_obj.fill_series_list()  
		del self.subChanArr 
		del self.trueTimeArr 
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
		self.datalen= []
		self.objId = self;
		self.param = []
		self.goodFit = True
		self.fitted = False
		self.checked = False
		self.toFit = False
		self.kcount = None
	   
		#main.data.append(filepath);
		#The master data object reference 
		#main.corrObjectRef.append(self)
		#The id in terms of how many things are loaded.
		#self.unqID = main.label.numOfLoaded;
		#main.label.numOfLoaded = main.label.numOfLoaded+1
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
		self.parentFn.updateFitList()
	def residual(self, param, x, data,options):
	
		A = equation_(param, x,options)
		residuals = data-A
		return residuals
	def fitToParameters(self):
		self.parentFn.updateParamFirst()
		self.parentFn.updateTableFirst()
		self.parentFn.updateParamFirst()
		

		#Populate param for lmfit.
		param = Parameters()
		#self.def_param.add('A1', value=1.0, min=0,max=1.0, vary=False)
		for art in self.param:
			
			if self.param[art]['to_show'] == True:
				param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']) ,max=float(self.param[art]['maxv']), vary=self.param[art]['vary']);
				
		
		#Find the index of the nearest point in the scale.
		
		data = np.array(self.autoNorm).astype(np.float64).reshape(-1)
		scale = np.array(self.autotime).astype(np.float64).reshape(-1)
		indx_L = int(np.argmin(np.abs(scale -  self.parentFn.dr.xpos)))
		indx_R = int(np.argmin(np.abs(scale -  self.parentFn.dr1.xpos)))
		
		#Run the fitting.
		res = minimize(self.residual, param, args=(scale[indx_L:indx_R+1],data[indx_L:indx_R+1], self.parentFn.def_options))

		#Repopulate the parameter object.
		for art in self.param:
			if self.param[art]['to_show'] == True:
				self.param[art]['value'] = param[art].value
		#Extra parameters, which are not fit or inherited.
		self.param['N_FCS']['value'] = np.round(1/self.param['GN0']['value'],4)


		self.residualVar = res.residual
		output = fit_report(param)
		print 'residual',res.chisqr
		if(res.chisqr>0.05):
			print 'CAUTION DATA DID NOT FIT WELL CHI^2 >0.05',res.chisqr
			self.goodFit = False
		else:
			self.goodFit = True
		self.fitted = True
		self.chisqr = res.chisqr
		rowArray =[];
		localTime = time.asctime( time.localtime(time.time()) )
		rowArray.append(str(self.name))  
		rowArray.append(str(localTime))
		rowArray.append(str(self.parentFn.diffModEqSel.currentText()))
		rowArray.append(str(self.parentFn.def_options['Diff_species']))
		rowArray.append(str(self.parentFn.tripModEqSel.currentText()))
		rowArray.append(str(self.parentFn.def_options['Triplet_species']))
		rowArray.append(str(self.parentFn.dimenModSel.currentText()))
		rowArray.append(str(scale[indx_L]))
		rowArray.append(str(scale[indx_R]))

		for key, value in param.iteritems() :
			rowArray.append(str(value.value))
			rowArray.append(str(value.stderr))
			if key =='GN0':
				try:
					rowArray.append(str(self.param['N_FCS']['value']))
					if self.ch_type !=2:
						rowArray.append(str(self.param['cpm']['value']))
					else:
						rowArray.append('')
				except:
					rowArray.append(str(0))
		#Adds non-fit parameters.
		try:
			rowArray.append(str(np.round(float(self.numberNandB),5)))
			rowArray.append(str(np.round(float(self.brightnessNandB),5)))

		except:
		   pass
		
		self.rowText = rowArray
		
		self.parentFn.updateTableFirst();
		self.model_autoNorm = equation_(param, scale[indx_L:indx_R+1],self.parentFn.def_options)
		self.model_autotime = scale[indx_L:indx_R+1]
		self.parentFn.on_show()

		#self.parentFn.axes.plot(model_autotime,model_autoNorm, 'o-')
		#self.parentFn.canvas.draw();
	
	def load_from_file(self,channel):
		tscale = [];
		tdata = [];
		int_tscale =[];
		int_tdata=[];
		if self.ext == 'SIN':
			self.parentFn.objIdArr.append(self.objId)
			proceed = False
			
			for line in csv.reader(open(self.filepath, 'rb'),delimiter='\t'):
				
				if proceed =='correlated':
					if line ==[]:
						proceed =False;
					else:
						tscale.append(float(line[0]))
						tdata.append(float(line[channel+1]))
				if proceed =='intensity':
					
					if line ==[]:
						proceed=False;
					elif line.__len__()> 1:
						
						int_tscale.append(float(line[0]))
						int_tdata.append(float(line[channel+1]))
				if (str(line)  == "[\'[CorrelationFunction]\']"):
					proceed = 'correlated';
				elif (str(line)  == "[\'[IntensityHistory]\']"):
					proceed = 'intensity';
				
				
				
			
			self.siblings = None
			self.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
			self.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
			self.name = self.name+'-CH'+str(channel)
			self.ch_type = channel;
			#self.prepare_for_fit()

			
			
			


			#Average counts per bin. For it to be seconds (Hz), must divide by duration.
			unit = int_tscale[-1]/(int_tscale.__len__()-1)
			#And to be in kHz we divide by 1000.
			self.kcount = np.average(np.array(int_tdata)/unit)/1000
			

			#var_per_bin = np.var(np.array(int_tdata))/1000
			#ave_per_bin = np.average(np.array(int_tdata))
			#self.brightness = var_per_bin/ave_per_bin
			#self.N_from_moment = (ave_per_bin**2)/var_per_bin

			#print 'self.brightnessSIN', self.brightness
			#print 'self.N_from_momentSIN', self.N_from_moment
			



			self.param = self.parentFn.def_param
			self.parentFn.fill_series_list()
			
		
					#Where we add the names.


		if self.ext == 'csv':
			r_obj = csv.reader(open(self.filepath, 'rb'))
			line_one = r_obj.next()
			if line_one.__len__()>1:
				if float(line_one[1]) == 2:
					
					version = 2
				else:
					print 'version not known:',line_one[1]
			else:
				version = 1

			if version == 1:
				self.parentFn.objIdArr.append(self)
				
				c = 0
				
				for line in csv.reader(open(self.filepath, 'rb')):
					if (c >0):
						tscale.append(line[0])
						tdata.append(line[1])
					c +=1;

				self.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
				self.autotime= np.array(tscale).astype(np.float64).reshape(-1)
				self.name = self.name+'-CH'+str(0)
				self.ch_type = 0
				self.datalen= len(tdata)

				self.param = self.parentFn.def_param
				self.parentFn.fill_series_list()
			if version == 2:
				
					
				numOfCH = float(r_obj.next()[1])
				
				if numOfCH == 1:
					self.parentFn.objIdArr.append(self)
					self.type =str(r_obj.next()[1])
					self.ch_type = int(r_obj.next()[1])
					self.name = self.name+'-CH'+str(self.ch_type)
					
					self.kcount = float(r_obj.next()[1])
					self.numberNandB =  float(r_obj.next()[1])
					self.brightnessNandB =  float(r_obj.next()[1])

					self.carpet_position =  int(r_obj.next()[1])
					
					

					pc_text =  int(r_obj.next()[1])
					
					if pc_text != False:
						self.name = self.name +'_pc_m'+str(pc_text)
						
					
					tscale = []
					tdata = []
					null = r_obj.next()
					line = r_obj.next()
					while  line[0] != 'end':

						tscale.append(line[0])
						tdata.append(line[1])
						line = r_obj.next()

					self.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
					self.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					self.siblings = None
					self.param = self.parentFn.def_param
					self.parentFn.fill_series_list()
				if numOfCH == 2:
					corrObj2 = corrObject(self.filepath,self.parentFn);
					corrObj3 = corrObject(self.filepath,self.parentFn);

					self.parentFn.objIdArr.append(self)
					self.parentFn.objIdArr.append(corrObj2)
					self.parentFn.objIdArr.append(corrObj3)
					
					line_type = r_obj.next()
					self.type = str(line_type[1])
					corrObj2.type = str(line_type[1])
					corrObj3.type = str(line_type[1])
					

					line_ch = r_obj.next()
					self.ch_type = int(line_ch[1])
					corrObj2.ch_type = int(line_ch[2])
					corrObj3.ch_type = int(line_ch[3])
					
					self.name = self.name+'-CH'+str(self.ch_type)
					corrObj2.name = corrObj2.name+'-CH'+str(corrObj2.ch_type)
					corrObj3.name = corrObj3.name+'-CH'+str(corrObj3.ch_type)
					
					line_kcount = r_obj.next()
					self.kcount = float(line_kcount[1])
					corrObj2.kcount = float(line_kcount[2])
					#corrObj3.kcount = float(line_kcount[3])

					line_numberNandB = r_obj.next()
					self.numberNandB =  float(line_numberNandB[1])
					corrObj2.numberNandB =  float(line_numberNandB[2])
					#corrObj3.numberNandB =  float(line_numberNandB[3])

					line_brightnessNandB = r_obj.next()
					self.brightnessNandB =  float(line_brightnessNandB[1])
					corrObj2.brightnessNandB =  float(line_brightnessNandB[2])

					self.carpet_position =  int(r_obj.next()[1])
					#corrObj3.brightnessNandB =  float(line_brightnessNandB[3])
					
					line_pc = r_obj.next()
					pc_text =  int(line_pc[1])
					
					if pc_text != False:
						self.name = self.name +'_pc_m'+str(pc_text)
						corrObj2.name = corrObj2.name +'_pc_m'+str(pc_text)
						corrObj3.name = corrObj3.name +'_pc_m'+str(pc_text)
					
					null = r_obj.next()
					line = r_obj.next()
					tscale = []
					tdata0 = []
					tdata1 = []
					tdata2 = []
					while  line[0] != 'end':

						tscale.append(line[0])
						tdata0.append(line[1])
						tdata1.append(line[2])
						tdata2.append(line[3])
						line = r_obj.next()

					
					self.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj2.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj3.autotime= np.array(tscale).astype(np.float64).reshape(-1)

					self.autoNorm= np.array(tdata0).astype(np.float64).reshape(-1)
					corrObj2.autoNorm= np.array(tdata1).astype(np.float64).reshape(-1)
					corrObj3.autoNorm= np.array(tdata2).astype(np.float64).reshape(-1)
					
					self.siblings = [corrObj2,corrObj3]
					corrObj2.siblings = [self,corrObj3]
					corrObj3.siblings = [self,corrObj2]
					
					self.param = self.parentFn.def_param
					corrObj2.param = self.parentFn.def_param
					corrObj3.param = self.parentFn.def_param
					self.parentFn.fill_series_list()


				





