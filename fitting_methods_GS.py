def initialise_fcs(int_obj):
	int_obj.def_options = {}
	int_obj.def_options['Diff_eq'] = 3

	offset = { 'alias':'offset','value':0.01,'minv':-0.5,'maxv':1.5,'vary':True,'to_show':True,'calc':False}
	N_FCS = {'alias':'N (FCS)','value':0.0,'minv':0.001,'maxv':1000.0,'vary':True,'to_show':True,'calc':True}
	GN0 = {'alias':'GN0','minv':0.001,'value':1,'maxv':1.0,'vary':True,'to_show':True,'calc':False}
	rxy = {'alias':'rxy','value':0.01,'minv':0.001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}
	rz = {'alias':'rz','value':0.01,'minv':0.001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}
	D=  {'alias':'D','value':0.01,'minv':0.0001,'maxv':2000.0,'vary':True,'to_show':True,'calc':False}

	int_obj.def_param = {'offset':offset,'N_FCS':N_FCS,'GN0':GN0,'rxy':rxy,'rz':rz,'D':D}
	int_obj.order_list = ['offset','GN0','N_FCS','GN0','rxy','rz','D']
def decide_which_to_show(int_obj):
	
	for art in int_obj.objId_sel.param:
		if int_obj.objId_sel.param[art]['to_show'] == True:
			int_obj.objId_sel.param[art]['to_show'] = False
	int_obj.objId_sel.param[ 'offset']['to_show'] = True
	int_obj.objId_sel.param[ 'GN0']['to_show'] = True
	int_obj.objId_sel.param[ 'rxy']['to_show'] = True
	int_obj.objId_sel.param[ 'rz']['to_show'] = True
	int_obj.objId_sel.param[ 'D']['to_show'] = True
	
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
	rxy = param['rxy'].value; 
	rz =param['rz'].value; 
	D =param['D'].value; 

	GDiff = (1/(np.sqrt(1+(4*tc/(rxy**2)))))*(1/(np.sqrt(1+(4*tc/(rxy**2)))))*(1/(np.sqrt(1+(4*tc/(rz**2)))))
			

	return offset + (GN0*GDiff)