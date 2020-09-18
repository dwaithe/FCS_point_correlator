
from focuspoint.fitting_methods import fitting_methods_SE as SE
from focuspoint.fitting_methods import fitting_methods_GS as GS
from focuspoint.correlation_objects import corrObject
import csv
import numpy as np
import copy
def fcs_import_method(fit_obj,file_path):
	text =[0]
	r_obj = csv.reader(open(file_path, 'r'),delimiter='\t')
	title = next(r_obj)
	line = next(r_obj) 
	line = next(r_obj)
	
	read = True
	ind = 0
	channelnum =0
	while  read == True:
		
		corrObj = corrObject(file_path,fit_obj);
		
		line = next(r_obj)
		text =[]
		for part in line:
			if part != '':
					text.append(part)


		while  text[0].split(' = ')[0] != 'CountRateArray':

			if text[0].split(' = ')[0] == 'Channel':
				channel_str = text[0].split(' = ')[1]
				channel = np.copy(channelnum)
				if channel_str[0:25] == 'Auto-correlation detector':
					
					if channelnum == 0: 
						name = 'CH0'
					if channelnum == 1:
						name = 'CH1'
				elif channel_str[0:26] == 'Cross-correlation detector':
					
					if channelnum == 2: 
						name = 'CH10'
					if channelnum == 3: 
						name = 'CH01'
				channelnum += 1
				
			try:
				line = next(r_obj)
			except:
				read = False
				break
				

			text =[]
			for part in line:
				if part != '':
					text.append(part)
		
		if read == False:
			break
		line = next(r_obj)
		
		dimensions = text[0].split(' = ')[1]
		len_of_seq = int(dimensions.split(' ')[0])

		if len_of_seq >0:
			cdata = []
			cscale = []
			
			for v in range(0,len_of_seq):

				text =[]
				for part in line:
					if part != '':
						text.append(part)
				if text.__len__() >1:
					cscale.append(float(text[0]))
					cdata.append(float(text[1]))

				line = next(r_obj)
		

		#Reads to first correlation array text.
		while  text[0].split(' = ')[0] != 'CorrelationArray':
			try:
				line = next(r_obj)
			except:
				break
				read = False

			text =[]
			for part in line:
				if part != '':
					text.append(part)
		
		
		dimensions = text[0].split(' = ')[1]
		len_of_seq = int(dimensions.split(' ')[0])
		if len_of_seq >0:
			tdata = []
			tscale = []
			line = next(r_obj)
			for v in range(0,len_of_seq):

				text =[]
				for part in line:
					if part != '':
						text.append(part)
				if text.__len__() >1:
					tscale.append(float(text[0]))
					tdata.append(float(text[1]))

				line = next(r_obj)

			
			fit_obj.objIdArr.append(corrObj)
			
			corrObj.name = corrObj.name+'_'+str(ind)+'_'+str(name)
			corrObj.parent_name = '.fcs files'
			corrObj.parent_uqid = '0'
			corrObj.siblings = None
			corrObj.autoNorm = np.array(tdata).astype(np.float64).reshape(-1)
			corrObj.autotime = np.array(tscale).astype(np.float64).reshape(-1)*1000
			

			#Average counts per bin. For it to be seconds (Hz), we have cscale-1 because the first value corresponds to zero recording time.
			unit = cscale[-1]/(cscale.__len__()-1)
			
			#must divide by duration (in seconds).And to be in kHz we divide by 1000. 
			corrObj.kcount = np.average(np.array(cdata)/unit)/1000
			
			corrObj.ch_type = channel;
			corrObj.param = copy.deepcopy(fit_obj.def_param)
			corrObj.calculate_suitability()
			#if fit_obj.diffModEqSel.currentIndex()+1 == 3:
			#	GS.calc_param_fcs(fit_obj,corrObj)
			#else:
		#		SE.calc_param_fcs(fit_obj,corrObj)

			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj)
			else:
				SE.calc_param_fcs(fit_obj,corrObj)
		
