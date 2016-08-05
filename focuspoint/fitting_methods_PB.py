import numpy as np
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
def initialise_fcs(int_obj):
	#default options for the fitting.
		
		

		
		
		#The offset
		offset = { 'alias':'offset','value':0.01,'minv':-0.5,'maxv':1.5,'vary':True,'to_show':True,'calc':False}
		#int_obj.defin.add('offset', value=0.0, min=-1.0,max=5.0,vary=False)
		#The amplitude
		GN0 = {'alias':'GN0','minv':0.001,'value':1,'maxv':1.0,'vary':True,'to_show':True,'calc':False}
		
		txy1 = {'alias':'txy1','value':0.01,'minv':0.001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}

		bA = {'alias':'bleach A','value':0.01,'minv':0.001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}

		Kz = {'alias':'Kz','value':0.01,'minv':0.001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}
		
		
		

		
		


		int_obj.def_param['txy1'] = txy1
		int_obj.def_param['offset'] = offset
		int_obj.def_param['GN0'] = GN0
		int_obj.def_param['bA'] = bA
		int_obj.def_param['Kz'] = Kz
		

		
		

def decide_which_to_show(int_obj):
	
		for art in int_obj.objId_sel.param:
			if int_obj.objId_sel.param[art]['to_show'] == True:
				int_obj.objId_sel.param[art]['to_show'] = False

		int_obj.objId_sel.param['offset']['to_show'] = True
		int_obj.objId_sel.param['GN0']['to_show'] = True
		int_obj.objId_sel.param['txy1']['to_show'] = True
		int_obj.objId_sel.param['bA']['to_show'] = True
		int_obj.objId_sel.param['Kz']['to_show'] = True
		
		
		
		
		calc_param_fcs(int_obj,objId=int_obj.objId_sel)

def update_each(int_obj,text):
		"""Will try and populate paramaters with what is present in the inteface, but if new option will goto the default"""
		try:
			exec("valueV = int_obj."+text+"_value.value()"); exec("minV = int_obj."+text+"_min.value()"); exec("maxV = int_obj."+text+"_max.value()"); exec("varyV = int_obj."+text+"_vary.isChecked()");
			
			int_obj.objId_sel.param[text]['value'] = valueV 
			int_obj.objId_sel.param[text]['minv'] = minV
			int_obj.objId_sel.param[text]['maxv'] = maxV
			int_obj.objId_sel.param[text]['vary'] = varyV
		except:
			
			int_obj.objId_sel.param[text] = copy.deepcopy(int_obj.def_param[text])
def update_param_fcs(int_obj):
		"""Depending on the menu options this function will update the params of the current data set. """
		if int_obj.objId_sel ==None:
			return
		decide_which_to_show(int_obj)
		#Set all the parameters to not show.

		for art in int_obj.objId_sel.param:
			if int_obj.objId_sel.param[art]['to_show'] == True:
				update_each(int_obj, art)
		
		calc_param_fcs(int_obj,objId=int_obj.objId_sel)
def calc_param_fcs(int_obj,objId):
		#Calculated parameters.
		try:
			objId.param['N_FCS']['value'] = 1/objId.param['GN0']['value']
			objId.param['N_FCS']['to_show'] = True
		except:
			objId.param['N_FCS']['value'] = 1
			objId.param['N_FCS']['to_show'] = False
		
		try:
			objId.param['cpm']['value'] = float(objId.kcount)/(1/objId.param['GN0']['value'])
			objId.param['cpm']['to_show'] = True
		except:
			objId.param['cpm']['value'] = 1
			objId.param['cpm']['to_show'] = False
		try:
			objId.param['N_mom']['value'] =  float(objId.numberNandB)
			objId.param['N_mom']['to_show'] = True
		except:
			objId.param['N_mom']['value'] =  1
			objId.param['N_mom']['to_show'] = False

		try:
			objId.param['bri']['value'] = float(objId.brightnessNandB)
			objId.param['bri']['to_show'] = True
		except:
			objId.param['bri']['value'] = 1
			objId.param['bri']['to_show'] = False
		try:
			objId.param['CV']['value'] = float(objId.CV)
			objId.param['CV']['to_show'] = True
		except:
			pass
		try:
			objId.param['f0']['value'] = float(objId.pbc_f0)
			objId.param['f0']['to_show'] = True
			objId.param['overtb']['value'] = float(objId.pbc_tb)
			objId.param['overtb']['to_show'] = True
		except:
			pass
		try:
			if int_obj.objIdArr != [] and objId.siblings !=None and objId.ch_type != 2 and objId.ch_type != 3:
					
					if objId.siblings[0].fitted == True:
						
						objId.param['ACAC']['value'] = float(objId.param['GN0']['value'])/float(objId.siblings[0].param['GN0']['value'])
						objId.param['ACAC']['to_show'] = True
						objId.param['ACCC']['value'] = float(objId.param['GN0']['value'])/float(objId.siblings[1].param['GN0']['value'])
						objId.param['ACCC']['to_show'] = True
		except:
			pass

def equation_(param, tc,options):
	"""This is equation for fitting"""

	#A1 is relative component of fluorescent species
	#tc is tau.
	#txy1 is xy difusion   for fluorescent species one.
	#alpha1 is
	#tz1 is z diffusion for fluorescent species one.
	offset =param['offset'].value; 
	GN0 =param['GN0'].value; 
	
	


						   
	
		
	txy1 = param['txy1'].value;
	#For one diffusing species
	GDiff = ((1+((tc/txy1)))**-1)

	bA = param['bA'].value; Kz = param['Kz'].value
	#Bleaching
	GBlea = (1-bA) + bA*np.exp(-Kz*tc)
		
	
	
	

			
	return offset + (GN0*GDiff*GBlea)