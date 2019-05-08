import numpy as np
import copy
from scipy.special import erf
def initialise_fcs(int_obj):
	#int_obj.def_options = {}
	#int_obj.def_options['Diff_eq'] = 3

	offset = { 'alias':'offset','value':0.01,'minv':-0.5,'maxv':1.5,'vary':True,'to_show':True,'calc':False}
	N_FCS = {'alias':'N (FCS)','value':0.0,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':True}
	GN0 = {'alias':'GN0','minv':0.001,'value':1,'maxv':1.0,'vary':True,'to_show':True,'calc':False}
	tdiff1 = {'alias':'tdiff1','minv':0.001,'value':1,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	tdiff2 = {'alias':'tdiff2','minv':0.001,'value':1,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	tdiff3 = {'alias':'tdiff3','minv':0.001,'value':1,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}

	Y = {'alias':'Y','minv':0.001,'value':1,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	


	B1 = {'alias':'B1','value':1.0,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	B2 = {'alias':'B2','value':1.0,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	B3 = {'alias':'B3','value':1.0,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}

	T1 = {'alias':'T1','value':1.0,'minv':0.0,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	T2 = {'alias':'T2','value':1.0,'minv':0.0,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	T3 = {'alias':'T3','value':1.0,'minv':0.0,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}

	tauT1 = {'alias':'tauT1','value':0.055,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	tauT2 = {'alias':'tauT2','value':0.055,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}
	tauT3 = {'alias':'tauT3','value':0.005,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':False}


	int_obj.def_param['offset'] = offset
	int_obj.def_param['N_FCS'] = N_FCS
	int_obj.def_param['GN0'] = GN0
	int_obj.def_param['tdiff1'] = tdiff1
	int_obj.def_param['tdiff2'] = tdiff2
	int_obj.def_param['tdiff3'] = tdiff3

	int_obj.def_param['Y'] = Y
	int_obj.def_param['B1'] = B1
	int_obj.def_param['B2'] = B2
	int_obj.def_param['B3'] = B3
	int_obj.def_param['T1'] = T1
	int_obj.def_param['T2'] = T2
	int_obj.def_param['T3'] = T3
	int_obj.def_param['tauT1'] = tauT1
	int_obj.def_param['tauT2'] = tauT2
	int_obj.def_param['tauT3'] = tauT3
	
	#int_obj.order_list = ['offset','GN0','N_FCS','GN0','rxy','rz','D']
def decide_which_to_show(int_obj):
	
	for art in int_obj.objId_sel.param:
		if int_obj.objId_sel.param[art]['to_show'] == True:
			int_obj.objId_sel.param[art]['to_show'] = False
	int_obj.objId_sel.param[ 'offset']['to_show'] = True
	int_obj.objId_sel.param[ 'GN0']['to_show'] = True
	int_obj.objId_sel.param['Y']['to_show'] = True
	

	int_obj.def_options['Diff_species'] = int_obj.diffNumSpecSpin.value()
	int_obj.def_options['Triplet_species'] =int_obj.tripNumSpecSpin.value()

	for i in range(1,int_obj.def_options['Diff_species']+1):
		int_obj.objId_sel.param['A'+str(i)]['to_show'] = True
		int_obj.objId_sel.param['tdiff'+str(i)]['to_show'] = True


	if int_obj.def_options['Triplet_eq'] == 2:
			#Triplet State equation1
			for i in range(1,int_obj.tripNumSpecSpin.value()+1):			 
				int_obj.objId_sel.param['B'+str(i)]['to_show'] = True
				int_obj.objId_sel.param['tauT'+str(i)]['to_show'] = True
				
	if int_obj.def_options['Triplet_eq'] == 3:
			#Triplet State equation2
			for i in range(1,int_obj.tripNumSpecSpin.value()+1):
				int_obj.objId_sel.param['T'+str(i)]['to_show'] = True
				int_obj.objId_sel.param['tauT'+str(i)]['to_show'] = True
	
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
	try:
		objId.param['N_FCS']['value'] = 1/objId.param['GN0']['value']
		objId.param['N_FCS']['to_show'] = True
	except:
		objId.param['N_FCS']['value'] = 1
		objId.param['N_FCS']['to_show'] = False

def equation_(param,tc,options):


	offset =param['offset'].value; 
	GN0 =param['GN0'].value; 
	Y = param['Y'].value;
	

	k = (0.689 + 0.34*np.exp(-0.37*(Y-0.5)**2))

	if(options['Triplet_eq'] ==1):
		#For no triplets.
		GT = 1
	elif(options['Triplet_eq'] ==2):
		#Equation (2) 1st equation.
		if (options['Triplet_species'] == 1):
			B1 = param['B1'].value;tauT1 = param['tauT1'].value;
			#For one dark state.
			GT = 1 + (B1*np.exp(-tc/tauT1))
		elif (options['Triplet_species'] == 2):
			B1 = param['B1'].value;tauT1 = param['tauT1'].value;
			B2 = param['B2'].value;tauT2 = param['tauT2'].value;
			#For two dark state
			GT = 1 + (B1*np.exp(-tc/tauT1))+(B2*np.exp(-tc/tauT2))
		elif (options['Triplet_species'] == 3):
			B1 = param['B1'].value;tauT1 = param['tauT1'].value;
			B2 = param['B2'].value;tauT2 = param['tauT2'].value;
			B3 = param['B3'].value;tauT3 = param['tauT3'].value;
			#For three dark state
			GT = 1 + (B1*np.exp(-tc/tauT1))+(B2*np.exp(-tc/tauT2))+(B3*np.exp(-tc/tauT3))
	
	elif(options['Triplet_eq'] ==3):       
		#Equation (2) 2nd equation.
		if (options['Triplet_species'] == 1):
			T1 = param['T1'].value;tauT1 = param['tauT1'].value;
			#For one dark state.
			GT = 1- T1 + (T1*np.exp(-tc/tauT1))
		elif (options['Triplet_species'] == 2):
			T1 = param['T1'].value;tauT1 = param['tauT1'].value;
			T1 = param['T2'].value;tauT1 = param['tauT2'].value;
			#For two dark state.
			GT = 1- (T1+T2 )+ ((T1*np.exp(-tc/tauT1))+(T2*np.exp(-tc/tauT2)))
		elif (options['Triplet_species'] == 3):
			T1 = param['T1'].value;tauT1 = param['tauT1'].value;
			T2 = param['T2'].value;tauT1 = param['tauT2'].value;
			T3 = param['T3'].value;tauT1 = param['tauT3'].value;
			#For three dark state.
			GT = 1- (T1+T2+T3)+ ((T1*np.exp(-tc/tauT1))+(T2*np.exp(-tc/tauT2))+(T3*np.exp(-tc/tauT3)))
	
	
	if (options['Diff_species'] == 1):
		A1 = param['A1'].value; tdiff1 = param['tdiff1'].value;

		gy1 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2) *tc/tdiff1)/(np.sqrt(1+tc/tdiff1))))
		gx1 = 1/np.sqrt(1+tc/tdiff1)
		
		GDiff = A1*gy1*gx1
	if (options['Diff_species'] == 2):
		A1 = param['A1'].value; tdiff1 = param['tdiff1'].value;
		A2 = param['A2'].value; tdiff2 = param['tdiff2'].value;

		param['A2'].value = 1.0-A1
		A2 = param['A2'].value

		gy1 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2) *tc/tdiff1)/(np.sqrt(1+tc/tdiff1))))
		gx1 = 1/np.sqrt(1+tc/tdiff1)
		gy2 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2) *tc/tdiff2)/(np.sqrt(1+tc/tdiff2))))
		gx2 = 1/np.sqrt(1+tc/tdiff2)

		GDiff = A1*gy1*gx1 + A2*gy2*gx2
	if (options['Diff_species'] == 3):
		A1 = param['A1'].value; tdiff1 = param['tdiff1'].value;
		A2 = param['A2'].value; tdiff2 = param['tdiff2'].value;
		A3 = param['A3'].value; tdiff3 = param['tdiff3'].value;

		param['A2'].value = 1.0-A1-A3
		A2 = param['A2'].value
		param['A3'].value = 1.0-A2-A1
		A3 = param['A3'].value
		

		gy1 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2)*tc/tdiff1)/(np.sqrt(1+tc/tdiff1))))
		gx1 = 1/np.sqrt(1+tc/tdiff1)
		gy2 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2)*tc/tdiff2)/(np.sqrt(1+tc/tdiff2))))
		gx2 = 1/np.sqrt(1+tc/tdiff2)
		gy3 = (np.sqrt(np.pi)/Y)*(1 + ((Y/np.sqrt(np.pi))*(erf(Y)/erf(Y/np.sqrt(2))**2)-1)*((np.exp(-k*(np.pi/Y)**2)*tc/tdiff3)/(np.sqrt(1+tc/tdiff3))))
		gx3 = 1/np.sqrt(1+tc/tdiff3)

		GDiff = A1*gy1*gx1 + A2*gy2*gx2 + A3*gy3*gx3

			

	return offset + (GN0* GT*GDiff)