def sin_import_method(fit_obj,file_path):
		tscale = [];
		tdata = [];
		tdata2 = [];
		tdata3 = [];
		tdata4 = [];
		int_tscale =[];
		int_tdata = [];
		int_tdata2 = [];
		
		
		proceed = False
		
		for line in csv.reader(open(file_path, 'r'),delimiter='\t'):
			
			if proceed =='correlated':
				if line ==[]:
					proceed =False;
				else:
					tscale.append(float(line[0]))
					tdata.append(float(line[1]))
					if line.__len__()>2:
						tdata2.append(float(line[2]))
					if line.__len__()>3:
						tdata3.append(float(line[3]))
					if line.__len__()>4:
						tdata4.append(float(line[4]))
			if proceed =='intensity':
				
				if line ==[]:
					proceed=False;
				elif line.__len__()> 1:
					
					int_tscale.append(float(line[0]))
					int_tdata.append(float(line[1]))
					if line.__len__()>2:
						int_tdata2.append(float(line[2]))
					
			if (str(line)  == "[\'[CorrelationFunction]\']"):
				proceed = 'correlated';
			elif (str(line)  == "[\'[IntensityHistory]\']"):
				proceed = 'intensity';
			
			
		
		corrObj1 = corrObject(file_path,fit_obj)
		corrObj1.siblings = None
		corrObj1.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
		corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
		
		corrObj1.name = corrObj1.name+'-CH0'
		corrObj1.parent_name = '.sin files'
		corrObj1.parent_uqid = '0'
					
					
		corrObj1.ch_type = 0;
		#Average counts per bin. Apparently they are normalised to time.
		unit = int_tscale[-1]/(int_tscale.__len__()-1)
		#And to be in kHz we divide by 1000.
		corrObj1.kcount = np.average(np.array(int_tdata))/1000
		corrObj1.param = copy.deepcopy(fit_obj.def_param)
		corrObj1.calculate_suitability()

		if fit_obj.def_options['Diff_eq'] == 4: 
			VD.calc_param_fcs(fit_obj,corrObj1)
		elif fit_obj.def_options['Diff_eq'] == 3: 
			GS.calc_param_fcs(fit_obj,corrObj1)
		else:
			SE.calc_param_fcs(fit_obj,corrObj1)

		fit_obj.objIdArr.append(corrObj1)

		#Basic 
		if tdata2 !=[]:
			corrObj2 = corrObject(file_path,fit_obj)
			corrObj2.autoNorm= np.array(tdata2).astype(np.float64).reshape(-1)
			corrObj2.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
			
			corrObj2.name = corrObj2.name+'-CH1'
			corrObj2.parent_name = '.sin files'
			corrObj2.parent_uqid = '0'
			corrObj2.ch_type = 1;
	
			#And to be in kHz we divide by 1000.
			corrObj2.kcount = np.average(np.array(int_tdata2))/1000
			corrObj2.param = copy.deepcopy(fit_obj.def_param)

			corrObj1.siblings = [corrObj2]
			corrObj2.siblings = [corrObj1]
			
			corrObj2.calculate_suitability()
			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj2)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj2)
			else:
				SE.calc_param_fcs(fit_obj,corrObj2)
			fit_obj.objIdArr.append(corrObj2)
		if tdata3 !=[]:
			corrObj3 = corrObject(file_path,fit_obj)
			corrObj3.autoNorm= np.array(tdata3).astype(np.float64).reshape(-1)
			corrObj3.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
			
			corrObj3.ch_type = 2;
			corrObj3.name = corrObj3.name+'-CH10'
			corrObj3.parent_name = '.sin files'
			corrObj3.parent_uqid = '0'
			
	
			#And to be in kHz we divide by 1000.
			#corrObj3.kcount = np.average(np.array(int_tdata3)/unit)/1000
			corrObj3.param = copy.deepcopy(fit_obj.def_param)

			corrObj1.siblings = [corrObj2,corrObj3]
			corrObj2.siblings = [corrObj1,corrObj3]
			corrObj3.siblings = [corrObj1,corrObj2]
			
			corrObj3.calculate_suitability()
			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj3)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj3)
			else:
				SE.calc_param_fcs(fit_obj,corrObj3)
			fit_obj.objIdArr.append(corrObj3)
		if tdata4 !=[]:
			corrObj4 = corrObject(file_path,fit_obj)
			corrObj4.autoNorm= np.array(tdata4).astype(np.float64).reshape(-1)
			corrObj4.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
			
			corrObj4.ch_type = 3;
			corrObj4.name = corrObj4.name+'-CH01'
			corrObj4.parent_name = '.sin files'
			corrObj4.parent_uqid = '0'
			
	
			#And to be in kHz we divide by 1000.
			#corrObj4.kcount = np.average(np.array(int_tdata4)/unit)/1000
			corrObj4.param = copy.deepcopy(fit_obj.def_param)

			corrObj1.siblings = [corrObj2,corrObj3,corrObj4]
			corrObj2.siblings = [corrObj1,corrObj3,corrObj4]
			corrObj3.siblings = [corrObj1,corrObj2,corrObj4]
			corrObj4.siblings = [corrObj1,corrObj2,corrObj3]
			
			corrObj4.calculate_suitability()
			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj4)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj4)
			else:
				SE.calc_param_fcs(fit_obj,corrObj4)
			fit_obj.objIdArr.append(corrObj4)


	
