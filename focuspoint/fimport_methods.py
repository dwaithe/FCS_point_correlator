
from focuspoint.fitting_methods import fitting_methods_SE as SE
from focuspoint.fitting_methods import fitting_methods_GS as GS
from focuspoint.correlation_objects import corrObject
import csv
import numpy as np
import copy

import time
def fcs_import_method(fit_obj,file_path,feed=None):
	
	
	if feed == None:
		#f.read().decode('UTF-8','replace')
		file = open(str(file_path),'rb').read()
		fileo = file.decode('UTF-8','replace').replace("\t","").split('\n')
		r_obj = csv.reader(fileo)
	else:
		r_obj = csv.reader(feed.replace("\t","").split('\n'))

	
	
	version = next(r_obj)
	print(version)
	null = next(r_obj)
	name =  next(r_obj)[0].split(' = ')[1]

	version_num = float(version[0].split("-")[2].split(" ")[2])
	if version_num != 3.0:
		print("Version of .fcs file:",version_num," must be 3.0 to continue. Please email Dominic with file.")
		return False

	
	read = True
	ind = 0
	channelnum =0

	tdata_arr = []
	tscale_arr = []
	cdata_arr = []
	cscale_arr = []
	

	#Main loop which ends once all file is read.
	while  read == True:
		text = next(r_obj)
		while True:
			if text[0].split(' = ')[0] == 'Name':
				name2 = text[0].split(' = ')[1]
				#print('text',name2,tscale_arr.__len__())

			if text[0].split(' = ')[0] == 'Channel':
				channel_str = text[0].split(' = ')[1]

			text = next(r_obj)
			if text  ==[]:

				read = False
				break
			if  text[0].split(' = ')[0] == 'CountRateArray':
				break
			
		if read == False or text == []:
			break
	
		dimensions = text[0].split(' = ')[1]
		len_of_seq = int(dimensions.split(' ')[0])
		if len_of_seq >0:
			cdata = []
			cscale = []
			text = next(r_obj)[0].split(" ")
			for v in range(0,len_of_seq):

				
				if text.__len__() >1:
					cscale.append(float(text[0]))
					cdata.append(float(text[1]))
				text = next(r_obj)[0].split(" ")
			cdata_arr.append(cdata)
			cscale_arr.append(cscale)
		#Reads to first correlation array text.
		while  text[0].split(' = ')[0] != 'CorrelationArray':
			text = next(r_obj)


		
		dimensions = text[0].split(' = ')[1]
		len_of_seq = int(dimensions.split(' ')[0])
		if len_of_seq >0:
			tdata = []
			tscale = []
			text = next(r_obj)[0].split(" ")

			for v in range(0,len_of_seq):

				
				#print(text)
				if text.__len__() >1:
					tscale.append(float(text[0]))
					tdata.append(float(text[1]))
				
				text = next(r_obj)[0].split(" ")
			tdata_arr.append(tdata)
			tscale_arr.append(tscale)
		#This is where we find-out how many channels. Unhelpfully after the raw data.
		while  text[0].split(' = ')[0] != 'Channels':
			text = next(r_obj)


		num_of_channels = int(text[0].split(' = ')[1])

		#Which channel is it. Found by matching string found earlier?? The only way I saw to do it.
		for i in range(num_of_channels):
			text = next(r_obj)[0].split(' = ')[1]
			if text == channel_str:
				this_is_ch = i

		if len_of_seq >0:
			print('num_of_channels',num_of_channels)
			#If a four channel file we want to skip until we have collected all channels.
			if num_of_channels == 4 and tdata_arr.__len__() != 4:
				continue
				
			corrObj1 = corrObject(file_path,fit_obj)
			corrObj1.siblings = None
			corrObj1.autoNorm= np.array(tdata_arr[0]).astype(np.float64).reshape(-1)
			corrObj1.autotime= np.array(tscale_arr[0]).astype(np.float64).reshape(-1)*1000
			

			corrObj1.name = name+'-CH0'
			corrObj1.parent_name = '.fcs files'
			corrObj1.parent_uqid = '0'
						
						
			corrObj1.ch_type = 0;

			if cscale_arr != []:
				#Average counts per bin. Apparently they are already in Hz
				#And to be in kHz we divide by 1000. This we found through comparison with Zeiss software.
				corrObj1.kcount = np.average(np.array(cdata_arr[0]))/1000
			corrObj1.param = copy.deepcopy(fit_obj.def_param)
			corrObj1.calculate_suitability()
			corrObj1.max = np.max(corrObj1.autoNorm)
			corrObj1.min = np.min(corrObj1.autoNorm)
			corrObj1.tmax = np.max(corrObj1.autotime)
			corrObj1.tmin = np.min(corrObj1.autotime)


			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj1)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj1)
			else:
				SE.calc_param_fcs(fit_obj,corrObj1)

			fit_obj.objIdArr.append(corrObj1)

			
			if num_of_channels == 1:
				tscale_arr = []
				tdata_arr = []
				cscale_arr = []
				cdata_arr = []
				continue;


			if num_of_channels == 4 and tdata_arr.__len__() == 4:
				
				corrObj2 = corrObject(file_path,fit_obj)
				corrObj2.autoNorm= np.array(tdata_arr[1]).astype(np.float64).reshape(-1)
				corrObj2.autotime= np.array(tscale_arr[1]).astype(np.float64).reshape(-1)*1000
				
				corrObj2.name = name+'-CH1'
				corrObj2.parent_name = '.fcs files'
				corrObj2.parent_uqid = '0'
				corrObj2.ch_type = 1;
		

				#And to be in kHz we divide by 1000. This we found through comparison with Zeiss software.
				if cscale_arr != []:
					corrObj2.kcount = np.average(np.array(cdata_arr[1]))/1000
				
				corrObj2.param = copy.deepcopy(fit_obj.def_param)

				corrObj2.calculate_suitability()
				corrObj2.max = np.max(corrObj2.autoNorm)
				corrObj2.min = np.min(corrObj2.autoNorm)
				corrObj2.tmax = np.max(corrObj2.autotime)
				corrObj2.tmin = np.min(corrObj2.autotime)
				
				if fit_obj.def_options['Diff_eq'] == 4: 
					VD.calc_param_fcs(fit_obj,corrObj2)
				elif fit_obj.def_options['Diff_eq'] == 3: 
					GS.calc_param_fcs(fit_obj,corrObj2)
				else:
					SE.calc_param_fcs(fit_obj,corrObj2)
				
				fit_obj.objIdArr.append(corrObj2)
			
				corrObj3 = corrObject(file_path,fit_obj)
				corrObj3.autoNorm= np.array(tdata_arr[2]).astype(np.float64).reshape(-1)
				corrObj3.autotime= np.array(tscale_arr[2]).astype(np.float64).reshape(-1)*1000
				
				corrObj3.ch_type = 2;
				corrObj3.name = name+'-CH01'
				corrObj3.parent_name = '.fcs files'
				corrObj3.parent_uqid = '0'
				
		
				#And to be in kHz we divide by 1000.
				#corrObj3.kcount = np.average(np.array(int_tdata3)/unit)/1000
				corrObj3.param = copy.deepcopy(fit_obj.def_param)

			
				
				corrObj3.calculate_suitability()
				corrObj3.max = np.max(corrObj3.autoNorm)
				corrObj3.min = np.min(corrObj3.autoNorm)
				corrObj3.tmax = np.max(corrObj3.autotime)
				corrObj3.tmin = np.min(corrObj3.autotime)
				if fit_obj.def_options['Diff_eq'] == 4: 
					VD.calc_param_fcs(fit_obj,corrObj3)
				elif fit_obj.def_options['Diff_eq'] == 3: 
					GS.calc_param_fcs(fit_obj,corrObj3)
				else:
					SE.calc_param_fcs(fit_obj,corrObj3)
				fit_obj.objIdArr.append(corrObj3)
				

				corrObj4 = corrObject(file_path,fit_obj)
				corrObj4.autoNorm= np.array(tdata_arr[3]).astype(np.float64).reshape(-1)
				corrObj4.autotime= np.array(tscale_arr[3]).astype(np.float64).reshape(-1)*1000
				
				corrObj4.ch_type = 3;
				corrObj4.name = name+'-CH10'
				corrObj4.parent_name = '.fcs files'
				corrObj4.parent_uqid = '0'
				
		
				#And to be in kHz we divide by 1000.
				#corrObj4.kcount = np.average(np.array(int_tdata4)/unit)/1000
				corrObj4.param = copy.deepcopy(fit_obj.def_param)

				corrObj1.siblings = [corrObj2,corrObj3,corrObj4]
				corrObj2.siblings = [corrObj1,corrObj3,corrObj4]
				corrObj3.siblings = [corrObj1,corrObj2,corrObj4]
				corrObj4.siblings = [corrObj1,corrObj2,corrObj3]
				
				corrObj4.calculate_suitability()
				corrObj4.max = np.max(corrObj4.autoNorm)
				corrObj4.min = np.min(corrObj4.autoNorm)
				corrObj4.tmax = np.max(corrObj4.autotime)
				corrObj4.tmin = np.min(corrObj4.autotime)
				
				if fit_obj.def_options['Diff_eq'] == 4: 
					VD.calc_param_fcs(fit_obj,corrObj4)
				elif fit_obj.def_options['Diff_eq'] == 3: 
					GS.calc_param_fcs(fit_obj,corrObj4)
				else:
					SE.calc_param_fcs(fit_obj,corrObj4)
				fit_obj.objIdArr.append(corrObj4)


				tscale_arr = []
				tdata_arr = []
				cscale_arr = []
				cdata_arr = []
		


	

