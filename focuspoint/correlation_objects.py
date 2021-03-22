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

		self.par_obj.data.append(filepath)
		self.par_obj.objectRef.append(self)
		
		#Imports pt3 file format to object.
		self.unqID = self.par_obj.numOfLoaded
		self.objId =[]
		
		self.processData()
		
		self.plotOn = True


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
				self.par_obj.data.pop(-1)
				self.par_obj.objectRef.pop(-1)
				self.exit = True
				
				return
		else:
			self.exit = True
			return 

		if self.type  == 'subObject':
			self.subArrayGeneration(self.xmin,self.xmax)			
		
		#Colour assigned to file.
		self.color = self.par_obj.colors[self.unqID % len(self.par_obj.colors)]

		#How many channels there are in the files.
		
		self.ch_present = np.sort(np.unique(np.array(self.subChanArr)))
		
		if self.ext == 'pt3' or self.ext == 'ptu'or self.ext == 'pt2':
			
			self.numOfCH =  self.ch_present.__len__() #Minus 1 because not interested in channel 15.

		else:
			self.numOfCH =  self.ch_present.__len__()
		#Finds the numbers which address the channels.
		
			
		self.photonDecay = []
		self.decayScale = []
		self.timeSeries = []
		self.timeSeriesScale = []
		self.kcount = []
		self.brightnessNandB = []
		self.numberNandB = []
		self.photonDecayMin = []
		self.photonDecayNorm = []

		

		for i in range(0,self.numOfCH):
			photonDecay, decayScale = delayTime2bin(np.array(self.dTimeArr),np.array(self.subChanArr),self.ch_present[i],self.winInt)
			self.photonDecay.append(photonDecay)
			self.decayScale.append(decayScale)

			#Normalisaation of the decay functions.
			if np.sum(self.photonDecay[i]) > 0:
				self.photonDecayMin.append(self.photonDecay[i]-np.min(self.photonDecay[i]))
				self.photonDecayNorm.append(self.photonDecayMin[i]/np.max(self.photonDecayMin[i]))
			else:
				self.photonDecayMin.append(0)
				self.photonDecayNorm.append(0)

			timeSeries, timeSeriesScale = delayTime2bin(np.array(self.trueTimeArr)/1000000,np.array(self.subChanArr),self.ch_present[i],self.photonCountBin)
			self.timeSeries.append(timeSeries)
			self.timeSeriesScale.append(timeSeriesScale)
			
			kcount, brightnessNandB, numberNandB = photonCountingStats(self.timeSeries[i],self.timeSeriesScale[i])
			self.kcount.append(kcount)
			self.brightnessNandB.append(brightnessNandB)
			self.numberNandB.append(numberNandB)
		
		#Correlation combinations.
		##Provides ordering of files and reduces repetition.

		corr_array = []
		corr_comb = []
		

		
		for i in range(0,self.numOfCH):
			corr_array.append([])
			for j in range(0,self.numOfCH):
				if i < j:
					corr_comb.append([i,j])
				corr_array[i].append([])
					
		
		for i,j in corr_comb:
			corr_fn = self.crossAndAuto(np.array(self.trueTimeArr),np.array(self.subChanArr),[self.ch_present[i],self.ch_present[j]])
			
			if corr_array[i][i]  == []:
				corr_array[i][i] = corr_fn[:,0,0].reshape(-1)
			if corr_array[j][j] == []:
				corr_array[j][j] = corr_fn[:,1,1].reshape(-1)
			corr_array[i][j] = corr_fn[:,0,1].reshape(-1)
			corr_array[j][i] = corr_fn[:,1,0].reshape(-1)
		self.autoNorm = corr_array  
		self.autotime = self.autotime.reshape(-1)
		self.CV = []			
		#Calculates the Auto and Cross-correlation functions.
		#self.crossAndAuto(np.array(self.trueTimeArr),np.array(self.subChanArr),np.array(self.ch_present)[0:2])
		
		if self.fit_obj != None:
			self.indx_arr = []

			#I order them this way, for systematic ordering in the plotting. 
			#All the plots are included. First the auto, then the cross.
			for i in range(0,self.numOfCH):
				self.indx_arr.append([i,i])
			for i in range(0,self.numOfCH):
				for j in range(0,self.numOfCH):
					if i != j:
						self.indx_arr.append([i,j])

			#If fit object provided then creates fit objects.
			traces = self.indx_arr.__len__()
			

			for c in range(0,traces):
				i,j = self.indx_arr[c]
				if self.objId.__len__() == c:
					corrObj= corrObject(self.filepath,self.fit_obj)
					self.objId.append(corrObj.objId)
					if self.type == "subObject":
						self.objId[c].parent_name = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
						self.objId[c].parent_uqid = 'pt FCS tgated -tg0: '+str(np.round(self.xmin,0))+' -tg1: '+str(np.round(self.xmax,0))
					else:
						self.objId[c].parent_name = 'point FCS'
						self.objId[c].parent_uqid = 'point FCS'

					self.fit_obj.objIdArr.append(corrObj.objId)
					self.objId[c].param = copy.deepcopy(self.fit_obj.def_param)
					
					self.objId[c].ch_type = str(i+1)+"_"+str(j+1)
					
					self.objId[c].prepare_for_fit()
					self.objId[c].siblings = None
				
					self.objId[c].item_in_list = False

					
						
					self.objId[c].name = self.name+'_CH'+str(self.indx_arr[c][0]+1)+'_CH'+str(self.indx_arr[c][1]+1)
					if i == j:
						self.objId[c].name += '_Auto_Corr'
						self.objId[c].kcount = self.kcount[i]
					else:
						self.objId[c].name += '_Cross_Corr'
						
					
				self.objId[c].autoNorm = corr_array[i][j]
				
				

				self.objId[c].autotime = np.array(self.autotime).reshape(-1)
				self.objId[c].param = copy.deepcopy(self.fit_obj.def_param)
				self.objId[c].max = np.max(self.objId[c].autoNorm)
				self.objId[c].min = np.min(self.objId[c].autoNorm)
				self.objId[c].tmax = np.max(self.objId[c].autotime)
				self.objId[c].tmin = np.min(self.objId[c].autotime)
				if i != j:
					self.objId[c].CV = calc_coincidence_value(self.timeSeries[i],self.timeSeries[j])
				else:
					self.objId[c].CV = None

				self.CV.append(self.objId[c].CV)
			
			self.fit_obj.fill_series_list()
		
		


		self.dTimeMin = 0
		self.dTimeMax = np.max(self.dTimeArr)
		self.subDTimeMin = self.dTimeMin
		self.subDTimeMax = self.dTimeMax
		self.exit = False
		#del self.subChanArr 
		#del self.trueTimeArr 
		del self.dTimeArr
	
	def crossAndAuto(self,trueTimeArr,subChanArr,channelsToUse):
		#For each channel we loop through and find only those in the correct time gate.
		#We only want photons in channel 1 or two.
		if self.numOfCH == 1:
			indices = subChanArr == channelsToUse[0]
			y = trueTimeArr[indices]
			validPhotons = subChanArr[indices]
		else:
			indices0 = subChanArr == channelsToUse[0]
			indices1 = subChanArr == channelsToUse[1]
			indices = indices0+indices1
			
			
			y = trueTimeArr[indices]
			validPhotons = subChanArr[indices]


		#Creates boolean for photon events in either channel.
		num = np.zeros((validPhotons.shape[0],2))
		num[:,0] = (np.array([np.array(validPhotons) == channelsToUse[0]])).astype(np.int32)
		if self.numOfCH >1:
			num[:,1] = (np.array([np.array(validPhotons) ==channelsToUse[1]])).astype(np.int32)
			

		self.count0 = np.sum(num[:,0]) 
		self.count1 = np.sum(num[:,1])



		t1 = time.time()
		auto, self.autotime = tttr2xfcs(y,num,self.NcascStart,self.NcascEnd, self.Nsub)
		t2 = time.time()
		

		#Normalisation of the TCSPC data:
		maxY = np.ceil(max(self.trueTimeArr))
		autoNorm = np.zeros((auto.shape))
		autoNorm[:,0,0] = ((auto[:,0,0]*maxY)/(self.count0*self.count0))-1
		
		if self.numOfCH >1:
			autoNorm[:,1,1] = ((auto[:,1,1]*maxY)/(self.count1*self.count1))-1
			autoNorm[:,1,0] = ((auto[:,1,0]*maxY)/(self.count1*self.count0))-1
			autoNorm[:,0,1] = ((auto[:,0,1]*maxY)/(self.count0*self.count1))-1
		return  autoNorm
	def subArrayGeneration(self,xmin,xmax):
		if(xmax<xmin):
			xmin1 = xmin
			xmin = xmax
			xmax = xmin1
		#self.subChanArr = np.array(self.chanArr)
		#Finds those photons which arrive above certain time or below certain time.
		photonInd = np.logical_and(self.dTimeArr>=xmin, self.dTimeArr<=xmax).astype(np.bool)
		
		self.subChanArr[np.invert(photonInd).astype(np.bool)] = 16
		

		return

	
	
