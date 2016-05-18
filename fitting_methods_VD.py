import numpy as np
import copy
from scipy import special as sp
def initialise_fcs(int_obj):
	
	GN0 = {'alias':'GN0','minv':0.001,'value':1,'maxv':1.0,'vary':True,'to_show':True,'calc':False}
	ves_radius = { 'alias':'Ves. radius','value':0.01,'minv':0.00001,'maxv':10.0,'vary':True,'to_show':True,'calc':False}
	D = {'alias':'D','value':0.01,'minv':0.00001,'maxv':10.0,'vary':True,'to_show':True,'calc':False}
	FWHM = {'alias':'FWHM','value':0.01,'minv':0.00001,'maxv':10.0,'vary':True,'to_show':True,'calc':False}
	offset = { 'alias':'offset','value':0.01,'minv':-0.5,'maxv':1.5,'vary':True,'to_show':True,'calc':False}

	int_obj.def_param['GN0'] = GN0
	int_obj.def_param['ves_radius'] = ves_radius
	int_obj.def_param['D'] = D
	int_obj.def_param['FWHM'] = FWHM
	int_obj.def_param['offset'] = offset
	
	#int_obj.order_list = ['alpha','dif']
def decide_which_to_show(int_obj):
	
	for art in int_obj.objId_sel.param:
		if int_obj.objId_sel.param[art]['to_show'] == True:
			int_obj.objId_sel.param[art]['to_show'] = False
	int_obj.objId_sel.param['ves_radius']['to_show'] = True
	int_obj.objId_sel.param['D']['to_show'] = True
	int_obj.objId_sel.param['FWHM']['to_show'] = True
	
	
	int_obj.objId_sel.param[ 'offset']['to_show'] = True
	int_obj.objId_sel.param[ 'GN0']['to_show'] = True
	
	
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
def lgwt(N, a, b):
    
    N = N-1
    N1 = N+1
    N2 = N+2
    
    xu = np.linspace(-1,1,N1)
    
    y = np.cos((2*np.arange(0,N+1).T+1)*np.pi/(2*N+2))+(0.27/N1)*np.sin(np.pi*xu*N/N2)
    
    L= np.zeros((N1,N2+1))
    Lp = np.zeros((N1,N2+1))
    
    y0 =2
    
    while np.max(abs(y-y0))>2.2204e-16:
        L[:,0] = 1.0
        Lp[:,0] = 0.0
        L[:,1] = y
        Lp[:,1] =1.0
        for k in range(2,N1+1):
            
            L[:,k] = (((2*k-1))*y*L[:,k-1]-(k-1)*L[:,k-2])/k
            
        #print 'L',np.sum(L)
        #print "L",L.shape
        
        Lp = N2*(L[:,N1-1]-y*L[:,N2-1])/(1.0-y**2).astype(np.float32)
        
        y0 = np.array(y)
        y = y0-L[:,N2]/Lp
    
    
        
    x = (a*(1-y)+b*(1+y))/2
    w = (b-a)/((1-y**2)*Lp**2)*(N2/N1)**2
    
    return x, w
def VesicleDiffusion(t,alpha,dif):
    nn = 100
    x,weight = lgwt(4*nn,-1.0,1.0)
    
    leg = np.zeros((nn,x.shape[0]))
    for r in range(1,nn+1):
        tmp = sp.legendre(r-1)(np.round(x,4))
        
        leg[r-1,:] = tmp
    
    
    
    weight = np.exp(alpha*x**2)*weight
    y = np.zeros((t.shape))
    nrm = 0
    for j in range(0,nn):
        fac = (2*j+1)*(np.dot(leg[j,:],weight))**2
        
        y = y + fac*np.exp(-dif*j*(j+1)*t)
        nrm = nrm + fac
    y = y/nrm
    return y


def equation_(param,tc,options):


	a =param['ves_radius'].value; 
	D =param['D'].value;
	offset =param['offset'].value; 
	GN0 =param['GN0'].value; 
	FWHM =param['FWHM'].value;

	sig = FWHM/(2*np.sqrt(2*np.log(2)))
	
	alpha = (a/(sig))**2/2
	diff = D/(a**2)

	y = VesicleDiffusion(tc,alpha,diff)
	return GN0*y+ offset