#for i in range():
#	corrObj.name = corrObj.name+'_'+str(ind)+'_'+str(name)
		
def sin_import_method(fit_obj,file_path,feed=None):

		if feed == None:
				r_obj = csv.reader(open(str(file_path)) ,delimiter='\t')
		else:
				r_obj = csv.reader(feed.split('\n'), delimiter='\t')
		tscale = [];
		tdata = [];
		tdata2 = [];
		tdata3 = [];
		tdata4 = [];
		int_tscale =[];
		int_tdata = [];
		int_tdata2 = [];

		
		
		proceed = False
		
		for line in r_obj:
			
			if proceed =='correlated':
				if line ==[]:
					proceed =False
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
					proceed=False
				elif line.__len__()> 1:
					
					int_tscale.append(float(line[0]))
					int_tdata.append(float(line[1]))
					if line.__len__()>2:
						int_tdata2.append(float(line[2]))
					
			if (str(line)  == "[\'[CorrelationFunction]\']"):
				proceed = 'correlated'
			elif (str(line)  == "[\'[IntensityHistory]\']"):
				proceed = 'intensity'
			
			
		
		corrObj1 = corrObject(file_path,fit_obj)
		corrObj1.siblings = None
		corrObj1.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
		corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
		
		corrObj1.name = corrObj1.name+'-CH0'
		corrObj1.parent_name = '.sin files'
		corrObj1.parent_uqid = '0'
					
					
		corrObj1.ch_type = 0
		#Average counts per bin. Apparently they are normalised to time.
		unit = int_tscale[-1]/(int_tscale.__len__()-1)
		#And to be in kHz we divide by 1000.
		corrObj1.kcount = np.average(np.array(int_tdata))/1000
		corrObj1.param = copy.deepcopy(fit_obj.def_param)
		corrObj1.calculate_suitability()
		corrObj1.max = np.max(corrObj1.autoNorm)
		corrObj1.min = np.min(corrObj1.autoNorm)
		corrObj1.tmax = np.max(corrObj1.autotime)
		corrObj1.tmin = np.min(corrObj1.autotime)


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
			corrObj2.ch_type = 1
	
			#And to be in kHz we divide by 1000.
			corrObj2.kcount = np.average(np.array(int_tdata2))/1000
			corrObj2.param = copy.deepcopy(fit_obj.def_param)

			corrObj1.siblings = [corrObj2]
			corrObj2.siblings = [corrObj1]


			
			corrObj2.calculate_suitability()
			corrObj2.max = np.max(corrObj2.autoNorm)
			corrObj2.min = np.min(corrObj2.autoNorm)
			corrObj2.tmax = np.max(corrObj2.autotime)
			corrObj2.tmin = np.min(corrObj2.autotime)
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
			corrObj3.name = corrObj3.name+'-CH01'

			corrObj3.parent_name = '.sin files'
			corrObj3.parent_uqid = '0'
			
	
			#And to be in kHz we divide by 1000.
			#corrObj3.kcount = np.average(np.array(int_tdata3)/unit)/1000
			corrObj3.param = copy.deepcopy(fit_obj.def_param)

			corrObj1.siblings = [corrObj2,corrObj3]
			corrObj2.siblings = [corrObj1,corrObj3]
			corrObj3.siblings = [corrObj1,corrObj2]
			
			corrObj3.calculate_suitability()
			corrObj3.max = np.max(corrObj3.autoNorm)
			corrObj3.min = np.min(corrObj3.autoNorm)
			corrObj3.tmax = np.max(corrObj3.autotime)
			corrObj3.tmin = np.min(corrObj3.autotime)
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
			corrObj4.name = corrObj4.name+'-CH10'

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
			corrObj4.max = np.max(corrObj4.autoNorm)
			corrObj4.min = np.min(corrObj4.autoNorm)
			corrObj4.tmax = np.max(corrObj4.autotime)
			corrObj4.tmin = np.min(corrObj4.autotime)
			if fit_obj.def_options['Diff_eq'] == 4: 
				VD.calc_param_fcs(fit_obj,corrObj4)
			elif fit_obj.def_options['Diff_eq'] == 3: 
				GS.calc_param_fcs(fit_obj,corrObj4)
			else:
				SE.calc_param_fcs(fit_obj,corrObj4)
			fit_obj.objIdArr.append(corrObj4)


	