def csv_import_method(fit_obj,file_path):
			r_obj = csv.reader(open(str(file_path), 'r'))
			line_one = next(r_obj)
			if line_one.__len__()>1:
				
					if float(line_one[1]) == 2:
						
						version = 2
					else:
						print('version not known:',line_one[1])
					
				
			else:
				version = 1

			corrObj1 = corrObject(file_path,fit_obj);

			if version == 1:
				fit_obj.objIdArr.append(corrObj1)
				
				c = 0
				
				for line in csv.reader(open(file_path, 'rb')):
					if (c >0):
						tscale.append(line[0])
						tdata.append(line[1])
					c +=1;

				corrObj1.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
				corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)
				corrObj1.calculate_suitability()
				corrObj1.name = corrObj1.name+'-CH'+str(0)
				corrObj1.ch_type = 0
				corrObj1.datalen= len(tdata)

				corrObj1.param = copy.deepcopy(fit_obj.def_param)
				fit_obj.fill_series_list()
			if version >= 2:
				
					
				numOfCH = float(next(r_obj)[1])
				
				if numOfCH == 1:
					fit_obj.objIdArr.append(corrObj1)
					corrObj1.type =str(next(r_obj)[1])
					corrObj1.ch_type = int(next(r_obj)[1])
					corrObj1.name = corrObj1.name+'-CH'+str(corrObj1.ch_type)
					corrObj1.parent_name = 'no name'
					corrObj1.parent_uqid = '0'
					
					line = next(r_obj)

					while  line[0] != 'Time (ns)':
						if line[0] == 'kcount':
							corrObj1.kcount = float(line[1])
						if line[0] == 'numberNandB':
							corrObj1.numberNandB = float(line[1])
						if line[0] == 'brightnessNandB':
							corrObj1.brightnessNandB =  float(line[1])
						if line[0] == 'CV':
							corrObj1.CV =  float(line[1])
						if line[0] == 'carpet pos':
							carpet = int(line[1])
						if line[0] == 'pc':
							pc_text = int(line[1])
						if line[0] == 'pbc_f0':
							corrObj1.pbc_f0 = float(line[1])
						if line[0] == 'pbc_tb':
							corrObj1.pbc_tb = float(line[1])
						if line[0] == 'parent_name':
							corrObj1.parent_name = str(line[1])
						if line[0] == 'parent_uqid':
							corrObj1.parent_uqid = str(line[1])
						
						line = next(r_obj)

					
					if pc_text != False:
						corrObj1.name = corrObj1.name +'_pc_m'+str(pc_text)
						
					
					tscale = []
					tdata = []

					#null = next(r_obj)
					

					line = next(r_obj)
					
					while  line[0] != 'end':

						tscale.append(line[0])
						tdata.append(line[1])
						line = next(r_obj)

					corrObj1.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
					corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj1.siblings = None
					corrObj1.param = copy.deepcopy(fit_obj.def_param)
					

				if numOfCH == 2:
					corrObj2 = corrObject(file_path,fit_obj);
					corrObj3 = corrObject(file_path,fit_obj);

					
					fit_obj.objIdArr.append(corrObj1)
					fit_obj.objIdArr.append(corrObj2)
					fit_obj.objIdArr.append(corrObj3)
					
					corrObj1.parent_name = 'no name'
					corrObj1.parent_uqid = '0'
					corrObj2.parent_name = 'no name'
					corrObj2.parent_uqid = '0'
					corrObj3.parent_name = 'no name'
					corrObj3.parent_uqid = '0'
					
					line_type = next(r_obj)
					corrObj1.type = str(line_type[1])
					corrObj2.type = str(line_type[1])
					corrObj3.type = str(line_type[1])
					

					line_ch = next(r_obj)
					corrObj1.ch_type = int(line_ch[1])
					corrObj2.ch_type = int(line_ch[2])
					corrObj3.ch_type = int(line_ch[3])
					
					corrObj1.name = corrObj1.name+'-CH'+str(corrObj1.ch_type)
					corrObj2.name = corrObj2.name+'-CH'+str(corrObj2.ch_type)
					corrObj3.name = corrObj3.name+'-CH'+str(corrObj3.ch_type)

					line = next(r_obj)
					while  line[0] != 'Time (ns)':
						if line[0] == 'kcount':
							corrObj1.kcount = float(line[1])
							corrObj2.kcount = float(line[2])
						if line[0] == 'numberNandB':
							corrObj1.numberNandB = float(line[1])
							corrObj2.numberNandB =  float(line[2])
						if line[0] == 'brightnessNandB':
							corrObj1.brightnessNandB =  float(line[1])
							corrObj2.brightnessNandB =  float(line[2])
						if line[0] == 'CV':
							corrObj1.CV =  float(line[1])
							corrObj2.CV = float(line[2])
							corrObj3.CV = float(line[3])
						if line[0] == 'carpet pos':
							corrObj1.carpet_position = int(line[1])
						if line[0] == 'pc':
							pc_text = int(line[1])
						if line[0] == 'pbc_f0':
							corrObj1.pbc_f0 = float(line[1])
							corrObj2.pbc_f0 = float(line[2])
						if line[0] == 'pbc_tb':
							corrObj1.pbc_tb = float(line[1])
							corrObj2.pbc_tb = float(line[2])
						if line[0] == 'parent_name':
							corrObj1.parent_name = str(line[1])
							corrObj2.parent_name = str(line[1])
							corrObj3.parent_name = str(line[1])
						if line[0] == 'parent_uqid':
							corrObj1.parent_uqid = str(line[1])
							corrObj2.parent_uqid = str(line[1])
							corrObj3.parent_uqid = str(line[1])
						print(line)
						line = next(r_obj)
					
					
					
					if pc_text != False:
						corrObj1.name = corrObj1.name +'_pc_m'+str(pc_text)
						corrObj2.name = corrObj2.name +'_pc_m'+str(pc_text)
						corrObj3.name = corrObj3.name +'_pc_m'+str(pc_text)
					
					#null = next(r_obj)
					line = next(r_obj)
					tscale = []
					tdata0 = []
					tdata1 = []
					tdata2 = []
					while  line[0] != 'end':

						tscale.append(line[0])
						tdata0.append(line[1])
						tdata1.append(line[2])
						tdata2.append(line[3])
						line = next(r_obj)

					
					corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj2.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj3.autotime= np.array(tscale).astype(np.float64).reshape(-1)

					corrObj1.autoNorm= np.array(tdata0).astype(np.float64).reshape(-1)
					corrObj2.autoNorm= np.array(tdata1).astype(np.float64).reshape(-1)
					corrObj3.autoNorm= np.array(tdata2).astype(np.float64).reshape(-1)

					
					
					corrObj1.siblings = [corrObj2,corrObj3]
					corrObj2.siblings = [corrObj1,corrObj3]
					corrObj3.siblings = [corrObj1,corrObj2]
					
					corrObj1.param = copy.deepcopy(fit_obj.def_param)
					corrObj2.param = copy.deepcopy(fit_obj.def_param)
					corrObj3.param = copy.deepcopy(fit_obj.def_param)

					corrObj1.calculate_suitability()
					corrObj2.calculate_suitability()
					corrObj3.calculate_suitability()

					SE.calc_param_fcs(fit_obj,corrObj1)
					


				






		
		


		
		
		
		

		
		
		


		
		

	