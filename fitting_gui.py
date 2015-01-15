
import sys, os, csv
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.transforms import ScaledTranslation
import matplotlib.gridspec as gridspec
import numpy as np
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
import time
import errno
import copy
import os.path
import subprocess
import pyperclip
import cPickle as pickle
from correlation_objects import corrObject

"""FCS Fitting Software

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

class folderOutput(QtGui.QMainWindow):
	
	def __init__(self,parent):
		super(folderOutput, self).__init__()
	   
		self.initUI()
		self.parent = parent
		self.parent.config ={}
		
		try:
			self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ));
			self.filepath = self.parent.config['output_filepath']
		except:
			self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
			try:
				os.makedirs(self.filepath)
			except OSError as exception:
				if exception.errno != errno.EEXIST:
					raise
		try:
			self.filepath_save_profile = self.parent.config['filepath_save_profile']
		except:
			self.filepath_save_profile = os.path.expanduser('~')+'/FCS_Analysis/output/'
		
		
	def initUI(self):      

		self.textEdit = QtGui.QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
		openFile.triggered.connect(self.showDialog)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openFile)       
		
		self.setGeometry(300, 300, 350, 500)
		self.setWindowTitle('Select a Folder')
		#self.show()
		
	def showDialog(self):

		if self.type == 'output_dir':
			#folderSelect = QtGui.QFileDialog()
			#folderSelect.setDirectory(self.filepath);
			tfilepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
			
			if tfilepath !='':
				self.filepath = tfilepath
			#Save to the config file.
				self.parent.config['output_filepath'] = str(tfilepath)
				pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "w" ))
			
		if self.type == 'profile_load':
			
			
			#filepath = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
			filepath =  QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.parent.filepath,'Fit Profile(*.profile);')
			self.parent.config['filepath_save_profile'] = pickle.load(self.parent.fit_profile, open(str(filepath),"w"));
		if self.type == 'profile_save':
			
			
			#filepath = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
			filename =  QtGui.QFileDialog.getSaveFileName(self, 'Open file',self.filepath_save_profile,'Fit Profile(*.profile);;')
			self.filepath_save_profile = str(QtCore.QFileInfo(filename).absolutePath())+'/'
			self.parent.config['filepath_save_profile']  = self.filepath_save_profile
			#Save the files to the 
			pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "w" ))
			#Save the 
			pickle.dump(self.parent.fit_profile, open(str(filename),"w"));


		#Save parameters to file.
class visualHisto(QtGui.QMainWindow):
	def __init__(self,parObj):
		QtGui.QMainWindow.__init__(self)
		#self.fileArray = fileArray
		#self.create_main_frame()
		self.parObj = parObj
		
		

	def create_main_frame(self):
		
		
		#self.trace_idx = self.parObj.clickedS1

		page = QtGui.QWidget()        
		hbox_main = QtGui.QHBoxLayout()
		vbox1 = QtGui.QVBoxLayout()
		vbox0 = QtGui.QVBoxLayout()
		self.setWindowTitle("Data Visualisation")
		self.figure1 = plt.figure(figsize=(10,4))
		
		# this is the Canvas Widget that displays the `figure`
		# it takes the `figure` instance as a parameter to __init__
		#self.canvas1 = FigureCanvas(self.figure1)
		
		self.figure1.patch.set_facecolor('white')
		self.canvas1 = FigureCanvas(self.figure1)

		
		self.plt1 = self.figure1.add_subplot(1,1,1)
		self.plt1.set_ylabel('frequency')
		self.plt1.set_xlabel('bins')

		
		
		
		
		self.generate_histogram_btn = QtGui.QPushButton('Generate Histogram')
		
		self.visual_param_select = QtGui.QComboBox();

		self.min_range_lbl = QtGui.QLabel("min range:") 
		self.min_range_txt = QtGui.QLineEdit();
		self.min_range_txt.setPlaceholderText("default:input data min")
		self.max_range_lbl = QtGui.QLabel("max range:") 
		self.max_range_txt = QtGui.QLineEdit();
		self.max_range_txt.setPlaceholderText("default:input data max")
		self.num_of_bins_lbl = QtGui.QLabel("bin width:") 
		self.num_of_bins_txt = QtGui.QLineEdit('2');

		min_box = QtGui.QHBoxLayout();
		min_box.addWidget(self.min_range_lbl)
		min_box.addWidget(self.min_range_txt)
		max_box = QtGui.QHBoxLayout();
		max_box.addWidget(self.max_range_lbl)
		max_box.addWidget(self.max_range_txt)
		bin_box = QtGui.QHBoxLayout();
		bin_box.addWidget(self.num_of_bins_lbl)
		bin_box.addWidget(self.num_of_bins_txt)

		self.generate_menu(self.visual_param_select) 
		self.generate_histogram_btn.clicked.connect(self.generate_histo)
		
		copy_data_btn = QtGui.QPushButton('Copy to clipboard')
		copy_data_btn.clicked.connect(self.copy_to_clipboard)
		save_data_btn = QtGui.QPushButton('Save to file')
		save_data_btn.clicked.connect(self.save_to_file)
		hbox_main.addLayout(vbox0)
		hbox_main.addLayout(vbox1)
		
		
		
	
		
		vbox0.addWidget(self.visual_param_select)
		

		
		vbox0.addLayout(min_box)
		vbox0.addLayout(max_box)
		vbox0.addLayout(bin_box)
		vbox0.addWidget(self.generate_histogram_btn)
		vbox0.addWidget(copy_data_btn)
		vbox0.addWidget(save_data_btn)
		vbox0.addStretch();
		vbox1.addWidget(self.canvas1)
		
		page.setLayout(hbox_main)
		self.setCentralWidget(page)
		self.show()
		

	def generate_histo(self):
		self.data = []
		indList = range(0,self.parObj.objIdArr.__len__())
		for v_ind in indList:
			if self.parObj.objIdArr[v_ind].toFit == True:
				if self.parObj.objIdArr[v_ind].fitted == True:
					for key,value in self.parObj.objIdArr[v_ind].param.iteritems() :
						if key == self.visual_param_select.currentText():
							self.data.append(value.value)

		
		if self.data !=[]:
			bin_width = float(self.num_of_bins_txt.text())
			min_range = self.min_range_txt.text()
			max_range = self.max_range_txt.text()
			if min_range == '':
				min_range = min(self.data)
			else:
				min_range = float(min_range)
			if max_range == '':
				max_range = max(self.data)
			else:
				max_range = float(min_range)
			self.plt1.cla();

			bins = np.arange(min_range,max_range+bin_width,bin_width)
			
			self.n, self.bins, patches = self.plt1.hist(np.array(self.data).astype(np.float64), bins, facecolor='green', alpha=0.75)
			#self.plt1.plot(range(0,10),range(0,10))
			self.canvas1.draw()
			
	def copy_to_clipboard(self):
		print self.bins.__len__()
		print 'd',self.n.__len__()
		copyStr = ""
		for i in range(0,self.n.__len__()):
			
			
			copyStr += str(self.bins[i])+"-"+str(self.bins[i+1])+"\t"+ str(self.n[i]) +"\n"
		
		pyperclip.copy(copyStr)
	def save_to_file(self):
		outPath = self.parObj.folderOutput.filepath
		filenameTxt = str(self.parObj.fileNameText.text())
		f = open(outPath+'/'+filenameTxt+'_histo_data.csv', 'w')
		
		
		f.write("bin"+","+str("frequency") +"\n")

		
		for i in range(0,self.n.__len__()):
			f.write(str(self.bins[i])+"-"+str(self.bins[i+1])+","+ str(self.n[i]) +"\n")
	


	def generate_menu(self,combo):
		#Ensures the headings are relevant to the fit.

		proceed=False;
		for i in range(0,self.parObj.objIdArr.__len__()):
			if self.parObj.objIdArr[i].toFit == True:
				if self.parObj.objIdArr[i].fitted == True:
					v_ind = i;
					proceed = True;
					break;
			

		if proceed == True:
			#Includes the headers for the data which is present.
			for key,value in self.parObj.objIdArr[v_ind].param.iteritems() :
				
				combo.addItem(key)
				#combo.addItem('stderr('+key+')')
				


class Form(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Form, self).__init__(parent)
		self.setWindowTitle('PyQt & matplotlib demo: Data plotting')
		
		#lines.
		self.left = 0
		self.right = 0
		self.activeObj = None
		self.objIdArr =[]
		self.objStruct = {}
		self.names = [];
		self.setAutoScale =True
		
			#Default parameters for each loaded file.
		self.def_param = Parameters()
		
	   
		#default options for the fitting.
		self.def_options ={}
		
		self.def_options['Diff_eq'] = 1
		self.def_options['Diff_species'] = 1
		self.def_options['Triplet_eq'] = 1
		self.def_options['Triplet_species'] = 1

		self.def_options['Dimen'] =1
		
		#Proportion of the diffusing species present
		self.def_param.add('A1', value=1.0, min=0,max=1.0, vary=False)
		self.def_param.add('A2', value=1.0, min=0,max=1.0, vary=False)
		self.def_param.add('A3', value=1.0, min=0,max=1.0, vary=False)
		#self.def_param.add('AC', value=1.0,vary=False)
		#self.def_param.add('A2', expr='1.0-A1')
		#self.def_param.add('A3', expr='1.0-A1-A2')

		
		
		#The offset
		self.def_param.add('DC', value=0.0, min=-1.0,max=5.0,vary=False)
		#The amplitude
		self.def_param.add('GN0', value=1.0, vary=True)
		#The alpha value
		self.def_param.add('alpha', value=1.0, min=0,max=1.0, vary=True)
		#lateral diffusion coefficent

		self.def_param.add('txy1', value=1.0,min=0.001,max=200.0, vary=True)
		self.def_param.add('txy2', value=1.0,min=0.001,max=200.0, vary=True)
		self.def_param.add('txy3', value=1.0, min=0.001,max=200.0,vary=True)
		
		self.def_param.add('alpha1', value=1.0,min=0,max=2.0, vary=True)
		


		self.def_param.add('alpha2', value=1.0,min=0,max=2.0, vary=True)
		self.def_param.add('alpha3', value=1.0,min=0,max=2.0, vary=True)



		#Axial diffusion coefficient
		self.def_param.add('tz1', value=1.0, min=0,max=1.0,vary=True)
		self.def_param.add('tz2', value=1.0,min=0,max=1.0, vary=True)
		self.def_param.add('tz3', value=1.0,min=0,max=1.0, vary=True)

		#Axial ratio coefficient
		self.def_param.add('AR1', value=1.0, vary=True)
		self.def_param.add('AR2', value=1.0, vary=True)
		self.def_param.add('AR3', value=1.0, vary=True)

		self.def_param.add('B1', value=1.0, min= 0.001, max= 1000,vary=True)
		self.def_param.add('B2', value=1.0, min= 0.001, max= 1000,vary=True)
		self.def_param.add('B3', value=1.0, min= 0.001, max= 1000,vary=True)

		self.def_param.add('T1', value=1.0, min= 0, max= 1000,vary=True)
		self.def_param.add('T2', value=1.0, min= 0, max= 1000,vary=True)
		self.def_param.add('T3', value=1.0, min= 0, max= 1000,vary=True)
	
		self.def_param.add('tauT1', value =0.005, min= 0.001, max= 1000,vary=True); 
		self.def_param.add('tauT2', value =0.005,min= 0.001, max= 1000, vary=True);
		self.def_param.add('tauT3', value =0.005, min= 0.001, max= 1000,vary=True);

		#Initiates dataHOlder object.
		#self.data = DataHolder('',self)

		self.series_list_model = QtGui.QStandardItemModel()
		
		self.create_menu()
		self.create_main_frame()
		self.create_status_bar()
		#self.update_ui()
		self.on_show()
	def load_file(self, filename=None):

		load_fileInt = QtGui.QFileDialog()
		try:
			f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'r')
			self.loadpath =f.readline()
			f.close() 
		except:
			self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'

		for filename in load_fileInt.getOpenFileNames(self, 'Open a data file', self.loadpath, 'CSV files (*.csv);SIN files (*.SIN);All Files (*.*)'):
				self.nameAndExt = os.path.basename(str(filename)).split('.')
				self.name = self.nameAndExt[0]
				self.ext = self.nameAndExt[-1]
				if self.ext == 'SIN' or self.ext == 'sin':
					corrObj1 = corrObject(filename,self)
					corrObj1.load_from_file(0)
					corrObj2 = corrObject(filename,self)
					corrObj2.load_from_file(1)
				if self.ext == 'CSV':
					self.corrObj = corrObject(filename,self)
					self.corrObj.objId.load_from_file(0)
				#self.corrObj.objId.param = self.def_param
				#Where we add the names.
				self.fill_series_list()
				self.status_text.setText("Loaded " + filename)
				
		
	   
		
	   

		try:
			self.loadpath = str(QtCore.QFileInfo(filename).absolutePath())
			
			
					#self.update_ui()
			f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'w')

			f.write(self.loadpath)
			f.close()
		except:
			print 'nofile'
		
	
	
	def on_show(self):
		self.axes.clear()        
		self.axes.grid(True)

		self.axes.set_ylabel('Correlation', fontsize=12)
		
		self.axes.xaxis.grid(True,'minor')
		self.axes.xaxis.grid(True,'major')
		self.axes.yaxis.grid(True,'minor')
		self.axes.yaxis.grid(True,'major')
		self.axes2.clear()        
		self.axes2.grid(True)
		
		self.axes2.set_xlabel('Residual Tau (ms)', fontsize=12)
		self.axes2.xaxis.grid(True,'minor')
		self.axes2.xaxis.grid(True,'major')
		self.axes2.yaxis.grid(True,'minor')
		self.axes2.yaxis.grid(True,'major')
		
		has_series = False
		scaleMin = 0
		scaleMax = 0
		if self.setAutoScale == False:
			self.axes.set_autoscale_on(False)
		else:
			self.axes.set_autoscale_on(True)
			
		row = 0;
		for objId in self.objIdArr:
			if objId.toFit == True:
				model_index = self.series_list_model.index(row, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)
				objId.checked = checked
				
				
				if checked:
					
					has_series = True
					#Takes the values from the interface 
					self.axes.set_xscale('log')
					self.axes2.set_xscale('log')
					self.scale = objId.autotime

					self.series = objId.autoNorm
					
					self.axes.plot(self.scale, self.series, 'o',markersize=3,mew= 0,label=objId.name)
					self.axes.set_autoscale_on(False)

				#if self.setAutoScale == False:

					#self.axes.set_ylim(bottom=float(objId.param['DC'].value)-0.001)
				row += 1  
		row = 0;
		for objId in self.objIdArr:
			if objId.toFit == True:
				model_index = self.series_list_model.index(row, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)

				
				
				if checked:
					has_series = True
					#Takes the values from the interface 
					if objId.model_autoNorm !=[]:
						self.mod_scale = objId.model_autotime
						self.mod_series = objId.model_autoNorm
						self.axes.plot(self.mod_scale, self.mod_series, '-',  label=objId.name+' fitted model')       
					   
						maxValue = np.max(objId.residualVar)
						minValue = np.min(objId.residualVar)
						if maxValue > scaleMax:
							scaleMax = maxValue
						if minValue < scaleMin:
							scaleMin = minValue
						self.axes2.set_ylim([scaleMin,scaleMax])
						self.axes2.plot(self.mod_scale,objId.residualVar,label=objId.name)
						self.axes2.set_ylim([scaleMin,scaleMax])
				row +=1        
				   
				
		if(self.series_list_model.rowCount()>0):
			
				#The line on the left.
				try:
					#Find the nearest position to the the vertical line.
					xpos1 = int(np.argmin(np.abs(self.scale -  self.dr.xpos)))
					xpos2 = int(np.argmin(np.abs(self.scale -  self.dr1.xpos)))
					xpos1a = np.argmax(self.series >0)
					xpos2a = int(self.series.shape[0]-np.argmax(self.series[::-1] >-1)-1)
					if (xpos1<xpos1a):
						xpos1 = xpos1a
					if(xpos2>xpos2a):
						xpos2 = xpos2a
				except:
					try:
						xpos1 = np.argmax(self.series >0)
						xpos2 = int(self.series.shape[0]-np.argmax(self.series[::-1] >-1)-1)
					except:
						xpos1 = 10
						xpos2 = 40


					

				self.line0=self.axes.axvline(x=self.scale[xpos1],linewidth=4, color='gray')
				self.dr = draggableLine(self.line0, self)
				self.dr.type = 'left'
				self.dr.xpos = self.scale[xpos1]
				#Set the spinbox values
				self.fit_btn_min.array = self.scale
				self.fit_btn_max.array = self.scale
				self.fit_btn_min.index = xpos1
				self.fit_btn_max.index = xpos2
				self.fit_btn_min.setValue(self.scale[xpos1])
				self.fit_btn_max.setValue(self.scale[xpos2])

				self.dr.connect()
				#The line on the right.
				self.line1=self.axes.axvline(x=self.scale[xpos2],linewidth=4, color='gray')
				self.dr1 = draggableLine(self.line1,self)
				self.dr1.type = 'right'
				self.dr1.xpos = self.scale[xpos2]
				self.dr1.connect()

				
				
			#redraw the canvas.self.axes.set_autoscale_on(False) 
		
		if self.legend_cb.isChecked():
			self.axes.legend(loc=3,prop={'size':8})
		self.canvas.draw()       

	   
		 
	def rescale_plot(self):
		"""Rescales the plot on movement of the lines"""
		#Get the scale locally
		scale = np.array(self.data.scale).astype(np.float64)
		#convert left line coordinate
		xdat = np.array(self.dr.xpos).astype(np.float64)
		#Find the index of the nearest point in the scale.
		indx = int(np.argmin(np.abs(scale - xdat)))
		self.left = indx
		#convertright line coordinate
		xdat = np.array(self.dr1.xpos).astype(np.float64)
		#Find the index of the nearest point in the scale.
		indx = int(np.argmin(np.abs(scale - xdat)))
		self.right = indx
		
		#Calculates min and max points for the plot.
		maxLevel = np.max(self.series[self.left:self.right])
		minLevel = np.min(self.series[self.left:self.right])
		#Changes y-axis.
		self.axes.set_ylim([minLevel,maxLevel])
		self.canvas.draw()


		
		
		
			
		

	def on_about(self):
		self.about_win = QtGui.QWidget()
		self.about_win.setWindowTitle('QWebView Interactive Demo')
 
		# And give it a layout
		layout = QtGui.QVBoxLayout()
		self.about_win.setLayout(layout)
		self.view = QtWebKit.QWebView()
		self.view.setHtml('''
		  <html>
			
		 
			<body>
			  <form>
				<h1 >Equation used for fitting:</h1>
				
				<br />
				<label >Diffusion equation 1: </label>
				<p>GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*((1+(tc/tz1))**-0.5)))+ (A2*(((1+((tc/txy2)**alpha2))**-1)*((1+(tc/tz2))**-0.5)))+ (A3*(((1+((tc/txy3)**alpha3))**-1)*((1+(tc/tz3))**-0.5)))</p>
				<label >Diffusion equation 2:</p>
				<p>GDiff = (A1*(((1+((tc/txy1)**alpha1))**-1)*(((1+(tc/((AR1**2)*txy1)))**-0.5))))+(A2*(((1+((tc/txy2)**alpha2))**-1)*(((1+(tc/((AR2**2)*txy2)))**-0.5))))+(A3*(((1+((tc/txy3)**alpha3))**-1)*(((1+(tc/((AR3**2)*txy3)))**-0.5))))</p>
				<label>Triplet equation 1:</label>
				<p>GT = 1 + (B1*np.exp(-tc/tauT1))+(B2*np.exp(-tc/tauT2))+(B3*np.exp(-tc/tauT3))</p>

				<label>Triplet equation 2:</label>
				<p>GT = 1- (T1+T2+T3)+ ((T1*np.exp(-tc/tauT1))+(T2*np.exp(-tc/tauT2))+(T3*np.exp(-tc/tauT3)))</p>

				
			   
				<br />
				<label >Full equation:</label>
				<p>DC + (GN0*GDiff*GT)</p>
				
				<br />
				
			  </form>
			</body>
		  </html>
		''')
		layout.addWidget(self.view)
		self.about_win.setLayout(layout)
		self.about_win.show()
		self.about_win.raise_()

	def fill_series_list(self):
		
		self.series_list_model.clear()
		
		for objId in self.objIdArr:
				
				#Find details of each dataset
				name = objId.name
				item = QtGui.QStandardItem(name)
				objId.series_list_id = item
				#If the item has been checked. Restore that state.
				if objId.checked == False:
					item.setCheckState(QtCore.Qt.Unchecked)
				else :
					item.setCheckState(QtCore.Qt.Checked)


				
				#Filter for CH identification:
				if self.ch_check_ch0.isChecked() == True and objId.ch_type == 0:
					objId.toFit = True
				elif self.ch_check_ch1.isChecked() == True and objId.ch_type == 1:
					objId.toFit = True
				elif self.ch_check_ch01.isChecked() == True and objId.ch_type == 2:
					objId.toFit = True
				elif self.ch_check_ch10.isChecked() == True and objId.ch_type == 3:
					objId.toFit = True
				else:
					
					objId.toFit = False
					continue;

				
				
				#Context sensitive colour highlighting
				if objId.goodFit == False:
					item.setBackground(QtGui.QColor('red'))
				elif objId.fitted == True:
					item.setBackground(QtGui.QColor('green'))
				else:    
					item.setBackground(QtGui.QColor('white'))
				item.setCheckable(True)
				self.series_list_model.appendRow(item)
		self.updateFitList()

				
	
	def create_main_frame(self):
		"""Creates the main layout of the fitting interface """
		self.main_frame = QtGui.QWidget()
		
		plot_frame = QtGui.QWidget()
		
		self.dpi = 100
		self.fig = Figure((8.0, 16.0), dpi=self.dpi)
		self.fig.patch.set_facecolor('white')
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1]) 
		self.axes = self.fig.add_subplot(gs[0])
		self.axes2 = self.fig.add_subplot(gs[1])
		self.fig.subplots_adjust(bottom = 0.1,top=0.95, right=0.95)


		

		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
		
		log_label = QtGui.QLabel("Data series:")
		self.series_list_view = QtGui.QListView()
		

		self.series_list_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
	  
		self.series_list_view.setModel(self.series_list_model)
		self.to_spin = QtGui.QSpinBox()

		
		self.show_button = QtGui.QPushButton("Plot Checked Data")
		self.connect(self.show_button, QtCore.SIGNAL('clicked()'), self.on_show)

		self.series_list_view2 = QtGui.QListView()

		#############The left panel.
		
		self.load_box = QtGui.QHBoxLayout()
		loadCorrFile = QtGui.QPushButton("Load Correlated File")
		loadCorrFile.clicked.connect(self.load_file)
		self.load_box.addWidget(loadCorrFile)
		on_about_btn = QtGui.QPushButton()
		on_about_btn.setText("About Equation")
		on_about_btn.clicked.connect(self.on_about)
		self.load_box.addStretch()
		self.load_box.addWidget(on_about_btn)
		

		self.model_layout = QtGui.QHBoxLayout()
		
		#Drop down list of equations for diffusing species
		self.diffModEqSel = comboBoxSp2(self);
		self.diffModEqSel.type ='Diff_eq'
		self.diffModEqSel.addItem('Equation 1A')
		self.diffModEqSel.addItem('Equation 1B')
		self.model_layout.addWidget(self.diffModEqSel)



		#Spin box for number of diffusing species
		diffNumSpecies = QtGui.QHBoxLayout()
		diffNumSpecLabel = QtGui.QLabel('Num. of: diffusing species')


		self.diffNumSpecSpin = QtGui.QSpinBox()
		self.diffNumSpecSpin.setRange(1,3);
		self.diffNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(diffNumSpecLabel)
		diffNumSpecies.addWidget(self.diffNumSpecSpin)
		
		#Drop down list of equations for Triplet equations
		self.tripModEqSel = comboBoxSp2(self);
		self.tripModEqSel.type ='Triplet_eq'
		self.tripModEqSel.addItem('no triplet')
		self.tripModEqSel.addItem('Triplet Eq 2A')
		self.tripModEqSel.addItem('Triplet Eq 2B')
		self.model_layout.addWidget(self.tripModEqSel)
		#Drop down box for selecting 2D or 3D model:
		self.dimenModSel = comboBoxSp2(self)
		self.dimenModSel.type ='Dimen'
		self.dimenModSel.addItem('2D')
		self.dimenModSel.addItem('3D')
		self.model_layout.addWidget(self.dimenModSel)
		self.model_layout.addStretch()
		#Drop-down list with all the available models.
		
		
		




		self.modelFitSel = comboBoxSp2(self)
		self.modelFitSel.type = 'Fit'

		fit_layout = QtGui.QHBoxLayout()
		

		
		self.fit_btn_min_label = QtGui.QLabel("Fit: from:")
		self.fit_btn_min = spinBoxSp3(self)
		self.fit_btn_min.type ='min'
		self.fit_btn_min.setMaximumWidth(90)
		self.fit_btn_min.setDecimals = 3
		self.fit_btn_min.valueChanged.connect(self.fit_btn_min.onEdit)
		

		self.fit_btn_max_label = QtGui.QLabel("to:")
		self.fit_btn_max = spinBoxSp3(self)
		self.fit_btn_max.type ='max'
		self.fit_btn_max.setMaximumWidth(90)
		self.fit_btn_max.setDecimals = 3
		self.fit_btn_max.valueChanged.connect(self.fit_btn_max.onEdit)


		#Profile panel for different buttons.
		default_profile_panel = QtGui.QHBoxLayout()

		load_default_profile = QtGui.QPushButton('Load Profile')
		self.load_default_profile_output = folderOutput(self)
		self.load_default_profile_output.type = 'profile_load'
		
		save_default_profile = QtGui.QPushButton('Save Profile')
		self.save_default_profile_output = folderOutput(self)
		self.save_default_profile_output.type = 'profile_save'

		default_profile_panel.addWidget(load_default_profile)
		default_profile_panel.addWidget(save_default_profile)

		
		save_default_profile.clicked.connect(self.save_default_profile_fn)
		load_default_profile.clicked.connect(self.load_default_profile_fn)


		#Spin box for number of diffusing species
		
		tripNumSpecLabel = QtGui.QLabel('Triplet states')
		self.tripNumSpecSpin = QtGui.QSpinBox()
		self.tripNumSpecSpin.setRange(1,3);
		self.tripNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(tripNumSpecLabel)
		diffNumSpecies.addWidget(self.tripNumSpecSpin)
		diffNumSpecies.addStretch()
		
		
		

		self.fitTable =[];
			#Table which has the fitting
		self.fitTable = QtGui.QTableWidget()
		

		self.defineTable()
		#self.fitTable.setMinimumWidth(320)
		self.fitTable.setMaximumWidth(320)
		self.fitTable.setMinimumHeight(100)
		self.fitTable.setMaximumHeight(600)
		
		
		
		self.fit_btn = QtGui.QPushButton("Current")
		self.fit_btn.clicked.connect(self.fit_equation)
		self.fit_btn.setToolTip('This will fit the data selected in the \"Display Model Parameters\" drop-down list.')


		self.fitAll_btn = QtGui.QPushButton("All")
		self.fitAll_btn.clicked.connect(self.fitAll_equation)

		#Horizontal Layout for fit_btns.
		fit_btns = QtGui.QHBoxLayout()
		
		#Fit components
		self.fit_btn_txt = QtGui.QLabel("Fit with param: ")
		self.fitSelected_btn = QtGui.QPushButton("Only highlighted")
		self.fitSelected_btn.clicked.connect(self.fitSelected_equation)

		#Fit button adding to layout.
		fit_btns.addWidget(self.fit_btn_txt)
		fit_btns.addWidget(self.fit_btn)
		fit_btns.addWidget(self.fitAll_btn)
		fit_btns.addWidget(self.fitSelected_btn)
		fit_btns.addStretch();
		



		
		
		modelFitSel_box = QtGui.QHBoxLayout()
		self.modelFitSel_label = QtGui.QLabel('Display model parameters for data:')
		modelFitSel_box.addWidget(self.modelFitSel_label)
		modelFitSel_box.addStretch()


		#main left panel layout.
		left_vboxTop = QtGui.QVBoxLayout()
		left_vboxMid = QtGui.QVBoxLayout()
		left_vboxBot = QtGui.QVBoxLayout()
		
		left_vboxTop.setSpacing(0.5)
		left_vboxBot.setSpacing(0.5)
		self.load_box.setSpacing(0.5)
		left_vboxTop.addLayout(self.load_box)
		left_vboxTop.addLayout(self.model_layout) 
		left_vboxTop.addLayout(diffNumSpecies) 
		
		left_vboxTop.addLayout(modelFitSel_box)
		
		left_vboxTop.addWidget(self.modelFitSel)
		left_vboxTop.addLayout(fit_btns)
		left_vboxTop.addLayout(fit_layout)
		
		left_vboxTop.addLayout(default_profile_panel)
		left_vboxTop.addWidget(self.fitTable)
		left_vboxTop.setAlignment(QtCore.Qt.AlignLeft)

		
		
		fit_layout.addWidget(self.fit_btn)
		fit_layout.addWidget(self.fit_btn_min_label)
		fit_layout.addWidget(self.fit_btn_min)
		fit_layout.addWidget(self.fit_btn_max_label)
		fit_layout.addWidget(self.fit_btn_max)
		fit_layout.addStretch()
		
		
		#left_vbox.addWidget(self.fitSelected_btn)
		#left_vbox.addWidget(self.saveOutput_btn)

		
		#Copy Fit parameters and the raw data inc. fit.
		copy_text = QtGui.QLabel("Copy: ")
		self.copy_output_btn = QtGui.QPushButton("parameters")
		self.copy_output_btn.setToolTip("Copies the learnt parameters to the clipboard.")
		self.copy_output_btn.clicked.connect(self.copyOutputDataFn)
		self.copy_model_btn = QtGui.QPushButton("plot data")
		self.copy_model_btn.setToolTip("Copies the raw data and fit data to the clipboard.");
		self.copy_model_btn.clicked.connect(self.copyModelFile)

		copy_layout = QtGui.QHBoxLayout()
		copy_layout.addWidget(copy_text)
		copy_layout.addWidget(self.copy_output_btn)
		copy_layout.addWidget(self.copy_model_btn)
		copy_layout.addStretch();

		

		#Save Fit parameters and the raw data inc. fit.
		save_text = QtGui.QLabel("Save: ")
		self.save_output_btn = QtGui.QPushButton("parameters")
		self.save_output_btn.setToolTip("Saves the learnt parameters to a file.")
		self.save_output_btn.clicked.connect(self.saveOutputDataFn)
		
		self.save_model_btn = QtGui.QPushButton("plot data")
		self.save_model_btn.setToolTip("Saves the raw data and fit data to a file.");
		self.save_model_btn.clicked.connect(self.saveModelFile)

		save_layout = QtGui.QHBoxLayout()
		save_layout.addWidget(save_text)
		save_layout.addWidget(self.save_output_btn)
		save_layout.addWidget(self.save_model_btn)
		save_layout.addStretch()


		output_layout = QtGui.QHBoxLayout()
		self.fileNameText = QtGui.QLineEdit('outputFileName')
		

		self.folderSelect_btn = QtGui.QPushButton('Output Folder')
		self.folderOutput = folderOutput(self)
		self.folderOutput.type = 'output_dir'
		self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

		output_layout.addWidget(self.fileNameText)
		output_layout.addWidget(self.folderSelect_btn)

		left_vboxBot.addLayout(copy_layout)
		left_vboxBot.addLayout(save_layout)
		left_vboxBot.addLayout(output_layout)
		
		

		
		left_vboxBot.addStretch()

		left_vbox = QtGui.QVBoxLayout()
		left_stretch = QtGui.QSplitter(QtCore.Qt.Vertical)
		left_vboxTopWid = QtGui.QWidget()
		left_vboxBotWid = QtGui.QWidget()
		
		left_vboxTopWid.setLayout(left_vboxTop)
		left_vboxBotWid.setLayout(left_vboxBot)

		left_stretch.addWidget(left_vboxTopWid)
		left_stretch.addWidget(left_vboxBotWid)
		left_vbox.addWidget(left_stretch)

		center_vbox = QtGui.QVBoxLayout()
		center_vbox.addWidget(self.canvas)
		center_vbox.addWidget(self.mpl_toolbar)
		resetScale = QtGui.QPushButton("Reset Scale")
		resetScale.clicked.connect(self.resetScaleFn)
		self.turnOffAutoScale = QtGui.QPushButton("Keep Scale")
		self.turnOffAutoScale.setCheckable(True)
		self.turnOffAutoScale.clicked.connect(self.autoScaleFn)
		center_hbox = QtGui.QHBoxLayout()
		center_vbox.addLayout(center_hbox)
		center_hbox.addWidget(resetScale)
		center_hbox.addWidget(self.turnOffAutoScale)
		center_hbox.setAlignment(QtCore.Qt.AlignLeft)


		right_vbox = QtGui.QVBoxLayout()
		right_vbox.addWidget(log_label)
		right_vbox.addWidget(self.series_list_view)
		self.series_list_view.setMinimumWidth(260)
		self.series_list_view.setMinimumHeight(260)
		#right_vbox.addLayout(spins_hbox)

		legend_box = QtGui.QHBoxLayout()
		self.legend_cb = QtGui.QCheckBox("Show L&egend")
		self.legend_cb.setChecked(False)
		legend_box.addWidget(self.legend_cb)
		

		
		
		self.right_check_all_none = QtGui.QPushButton("check all")
		self.switch_true_false = True
		legend_box.addWidget(self.right_check_all_none)
		self.right_check_all_none.clicked.connect(self.check_all_none)

		right_vbox.addLayout(legend_box)

		right_ch_check = QtGui.QHBoxLayout()
		#Channel 0 auto-correlation
		ch_check_ch0_label = QtGui.QLabel("ac: CH0")
		self.ch_check_ch0 = QtGui.QCheckBox()
		self.ch_check_ch0.setChecked(True)
		self.ch_check_ch0.setToolTip("check to display CH0 auto-correlation data.")
		self.ch_check_ch0.stateChanged.connect(self.fill_series_list)
		#Channel 1 auto-correlation
		ch_check_ch1_label = QtGui.QLabel("CH1")
		self.ch_check_ch1 = QtGui.QCheckBox()
		self.ch_check_ch1.setChecked(True)
		self.ch_check_ch1.setToolTip("check to display CH1 auto-correlation data.")
		self.ch_check_ch1.stateChanged.connect(self.fill_series_list)
		#Channel 01 cross-correlation
		ch_check_ch01_label = QtGui.QLabel("cc: CH01")
		self.ch_check_ch01 = QtGui.QCheckBox()
		self.ch_check_ch01.setChecked(True)
		self.ch_check_ch01.setToolTip("check to display CH01 cross-correlation data.")
		self.ch_check_ch01.stateChanged.connect(self.fill_series_list)
		#Channel 10 cross-correlation
		ch_check_ch10_label = QtGui.QLabel("CH10")
		self.ch_check_ch10 = QtGui.QCheckBox()
		self.ch_check_ch10.setChecked(False)
		self.ch_check_ch10.setToolTip("check to display CH10 cross-correlation data.")
		self.ch_check_ch10.stateChanged.connect(self.fill_series_list)
		#Add widgets.
		right_ch_check.addWidget(ch_check_ch0_label)
		right_ch_check.addWidget(self.ch_check_ch0)
		right_ch_check.addWidget(ch_check_ch1_label)
		right_ch_check.addWidget(self.ch_check_ch1)
		right_ch_check.addWidget(ch_check_ch01_label)
		right_ch_check.addWidget(self.ch_check_ch01)
		right_ch_check.addWidget(ch_check_ch10_label)
		right_ch_check.addWidget(self.ch_check_ch10)
		#Add to main layout.
		right_vbox.addLayout(right_ch_check)

		right_vbox.addWidget(self.show_button)

		right_vbox.addWidget(self.right_check_all_none)
		self.remove_btn = QtGui.QPushButton("Remove Highlighted Data")
		self.remove_btn.clicked.connect(self.removeDataFn)
		self.clearFits_btn = QtGui.QPushButton("Clear Fit Data All/Highlighted")
		self.clearFits_btn.clicked.connect(self.clearFits)
		self.visual_histo = visualHisto(self)
		visual_histo_btn = QtGui.QPushButton("Generate Histogram");
		visual_histo_btn.clicked.connect(self.visual_histo.create_main_frame)

		right_vbox.addWidget(self.remove_btn)
		right_vbox.addWidget(self.clearFits_btn)
		right_vbox.addWidget(visual_histo_btn)
		right_vbox.addStretch(1)
		
		hbox = QtGui.QHBoxLayout()
		splitter = QtGui.QSplitter();
		
		hbox1 =QtGui.QWidget()
		hbox1.setLayout(left_vbox)
		hbox2 =QtGui.QWidget()
		hbox2.setLayout(center_vbox)
		hbox3 = QtGui.QWidget()
		hbox3.setLayout(right_vbox)
		#hbox.addLayout(right_vbox)
		splitter.addWidget(hbox1)
		splitter.addWidget(hbox2)
		splitter.addWidget(hbox3)
		#Splitter instance. Can't have 
		
		container = QtGui.QWidget()

		hbox.addWidget(splitter)
		
		self.main_frame.setLayout(hbox)

		self.setCentralWidget(self.main_frame)
	def check_all_none(self):
		
		for objId in self.objIdArr:
			if objId.toFit == True:
				objId.checked = self.switch_true_false
				
		self.fill_series_list()

		if self.switch_true_false == True:
			self.switch_true_false = False
			self.right_check_all_none.setText("check none")

		else:
			self.switch_true_false = True
			self.right_check_all_none.setText("check all")
	def load_default_profile_fn(self):
		print 'load profile'
		self.fit_profile = {}
		self.load_default_profile_output.showDialog()
		self.fit_profile['param'] = self.objId_sel.param
		self.fit_profile['def_options'] = self.def_options
		self.save_default_profile_output.showDialog()
	def save_default_profile_fn(self):
		print 'save profile'
		self.fit_profile = {}
		param = self.objId_sel.param
		self.fit_profile['param'] = self.objId_sel.param
		self.fit_profile['def_options'] = self.def_options
		self.save_default_profile_output.showDialog()

		

	def fitSelected_equation(self):
		
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		for v_ind in listToFit:
			#Finds the unique item names which are currently selected.
			indList.append(self.series_list_model.itemFromIndex(v_ind))


		
		for i in range(self.objIdArr.__len__()-1,-1,-1):
			#Looks through the objects in objIdArr and deletes them if they match.
			for indL in indList:
				if self.objIdArr[i].series_list_id == indL:
					self.objIdArr[i].param = self.objId_sel.param
					self.objIdArr[i].fitToParameters()
		self.fill_series_list()
	def removeDataFn(self):
		"""Removes data from the displayed dataseries."""

		#Reads those indices which are highlighted.
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		for v_ind in listToFit:
			#Finds the unique item names which are currently selected.
			indList.append(self.series_list_model.itemFromIndex(v_ind))
		
		
		for i in range(self.objIdArr.__len__()-1,-1,-1):
			#Looks through the objects in objIdArr and deletes them if they match.
			for indL in indList:
				if self.objIdArr[i].series_list_id == indL:
					del self.objIdArr[i]
					break
		
		self.fill_series_list()
		self.updateFitList()
		self.on_show()
	def updateFitList(self):
		"""This is the list which the user selects to bring up parameters.
		All data is displayed here if it has not been filtered through either channel or another attribute."""
		
		#Finds the current name selected in the list, before things change.
		curr_name = self.objIdArr[self.modelFitSel.model_obj_ind_list[self.modelFitSel.currentIndex()]]
					

		#Clears all menu items
		self.modelFitSel.clear()
		self.modelFitSel.model_obj_list = []
		self.modelFitSel.model_obj_ind_list = []
		
		
		#init, if the data is still in list it will selected.
		name_found = False
		#Loop through all the datasets.
		for i in range(0,self.objIdArr.__len__()):
			objId = self.objIdArr[i]
			

			#If they are valid after filtering.
			if objId.toFit == True:
			   
				#Add to list
				self.modelFitSel.addItem(objId.name)
				self.modelFitSel.model_obj_list.append(objId)
				self.modelFitSel.model_obj_ind_list.append(i)
				#If the current entry was previously selected before the refresh.
				
				if curr_name == objId:
					
					#Save the index. Only one should be positive in all the data.
					self.modelFitSel.setCurrentIndex(self.modelFitSel.count()-1)
					self.modelFitSel.selected_name = self.objIdArr[i]
					self.modelFitSel.objId_ind = i
					#The name was found.
					name_found = True
		#If the name wasn't found in the list, because it was filtered out. Default to first entry.      
		if name_found == False:
			self.modelFitSel.setCurrentIndex(0);
			self.modelFitSel.objId_ind = self.objIdArr[self.modelFitSel.currentIndex()]
		#Redraw the table
		#If the currentIndex is valid
		if self.modelFitSel.currentIndex() !=-1:
			#Update the selected entry.
			self.modelFitSel.selected_name = self.objIdArr[self.modelFitSel.currentIndex()]
		

		#Redraw the table
		self.updateTableFirst()


	def resetScaleFn(self):
		self.setAutoScale = True;
		self.on_show()
		self.setAutoScale = False;
	def autoScaleFn(self):
		#self.turnOffAutoScale.setFlat(True)
		if self.turnOffAutoScale.isChecked() == True:
			self.setAutoScale = False;
		else:
			self.setAutoScale = True;
	def copyOutputDataFn(self):

		self.saveOutputDataFn(True)
	def saveOutputDataFn(self,copy_fn=False):
		localTime = time.asctime( time.localtime(time.time()) )
		keyArray = []
		
		copyStr =""
		
		keys = self.objId_sel.param.keys
		keyArray.append('name of file')
		keyArray.append('time of fit')
		keyArray.append('Diff_eq')
		keyArray.append('Diff_species')
		keyArray.append('Triplet_eq')
		keyArray.append('Triplet_species')
		keyArray.append('Dimen')
		keyArray.append('xmin')
		keyArray.append('xmax')


		#Ensures the headings are relevant to the fit.
		for i in range(0,self.objIdArr.__len__()):

			if self.objIdArr[i].fitted == True:
				v_ind = i;
				break;
			else:
				v_ind =0;

		#Includes the headers for the data which is present.
		for key,value in self.objIdArr[v_ind].param.iteritems() :
			if key =='DC':
					keyArray.append('Offset')
			else:
				keyArray.append(key)
			keyArray.append('stderr('+key+')')
			if key =='GN0':
					keyArray.append('N')
			
		headerText = '\t'.join(keyArray)
		copyStr +=headerText +'\n'
		
		
		
		
		   
		
		#Find highlighted indices
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		#If no highlighted indices. Take all those which are fitted.
		if listToFit ==[]:
			indList = range(0,self.objIdArr.__len__())
		else:
			for v_ind in listToFit:
				indList.append(v_ind.row())
		
		
				   
		if copy_fn == True:
			for v_ind in indList:
				if(self.objIdArr[v_ind].toFit == True):
					if(self.objIdArr[v_ind].fitted == True):
						 copyStr += str('\t'.join(self.objIdArr[v_ind].rowText)) +'\n'
			pyperclip.copy(copyStr)
		else:
			#Opens export files
			outPath = self.folderOutput.filepath
			filenameTxt = str(self.fileNameText.text())
			with open(outPath+'/'+filenameTxt+'_outputParam.csv', 'a') as csvfile:
				spamwriter = csv.writer(csvfile)
				spamwriter.writerow(keyArray)
			for v_ind in indList:
				with open(outPath+'/'+filenameTxt+'_outputParam.csv', 'a') as csvfile:
					if(self.objIdArr[v_ind].toFit == True):
						if(self.objIdArr[v_ind].fitted == True):
							spamwriter = csv.writer(csvfile,  dialect='excel')
							spamwriter.writerow(self.objIdArr[v_ind].rowText)

	def clearFits(self):
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		if listToFit ==[]:
			indList = range(0,self.objIdArr.__len__())
		else:
			for v_ind in listToFit:
				indList.append(v_ind.row())
		
		for v_ind in indList:
			self.objIdArr[v_ind].fitted = False;
			self.objIdArr[v_ind].param = self.def_param
			self.objIdArr[v_ind].model_autoNorm =[]
			self.objIdArr[v_ind].model_autotime = []
		self.fill_series_list()
		self.updateFitList()
		self.on_show()
	def copyModelFile(self):
		self.saveModelFile(True)
	def saveModelFile(self, copy_fn = False):
		"""Save files as .csv"""
		
		copyStr =""
		xpos1 = int(np.argmin(np.abs(self.scale -  self.dr.xpos)))
		xpos2 = int(np.argmin(np.abs(self.scale -  self.dr1.xpos)))

		outPath = self.folderOutput.filepath
		filenameTxt = str(self.fileNameText.text())

		if copy_fn == True:
			copyStr += 'Time (ms)'+'\t'
		else:
			f = open(outPath+'/'+filenameTxt+'_rawFitData.csv', 'w')
			f.write('Time (ms)'+',');
		


		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		if listToFit ==[]:
			indList = range(0,self.objIdArr.__len__())
		else:
			for v_ind in listToFit:
				indList.append(v_ind.row())
		
		if copy_fn == True:
			for v_ind in indList:
				if self.objIdArr[v_ind].model_autoNorm !=[]:
					copyStr += self.objIdArr[v_ind].name+'\t'+self.objIdArr[v_ind].name+' fitted model: '+'\t'
		
			copyStr +=str('\n')
		else:
			for v_ind in indList:
				if self.objIdArr[v_ind].model_autoNorm !=[]:
					f.write(self.objIdArr[v_ind].name+','+self.objIdArr[v_ind].name+' fitted model: '+',')
			f.write('\n')
			

		if copy_fn == True:
			for x in range(0,self.scale.shape[0]):
				copyStr += str(self.scale[x])+'\t'
				for v_ind in indList:
					if self.objIdArr[v_ind].model_autoNorm !=[]:
						copyStr += str(self.objIdArr[v_ind].autoNorm[x])+'\t'
						if x >=xpos1 and x<xpos2:
							copyStr += str(self.objIdArr[v_ind].model_autoNorm[x-xpos1])+'\t'
						else:
							copyStr +=str(' ') +'\t'
				copyStr +=str('\n')
				pyperclip.copy(copyStr)
		else:
			for x in range(0,self.scale.shape[0]):
				f.write(str(self.scale[x])+',')    
				for v_ind in indList:
					if self.objIdArr[v_ind].model_autoNorm !=[]:
						f.write(str(self.objIdArr[v_ind].autoNorm[x])+',')
						
						if x >=xpos1 and x<xpos2:
							f.write(str(self.objIdArr[v_ind].model_autoNorm[x-xpos1])+',')
							
						else:
							f.write(str(' ') +',')
							
				f.write('\n')
				


	def paramFactory(self,paraTxt,setDec,setSingStep, paraMin,paraMax,row,param):
				"""UI factory function"""
				#exec("self."+paraTxt+"_label = QtGui.QLabel()");
				
				exec("self."+paraTxt+"_value = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_value.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_value.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_value.setRange("+str(paraMin)+","+str(paraMax)+")");
				
				try:
					exec("self."+paraTxt+"_value.setValue(float(param[\'"+paraTxt+"\'].value))");
				except:
					exec("self."+paraTxt+"_value.setValue(float(self.def_param[\'"+paraTxt+"\'].value))");
				
				exec("self."+paraTxt+"_vary = QtGui.QCheckBox()");
				checkCont = QtGui.QHBoxLayout()
				try:
					exec("self."+paraTxt+"_vary.setChecked(param[\'"+paraTxt+"\'].vary)");
				except:
					exec("self."+paraTxt+"_vary.setChecked(self.def_param[\'"+paraTxt+"\'].vary)");
				exec("self."+paraTxt+"_min = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_min.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_min.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_min.setRange("+str(paraMin)+","+str(paraMax)+")");
				
				try:
					exec("self."+paraTxt+"_min.setValue(float(param[\'"+paraTxt+"\'].min))");
				except:
					exec("self."+paraTxt+"_min.setValue(float(self.def_param[\'"+paraTxt+"\'].min))");
				exec("self."+paraTxt+"_max = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_max.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_max.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_max.setRange("+str(paraMin)+","+str(paraMax)+")");
				exec("self."+paraTxt+"_label = QtGui.QLabel()");
				try:
					exec("self."+paraTxt+"_max.setValue(float(param[\'"+paraTxt+"\'].max))");
				except:
					 exec("self."+paraTxt+"_max.setValue(float(self.def_param[\'"+paraTxt+"\'].max))");
				
				#exec("self.fitTable.setCellWidget(row, 0, self."+paraTxt+"_label)");
				exec("self.fitTable.setCellWidget(row, 0, self."+paraTxt+"_value)");
				
			   
				
				exec("self.fitTable.setCellWidget(row, 1, self."+paraTxt+"_vary)");
				exec("self.fitTable.setCellWidget(row, 2, self."+paraTxt+"_min)");
				exec("self.fitTable.setCellWidget(row, 3, self."+paraTxt+"_max)");
	def defineTable(self):
			"""Creates all the fields on the parameter table"""
			self.fitTable.setCurrentCell(0,0)
			self.fitTable.setRowCount(30)
			self.fitTable.setColumnCount(4)
			self.fitTable.setHorizontalHeaderLabels(QtCore.QString("Init, Vary,Min,Max, , , ").split(","))
			#self.fitTable.setVerticalHeaderLabels(QtCore.QString(", show, ,,, , , , ").split(","))
			
			self.fitTable.setColumnWidth(0,75);
			self.fitTable.setColumnWidth(1,32);
			self.fitTable.setColumnWidth(2,75);
			self.fitTable.setColumnWidth(3,75);
			row = 0;
			self.fitTable.repaint()
			self.fitTable.reset()
			self.labelArray =[]

			self.def_options['Diff_species'] = self.diffNumSpecSpin.value()
			self.def_options['Triplet_species'] = self.tripNumSpecSpin.value()
			
			
			

			#If no data files present, populate with the defualt.s
			if self.objIdArr != []:
				#Finds the active data set from the combo box.
				
				self.objId_sel = None
				self.objId_sel = self.modelFitSel.model_obj_list[self.modelFitSel.currentIndex()]
				
				param = self.objId_sel.param
			else:
				param = self.def_param
			#Offset e.g. DC
			self.paramFactory(paraTxt='DC',setDec=4,setSingStep=0.01, paraMin=-1,paraMax=5,row=row, param=param)
			self.labelArray.append(' offset')
			row +=1
			text = 'GN0'
			self.paramFactory(paraTxt=text,setDec=4,setSingStep=0.01, paraMin=-1,paraMax=5,row=row,param=param)
			self.labelArray.append(' '+text)
			row +=1

			try:
				self.N = QtGui.QLabel(str(np.round(1/self.GN0_value.value(),4)))
			except:
				self.N = QtGui.QLabel(str(0))
			self.labelArray.append(' N')
			self.fitTable.setCellWidget(row, 0, self.N)
			row +=1
			#Diffusion Variables
			for i in range(1,self.diffNumSpecSpin.value()+1):
				
				text = 'A'+str(i)
				self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=0,paraMax=1,row=row,param=param)
				self.labelArray.append(' '+text)
				row +=1
				text = 'txy'+str(i)
				self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.1, paraMin=0,paraMax=400,row=row,param=param)
				self.labelArray.append(' '+text)
				row +=1
				text = 'alpha'+str(i)
				self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=0,paraMax=100,row=row,param=param)
				self.labelArray.append(' '+text)
				row +=1
				#2 in this case corresponds to 3D:
				if self.def_options['Dimen'] == 2:
					if self.def_options['Diff_eq'] == 1:
						text = 'tz'+str(i)
						self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=0,paraMax=100,row=row,param=param)
						self.labelArray.append(' '+text)
						row +=1
					if self.def_options['Diff_eq'] == 2:
						text = 'AR'+str(i)
						self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=-1,paraMax=100,row=row,param=param)
						self.labelArray.append(' '+text)
						row +=1
				  
			

		   
			if self.def_options['Triplet_eq'] == 2:
				#Triplet State equation1
				for i in range(1,self.tripNumSpecSpin.value()+1):
				
					text = 'B'+str(i)
					self.paramFactory(paraTxt=text,setDec=4,setSingStep=0.01, paraMin=-1,paraMax=1,row=row,param=param)
					self.labelArray.append(' '+text)
					row +=1
					text = 'tauT'+str(i)
					self.paramFactory(paraTxt=text,setDec=4,setSingStep=0.01, paraMin=-1,paraMax=1,row=row,param=param)
					self.labelArray.append(' '+text)
					row +=1
			if self.def_options['Triplet_eq'] == 3:
				#Triplet State equation2
				for i in range(1,self.tripNumSpecSpin.value()+1):
				
					text = 'T'+str(i)
					self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=-1,paraMax=1,row=row,param=param)
					self.labelArray.append(' '+text)
					row +=1
					text = 'tauT'+str(i)
					self.paramFactory(paraTxt=text,setDec=3,setSingStep=0.01, paraMin=-1,paraMax=1,row=row,param=param)
					self.labelArray.append(' '+text)
					row +=1
			self.fitTable.setVerticalHeaderLabels(self.labelArray)
			self.fitTable.setRowCount(row)
				
				
	
			
			
	
	
	def create_status_bar(self):
		self.status_text = QtGui.QLabel("Please load a data file")
		self.statusBar().addWidget(self.status_text, 1)

	def create_menu(self):        
		self.file_menu = self.menuBar().addMenu("&File")
		
		load_action = self.create_action("&Load file",
			shortcut="Ctrl+L", slot=self.load_file, tip="Load a file")
		quit_action = self.create_action("&Quit", slot=self.close, 
			shortcut="Ctrl+Q", tip="Close the application")
		
		self.add_actions(self.file_menu, 
			(load_action, None, quit_action))
			
		self.help_menu = self.menuBar().addMenu("&Help")
		about_action = self.create_action("&About", 
			shortcut='F1', slot=self.on_about, 
			tip='About the demo')
		
		self.add_actions(self.help_menu, (about_action,))

	def add_actions(self, target, actions):
		for action in actions:
			if action is None:
				target.addSeparator()
			else:
				target.addAction(action)

	def create_action(  self, text, slot=None, shortcut=None, 
						icon=None, tip=None, checkable=False, 
						signal="triggered()"):
		action = QtGui.QAction(text, self)
		if icon is not None:
			action.setIcon(QIcon(":/%s.png" % icon))
		if shortcut is not None:
			action.setShortcut(shortcut)
		if tip is not None:
			action.setToolTip(tip)
			action.setStatusTip(tip)
		if slot is not None:
			self.connect(action, QtCore.SIGNAL(signal), slot)
		if checkable:
			action.setCheckable(True)
		return action
	def updateParam(self):
		"""Depending on the options this function will update the params of the current data set. """
		self.objId_sel.param = Parameters()
		self.objId_sel.param.add('DC', value= self.DC_value.value(),min=self.DC_min.value(),max=self.DC_max.value(),vary=self.DC_vary.isChecked())
		self.objId_sel.param.add('GN0', value= self.GN0_value.value(),min=self.GN0_min.value(),max=self.GN0_max.value(),vary=self.GN0_vary.isChecked())
		for i in range(1,self.def_options['Diff_species']+1):
		#for i in range(1,self.diffNumSpecSpin.value()+1):
				#if i ==1:
				text = 'A'+str(i);
				exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
				self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
				#if i ==2:
					#text = 'A'+str(i);
					#self.objId_sel.param.add(text, expr='1.0-A1')w
				text = 'txy'+str(i)
				exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
				self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
				
				
				text = 'alpha'+str(i) 
				exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
				self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
			   
				#2 in this case corresponds to 3D:
				if self.def_options['Dimen'] == 2:
					if self.def_options['Diff_eq'] == 1:
						text = 'tz'+str(i)
						try:
							exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
							self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
						except:
							self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

					if self.def_options['Diff_eq'] == 2:
						text = 'AR'+str(i)
						try:
							exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
							self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
						except:
							self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

		if self.def_options['Triplet_eq'] == 2:
				#Triplet State equation1
				for i in range(1,self.tripNumSpecSpin.value()+1):
					text = 'B'+str(i)
					try:
						exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
						self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
					except:
						self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

					text = 'tauT'+str(i)
					try:
						exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
						self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
					except:
						self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

		if self.def_options['Triplet_eq'] == 3:
				#Triplet State equation2
				for i in range(1,self.tripNumSpecSpin.value()+1):
					text = 'T'+str(i)
					try:
						exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
						self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
					except:
						self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

					text = 'tauT'+str(i)
					try:
						exec("valueV = self."+text+"_value.value()"); exec("minV = self."+text+"_min.value()"); exec("maxV = self."+text+"_max.value()"); exec("varyV = self."+text+"_vary.isChecked()");
						self.objId_sel.param.add(text, value=valueV ,min=minV,max=maxV,vary=varyV)
					except:
						self.objId_sel.param.add(text, value=self.def_param[text].value ,min=self.def_param[text].min,max=self.def_param[text].max,vary=self.def_param[text].vary)

				  
			

		
	def updateParamFirst(self):
		self.updateParam()
		self.defineTable()
	def updateTableFirst(self):
		self.defineTable()
		self.updateParam()
	def fit_equation(self):
	   
		
		if self.objId_sel.toFit == True:
			self.objId_sel.fitToParameters()
			self.fill_series_list()
	def fitAll_equation(self):
		"""Take the active parameters and applies them to all the other data which is not filtered"""
		#Make sure all table properties are stored
		self.updateParam()

		for objId in self.objIdArr:
			if objId.toFit == True:
				
				objId.param = Parameters();
				objId.param = self.objId_sel.param
				objId.fitToParameters()
		
		
			   
		self.fill_series_list()
	
		

class draggableLine:
	"""Prototype class for the draggable lines """
	def __init__(self, line, parent):
		self.type =None
		self.line = line
		self.press = None
		self.xpos = 0
		self.parent = parent
		#self.trans = trans

	def connect(self):
		'connect to all the events we need'
		self.cidpress = self.line.figure.canvas.mpl_connect(
			'button_press_event', self.on_press)
		self.cidrelease = self.line.figure.canvas.mpl_connect(
			'button_release_event', self.on_release)
		self.cidmotion = self.line.figure.canvas.mpl_connect(
			'motion_notify_event', self.on_motion)

	def on_press(self, event):
		'on button press we will see if the mouse is over us and store some data'
		if event.inaxes != self.line.axes: return
		contains, attrd = self.line.contains(event)
		if not contains: return
		self.press = True
		

	def on_motion(self, event):
		'on motion we will move the rect if the mouse is over us'
		if self.press is None: return
		if event.inaxes != self.line.axes: return
		if self.type == 'left':
			if(event.xdata < self.parent.dr1.xpos):
				self.line.set_xdata(event.xdata)
				self.xpos = event.xdata
				
			#else:
			#    self.line.set_xdata(form.dr1.xpos-3)

		if self.type == 'right':
			
			if(event.xdata > self.parent.dr.xpos):
				self.line.set_xdata(event.xdata)
				self.xpos = event.xdata
				
		
		
		self.line.figure.canvas.draw()
	def just_update(self):
			self.line.set_xdata(self.xpos)

			self.line.figure.canvas.draw()


	def on_release(self, event):
		'on release we reset the press data'
		
	   
		if(self.press == True):
			self.line.figure.canvas.draw()
			
			#Get the scale locally
			#scale = self.data.get_series_scale(form.names[0])
			#convert line coordinate
			xdat = np.array(event.xdata).astype(np.float64)
			#Find the index of the nearest point in the scale.
			#indx = int(np.argmin(np.abs(scale - xdat)))
			indx = xdat
			if(self.type =='left'):
				self.parent.left = indx
				self.parent.fit_btn_min.setValue(event.xdata)
				self.parent.fit_btn_min.index =int(np.argmin(np.abs(self.parent.scale -  self.parent.dr.xpos)))
			else:
				self.parent.right  = indx
				self.parent.fit_btn_max.setValue(event.xdata)
				self.parent.fit_btn_max.index =int(np.argmin(np.abs(self.parent.scale -  self.parent.dr1.xpos)))
				#self.parent.fit_btn_max.setText(str(self.xpos))
		   
		#self.parent.rescale_plot()
		self.press = None
	def disconnect(self):
		'disconnect all the stored connection ids'
		self.line.figure.canvas.mpl_disconnect(self.cidpress)
		self.line.figure.canvas.mpl_disconnect(self.cidrelease)
		self.line.figure.canvas.mpl_disconnect(self.cidmotion)
class comboBoxSp2(QtGui.QComboBox):
	"""class which is used for multiple dynamic drop-down lists.
	including the model parameter selection."""
	def __init__(self, parent=None):
		QtGui.QComboBox.__init__(self, parent)
		self.activated[str].connect(self.__activated) 
		self.obj = []
		self.TGid =[]
		self.type = []
		self.selected_name =[]
		self.model_obj_list =[]
		self.parent = parent
		self.objId_ind = 0
		self.model_obj_ind_list = [0]
	def __activated(self,selected):
		#Saves parameters.
		self.parent.updateParam()
		self.parent.def_options[self.type] = self.currentIndex()+1
		
		
		self.parent.defineTable()
class spinBoxSp3(QtGui.QDoubleSpinBox):
	def __init__(self,parent):
		QtGui.QDoubleSpinBox.__init__(self,parent)
		self.setDecimals(5)
		self.setMaximum(10000)
		self.start =[]
		self.array =[9,3,2,65,34]
		self.index = 3
		self.setValue(self.array[self.index])
		self.parent = parent

		
	def stepBy(self,val):
		"""When user clicks the up or down iterator"""
		ind = self.index + val
		if ind > -1 and ind < self.array.__len__():
			self.index += val
			self.setValue((self.array[self.index]))
			if self.type == 'min':
				self.parent.dr.xpos = self.array[self.index]
				self.parent.dr.just_update()
			if self.type == 'max':
				self.parent.dr1.xpos = self.array[self.index]
				self.parent.dr1.just_update()
	def stepEnabled(self):  
		return QtGui.QAbstractSpinBox.StepUpEnabled | QtGui.QAbstractSpinBox.StepDownEnabled 
	def onEdit(self):
		"""Called when user manually changes test"""
		if self.type == 'min':
			self.parent.dr.xpos = self.value()
			self.parent.dr.just_update()
		if self.type == 'max':
			self.parent.dr1.xpos = self.value()
			self.parent.dr1.just_update()






			


def pyqt_set_trace():
	'''Set a tracepoint in the Python debugger that works with Qt'''
	from PyQt4.QtCore import pyqtRemoveInputHook
	import pdb
	import sys
	pyqtRemoveInputHook()
	# set up the debugger
	debugger = pdb.Pdb()
	debugger.reset()
	# custom next to get outside of function scope
	debugger.do_next(None) # run the next command
	users_frame = sys._getframe().f_back # frame where the user invoked `pyqt_set_trace()`
	debugger.interaction(users_frame, None)



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	form = Form()
	form.show()
	app.exec_()
	
	
	
	
	
	 