def csv_import_method(fit_obj,file_path, feed = None):
			if feed == None:
				r_obj = csv.reader(open(str(file_path), 'r'))
			else:
				r_obj = csv.reader(feed.split('\n'), delimiter=',')
				

			line_one = next(r_obj)
			if line_one.__len__()>1:
				
					if float(line_one[1]) == 2:
						version = 2
					elif float(line_one[1]) == 3:
						version = 3
					else:
						print('version not known:',line_one[1])
					
				
			else:
				version = 1

			corrObj1 = corrObject(file_path,fit_obj)

			if version == 1:
				fit_obj.objIdArr.append(corrObj1)
				
				c = 0

				tscale = []
				tdata = []
				
				for line in csv.reader(open(file_path, 'r')):
					if (c >0):
						tscale.append(line[0])
						tdata.append(line[1])
					c +=1

				corrObj1.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
				corrObj1.autotime= np.array(tscale).astype(np.float64).reshape(-1)
				corrObj1.max = np.max(corrObj1.autoNorm)
				corrObj1.min = np.min(corrObj1.autoNorm)
				corrObj1.calculate_suitability()
				corrObj1.name = corrObj1.name+'-CH'+str(0)
				corrObj1.ch_type = 0
				corrObj1.datalen= len(tdata)

				corrObj1.param = copy.deepcopy(fit_obj.def_param)
				fit_obj.fill_series_list()
			if version == 2:
				
					
				numOfCH = float(next(r_obj)[1])
				
				if numOfCH == 1:
					fit_obj.objIdArr.append(corrObj1)
					corrObj1.type =str(next(r_obj)[1])
					corrObj1.ch_type = int(next(r_obj)[1])
					corrObj1.name = corrObj1.name+'-CH'+str(corrObj1.ch_type)
					corrObj1.parent_name = 'no name'
					corrObj1.parent_uqid = '0'
					
					line = next(r_obj)

					while  line[0][:4] != 'Time':
						
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
					corrObj1.max = np.max(corrObj1.autoNorm)
					corrObj1.min = np.min(corrObj1.autoNorm)
					corrObj1.tmax = np.max(corrObj1.autotime)
					corrObj1.tmin = np.min(corrObj1.autotime)
					
					corrObj1.siblings = None
					corrObj1.param = copy.deepcopy(fit_obj.def_param)

				elif numOfCH == 2:
					corrObj2 = corrObject(file_path,fit_obj)
					corrObj3 = corrObject(file_path,fit_obj)
					
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

					while  line[0][:4] != 'Time':
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

					corrObj1.max = np.max(corrObj1.autoNorm)
					corrObj1.min = np.min(corrObj1.autoNorm)
					corrObj2.max = np.max(corrObj2.autoNorm)
					corrObj2.min = np.min(corrObj2.autoNorm)
					corrObj3.max = np.max(corrObj3.autoNorm)
					corrObj3.min = np.min(corrObj3.autoNorm)

					corrObj1.tmax = np.max(corrObj1.autotime)
					corrObj1.tmin = np.min(corrObj1.autotime)
					corrObj2.tmax = np.max(corrObj2.autotime)
					corrObj2.tmin = np.min(corrObj2.autotime)
					corrObj3.tmax = np.max(corrObj3.autotime)
					corrObj3.tmin = np.min(corrObj3.autotime)
					
					
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

			if version == 3:
				
				objIdArT = []
				numOfCH = float(next(r_obj)[1])
				
				
								
				line = next(r_obj)
				metadata = {}
				
				while  line[0][:4] != 'Time':
					metadata[line[0]] = line[1:]
					line = next(r_obj)

				#null = next(r_obj)
				line = next(r_obj)

				tscale = []
				tdata = []
				
				while  line[0] != 'end':
					tscale.append(line[0])
					tdata.append(line[1:])		
					line = next(r_obj)

				for i in range(0,int(numOfCH**2)):
					corrObj = corrObject(file_path,fit_obj)
					objIdArT.append(corrObj)
					fit_obj.objIdArr.append(corrObj)	

					corrObj.parent_name = 'no name'
					corrObj.parent_uqid = '0'
					corrObj.numOfCH = numOfCH
					
					corrObj.type = str(metadata['type'])				
					corrObj.ch_type = str(metadata['ch_type'][i])
					
					corrObj.name = objIdArT[i].name+'-CH'+str(objIdArT[i].ch_type)
					
					if 'kcount' in metadata:
						if i < numOfCH:
							corrObj.kcount = float(metadata['kcount'][i])
					if 'numberNandB' in metadata:
						if i < numOfCH:
							corrObj.numberNandB = float(metadata['numberNandB'][i])
					if 'brightnessNandB' in metadata:
						if i < numOfCH:
							corrObj.brightnessNandB = float(metadata['brightnessNandB'][i])
					if 'CV' in metadata:
						if i >= numOfCH:
							corrObj.CV = float(metadata['CV'][i])
					if 'carpet pos' in metadata:
						corrObj.carpet_position = int(metadata['carpet pos'][0])
					if 'pc' in metadata:
						pc_text = float(metadata['pc'][0])
					if 'pbc_f0' in metadata:
						corrObj.pbc_f0 = float(metadata['pbc_f0'][i])
					if 'pbc_tb' in metadata:
						corrObj.pbc_tb = float(metadata['pbc_tb'][i])	
					if 'parent_name' in metadata:
						corrObj.parent_name = str(metadata['parent_name'][0])
					if 'parent_uqid' in metadata:
						corrObj.parent_uqid = str(metadata['parent_uqid'][0])	
						
				
					
					td = []
					for tda in tdata:
						td.append(tda[i])

					corrObj.autotime= np.array(tscale).astype(np.float64).reshape(-1)
					corrObj.autoNorm= np.array(td).astype(np.float64).reshape(-1)
					
					corrObj.max = np.max(corrObj.autoNorm)
					corrObj.min = np.min(corrObj.autoNorm)
					
					corrObj.tmax = np.max(corrObj.autotime)
					corrObj.tmin = np.min(corrObj.autotime)

					corrObj.param = copy.deepcopy(fit_obj.def_param)
					corrObj.calculate_suitability()
					SE.calc_param_fcs(fit_obj,corrObj)

				#corrObj.siblings = [corrObj2,corrObj3]
				#corrObj.siblings = [corrObj1,corrObj3]
				#corrObj.siblings = [corrObj1,corrObj2]