class subPicoObject(picoObject):
	def __init__(self,parentId,xmin,xmax,TGid,par_obj):
		#Binning window for decay function
		self.TGid = TGid
		#Parameters for auto-correlation and cross-correlation.
		self.parentId = parentId
		self.par_obj = par_obj
		
		self.fit_obj = self.parentId.fit_obj
		self.ext = self.parentId.ext
		
		self.type = 'subObject'
		#Appends the object to the subObject register.
		self.par_obj.subObjectRef.append(self)
		self.unqID = self.par_obj.subNum
		self.parentUnqID = self.parentId.unqID

		self.color = self.parentId.color
		self.numOfCH = self.parentId.numOfCH
		self.ch_present = self.parentId.ch_present
		self.photonCountBin = 25#self.par_obj.photonCountBin

		self.filepath = str(self.parentId.filepath)
		self.xmin = xmin
		self.xmax = xmax

		self.objId =[]
		self.nameAndExt = os.path.basename(self.filepath).split('.')
		self.name = self.nameAndExt[0]+'-TG-'+str(self.unqID)+'-xmin_'+str(round(xmin,0))+'-xmax_'+str(round(xmax,0))
		#self.processData = self.parentId.processData
		self.processData()
		self.plotOn = True
		
		
	
def photonCountingStats(timeSeries,timeSeriesScale):
	unit = timeSeriesScale[-1]/timeSeriesScale.__len__()

	#Converts to counts per 
	kcount_CH = np.average(timeSeries)

	raw_count = np.average(timeSeries) #This is the unnormalised intensity count for int_time duration (the first moment)
	var_count = np.var(timeSeries)

	brightnessNandBCH=(((var_count -raw_count)/(raw_count))/(float(unit)))
	if (var_count-raw_count) == 0:
		numberNandBCH =0
	else:
		numberNandBCH = (raw_count**2/(var_count-raw_count))
	return kcount_CH, brightnessNandBCH, numberNandBCH 
