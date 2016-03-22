import numpy as np
import copy
from scipy import special as sp
def initialise_fcs(int_obj):
	

	alpha = { 'alias':'alpha','value':0.01,'minv':0.00001,'maxv':10.0,'vary':True,'to_show':True,'calc':False}
	dif = {'alias':'D','value':0.01,'minv':0.00001,'maxv':10.0,'vary':True,'to_show':True,'calc':False}
	offset = { 'alias':'offset','value':0.01,'minv':-0.5,'maxv':1.5,'vary':True,'to_show':True,'calc':False}

	int_obj.def_param['alpha'] = alpha
	int_obj.def_param['dif'] = dif
	int_obj.def_param['offset'] = offset
	
	#int_obj.order_list = ['alpha','dif']
def decide_which_to_show(int_obj):
	
	for art in int_obj.objId_sel.param:
		if int_obj.objId_sel.param[art]['to_show'] == True:
			int_obj.objId_sel.param[art]['to_show'] = False
	int_obj.objId_sel.param[ 'alpha']['to_show'] = True
	int_obj.objId_sel.param[ 'dif']['to_show'] = True
	int_obj.objId_sel.param[ 'offset']['to_show'] = True
	
	
	calc_param_fcs(int_obj,objId=int_obj.objId_sel)

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
def calc_param_fcs(int_obj,objId):
	#Calculated parameters.
	pass


def equation_(param,tc,options):


	alpha =param['alpha'].value; 
	dif =param['dif'].value;
	offset =param['offset'].value; 
	

	dx = 5e-4
	x = np.arange(-1.0+dx/2.0,1.0,dx)
	
	tmp = np.exp(alpha*x**2)
	y = np.zeros(tc.shape[0])
	nrm = 0;
	for j in range(0,51):
		
		leg = sp.legendre(2*j)(x)
		fac = dx*(4*j+1)*(np.dot(leg,tmp))**2
		
		inc = fac*np.exp(-dif*2*j*(2*j+1)*tc)
		y = y + inc
	   
		nrm = nrm +fac
			 
	y = y/nrm
	return y + offset