import pyperclip
def saveOutputDataFn(fit_obj,indList,copy_fn=False):
		localTime = time.asctime( time.localtime(time.time()) )
		coreArray = []
		
		copyStr =""
		
		
		coreArray.append('name_of_plot')
		coreArray.append('master_file')
		coreArray.append('parent_name')
		coreArray.append('parent_uqid')
		coreArray.append('time of fit')
		coreArray.append('Diff_eq')
		coreArray.append('Diff_species')
		coreArray.append('Triplet_eq')
		coreArray.append('Triplet_species')
		coreArray.append('Dimen')
		coreArray.append('xmin')
		coreArray.append('xmax')
		
		#Old key Array. 
		okeyArray =[None]
		
		
		
		
		#Opens export files
		outPath = fit_obj.folderOutput.filepath
		filenameTxt = str(fit_obj.fileNameText.text())
		if copy_fn == False:
			csvfile = open(outPath+'/'+filenameTxt+'_outputParam.csv', 'a')
			#spamwriter = csv.writer(csvfile)
			spamwriter = csv.writer(csvfile,  dialect='excel')
			
		for v_ind in indList:
			
				
			if(fit_obj.objIdArr[v_ind].toFit == True):
				if(fit_obj.objIdArr[v_ind].fitted == True):
					
					#Includes the headers for the data which is present.
					keyArray = copy.deepcopy(coreArray)
					for item in fit_obj.order_list:
						if fit_obj.objIdArr[v_ind].param[item]['to_show'] == True:
							if  fit_obj.objIdArr[v_ind].param[item]['calc'] == False:
								keyArray.append(str(fit_obj.objIdArr[v_ind].param[item]['alias']))
								keyArray.append('stdev('+str(fit_obj.objIdArr[v_ind].param[item]['alias'])+')')
							else:
								keyArray.append(str(fit_obj.objIdArr[v_ind].param[item]['alias']))

					#If there are any dissimilarities between the current keys and the last we reprint the headers.
					reprint = False
					
					if keyArray.__len__() != okeyArray.__len__():
						#If they are not same length then something is different.
						reprint = True
					else:
						#Just to be really sure. Might remove if gets too slow.
						for key,okey in zip(keyArray, okeyArray):
							if key != okey:
								reprint = True
								break

					if reprint == True:
						headerText = '\t'.join(keyArray)
						copyStr +=headerText +'\n'
						if copy_fn == False:
							spamwriter.writerow(keyArray)

					param = fit_obj.objIdArr[v_ind].param
					rowText = []
					rowText.append(str(fit_obj.objIdArr[v_ind].name))
					rowText.append(str(fit_obj.objIdArr[v_ind].file_name))
					rowText.append(str(fit_obj.objIdArr[v_ind].parent_name))
					rowText.append(str(fit_obj.objIdArr[v_ind].parent_uqid))
					rowText.append(str(fit_obj.objIdArr[v_ind].localTime))
					rowText.append(str(fit_obj.diffModEqSel.currentText()))
					rowText.append(str(fit_obj.def_options['Diff_species']))
					rowText.append(str(fit_obj.tripModEqSel.currentText()))
					rowText.append(str(fit_obj.def_options['Triplet_species']))
					rowText.append(str(fit_obj.dimenModSel.currentText()))
					rowText.append(str(fit_obj.objIdArr[v_ind].model_autotime[0]))
					rowText.append(str(fit_obj.objIdArr[v_ind].model_autotime[-1]))
					
					
					for item in fit_obj.order_list:
							if  param[item]['calc'] == False:
								if param[item]['to_show'] == True:
									
									rowText.append(str(param[item]['value']))
									rowText.append(str(param[item]['stderr']))
									
							else:
								if param[item]['to_show'] == True:
									rowText.append(str(param[item]['value']))

								
					if copy_fn == True:
						copyStr += str('\t'.join(rowText)) +'\n'
					if copy_fn == False:
						spamwriter.writerow(rowText)
					
					#Updates the old  key array
					okeyArray = copy.deepcopy(keyArray)
		copyStr += str('end\n')
		if copy_fn == True:
			
			pyperclip.copy(copyStr)
		else:
			csvfile.close()
		return copyStr