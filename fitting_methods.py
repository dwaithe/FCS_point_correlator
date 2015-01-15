
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

def equation_(param, tc,options):
	"""This is equation for fitting"""
	#A1 is relative component of fluorescent species
	#tc is tau.
	#txy1 is xy difusion   for fluorescent species one.
	#alpha1 is
	#tz1 is z diffusion for fluorescent species one.
	DC =param['DC'].value; 
	GN0 =param['GN0'].value; 
	
	
	if(options['Dimen'] == 2):
		if(options['Diff_eq']==1):
			#Equation 1A with 3D term.
			if (options['Diff_species'] == 1):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;tz1 = param['tz1'].value;
				#For one diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*((1+(tc/tz1))**-0.5)))
			elif (options['Diff_species'] == 2):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;tz1 = param['tz1'].value;
				A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;tz2 = param['tz2'].value;
				param['A2'].value = 1.0-A1
				A2 = param['A2'].value
				#For two diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*((1+(tc/tz1))**-0.5)))+ (A2*(((1+((tc/txy2)**alpha2))**-1)*((1+(tc/tz2))**-0.5)))
			elif (options['Diff_species'] == 3):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;tz1 = param['tz1'].value;
				A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;tz2 = param['tz2'].value;
				A3 = param['A3'].value; txy3 = param['txy3'].value; alpha3 = param['alpha3'].value;tz3 = param['tz3'].value;
				param['A2'].value = 1.0-A1-A3
				A2 = param['A2'].value
				param['A3'].value = 1.0-A2-A1
				A3 = param['A3'].value
				#For three diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*((1+(tc/tz1))**-0.5)))+ (A2*(((1+((tc/txy2)**alpha2))**-1)*((1+(tc/tz2))**-0.5)))+ (A3*(((1+((tc/txy3)**alpha3))**-1)*((1+(tc/tz3))**-0.5)))
		elif(options['Diff_eq']==2):
			if (options['Diff_species'] == 1):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;AR1 = param['AR1'].value;
				#For one diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*(((1+(tc/((AR1**2)*txy1)))**-0.5))))
			elif (options['Diff_species'] == 2):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;AR1 = param['AR1'].value;
				A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;AR2 = param['AR2'].value;
				param['A2'].value = 1.0-A1
				A2 = param['A2'].value
				#For two diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*(((1+(tc/((AR1**2)*txy1)))**-0.5))))+(A2*(((1+((tc/txy2)**alpha2))**-1)*(((1+(tc/((AR2**2)*txy2)))**-0.5))))
			elif (options['Diff_species'] == 3):
				A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;AR1 = param['AR1'].value;
				A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;AR2 = param['AR2'].value;
				A3 = param['A3'].value; txy3 = param['txy3'].value; alpha3 = param['alpha3'].value;AR3 = param['AR3'].value;
				#For two diffusing species
				param['A2'].value = 1.0-A1-A3
				A2 = param['A2'].value
				param['A3'].value = 1.0-A2-A1
				A3 = param['A3'].value
				#For three diffusing species
				GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*(((1+(tc/((AR1**2)*txy1)))**-0.5))))+(A2*(((1+((tc/txy2)**alpha2))**-1)*(((1+(tc/((AR2**2)*txy2)))**-0.5))))+(A3*(((1+((tc/txy3)**alpha3))**-1)*(((1+(tc/((AR3**2)*txy3)))**-0.5))))
																														   
	if(options['Dimen'] == 1):
		#Equation 1A with 2D term.
		if (options['Diff_species'] == 1):
			A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;
			#For one diffusing species
			GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)))
		elif (options['Diff_species'] == 2):
			A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;
			A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;
			#For two diffusing species

			param['A2'].value = 1.0-A1
			A2 = param['A2'].value

			GDiff = (A1*(((1+(tc/txy1)**alpha1)**-1)))+(A2*(((1+(tc/txy2)**alpha2)**-1)))

			#if A1 +A2 != 1.0:
			#    GDiff = 99999999999
		elif (options['Diff_species'] == 3):
			A1 = param['A1'].value; txy1 = param['txy1'].value; alpha1 = param['alpha1'].value;
			A2 = param['A2'].value; txy2 = param['txy2'].value; alpha2 = param['alpha2'].value;
			A3 = param['A3'].value; txy3 = param['txy3'].value; alpha3 = param['alpha3'].value;
			#For two diffusing species
			param['A2'].value = 1.0-A1-A3
			A2 = param['A2'].value
			param['A3'].value = 1.0-A2-A1
			A3 = param['A3'].value
			#For three diffusing species
			GDiff = (A1*(((1+(tc/txy1)**alpha1)**-1)))+(A2*(((1+(tc/txy2)**alpha2)**-1)))+(A3*(((1+(tc/txy3)**alpha3)**-1)))
	
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
			
	return DC + (GN0*GDiff*GT)