def calc_coincidence_value(timeSeries1,timeSeries2):
	N1 = np.bincount((np.array(timeSeries1)).astype(np.int64))
	N2 = np.bincount((np.array(timeSeries2)).astype(np.int64))
	
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
		self.objId = self
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
		if self.parentFn.ch_check_ch1.isChecked() == True and self.ch_type == 0:
			self.toFit = True
		if self.parentFn.ch_check_ch2.isChecked() == True and self.ch_type == 1:
			self.toFit = True
			
		if self.parentFn.ch_check_ch12.isChecked() == True and self.ch_type == 2:
			self.toFit = True
		if self.parentFn.ch_check_ch21.isChecked() == True and self.ch_type == 3:
			self.toFit = True

		if self.parentFn.ch_check_ch1.isChecked() == True and self.ch_type == '1_1':
			self.toFit = True
		elif self.parentFn.ch_check_ch2.isChecked() == True and self.ch_type == '2_2':
			self.toFit = True
		elif self.parentFn.ch_check_ch3.isChecked() == True and self.ch_type == '3_3':
			self.toFit = True
		elif self.parentFn.ch_check_ch4.isChecked() == True and self.ch_type == '4_4':
			self.toFit = True
		elif self.parentFn.ch_check_ch12.isChecked() == True and self.ch_type == '1_2':
			self.toFit = True
		elif self.parentFn.ch_check_ch13.isChecked() == True and self.ch_type == '1_3':
			self.toFit = True
		elif self.parentFn.ch_check_ch14.isChecked() == True and self.ch_type == '1_4':
			self.toFit = True
		elif self.parentFn.ch_check_ch23.isChecked() == True and self.ch_type == '2_3':
			self.toFit = True
		elif self.parentFn.ch_check_ch24.isChecked() == True and self.ch_type == '2_4':
			self.toFit = True
		elif self.parentFn.ch_check_ch34.isChecked() == True and self.ch_type == '3_4':
			self.toFit = True
		elif self.parentFn.ch_check_ch21.isChecked() == True and self.ch_type == '2_1':
			self.toFit = True
		elif self.parentFn.ch_check_ch31.isChecked() == True and self.ch_type == '3_1':
			self.toFit = True
		elif self.parentFn.ch_check_ch41.isChecked() == True and self.ch_type == '4_1':
			self.toFit = True
		elif self.parentFn.ch_check_ch32.isChecked() == True and self.ch_type == '3_2':
			self.toFit = True
		elif self.parentFn.ch_check_ch42.isChecked() == True and self.ch_type == '4_2':
			self.toFit = True
		elif self.parentFn.ch_check_ch43.isChecked() == True and self.ch_type == '4_3':
			self.toFit = True
		else:
			self.toFit = False

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
				
				param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']), max=float(self.param[art]['maxv']), vary=self.param[art]['vary'])
				
		


		
		#Find the index of the nearest point in the scale.
		
		data = np.array(self.autoNorm).astype(np.float64).reshape(-1)
		
		scale = np.array(self.autotime).astype(np.float64).reshape(-1)
		if self.parentFn.dr == None or  self.parentFn.dr1 == None:
			self.indx_L = 0
			self.indx_R = -2
		else:
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
				boot_ind = np.random.choice(np.arange(0,lim_data.shape[0]),size=lim_data.shape[0],replace=True)


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
				
				plot_param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']), max=float(self.param[art]['maxv']), vary=self.param[art]['vary'])
				

		
		
		
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

		
		