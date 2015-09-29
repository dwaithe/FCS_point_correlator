
import sys, os, csv
from PyQt4 import QtCore, QtWebKit
from PyQt4 import QtGui
from scipy.special import _ufuncs_cxx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
from matplotlib.transforms import ScaledTranslation
import matplotlib.gridspec as gridspec
import numpy as np
from fitting_extended import TableFilterBox, visualHisto, visualScatter
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
import time
import errno
import copy
import os.path
import subprocess
import pyperclip
import cPickle as pickle
import copy
from fitting_methods import update_param_fcs, calc_param_fcs, decide_which_to_show, initialise_fcs
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
			filepath =  QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.filepath_save_profile,'Fit Profile(*.profile);;')
			if filepath != '':
				opened_file = pickle.load(open(str(filepath),"rb"));
				self.parent.fit_profile = opened_file;
		if self.type == 'profile_save':
			
			
			#filepath = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
			filepath =  QtGui.QFileDialog.getSaveFileName(self, 'Open file',self.filepath_save_profile,'Fit Profile(*.profile);;')
			if filepath != '':
				self.filepath_save_profile = str(QtCore.QFileInfo(filepath).absolutePath())+'/'

				self.parent.config['filepath_save_profile']  = self.filepath_save_profile
				#Save the files to the 
				pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "w" ))
				#Save the 
				pickle.dump(self.parent.fit_profile, open(str(filepath),"w"));

				


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
		self.colors = ['blue','green','red','cyan','magenta','black']  
			#Default parameters for each loaded file.
		#self.def_param = Parameters()
		
		#Initialise the FCS variables
	   	initialise_fcs(self)
		
		self.series_list_model = QtGui.QStandardItemModel()
		self.series_list_model.itemChanged.connect(self.item_edited)
		
		self.create_menu()
		self.create_main_frame()
		
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
					corrObj1.siblings = [corrObj2]
					corrObj2.siblings = [corrObj1]
						
				if self.ext == 'CSV' or self.ext == 'csv':
					self.corrObj = corrObject(filename,self)
					self.corrObj.siblings = None
					self.corrObj.objId.load_from_file(0)

				#self.corrObj.objId.param = self.def_param
				#Where we add the names.
				self.fill_series_list()
				
				self.image_status_text.showMessage("Loaded " + filename)
				self.image_status_text.setStyleSheet("QLabel {  color : green }")
		
				
		
	   
		
	   

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
		try:
			self.canvas.mpl_disconnect(self.cid)
		except:
			'fail'
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
		row_checked = 0
		def onpick(event):
			thisline = event.artist
			xdata = thisline.get_xdata()
			ydata = thisline.get_ydata()
			ind = event.ind
			

			#Finds the model which has been clicked based on the label association.
			for objId in self.objIdArr:
				objId.clicked = False
				if str(objId) == str(thisline.get_label()):
					objId.clicked = True
					#self.axes.plot(objId.autotime, objId.autoNorm, 'o',markersize=2, color="red", label=objId,picker=4.0,alpha=alpha)
					#self.canvas.draw()
			self.fill_series_list()
		for objId in self.objIdArr:
			if objId.toFit == True:
				model_index = self.series_list_model.index(row, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)
				objId.checked = checked
				if objId.filter ==True:
					alpha = 0.1;
				else:
					alpha = 1.0
				
				if checked:
					
					has_series = True
					#Takes the values from the interface 
					self.axes.set_xscale('log')
					self.axes2.set_xscale('log')
					self.scale = objId.autotime
					
					self.series = objId.autoNorm
					
					
					self.axes.plot(self.scale, self.series, 'o',markersize=2, color="grey", label=objId,picker=4.0,alpha=alpha)
					

					self.axes.set_autoscale_on(False)
					row_checked += 1


				#if self.setAutoScale == False:

					#self.axes.set_ylim(bottom=float(objId.param['offset'].value)-0.001)
				row += 1  
		row = 0;
		
		
		for objId in self.objIdArr:
			if objId.toFit == True:
				model_index = self.series_list_model.index(row, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)
				if objId.filter ==True:
					alpha = 0.1;
				else:
					alpha = 1.0
				
				
				if checked:
					has_series = True
					#Takes the values from the interface 
					if objId.model_autoNorm !=[]:
						self.mod_scale = objId.model_autotime

						self.mod_series = objId.model_autoNorm
						
							#self.colors[row % len(self.colors)]
						self.axes.plot(self.mod_scale, self.mod_series, '-', color="blue", label=objId,picker=4.0, alpha=alpha)       
						
						maxValue = np.max(objId.residualVar)
						minValue = np.min(objId.residualVar)
						if maxValue > scaleMax:
							scaleMax = maxValue
						if minValue < scaleMin:
							scaleMin = minValue
						self.axes2.set_ylim([scaleMin,scaleMax])
						self.axes2.plot(self.mod_scale,objId.residualVar,color="grey",label=objId.name,alpha=alpha)
						self.axes2.set_ylim([scaleMin,scaleMax])
						
				row +=1        
				   
		self.cid = self.canvas.mpl_connect('pick_event',onpick)	
		if(self.series_list_model.rowCount()>0 and row_checked>0):
			
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
						
						xpos1 = np.argmax(self.scale >0)
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
		
		#if self.legend_cb.isChecked():
		#	self.axes.legend(loc=3,prop={'size':8})
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
				<p>offset + (GN0*GDiff*GT)</p>
				
				<br />
				
			  </form>
			</body>
		  </html>
		''')
		layout.addWidget(self.view)
		self.about_win.setLayout(layout)
		self.about_win.show()
		self.about_win.raise_()
	def item_edited(self,model_index):
		"""If the text is edited this will update the name of the object"""
		for objId in self.objIdArr:
			item = objId.series_list_id
			objId.name = item.text()

	def fill_series_list(self):
		
		self.series_list_model.clear()
		to_focus_item = None
		to_focus = 0
		for objId in self.objIdArr:
				
				#Find details of each dataset
				name = objId.name
				item = QtGui.QStandardItem(name)
				objId.filter = False
				objId.toFit = True


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
				
				for filt in self.tfb.filter_list:
					if objId.filter == False:
						if filt[1] == '>':
							
							if objId.param[filt[0]]['value'] < float(filt[2]):
								if filt[3]  == 0:
									#show
									objId.toFit = True
									objId.filter = False
								if filt[3]  == 1:
									#apply
									objId.toFit = True
									objId.filter =True
								if filt[3] == 2:
									#off
									objId.toFit = False
									objId.filter = False
							else:
								objId.filter = False
								
								
							
								
						else:
							if objId.param[filt[0]]['value'] > float(filt[2]):
								if filt[3]  == 0:
									objId.toFit = True
									objId.filter = False
								if filt[3]  == 1:
									objId.toFit = True
									objId.filter = True
								if filt[3] == 2:
									objId.toFit = False
									objId.filter = False
							else:
								objId.filter = False
						
							


				

				
				if objId.toFit == True:
					#Context sensitive colour highlighting

					#if objId.goodFit == False:
					#	item.setBackground(QtGui.QColor('red'))
					#elif objId.fitted == True:
					#	item.setBackground(QtGui.QColor('green'))
					#else:    
					#	item.setBackground(QtGui.QColor('white'))
					if objId.clicked == True:
						item.setBackground(QtGui.QColor(0, 0, 255, 127))
						to_focus = self.series_list_model.rowCount()
						to_focus_item = item


				
				
					item.setCheckable(True)
					self.series_list_model.appendRow(item)
		if to_focus_item != None:
			self.series_list_view.scrollTo(self.series_list_model.indexFromItem(to_focus_item))
		
		self.updateFitList()

				
	
	def create_main_frame(self):
		"""Creates the main layout of the fitting interface """
		self.main_frame = QtGui.QWidget()
		
		plot_frame = QtGui.QWidget()
		
		self.dpi = 300
		self.fig = Figure((8.0, 16.0), )
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

		text_default_profile = QtGui.QLabel('Profile:')

		load_default_profile = QtGui.QPushButton('load')
		self.load_default_profile_output = folderOutput(self)
		self.load_default_profile_output.type = 'profile_load'
		
		save_default_profile = QtGui.QPushButton('save')
		self.save_default_profile_output = folderOutput(self)
		self.save_default_profile_output.type = 'profile_save'

		store_default_profile = QtGui.QPushButton('store')
		apply_default_profile = QtGui.QPushButton('apply')
		
		default_profile_panel.addWidget(text_default_profile)
		default_profile_panel.addWidget(load_default_profile)
		default_profile_panel.addWidget(save_default_profile)
		default_profile_panel.addWidget(store_default_profile)
		default_profile_panel.addWidget(apply_default_profile)

		
		save_default_profile.clicked.connect(self.save_default_profile_fn)
		load_default_profile.clicked.connect(self.load_default_profile_fn)
		store_default_profile.clicked.connect(self.store_default_profile_fn)
		apply_default_profile.clicked.connect(self.apply_default_profile_fn)


		#Spin box for number of diffusing species
		
		tripNumSpecLabel = QtGui.QLabel('Triplet states')
		self.tripNumSpecSpin = QtGui.QSpinBox()
		self.tripNumSpecSpin.setRange(1,3);
		self.tripNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(tripNumSpecLabel)
		diffNumSpecies.addWidget(self.tripNumSpecSpin)
		diffNumSpecies.addStretch()
		
		
		

		
			#Table which has the fitting
		self.fitTable = QtGui.QTableWidget()
		

		
		#self.fitTable.setMinimumWidth(320)
		self.fitTable.setMaximumWidth(400)
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
		#self.legend_cb = QtGui.QCheckBox("Show L&egend")
		#self.legend_cb.setChecked(False)
		#legend_box.addWidget(self.legend_cb)
		

		self.right_check_all_none = QtGui.QPushButton("check all")
		self.show_button = QtGui.QPushButton("Plot Checked Data")
		
		self.switch_true_false = True



		legend_box.addWidget(self.show_button)
		legend_box.addWidget(self.right_check_all_none)
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
		self.right_check_all_none.clicked.connect(self.check_all_none)
		self.connect(self.show_button, QtCore.SIGNAL('clicked()'), self.on_show)
		right_vbox.addLayout(right_ch_check)

		

		right_vbox.addWidget(self.right_check_all_none)
		self.remove_btn = QtGui.QPushButton("Remove Highlighted Data")
		self.remove_btn.clicked.connect(self.removeDataFn)
		self.create_average_btn = QtGui.QPushButton("Create average of Highlighted")
		self.create_average_btn.clicked.connect(self.create_average_btn_fn)
		self.clearFits_btn = QtGui.QPushButton("Clear Fit Data All/Highlighted")
		self.clearFits_btn.clicked.connect(self.clearFits)
		self.visual_histo = visualHisto(self)
		visual_histo_btn = QtGui.QPushButton("Generate Histogram");
		visual_histo_btn.clicked.connect(self.visual_histo.create_main_frame)
		self.visual_scatter = visualScatter(self)
		visual_scatter_btn = QtGui.QPushButton("Generate Scatter");
		visual_scatter_btn.clicked.connect(self.visual_scatter.create_main_frame)

		right_vbox.addWidget(self.remove_btn)
		right_vbox.addWidget(self.create_average_btn)
		right_vbox.addWidget(self.clearFits_btn)
		right_vbox.addWidget(visual_histo_btn)
		right_vbox.addWidget(visual_scatter_btn)
		right_vbox.addStretch(1)

		filter_box = QtGui.QHBoxLayout()
		right_vbox.addLayout(filter_box)


		self.tfb = TableFilterBox(self)


		filter_box.addWidget(self.tfb)
		self.filter_add_panel = QtGui.QHBoxLayout()
		self.filter_select = QtGui.QComboBox()
		self.filter_select.setMaximumWidth(100)
		

		for item in self.def_param:
			self.filter_select.addItem(item)

		self.filter_lessthan = QtGui.QComboBox()
		self.filter_lessthan.addItem('<')
		self.filter_lessthan.addItem('>')
		self.filter_lessthan.setMaximumWidth(50)
		self.filter_value = QtGui.QLineEdit('10.0')
		self.filter_value.setMaximumWidth(50)
		self.filter_value.setMinimumWidth(50)
		self.filter_add = QtGui.QPushButton('add')
		self.filter_add_panel.addWidget(self.filter_select)
		self.filter_add_panel.addWidget(self.filter_lessthan)
		self.filter_add_panel.addWidget(self.filter_value)
		self.filter_add_panel.addWidget(self.filter_add)
		right_vbox.addLayout(self.filter_add_panel)
		

		self.filter_add.clicked.connect(self.tfb.filter_add_fn)
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

		self.image_status_text = QtGui.QStatusBar()
		
		self.image_status_text.showMessage("Please load a data file. ")
		self.image_status_text.setStyleSheet("QLabel {  color : green }")
		left_vbox.addWidget(self.image_status_text)

		hbox.addWidget(splitter)
		self.defineTable()
		self.main_frame.setLayout(hbox)

		self.setCentralWidget(self.main_frame)
	
		
		

	def create_average_btn_fn(self):
		#Reads those indices which are highlighted.
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		for v_ind in listToFit:
			#Finds the unique item names which are currently selected.
			indList.append(self.series_list_model.itemFromIndex(v_ind))
		
		series_2_average = []
		for i in range(self.objIdArr.__len__()-1,-1,-1):
			#Looks through the objects in objIdArr and deletes them if they match.
			for indL in indList:
				if self.objIdArr[i].series_list_id == indL:
					
					series_2_average.append(self.objIdArr[i].autoNorm)
					if series_2_average.__len__() == 1:
						autotime = self.objIdArr[i].autotime
						sum_auto = np.sum(np.array(autotime))
					else:
						if np.sum(self.objIdArr[i].autotime) != sum_auto:
							series_2_average.pop(-1)

					break
		if series_2_average == []:
			return
		matrix_2_average = np.zeros((series_2_average.__len__(),series_2_average[0].__len__()))

		for i in range(0,series_2_average.__len__()):
			matrix_2_average[i,:] = series_2_average[i]

		average_out = np.average(matrix_2_average,0)


		corrObj1 = corrObject(None,self);
		corrObj1.siblings = None
		self.objIdArr.append(corrObj1.objId)
		corrObj1.param = copy.deepcopy(self.def_param)
		corrObj1.ch_type = 0
		corrObj1.prepare_for_fit()
		
		corrObj1.kcount = None #objId.kcountCH0[i]
		corrObj1.numberNandB = None #objId.numberNandBCH0[i]
		corrObj1.brightnessNandB = None #objId.brightnessNandBCH0[i]
		corrObj1.type = "scan"
		#corrObj1.siblings = None

		
		corrObj1.name = 'average_data'
		corrObj1.autotime = autotime
		corrObj1.autoNorm = average_out

		self.fill_series_list()
		

		

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
		
		self.def_options = self.fit_profile['def_options']
		self.diffNumSpecSpin.setValue(self.def_options['Diff_species'])
		self.tripNumSpecSpin.setValue(self.def_options['Triplet_species'])
		self.objId_sel.param = copy.deepcopy(self.fit_profile['param'])


		self.diffModEqSel.setCurrentIndex(self.def_options['Diff_eq']-1)
		self.tripModEqSel.setCurrentIndex(self.def_options['Triplet_eq']-1)
		self.dimenModSel.setCurrentIndex(self.def_options['Dimen']-1)
		
		self.defineTable()
		
		
		self.updateParamFirst()
	def save_default_profile_fn(self):
		
		self.fit_profile = {}
		
		self.fit_profile['param'] = copy.deepcopy(self.objId_sel.param)
		self.fit_profile['def_options'] = self.def_options
		
		self.save_default_profile_output.showDialog()
	def store_default_profile_fn(self):
		
		self.fit_profile = {}
		
		self.fit_profile['param'] = copy.deepcopy(self.objId_sel.param)
		self.fit_profile['def_options'] = self.def_options
		self.image_status_text.showMessage('Profile stored, use the \'Apply\' button to apply.')
		
	def apply_default_profile_fn(self):
		self.def_options = self.fit_profile['def_options']
		self.diffNumSpecSpin.setValue(self.def_options['Diff_species'])
		self.tripNumSpecSpin.setValue(self.def_options['Triplet_species'])
		self.objId_sel.param = copy.deepcopy(self.fit_profile['param'])


		self.diffModEqSel.setCurrentIndex(self.def_options['Diff_eq']-1)
		self.tripModEqSel.setCurrentIndex(self.def_options['Triplet_eq']-1)
		self.dimenModSel.setCurrentIndex(self.def_options['Dimen']-1)
		
		self.defineTable()
		
		
		self.updateParamFirst()
		self.image_status_text.showMessage('Profile Applied.')

	def fitSelected_equation(self):
		
		listToFit = self.series_list_view.selectedIndexes()
		indList =[];
		for v_ind in listToFit:
			#Finds the unique item names which are currently selected.
			indList.append(self.series_list_model.itemFromIndex(v_ind))

		c = 0;
		
		for i in range(self.objIdArr.__len__()-1,-1,-1):
			#Fits the ones which are highlighted.
			for indL in indList:
				if self.objIdArr[i].series_list_id == indL:
					c = c+1
					self.objIdArr[i].param = copy.deepcopy(self.objId_sel.param)
					self.objIdArr[i].fitToParameters()
					self.image_status_text.showMessage("Fitting  "+str(c)+" of "+str(indList.__len__())+" plots.")
					self.app.processEvents()
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
		#Makes sure there are files to be had.
		try:
			curr_name = self.objIdArr[self.modelFitSel.model_obj_ind_list[self.modelFitSel.currentIndex()]]
		except:
			curr_name = None

					

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
		
		if name_found == False and self.modelFitSel.model_obj_list !=[]:
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
		for item in self.order_list:
			if self.objId_sel.param[item]['to_show'] == True:
				if  self.objId_sel.param[item]['calc'] == False:
					keyArray.append(str(self.objId_sel.param[item]['alias']))
					keyArray.append('stdev('+str(self.objId_sel.param[item]['alias'])+')')
				else:
					keyArray.append(str(self.objId_sel.param[item]['alias']))

				
		
		
		

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
		
	  	
		#Opens export files
		outPath = self.folderOutput.filepath
		filenameTxt = str(self.fileNameText.text())
		if copy_fn == False:
			csvfile = open(outPath+'/'+filenameTxt+'_outputParam.csv', 'a')
			spamwriter = csv.writer(csvfile)
			spamwriter.writerow(keyArray)
		for v_ind in indList:
			
				
			if(self.objIdArr[v_ind].toFit == True):
				if(self.objIdArr[v_ind].fitted == True):
					param = self.objIdArr[v_ind].param
					rowText = []
					rowText.append(str(self.objIdArr[v_ind].name))
					rowText.append(str(self.objIdArr[v_ind].localTime))
					rowText.append(str(self.diffModEqSel.currentText()))
					rowText.append(str(self.def_options['Diff_species']))
					rowText.append(str(self.tripModEqSel.currentText()))
					rowText.append(str(self.def_options['Triplet_species']))
					rowText.append(str(self.dimenModSel.currentText()))
					rowText.append(str(self.objIdArr[v_ind].model_autotime[0]))
					rowText.append(str(self.objIdArr[v_ind].model_autotime[-1]))
					for item in self.order_list:
						
							if  param[item]['calc'] == False:
								if param[item]['to_show'] == True:
									rowText.append(str(param[item]['value']))
									rowText.append(str(param[item]['stderr']))
							else:
								if param[item]['to_show'] == True:
									rowText.append(str(param[item]['value']))
								else:
									rowText.append(str(' '))
					if copy_fn == True:
						copyStr += str('\t'.join(rowText)) +'\n'
					if copy_fn == False:
						spamwriter = csv.writer(csvfile,  dialect='excel')
						spamwriter.writerow(rowText)

		if copy_fn == True:
			copyStr += str('end\n')
			pyperclip.copy(copyStr)
		else:
			csvfile.close()
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
			self.objIdArr[v_ind].param = copy.deepcopy(self.def_param)
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
				


	def paramFactory(self,paraTxt,setDec,paraMin,paraMax,setSingStep,row,param):
				"""UI factory function"""
				#exec("self."+paraTxt+"_label = QtGui.QLabel()");
				
				
				exec("self."+paraTxt+"_value = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_value.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_value.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_value.setRange("+str(paraMin)+","+str(paraMax)+")");
				
				try:
					exec("self."+paraTxt+"_value.setValue(float(param[\'"+paraTxt+"\']['value']))");
				except:
					
					exec("self."+paraTxt+"_value.setValue(float(self.def_param[\'"+paraTxt+"\']['value']))");
				
				exec("self."+paraTxt+"_vary = QtGui.QCheckBox()");
				checkCont = QtGui.QHBoxLayout()
				try:
					exec("self."+paraTxt+"_vary.setChecked(param[\'"+paraTxt+"\']['vary'])");
				except:
					exec("self."+paraTxt+"_vary.setChecked(self.def_param[\'"+paraTxt+"\']['vary'])");
				exec("self."+paraTxt+"_min = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_min.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_min.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_min.setRange("+str(paraMin)+","+str(paraMax)+")");
				
				try:
					exec("self."+paraTxt+"_min.setValue(float(param[\'"+paraTxt+"\']['minv']))");
				except:
					exec("self."+paraTxt+"_min.setValue(float(self.def_param[\'"+paraTxt+"\']['minv']))");
				exec("self."+paraTxt+"_max = QtGui.QDoubleSpinBox()");
				exec("self."+paraTxt+"_max.setDecimals("+str(setDec)+")");
				exec("self."+paraTxt+"_max.setSingleStep("+str(setSingStep)+")");
				exec("self."+paraTxt+"_max.setRange("+str(paraMin)+","+str(paraMax)+")");
				exec("self."+paraTxt+"_label = QtGui.QLabel()");
				try:
					exec("self."+paraTxt+"_max.setValue(float(param[\'"+paraTxt+"\']['maxv']))");
				except:
					 exec("self."+paraTxt+"_max.setValue(float(self.def_param[\'"+paraTxt+"\']['maxv']))");
				
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
			
			
			self.fitTable.setColumnWidth(0,75);
			self.fitTable.setColumnWidth(1,32);
			self.fitTable.setColumnWidth(2,75);
			self.fitTable.setColumnWidth(3,75);
			row = 0;
			self.fitTable.repaint()
			self.fitTable.reset()
			self.labelArray =[]

			
			
			#If data is present in the array.
			if self.objIdArr != []:
				#Finds the active data set from the combo box.
				if  self.modelFitSel.model_obj_list != []:
					self.objId_sel = self.modelFitSel.model_obj_list[self.modelFitSel.currentIndex()]
					decide_which_to_show(self)
					calc_param_fcs(self,self.objId_sel)
					param = copy.deepcopy(self.objId_sel.param)
				else:
					param = copy.deepcopy(self.def_param)
			else:
				param = copy.deepcopy(self.def_param)

			#For the filter list we redefine the options.
			self.filter_select.clear()
			
			col =0
			for item in self.order_list:
				
				if param[item]['to_show'] == True:

					self.filter_select.addItem(item)
					if param[item]['calc'] == False:
						self.paramFactory(paraTxt=item,setDec=4,paraMin=-1.0,paraMax=100000,setSingStep=0.01,row=row, param=param)
						self.labelArray.append(' '+param[item]['alias'])
						row +=1
					else:
						if col == 0:
							label = QtGui.QLabel(' '+str(np.round(param[item]['value'],3)))
							self.fitTable.setCellWidget(row, 0, label)
							self.labelArray.append(' '+param[item]['alias'])
							
							col = 2
							row +=1
							continue;
						if col ==2:
							label = QtGui.QLabel(' '+str(np.round(param[item]['value'],3)))
							label_2 = QtGui.QLabel(str(' '+param[item]['alias']))
							self.fitTable.setCellWidget(row-1, 3, label)
							self.fitTable.setCellWidget(row-1, 2,label_2)
							
							col = 0

			self.fitTable.setVerticalHeaderLabels(self.labelArray)
			self.fitTable.setRowCount(row)

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
		update_param_fcs(self)
	def update_calc(self,objId):
		calc_param_fcs(self,objId)
		
	def updateParamFirst(self):
		self.updateParam()
		self.defineTable()
	def updateTableFirst(self):
		self.defineTable()
		self.updateParam()
	def fit_equation(self):
	   
		self.updateParamFirst()
		if self.objId_sel.toFit == True:
			self.objId_sel.fitToParameters()
			self.update_calc(self.objId_sel)
			self.fill_series_list()
			self.on_show()	
	def fitAll_equation(self):
		"""Take the active parameters and applies them to all the other data which is not filtered"""
		#Make sure all table properties are stored
		self.updateParamFirst()
		c = 0;
		for objId in self.objIdArr:
			if objId.toFit == True:
				c = c+1
				if objId != self.objId_sel:
					#objId.param = Parameters();
					objId.param = copy.deepcopy(self.objId_sel.param)
				
				objId.fitToParameters()
				self.update_calc(objId)
				self.image_status_text.showMessage("Fitting  "+str(c)+" of "+str(self.modelFitSel.model_obj_ind_list.__len__())+" images.")
				self.app.processEvents()


		
		
		self.on_show()	   
		self.fill_series_list()
	
		

class draggableLine:
	"""Prototype class for the draggable lines """
	def __init__(self, line, parent):
		self.type =None
		self.line = line
		self.press = None
		self.xpos = 1
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
		#self.parent.updateParam()
		#self.parent.objId_sel = self.parent.modelFitSel.model_obj_list[self.parent.modelFitSel.currentIndex()]

		#Store the existing parameters.
		self.parent.def_options[self.type] = self.currentIndex()+1
		self.parent.updateParam()
		
		#Update the table display.
		decide_which_to_show(self.parent)
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
			try:
				self.parent.dr.xpos = self.value()
				self.parent.dr.just_update()
			except:
				pass
		if self.type == 'max':
			try:
				self.parent.dr1.xpos = self.value()
				self.parent.dr1.just_update()
			except:
				pass






			


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
	
	
	
	
	
	 