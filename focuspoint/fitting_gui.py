import sys, os, csv
from PyQt5 import QtCore
from PyQt5 import QtGui

from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView,QWebEnginePage as QWebPage
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QComboBox, QDoubleSpinBox, QAction, QWidget, QLabel,QTreeView,QAbstractItemView
from PyQt5.QtWidgets import QSpinBox,QListView,QHBoxLayout,QPushButton,QTextEdit,QTableWidget,QVBoxLayout,QLineEdit,QSplitter
from PyQt5.QtWidgets import QCheckBox, QStatusBar,QAbstractSpinBox, QWidget, QFileDialog, qApp, QShortcut
from PyQt5.QtGui import QStandardItem, QColor, QIcon, QKeySequence

from scipy.special import _ufuncs_cxx

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.transforms import ScaledTranslation
import matplotlib.gridspec as gridspec
import numpy as np
from focuspoint.fitting_extended import TableFilterBox, visualHisto, visualScatter
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
import time
import errno
import copy
import os.path
import subprocess
import pyperclip
import pickle

from focuspoint.fimport_methods import fcs_import_method,sin_import_method,csv_import_method, saveOutputDataFn
import focuspoint.fitting_methods.fitting_methods_SE as SE
import focuspoint.fitting_methods.fitting_methods_GS as GS
import focuspoint.fitting_methods.fitting_methods_VD as VD
import focuspoint.fitting_methods.fitting_methods_PB as PB


from focuspoint.correlation_objects import corrObject

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

class folderOutput(QMainWindow):
	
	def __init__(self,parent):
		super(folderOutput, self).__init__()
	   
		self.initUI()
		self.parent = parent
		self.parent.config ={}
		
		try:
			self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ))
			self.filepath = self.parent.config['output_filepath']
		except:
			self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
			try:
				os.makedirs(self.filepath)
			except OSError as exception:
				if exception.errno != errno.EEXIST:
					raise
		try:
			self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ))
			self.folder_to_process = self.parent.config['folder_to_process']
		except:
			self.folder_to_process = os.path.expanduser('~')+'/FCS_Analysis/output/'
			try:
				os.makedirs(self.folder_to_process)
			except OSError as exception:
				if exception.errno != errno.EEXIST:
					raise

		
		try:
			self.filepath_save_profile = self.parent.config['filepath_save_profile']
		except:
			self.filepath_save_profile = os.path.expanduser('~')+'/FCS_Analysis/output/'

		
		
	def initUI(self):      

		self.textEdit = QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QAction(QIcon('open.png'), 'Open', self)
		openFile.triggered.connect(self.showDialog)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openFile)       
		
		self.setGeometry(300, 300, 350, 500)
		self.setWindowTitle('Select a Folder')
		#self.show()
		
	def showDialog(self):

		if self.type == 'output_dir':
			
			tfilepath = str(QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
			
			if tfilepath !='':
				self.filepath = tfilepath
			#Save to the config file.
				self.parent.config['output_filepath'] = str(tfilepath)
				pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "wb" ))
		if self.type == 'folder_to_process':
			
			folder_to_process = str(QFileDialog.getExistingDirectory(self, "Select Directory",self.folder_to_process))
			
			if folder_to_process !='':
				self.folder_to_process = folder_to_process
				self.parent.config['folder_to_process'] = str(folder_to_process)
				pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "wb" ))
				
				paths_to_load = []
				files_to_load = [ f for f in os.listdir(folder_to_process) if os.path.isfile(os.path.join(folder_to_process,f)) ]
				for file_name in files_to_load:
					paths_to_load.append(folder_to_process+'/'+file_name)
				
				self.parent.load_series(paths_to_load)
		if self.type == 'profile_load':
			
			
			#filepath = QFileDialog.getOpenFileName(self, 'Open file', '/home')
			filepath =  QFileDialog.getOpenFileName(self, 'Open file',self.filepath_save_profile,'Fit Profile(*.profile);;')
			if filepath != '':
				opened_file = pickle.load(open(str(filepath),"rb"))
				self.parent.fit_profile = opened_file
		if self.type == 'profile_save':
			
			
			#filepath = QFileDialog.getOpenFileName(self, 'Open file', '/home')
			filepath =  QFileDialog.getSaveFileName(self, 'Open file',self.filepath_save_profile,'Fit Profile(*.profile);;')
			if filepath != '':
				self.filepath_save_profile = str(QtCore.QFileInfo(filepath).absolutePath())+'/'

				self.parent.config['filepath_save_profile']  = self.filepath_save_profile
				#Save the files to the 
				pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "wb" ))
				#Save the 
				pickle.dump(self.parent.fit_profile, open(str(filepath),"w"))

				


class Form(QMainWindow):
	def __init__(self, type,parent=None):
		super(Form, self).__init__(parent)
		self.setWindowTitle('FoCuS FCS fitting software.')
		
		#lines.
		self.left = 0
		self.right = 0
		self.activeObj = None
		self.objIdArr =[]
		self.objStruct = {}
		self.names = []
		self.setAutoScale =True
		self.colors = ['blue','green','red','orange','magenta','midnightblue','black']
		self.objId_sel = None
		self.root_name ={}
		self.win_obj = parent
		self.type = type
		self.chisqr = 0.05
		self.norm_to_one = False
		self.yscale_min = 0.
		self.yscale_max = 1.
		self.xscale_min = 0.0001
		self.xscale_max = 100000.
		self.dr = None
		self.dr1 = None
		

			#Default parameters for each loaded file.
		#self.def_param = Parameters()
		
		#Initialise the FCS variables
		SE.initialise_fcs(self)
		GS.initialise_fcs(self)
		VD.initialise_fcs(self)
		PB.initialise_fcs(self)
		self.order_list = ['offset','GN0','N_FCS','cpm','A1','A2','A3','txy1','txy2','txy3','tz1','tz2','tz3','alpha1','alpha2','alpha3','AR1','AR2','AR3','B1','B2','B3','T1','T2','T3','tauT1','tauT2','tauT3','N_mom','bri','CV','f0','overtb','ACAC','ACCC','above_zero','s2n']

		
		self.series_list_model = QtGui.QStandardItemModel()
		
		
		
		self.create_main_frame()
		
		#self.update_ui()
		self.on_show()
	def load_file(self, filename=None):

		load_fileInt = QFileDialog()
		try:
			f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'r')
			self.loadpath =f.readline()
			f.close() 
		except:
			self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'
		
		# The first index of the returned tuple contains the file list.
		files_to_load = load_fileInt.getOpenFileNames(self, 'Open a data file', self.loadpath, 'Supported Files (*.csv *.sin *.fcs);;All Files (*.*)')
		self.load_series(files_to_load)
		
		try:
			self.loadpath = str(QtCore.QFileInfo(files_to_load[0][0]).absolutePath())
			f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'w')
			f.write(self.loadpath)
			f.close()
		except:
			pass


	def load_series(self,files_to_load):
		counter = 0
		for file_path in  files_to_load[0]:
				self.nameAndExt = os.path.basename(str(file_path)).split('.')
				print("nameAndExt", file_path)
				self.name = self.nameAndExt[0]
				self.ext = self.nameAndExt[-1]
				#try:
				if self.ext == 'SIN' or self.ext == 'sin':
					sin_import_method(self,file_path)
				elif self.ext == 'fcs':
					fcs_import_method(self,file_path)
				elif self.ext == 'CSV' or self.ext == 'csv' :
					csv_import_method(self,file_path)
					
				else:
					
					self.image_status_text.showMessage("File format not recognised please request via github page.")
					self.image_status_text.setStyleSheet("color : red")
					return
				#Where we add the names.
				counter = counter+1
				self.image_status_text.showMessage("Applying to carpet: "+str(counter+1)+' of '+str(files_to_load.__len__()+1)+' selected.')
				self.app.processEvents()
				
		self.image_status_text.showMessage("Files loaded")
		self.image_status_text.setStyleSheet("color : green")
		self.fill_series_list()
				
		
	   
		
	   

		
	def on_resize(self,event):
		
		
		self.fig.tight_layout(pad=1.08,w_pad=1.08)
		
	
	
	def on_show(self):
		self.axes.clear()        
		self.axes.grid(True)
		try:
			self.canvas.mpl_disconnect(self.cid)
		except:
			pass
		self.canvas.mpl_connect('resize_event',self.on_resize)
		self.axes.set_ylabel('Correlation', fontsize=12)
		self.axes.format_coord = lambda x, y: ''
		
		self.axes.xaxis.grid(True,'minor')
		self.axes.xaxis.grid(True,'major')
		self.axes.yaxis.grid(True,'minor')
		self.axes.yaxis.grid(True,'major')
		self.axes2.clear()        
		self.axes2.grid(True)
		self.axes2.format_coord = lambda x, y: ''
		
		self.axes2.set_xlabel('Residual Tau (ms)', fontsize=12)
		self.axes2.xaxis.grid(True,'minor')
		self.axes2.xaxis.grid(True,'major')
		self.axes2.yaxis.grid(True,'minor')
		self.axes2.yaxis.grid(True,'major')
		
		
		
		has_series = False
		scaleMin = 0
		scaleMax = 0
		
		if self.setAutoScale == False: # Keep Scale is On.
			self.axes.set_xlim(self.xscale_min, self.xscale_max)
			self.axes.set_ylim(self.yscale_min, self.yscale_max)
			
		else:#Keep Scale is off
			if self.norm_to_one == True:
				self.axes.set_ylim(-0.1,1.1)
			else:
				
				max_arr = []
				min_arr = []
				tmax_arr = []
				tmin_arr = []
				for Id, objId in enumerate(self.objIdArr):
					if objId.item_in_list == False: #i.e. we are not looking at this channel.
						continue
					model_index = objId.item_in_list

					checked = model_index.checkState() == QtCore.Qt.Checked
					if checked:
						max_arr.append(objId.max)
						min_arr.append(objId.min)
						tmax_arr.append(objId.tmax)
						tmin_arr.append(objId.tmin)
				
				if min_arr != []:
					self.yscale_max = np.max(np.array(max_arr))*1.1
					self.yscale_min = np.min(np.array(min_arr))
					self.axes.set_ylim(self.yscale_min,self.yscale_max)
					
					self.xscale_max = np.max(np.array(tmax_arr))*1.2
					self.xscale_min = np.min(np.array(tmin_arr))
					if self.xscale_min == 0:
						self.xscale_min = 0.0001
					self.axes.set_xlim(self.xscale_min,self.xscale_max)
				else:
					self.axes.autoscale(None)
				
			
		row = 0
		row_checked = 0
		def onpick(event):
			thisline = event.artist
			xdata = thisline.get_xdata()
			ydata = thisline.get_ydata()
			ind = event.ind
			
			#Finds the model which has been clicked based on the label association.
			for Id, objId in enumerate(self.objIdArr):
				objId.clicked = False
				if str(objId) == str(thisline.get_label()):
					objId.clicked = True
					#self.axes.plot(objId.autotime, objId.autoNorm, 'o',markersize=2, color="red", label=objId,picker=4.0,alpha=alpha)
					#self.canvas.draw()
			self.fill_series_list()

		
		for Id, objId in enumerate(self.objIdArr):
			if objId.toFit == True:
				model_index = objId.item_in_list

				checked = model_index.checkState() == QtCore.Qt.Checked
				
				objId.checked = checked
				if objId.filter ==True:
					alpha = 0.1
				else:
					alpha = 1.0
				
				if checked:
					
					has_series = True
					#Takes the values from the interface 
					
					self.scale = objId.autotime
					
					self.series = objId.autoNorm

					if self.norm_to_one == True:
						self.series = self.series - np.average(self.series[-5:])
						self.series = self.series / np.average(self.series[:5])
					self.axes.set_xscale('log')
					self.axes2.set_xscale('log')

					
					
					self.axes.plot(self.scale, self.series, 'o',markersize=2, color="grey", label=objId,picker=4.0,alpha=alpha, linewidth=1.0)
					

					#self.axes.autoscale(False)
					row_checked += 1


				#if self.setAutoScale == False:

					#self.axes.set_ylim(bottom=float(objId.param['offset'].value)-0.001)
				row += 1  
		row = 0
		
		
		for Id, objId in enumerate(self.objIdArr):
			if objId.toFit == True:
				model_index = objId.item_in_list
				checked = model_index.checkState() == QtCore.Qt.Checked
				if objId.filter ==True:
					alpha = 0.1
				else:
					alpha = 1.0
				
				
				if checked:
					has_series = True
					#Takes the values from the interface 
					if objId.model_autoNorm !=[]:
						self.mod_scale = objId.model_autotime

						self.mod_series = objId.model_autoNorm

						if self.norm_to_one == True:
							self.mod_series = self.mod_series - np.average(self.mod_series[-5:])
							self.mod_series = self.mod_series / np.average(self.mod_series[:5])
						
							#self.colors[row % len(self.colors)]
						self.axes.plot(self.mod_scale, self.mod_series, '-', color="blue", label=objId,picker=4.0, alpha=alpha, linewidth=1.0)       
						
						maxValue = np.max(objId.residualVar)
						minValue = np.min(objId.residualVar)
						if maxValue > scaleMax:
							scaleMax = maxValue
						if minValue < scaleMin:
							scaleMin = minValue
						self.axes2.set_ylim([scaleMin,scaleMax])
						self.axes2.plot(self.mod_scale,objId.residualVar, color="grey", label=objId.name,alpha=alpha, linewidth=1.0)
						self.axes2.set_ylim([scaleMin,scaleMax])
						
				row +=1        
				   
		self.cid = self.canvas.mpl_connect('pick_event',onpick)	
		if(self.series_list_model.rowCount()>0 and row_checked>0):
			
				#The line on the left.
				try:
					#Find the nearest position to the the vertical line.
					xpos1 = int(np.argmin(np.abs(self.scale -  self.dr.xpos)))
					xpos2 = int(np.argmin(np.abs(self.scale -  self.dr1.xpos)))
					xpos1a = np.argmin(self.series >0)
					xpos2a = int(self.series.shape[0]-np.argmax(self.series[::-1] >-1)-1)
					if (xpos1<xpos1a):
						xpos1 = xpos1a
					if(xpos2>xpos2a):
						xpos2 = xpos2a
				except:
					
					try:	
						xpos1 = 10
						xpos2 = int(self.series.shape[0]-np.argmax(self.series[::-1] >-1)-1)
					except:
						
						xpos1 = 10
						xpos2 = 40


				

				self.line0=self.axes.axvline(x=self.scale[xpos1],linewidth=4, color='gray')
				self.dr = draggableLine(self.line0, self)
				self.dr.type = 'left'
				self.dr.xpos = self.scale[xpos1]
				self.dr.connect()
				#Set the spinbox values
				self.fit_btn_min.array = self.scale
				self.fit_btn_max.array = self.scale
				self.fit_btn_min.index = xpos1
				self.fit_btn_max.index = xpos2
				self.fit_btn_min.setValue(self.scale[xpos1])
				self.fit_btn_max.setValue(self.scale[xpos2])

				
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
		self.about_win = QWidget()
		self.about_win.setWindowTitle('QWebView Interactive Demo')
 
		# And give it a layout
		layout = QVBoxLayout()
		self.about_win.setLayout(layout)
		self.view = QWebView()
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
	#def item_edited(self,model_index):
	#	"""If the text is edited this will update the name of the object"""
	#	for Id, objId in enumerate(self.objIdArr):
	#		item = objId.series_list_id
	#lis		objId.name = item.text()
	def file_item_edited(self, model_index):
		# In case a parent is selected.
		if model_index.hasChildren() == True:
			self.series_list_model.itemChanged.disconnect()
			for file_id in self.root_name:
				checked = self.root_name[file_id]['file_item'].checkState() == QtCore.Qt.Checked
				
				objId_list = self.root_name[file_id]['objIdArr']
				for objId in objId_list:
					if objId.toFit == True:
						if checked == False:
							objId.checked = False
							objId.item_in_list.setCheckState(QtCore.Qt.Unchecked)
						else:
							objId.checked = True
							objId.item_in_list.setCheckState(QtCore.Qt.Checked)
			self.series_list_model.itemChanged.connect(self.file_item_edited)
		# In case a child (correlated data) is selected.
		else:
			corrObj = self.objIdArr[self.obj_hash_list[self.tree_hash_list[id(model_index)]]]
			corrObj.name = model_index.text()

			# Update the fit list with the new name.
			self.updateFitList()

	def colour_entry(self,objId):
		#Context sensitive colour highlighting
		if objId.goodFit == False:
			objId.series_list_id.setBackground(QColor('red'))
		elif objId.fitted == True:
			objId.series_list_id.setBackground(QColor('green'))
		else:    
			objId.series_list_id.setBackground(QColor('white'))
	def fill_series_list(self):
		

		try:
			#Makes sure the root file names don't trigger strange effects
			self.series_list_model.itemChanged.disconnect(self.file_item_edited)
		except:
			pass
		#Trys to check to 
		for Id, objId in enumerate(self.objIdArr):
			if objId.toFit == True and objId.item_in_list !=False:
				model_index = objId.item_in_list

				checked = model_index.checkState() == QtCore.Qt.Checked
				objId.checked = checked

		#except:
			#print('passed')
			#pass

		
		self.root_name_copy = {}
		for file_id,idx in enumerate(self.root_name):
			to_focus_item = self.root_name[file_id]['file_item']
			self.root_name_copy[file_id] = [self.series_list_view.isExpanded(self.series_list_model.indexFromItem(to_focus_item)),self.root_name[file_id]['file_item'].checkState()]
			


		self.series_list_model.clear()
		to_focus_item = None
		to_focus = 0




		

		#Regenerates root_name list.
		self.root_name = {}
		self.obj_hash_list = {}

		c = -1
		for Id, objId in enumerate(self.objIdArr):
			#Find details of each dataset
				parent_name = objId.parent_name
				parent_uqid = objId.parent_uqid

				#If the name already exists.
				if c in self.root_name and parent_name in self.root_name[c]:
					pass
				#If not then populate root_name with details.
				else:
					c = c+1
					self.root_name[c] = {}
					self.root_name[c]['file_item'] = QStandardItem(parent_name)
					self.root_name[c]['file_item'].setCheckable(True)
					self.root_name[c]['file_item'].setCheckState(QtCore.Qt.Unchecked)
					
					
					self.root_name[c][parent_name] = []
					self.root_name[c]['parent_uqid'] = parent_uqid
					self.series_list_model.appendRow(self.root_name[c]['file_item'])

					#If the root_name previously existed a
					if c in self.root_name_copy:
						#If the rootname was checked. Make sure it is (or isn't) when list is rebuilt.
						self.root_name[c]['file_item'].setCheckState(self.root_name_copy[c][1])
						#If the rootname was expanded make sure it is (or isn't) when list is rebuilt.
						self.series_list_view.setExpanded(self.series_list_model.indexFromItem(self.root_name[c]['file_item']), self.root_name_copy[c][0])
					self.root_name[c]['objIdArr'] = []

				#Add the individual plots to the root list.
				self.root_name[c]['objIdArr'].append(objId)

					
		bid = 0
		lid = -1
		self.tree_hash_list ={}
		for file_id in self.root_name:
		#Files are organised by their root name.

			idx = 0
			objId_list = self.root_name[file_id]['objIdArr']
			for objId in objId_list:
				lid = lid +1
				#For each objecct.
		
				
				objId.filter = False
				objId.toFit = True
				
				



				#Filter for CH identification:
				if self.ch_check_ch1.isChecked() == True and (objId.ch_type == '1_1' or objId.ch_type == 0):
					objId.toFit = True
				elif self.ch_check_ch2.isChecked() == True and (objId.ch_type == '2_2' or objId.ch_type == 1):
					objId.toFit = True
				elif self.ch_check_ch3.isChecked() == True and objId.ch_type == '3_3':
					objId.toFit = True
				elif self.ch_check_ch4.isChecked() == True and objId.ch_type == '4_4':
					objId.toFit = True
				elif self.ch_check_ch12.isChecked() == True and (objId.ch_type == '1_2' or objId.ch_type == 2):
					objId.toFit = True
				elif self.ch_check_ch13.isChecked() == True and objId.ch_type == '1_3':
					objId.toFit = True
				elif self.ch_check_ch14.isChecked() == True and objId.ch_type == '1_4':
					objId.toFit = True
				elif self.ch_check_ch23.isChecked() == True and objId.ch_type == '2_3':
					objId.toFit = True
				elif self.ch_check_ch24.isChecked() == True and objId.ch_type == '2_4':
					objId.toFit = True
				elif self.ch_check_ch34.isChecked() == True and objId.ch_type == '3_4':
					objId.toFit = True
				elif self.ch_check_ch21.isChecked() == True and (objId.ch_type == '2_1' or objId.ch_type == 3):
					objId.toFit = True
				elif self.ch_check_ch31.isChecked() == True and objId.ch_type == '3_1':
					objId.toFit = True
				elif self.ch_check_ch41.isChecked() == True and objId.ch_type == '4_1':
					objId.toFit = True
				elif self.ch_check_ch32.isChecked() == True and objId.ch_type == '3_2':
					objId.toFit = True
				elif self.ch_check_ch42.isChecked() == True and objId.ch_type == '4_2':
					objId.toFit = True
				elif self.ch_check_ch43.isChecked() == True and objId.ch_type == '4_3':
					objId.toFit = True
				else:
					objId.toFit = False


				
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
						
							


				
				
				
				

				#If the data should appear in the list:
				if objId.toFit == True:
					name = objId.name
					#Creat an item.
					item = QStandardItem(name)
					#Store the index
					self.tree_hash_list[id(item)] = bid
					self.obj_hash_list[bid] = lid
					#Iterate index for next.
					bid = bid + 1

					
					
					

					#Store the item.
					objId.series_list_id = item
					#If the item has been checked. Restore that state.
					#Remember whether it was checked or not.
					if objId.checked == False:
						item.setCheckState(QtCore.Qt.Unchecked)
					else :
						item.setCheckState(QtCore.Qt.Checked)
					#self.root_name[file_id]['file_item'].setCheckState(QtCore.Qt.Checked)
					#Context sensitive colour highlighting

					self.colour_entry(objId)


				
					self.root_name[file_id]['file_item'].setChild(idx,item)
					idx = idx +1
					item.setCheckable(True)
					#item.setEditable(False)
					
					objId.item_in_list = item
					if objId.clicked == True:
						item.setBackground(QColor(0, 0, 255, 127))
						to_focus = self.series_list_model.rowCount()
						to_focus_item = item

				else:
					objId.item_in_list = False
					
		if to_focus_item != None:
			self.series_list_view.scrollTo(self.series_list_model.indexFromItem(to_focus_item))

		
		
		self.updateFitList()
		self.series_list_model.itemChanged.connect(self.file_item_edited)
		self.series_list_view.selectionModel().selectionChanged.connect(self.selection_method)

				


				
	def selection_method(self,index):
		"""Called when a selection is made in the data tree"""
		#Returns the indices of what has been double clicked.
		try:
			itemToSelect = self.series_list_view.selectedIndexes()[0]
		except:
			# No selection has been made
			return
		#Gets the associated index.
		item = self.series_list_model.itemFromIndex(itemToSelect)
		if item.hasChildren():
			#If we double click header we don't want to do anything.
			pass
		else:
			#Returns actual value.
			to_select = self.tree_hash_list[id(item)]
			#updates selected.
			self.modelFitSel.setCurrentIndex(to_select)
			#updates the whole list (not necessary but makes sure all is correct)
			self.updateFitList()
			
	def create_main_frame(self):
		"""Creates the main layout of the fitting interface """
		self.main_frame = QWidget()
		
		plot_frame = QWidget()
		
		self.dpi = 72
		self.fig = Figure((8.0, 16.0), )
		#self.fig.patch.set_facecolor('#C6d3e0')
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1]) 
		self.axes = self.fig.add_subplot(gs[0])
		self.axes2 = self.fig.add_subplot(gs[1])
		self.axes.set_facecolor('#C6d3e0')
		self.axes2.set_facecolor('#C6d3e0')
		self.fig.subplots_adjust(bottom = 0.1,top=0.95, right=0.95)


		

		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
		
		log_label = QLabel("Data Series Viewer:")
		self.series_list_view = QTreeView()
		self.series_list_view.setHeaderHidden(True)
		

		self.series_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
	  
		self.series_list_view.setModel(self.series_list_model)
		self.to_spin = QSpinBox()

		self.shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
		self.shortcut.activated.connect(self.selectAll)

		
		
		

		self.series_list_view2 = QListView()

		#############The left panel.
		
		self.load_box = QHBoxLayout()
		self.load_box.setSpacing(16)
		self.load_corr_file_btn = QPushButton("Load Correlated File")
		self.load_corr_file_btn.setToolTip('Open dialog for importing correlated files.')
		self.load_corr_file_btn.clicked.connect(self.load_file)

		self.load_box.addWidget(self.load_corr_file_btn)
		
		self.load_folder_btn = QPushButton('load Folder')
		self.load_folder_output = folderOutput(self)
		self.load_folder_output.type = 'folder_to_process'
		self.load_folder_output.setToolTip('Opens dialog for selecting a folder to import all correlated files from.')
		self.load_folder_btn.clicked.connect(self.load_folder_fn)
		self.load_box.addWidget(self.load_folder_btn)


		self.on_about_btn = QPushButton()
		self.on_about_btn.setText("About Equation")
		self.on_about_btn.setToolTip("Provides more information about the equations used for fitting the correlation functions.")
		self.on_about_btn.clicked.connect(self.on_about)
		
		self.load_box.addWidget(self.on_about_btn)
		self.load_box.addStretch()
		

		self.model_layout = QHBoxLayout()
		self.model_layout.setSpacing(16)
		
		#Drop down list of equations for diffusing species
		self.diffModEqSel = comboBoxSp2(self)
		self.diffModEqSel.setToolTip('Set the type of equation to fit (see documentation for more advice).')
		self.diffModEqSel.type ='Diff_eq'
		self.diffModEqSel.addItem('Equation 1A')
		self.diffModEqSel.addItem('Equation 1B')
		self.diffModEqSel.addItem('GS neuron')
		self.diffModEqSel.addItem('Vesicle Diffusion')
		self.diffModEqSel.addItem('PB Correction')
		self.model_layout.addWidget(self.diffModEqSel)



		#Spin box for number of diffusing species
		diffNumSpecies = QHBoxLayout()
		diffNumSpecies.setSpacing(16)
		diffNumSpecLabel = QLabel('Num. of: diffusing species')
		diffNumSpecLabel.setToolTip('Set the number of diffusing species to be included in the fitting.')


		self.diffNumSpecSpin = QSpinBox()
		self.diffNumSpecSpin.setRange(1,3)
		self.diffNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(diffNumSpecLabel)
		diffNumSpecies.addWidget(self.diffNumSpecSpin)

		
		#Drop down list of equations for Triplet equations
		self.tripModEqSel = comboBoxSp2(self)
		self.tripModEqSel.setToolTip('Set the number of Triplet states to be included in the fitting')
		self.tripModEqSel.type ='Triplet_eq'
		self.tripModEqSel.addItem('no triplet')
		self.tripModEqSel.addItem('Triplet Eq 2A')
		self.tripModEqSel.addItem('Triplet Eq 2B')

		self.model_layout.addWidget(self.tripModEqSel)
		#Drop down box for selecting 2D or 3D model:
		self.dimenModSel = comboBoxSp2(self)
		self.dimenModSel.setToolTip('Set the dimensionality of the equation for fitting.')
		self.dimenModSel.type ='Dimen'
		self.dimenModSel.addItem('2D')
		self.dimenModSel.addItem('3D')
		self.model_layout.addWidget(self.dimenModSel)
		self.model_layout.addStretch()
		#Drop-down list with all the available models.
		
		#Spin box for number of diffusing species
		
		tripNumSpecLabel = QLabel('Triplet states')
		self.tripNumSpecSpin = QSpinBox()
		self.tripNumSpecSpin.setRange(1,3)
		self.tripNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(tripNumSpecLabel)
		diffNumSpecies.addWidget(self.tripNumSpecSpin)
		diffNumSpecies.addStretch()
		




		self.modelFitSel = comboBoxSp2(self)
		self.modelFitSel.type = 'Fit'

		fit_layout = QHBoxLayout()
		fit_layout.setSpacing(16)
		

		
		self.fit_btn_min_label = QLabel("Fit from:")
		self.fit_btn_min = spinBoxSp3(self)
		self.fit_btn_min.setToolTip("Sets the position of the lower limit handle for the data fitting")
		self.fit_btn_min.type ='min'
		self.fit_btn_min.setMaximumWidth(90)
		self.fit_btn_min.setDecimals = 3
		self.fit_btn_min.valueChanged.connect(self.fit_btn_min.onEdit)
		

		self.fit_btn_max_label = QLabel("to:")
		self.fit_btn_max = spinBoxSp3(self)
		self.fit_btn_min.setToolTip("Sets the position of the upper limit handle for the data fitting")
		self.fit_btn_max.type ='max'
		self.fit_btn_max.setMaximumWidth(90)
		self.fit_btn_max.setDecimals = 3
		self.fit_btn_max.valueChanged.connect(self.fit_btn_max.onEdit)


		#Profile panel for different buttons.
		default_profile_panel = QHBoxLayout()
		default_profile_panel.setSpacing(16)

		text_default_profile = QLabel('Profile:')

		load_default_profile = QPushButton('load')
		load_default_profile.setToolTip('Will open a dialog to load a previously saved paramter fit profile')
		self.load_default_profile_output = folderOutput(self)
		self.load_default_profile_output.type = 'profile_load'
		
		save_default_profile = QPushButton('save')
		save_default_profile.setToolTip('Will open a dialog to save a parameter profile for the fitting')
		self.save_default_profile_output = folderOutput(self)
		self.save_default_profile_output.type = 'profile_save'

		store_default_profile = QPushButton('store')
		store_default_profile.setToolTip('Allows you to temporary store a parameter fit profile')
		apply_default_profile = QPushButton('apply')
		store_default_profile.setToolTip('Allows you to apply a parameter fit profile which has been previously loaded or stored')
		
		default_profile_panel.addWidget(text_default_profile)
		default_profile_panel.addWidget(load_default_profile)
		default_profile_panel.addWidget(save_default_profile)
		default_profile_panel.addWidget(store_default_profile)
		default_profile_panel.addWidget(apply_default_profile)
		default_profile_panel.addStretch()

		
		save_default_profile.clicked.connect(self.save_default_profile_fn)
		load_default_profile.clicked.connect(self.load_default_profile_fn)
		store_default_profile.clicked.connect(self.store_default_profile_fn)
		apply_default_profile.clicked.connect(self.apply_default_profile_fn)


		
		
		
		

		
			#Table which has the fitting
		self.fitTable = QTableWidget()


		

		
		#self.fitTable.setMinimumWidth(320)
		#self.fitTable.setMaximumWidth(400)
		self.fitTable.setMinimumHeight(100)
		self.fitTable.setMaximumHeight(600)
		
		
		
		self.fit_btn = QPushButton("Current")
		self.fit_btn.clicked.connect(self.fit_equation)
		self.fit_btn.setToolTip('This will fit the data selected in the \"Display Model Parameters\" drop-down list.')


		self.fitAll_btn = QPushButton("All")
		self.fitAll_btn.setToolTip('This will fit all the data in the \"Data Series Viewer\" ')
		self.fitAll_btn.clicked.connect(self.fitAll_equation)

		#Horizontal Layout for fit_btns.
		fit_btns = QHBoxLayout()
		fit_btns.setSpacing(16)
		
		#Fit components
		self.fit_btn_txt = QLabel("Fit with param: ")
		self.fitSelected_btn = QPushButton("Only highlighted")
		self.fitSelected_btn.setToolTip("This will fit data which is highlighted in the \"Data Series Viewer\"")
		self.fitSelected_btn.clicked.connect(self.fitSelected_equation)

		#Fit button adding to layout.
		fit_btns.addWidget(self.fit_btn_txt)
		fit_btns.addWidget(self.fit_btn)
		fit_btns.addWidget(self.fitAll_btn)
		fit_btns.addWidget(self.fitSelected_btn)
		fit_btns.addStretch()

		#bootstrap.
		bootstrap_panel = QHBoxLayout()
		bootstrap_panel.setSpacing(16)
		bootstrap_panel.addSpacing(200)

		self.bootstrap_enable_toggle = False
		self.bootstrap_enable_btn = QPushButton('OFF')
		self.bootstrap_enable_btn.setStyleSheet("color: red")
		self.bootstrap_enable_btn.setFixedWidth(60)
		self.bootstrap_enable_btn.clicked.connect(self.bootstrap_enable_toggle_fn)
		self.bootstrap_enable_btn.setToolTip('This will enable bootstapping (see documentation formore details)')
		self.bootstrap_samples = QSpinBox()
		self.bootstrap_samples.setRange (1,400)
		self.bootstrap_samples.setValue(100)
		self.bootstrap_samples.setToolTip('This number represents the quantity of bootstrap samples to use.')

		bootstrap_panel.addWidget(QLabel('bootstrap:'))
		bootstrap_panel.addWidget(self.bootstrap_enable_btn)
		bootstrap_panel.addWidget(self.bootstrap_samples)
		bootstrap_panel.addStretch()
		
		



		
		
		modelFitSel_box = QHBoxLayout()
		modelFitSel_box.setSpacing(16)
		self.modelFitSel_label = QLabel('Display model parameters for data:')
		modelFitSel_box.addWidget(self.modelFitSel_label)
		modelFitSel_box.addStretch()


		#main left panel layout.
		left_vboxTop = QVBoxLayout()
		left_vboxMid = QVBoxLayout()
		left_vboxBot = QVBoxLayout()
		
		left_vboxTop.setContentsMargins(0,0,0,0)
		left_vboxTop.setSpacing(2)
		left_vboxMid.setContentsMargins(0,0,0,0)
		left_vboxMid.setSpacing(2)
		left_vboxBot.setContentsMargins(0,0,0,0)
		left_vboxBot.setSpacing(2)
		#self.load_box.setContentsMargins(0,0,0,0)
		#self.load_box.setSpacing(16)
		#left_vboxBot.setSpacing(0.5)
		#self.load_box.setSpacing(0.5)
		left_vboxTop.addLayout(self.load_box)
		left_vboxTop.addLayout(self.model_layout) 
		left_vboxTop.addLayout(diffNumSpecies) 
		
		left_vboxTop.addLayout(modelFitSel_box)
		
		left_vboxTop.addWidget(self.modelFitSel)
		left_vboxTop.addLayout(fit_btns)
		if self.type == 'scan':
			left_vboxTop.addLayout(bootstrap_panel)
		left_vboxTop.addLayout(fit_layout)
		
		left_vboxTop.addLayout(default_profile_panel)
		left_vboxTop.addSpacing(4)
		left_vboxTop.addWidget(self.fitTable)
		left_vboxTop.addSpacing(4)
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
		copy_text = QLabel("Copy: ")
		self.copy_output_btn = QPushButton("parameters")
		self.copy_output_btn.setToolTip("Copies the fit parameters to the clipboard.")
		self.copy_output_btn.clicked.connect(self.copyOutputDataFn)
		self.copy_model_btn = QPushButton("plot data")
		self.copy_model_btn.setToolTip("Copies the raw data and fit data to the clipboard.")
		self.copy_model_btn.clicked.connect(self.copyModelFile)

		copy_layout = QHBoxLayout()
		copy_layout.setSpacing(16)
		copy_layout.addWidget(copy_text)
		copy_layout.addWidget(self.copy_output_btn)
		copy_layout.addWidget(self.copy_model_btn)
		copy_layout.addStretch()

		

		#Save Fit parameters and the raw data inc. fit.
		save_text = QLabel("Save: ")
		self.save_output_btn = QPushButton("parameters")
		self.save_output_btn.setToolTip("Saves the learnt parameters to a file.")
		self.save_output_btn.clicked.connect(self.saveOutputDataFn)
		
		self.save_model_btn = QPushButton("plot data")
		self.save_model_btn.setToolTip("Saves the raw data and fit data to a file.")
		self.save_model_btn.clicked.connect(self.saveModelFile)

		save_layout = QHBoxLayout()
		save_layout.setSpacing(16)
		save_layout.addWidget(save_text)
		save_layout.addWidget(self.save_output_btn)
		save_layout.addWidget(self.save_model_btn)
		save_layout.addStretch()


		output_layout = QHBoxLayout()
		output_layout.setSpacing(16)
		self.fileNameText = QLineEdit('outputFileName')
		

		self.folderSelect_btn = QPushButton('Output Folder')
		self.folderSelect_btn.setToolTip('Select the output folder for saving the files to.')
		self.folderOutput = folderOutput(self)
		self.folderOutput.type = 'output_dir'
		self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

		output_layout.addWidget(self.fileNameText)
		output_layout.addWidget(self.folderSelect_btn)
		output_layout.addStretch()

		left_vboxBot.addSpacing(12)
		left_vboxBot.addLayout(copy_layout)
		left_vboxBot.addLayout(save_layout)
		left_vboxBot.addLayout(output_layout)
		
		

		
		left_vboxBot.addStretch()

		left_vbox = QVBoxLayout()
		left_vbox.setContentsMargins(0,0,0,0)
		left_vbox.setSpacing(16)

		left_stretch = QSplitter(QtCore.Qt.Vertical)
		left_vboxTopWid = QWidget()
		left_vboxBotWid = QWidget()
		
		left_vboxTopWid.setLayout(left_vboxTop)
		left_vboxBotWid.setLayout(left_vboxBot)

		left_stretch.addWidget(left_vboxTopWid)
		left_stretch.addWidget(left_vboxBotWid)
		left_vbox.addWidget(left_stretch)

		center_vbox = QVBoxLayout()
		center_vbox.addWidget(self.canvas)
		center_vbox.addWidget(self.mpl_toolbar)
		resetScale = QPushButton("Reset Scale")
		resetScale.setToolTip('Will reset the scale to be the bounds of the plot with the largest amplitude')
		resetScale.clicked.connect(self.resetScaleFn)
		
		self.turnOffAutoScale = QPushButton("Keep Scale")
		self.turnOffAutoScale.setToolTip("Will stop the scale from dynamically changeing.")
		self.turnOffAutoScale.setCheckable(True)
		self.turnOffAutoScale.clicked.connect(self.autoScaleFn)

		self.norm_to_one_btn = QPushButton("Normalize Function")
		self.norm_to_one_btn.setToolTip("Will ensure all curves scale between 1.0 and 0.0")
		self.norm_to_one_btn.setCheckable(True)
		self.norm_to_one_btn.clicked.connect(self.norm_to_one_fn)
		
		center_hbox = QHBoxLayout()
		center_hbox.setSpacing(16)
		center_vbox.addLayout(center_hbox)
		center_hbox.addWidget(resetScale)
		center_hbox.addWidget(self.turnOffAutoScale)
		center_hbox.addWidget(self.norm_to_one_btn)
		center_hbox.setAlignment(QtCore.Qt.AlignLeft)


		right_vbox = QVBoxLayout()
		right_vbox.addWidget(log_label)
		right_vbox.addWidget(self.series_list_view)
		self.series_list_view.setMinimumWidth(260)
		self.series_list_view.setMinimumHeight(260)
		#right_vbox.addLayout(spins_hbox)

		legend_box = QHBoxLayout()
		legend_box.setSpacing(16)
		#self.legend_cb = QCheckBox("Show L&egend")
		#self.legend_cb.setChecked(False)
		#legend_box.addWidget(self.legend_cb)
		

		self.right_check_all_none = QPushButton("check all")
		self.show_button = QPushButton("Plot Checked Data")
		
		self.switch_true_false = True



		legend_box.addWidget(self.show_button)
		legend_box.addWidget(self.right_check_all_none)
		right_vbox.addLayout(legend_box)

		right_ch_check = QHBoxLayout()
		right_ch_check.setSpacing(16)
		right_ch_check1 = QHBoxLayout()
		right_ch_check1.setSpacing(8)
		right_ch_check2 = QHBoxLayout()
		right_ch_check2.setSpacing(8)

		right_ch_VH = QVBoxLayout()
	
		
		#Channel 1 auto-correlation
		ch_check_ch1_label = QLabel("ac: CH1")
		self.ch_check_ch1 = QCheckBox()
		self.ch_check_ch1.setChecked(True)
		self.ch_check_ch1.setToolTip("check to display CH1 auto-correlation data.")
		self.ch_check_ch1.stateChanged.connect(self.fill_series_list)
		#Channel 2 auto-correlation
		ch_check_ch2_label = QLabel("CH2")
		self.ch_check_ch2 = QCheckBox()
		self.ch_check_ch2.setChecked(True)
		self.ch_check_ch2.setToolTip("check to display CH2 auto-correlation data.")
		self.ch_check_ch2.stateChanged.connect(self.fill_series_list)
		#Channel 3 auto-correlation
		ch_check_ch3_label = QLabel("CH3")
		self.ch_check_ch3 = QCheckBox()
		self.ch_check_ch3.setChecked(True)
		self.ch_check_ch3.setToolTip("check to display CH3 auto-correlation data.")
		self.ch_check_ch3.stateChanged.connect(self.fill_series_list)
		#Channel 4 auto-correlation
		ch_check_ch4_label = QLabel("CH4")
		self.ch_check_ch4 = QCheckBox()
		self.ch_check_ch4.setChecked(True)
		self.ch_check_ch4.setToolTip("check to display CH4 auto-correlation data.")
		self.ch_check_ch4.stateChanged.connect(self.fill_series_list)
		#Channel 12 cross-correlation
		ch_check_ch12_label = QLabel("CH12")
		self.ch_check_ch12 = QCheckBox()
		self.ch_check_ch12.setChecked(True)
		self.ch_check_ch12.setToolTip("check to display CH12 cross-correlation data.")
		self.ch_check_ch12.stateChanged.connect(self.fill_series_list)
		#Channel 13 cross-correlation
		ch_check_ch13_label = QLabel("CH13")
		self.ch_check_ch13 = QCheckBox()
		self.ch_check_ch13.setChecked(True)
		self.ch_check_ch13.setToolTip("check to display CH12 cross-correlation data.")
		self.ch_check_ch13.stateChanged.connect(self.fill_series_list)
		#Channel 10 cross-correlation
		ch_check_ch14_label = QLabel("CH14")
		self.ch_check_ch14 = QCheckBox()
		self.ch_check_ch14.setChecked(True)
		self.ch_check_ch14.setToolTip("check to display CH10 cross-correlation data.")
		self.ch_check_ch14.stateChanged.connect(self.fill_series_list)
		#Channel 23 cross-correlation
		ch_check_ch23_label = QLabel("CH23")
		self.ch_check_ch23 = QCheckBox()
		self.ch_check_ch23.setChecked(True)
		self.ch_check_ch23.setToolTip("check to display CH23 cross-correlation data.")
		self.ch_check_ch23.stateChanged.connect(self.fill_series_list)
		#Channel 24 cross-correlation
		ch_check_ch24_label = QLabel("CH24")
		self.ch_check_ch24 = QCheckBox()
		self.ch_check_ch24.setChecked(True)
		self.ch_check_ch24.setToolTip("check to display CH24 cross-correlation data.")
		self.ch_check_ch24.stateChanged.connect(self.fill_series_list)
		#Channel 34 cross-correlation
		ch_check_ch34_label = QLabel("CH34")
		self.ch_check_ch34 = QCheckBox()
		self.ch_check_ch34.setChecked(True)
		self.ch_check_ch34.setToolTip("check to display CH34 cross-correlation data.")
		self.ch_check_ch34.stateChanged.connect(self.fill_series_list)

		#Channel 21 cross-correlation
		ch_check_ch21_label = QLabel("CH21")
		self.ch_check_ch21 = QCheckBox()
		self.ch_check_ch21.setChecked(True)
		self.ch_check_ch21.setToolTip("check to display CH21 cross-correlation data.")
		self.ch_check_ch21.stateChanged.connect(self.fill_series_list)
		#Channel 31 cross-correlation
		ch_check_ch31_label = QLabel("CH31")
		self.ch_check_ch31 = QCheckBox()
		self.ch_check_ch31.setChecked(True)
		self.ch_check_ch31.setToolTip("check to display CH31 cross-correlation data.")
		self.ch_check_ch31.stateChanged.connect(self.fill_series_list)
		#Channel 32 cross-correlation
		ch_check_ch32_label = QLabel("CH32")
		self.ch_check_ch32 = QCheckBox()
		self.ch_check_ch32.setChecked(True)
		self.ch_check_ch32.setToolTip("check to display CH32 cross-correlation data.")
		self.ch_check_ch32.stateChanged.connect(self.fill_series_list)
		#Channel 41 cross-correlation
		ch_check_ch41_label = QLabel("CH41")
		self.ch_check_ch41 = QCheckBox()
		self.ch_check_ch41.setChecked(True)
		self.ch_check_ch41.setToolTip("check to display CH41 cross-correlation data.")
		self.ch_check_ch41.stateChanged.connect(self.fill_series_list)
		#Channel 42 cross-correlation
		ch_check_ch42_label = QLabel("CH42")
		self.ch_check_ch42 = QCheckBox()
		self.ch_check_ch42.setChecked(True)
		self.ch_check_ch42.setToolTip("check to display CH42 cross-correlation data.")
		self.ch_check_ch42.stateChanged.connect(self.fill_series_list)
		
		#Channel 43 cross-correlation
		ch_check_ch43_label = QLabel("CH43")
		self.ch_check_ch43 = QCheckBox()
		self.ch_check_ch43.setChecked(True)
		self.ch_check_ch43.setToolTip("check to display CH43 cross-correlation data.")
		self.ch_check_ch43.stateChanged.connect(self.fill_series_list)
		#Add widgets.
		aa_check_export_fns = QtWidgets.QGroupBox('auto-correlation')
		cc_check_export_fns = QtWidgets.QGroupBox('cross-correlation')

		right_ch_check.addWidget(ch_check_ch1_label)
		right_ch_check.addWidget(self.ch_check_ch1)
		right_ch_check.addWidget(ch_check_ch2_label)
		right_ch_check.addWidget(self.ch_check_ch2)
		right_ch_check.addWidget(ch_check_ch3_label)
		right_ch_check.addWidget(self.ch_check_ch3)
		right_ch_check.addWidget(ch_check_ch4_label)
		right_ch_check.addWidget(self.ch_check_ch4)
		right_ch_check.addStretch()

		right_ch_check1.addWidget(ch_check_ch12_label)
		right_ch_check1.addWidget(self.ch_check_ch12)
		right_ch_check1.addWidget(ch_check_ch13_label)
		right_ch_check1.addWidget(self.ch_check_ch13)
		right_ch_check1.addWidget(ch_check_ch14_label)
		right_ch_check1.addWidget(self.ch_check_ch14)
		right_ch_check1.addWidget(ch_check_ch23_label)
		right_ch_check1.addWidget(self.ch_check_ch23)
		right_ch_check1.addWidget(ch_check_ch24_label)
		right_ch_check1.addWidget(self.ch_check_ch24)
		right_ch_check1.addWidget(ch_check_ch34_label)
		right_ch_check1.addWidget(self.ch_check_ch34)

		right_ch_check2.addWidget(ch_check_ch21_label)
		right_ch_check2.addWidget(self.ch_check_ch21)
		right_ch_check2.addWidget(ch_check_ch31_label)
		right_ch_check2.addWidget(self.ch_check_ch31)
		right_ch_check2.addWidget(ch_check_ch41_label)
		right_ch_check2.addWidget(self.ch_check_ch41)
		right_ch_check2.addWidget(ch_check_ch32_label)
		right_ch_check2.addWidget(self.ch_check_ch32)
		right_ch_check2.addWidget(ch_check_ch42_label)
		right_ch_check2.addWidget(self.ch_check_ch42)
		right_ch_check2.addWidget(ch_check_ch43_label)
		right_ch_check2.addWidget(self.ch_check_ch43)
		#Add to main layout.
		self.right_check_all_none.clicked.connect(self.check_all_none)
		self.show_button.clicked.connect(self.on_show)
		#self.connect(self.show_button, QtCore.SIGNAL('clicked()'), self.on_show)
		right_vbox.addWidget(aa_check_export_fns)
		right_vbox.addWidget(cc_check_export_fns)
		
		aa_check_export_fns.setLayout(right_ch_check)

		right_ch_VH.addLayout(right_ch_check1)
		right_ch_VH.addLayout(right_ch_check2)
		cc_check_export_fns.setLayout(right_ch_VH)


		

		right_vbox.addWidget(self.right_check_all_none)
		
		self.chi_limit_label = QLabel('chi^2 cut-off value')
		self.chi_limit = QDoubleSpinBox()
		self.chi_limit.setToolTip('The Data Series Viewer cut-off. Fits with chi^2 above this value will be red, lower geen.')
		self.chi_limit.setMinimum(0)
		self.chi_limit.setDecimals(3)
		self.chi_limit.setMaximum(99.999)
		self.chi_limit.setSingleStep(0.001)
		self.chi_limit.setValue(self.chisqr)
		self.chi_limit.valueChanged.connect(self.chi_limit_update)
		chi_limit_box = QHBoxLayout()
		chi_limit_box.addStretch()
		chi_limit_box.addWidget(self.chi_limit_label)
		chi_limit_box.addWidget(self.chi_limit)

		self.remove_btn = QPushButton("Remove Highlighted Data")
		self.remove_btn.setToolTip('Remove highlighted data from \"Data Series Viewer\" ')
		self.remove_btn.clicked.connect(self.removeDataFn)
		self.create_average_btn = QPushButton("Create average of Highlighted")
		self.create_average_btn.setToolTip('Creates a new average plot from any plots highlighted in the \"Data Series Viewer\" ')
		self.create_average_btn.clicked.connect(self.create_average_fn)
		self.clearFits_btn = QPushButton("Clear Fit Data All/Highlighted")
		self.clearFits_btn.setToolTip('Clears the fit parameters only from any data-files highlighted in the \"Data Series Viewer\" ')
		self.clearFits_btn.clicked.connect(self.clearFits)
		self.visual_histo = visualHisto(self)
		visual_histo_btn = QPushButton("Generate Histogram")
		visual_histo_btn.setToolTip('Opens the Generate Histogram plot dialog')
		visual_histo_btn.clicked.connect(self.visual_histo.create_main_frame)
		self.visual_scatter = visualScatter(self)
		visual_scatter_btn = QPushButton("Generate Scatter")
		visual_histo_btn.setToolTip('Opens the Generate Scatter plot dialog')
		visual_scatter_btn.clicked.connect(self.visual_scatter.create_main_frame)

		right_vbox.addLayout(chi_limit_box)
		right_vbox.addWidget(self.remove_btn)
		right_vbox.addWidget(self.create_average_btn)
		right_vbox.addWidget(self.clearFits_btn)
		right_vbox.addWidget(visual_histo_btn)
		right_vbox.addWidget(visual_scatter_btn)
		right_vbox.addStretch(1)

		filter_box = QHBoxLayout()
		right_vbox.addLayout(filter_box)


		self.tfb = TableFilterBox(self)


		filter_box.addWidget(self.tfb)
		self.filter_add_panel = QHBoxLayout()
		self.filter_select = QComboBox()
		self.filter_select.setMaximumWidth(100)
		self.filter_select.setToolTip('Specifies parameter of fit to filter')
		

		for item in self.def_param:
			self.filter_select.addItem(item)

		self.filter_lessthan = QComboBox()
		self.filter_lessthan.addItem('<')
		self.filter_lessthan.addItem('>')
		self.filter_lessthan.setToolTip("Species direction of filter")
		self.filter_lessthan.setMaximumWidth(50)
		self.filter_value = QLineEdit('10.0')
		self.filter_value.setMaximumWidth(50)
		self.filter_value.setMinimumWidth(50)
		self.filter_add = QPushButton('add')
		self.filter_add.setToolTip('Will add a filter which processes the data in the \"Data Series Viewer\"')
		self.filter_add_panel.addWidget(self.filter_select)
		self.filter_add_panel.addWidget(self.filter_lessthan)
		self.filter_add_panel.addWidget(self.filter_value)
		self.filter_add_panel.addWidget(self.filter_add)
		right_vbox.addLayout(self.filter_add_panel)
		

		self.filter_add.clicked.connect(self.tfb.filter_add_fn)
		hbox = QHBoxLayout()
		splitter = QSplitter()
		
		hbox1 =QWidget()
		hbox1.setLayout(left_vbox)
		hbox2 =QWidget()
		hbox2.setLayout(center_vbox)
		hbox3 = QWidget()
		hbox3.setLayout(right_vbox)
		#hbox.addLayout(right_vbox)
		splitter.addWidget(hbox1)
		splitter.addWidget(hbox2)
		splitter.addWidget(hbox3)
		#Splitter instance. Can't have 
		
		container = QWidget()

		self.image_status_text = QStatusBar()
		
		self.image_status_text.showMessage("Please load a data file. ")
		self.image_status_text.setStyleSheet("QLabel {  color : green }")
		left_vbox.addWidget(self.image_status_text)

		hbox.addWidget(splitter)
		self.defineTable()
		self.main_frame.setLayout(hbox)

		self.setCentralWidget(self.main_frame)
	def chi_limit_update(self):
		

		self.chisqr = float(self.chi_limit.value())
	def bootstrap_enable_toggle_fn(self):
		#Toggle the bootstrap toggle.
		if self.bootstrap_enable_toggle == False:
			self.bootstrap_enable_btn.setText('ON')
			self.bootstrap_enable_btn.setStyleSheet("color: green")
			self.bootstrap_enable_toggle = True
		else:
			self.bootstrap_enable_btn.setText('OFF')
			self.bootstrap_enable_btn.setStyleSheet("color: red")
			self.bootstrap_enable_toggle = False
	
		
		

	def create_average_fn(self):
		#Reads those indices which are highlighted.
		
		#Reads those indices which are highlighted.
		listToFit = self.series_list_view.selectedIndexes()
		indList = self.return_obj_ind_list(listToFit)

		
		#Removes duplicates
		indList = list(set(indList))
		#Reverses order.
		indList.sort(reverse=True)
		
		series_2_average = []
		#deletes the objects
		for indL in indList:
				if self.objIdArr[indL].toFit == True:
					
					series_2_average.append(self.objIdArr[indL].autoNorm)
					if series_2_average.__len__() == 1:
						autotime = self.objIdArr[indL].autotime
						sum_auto = np.sum(np.array(autotime))
					else:
						if np.sum(self.objIdArr[indL].autotime) != sum_auto:
							series_2_average.pop(-1)

							
		
		


		if series_2_average == []:
			return
		matrix_2_average = np.zeros((series_2_average.__len__(),series_2_average[0].__len__()))

		for i in range(0,series_2_average.__len__()):
			matrix_2_average[i,:] = series_2_average[i]

		average_out = np.average(matrix_2_average,0)


		corrObj1 = corrObject(None,self)
		corrObj1.siblings = None
		self.objIdArr.append(corrObj1.objId)
		corrObj1.param = copy.deepcopy(self.def_param)
		corrObj1.ch_type = 0
		corrObj1.prepare_for_fit()
		
		corrObj1.kcount = None #objId.kcountCH0[i]
		corrObj1.numberNandB = None #objId.numberNandBCH0[i]
		corrObj1.brightnessNandB = None #objId.brightnessNandBCH0[i]
		corrObj1.type = "scan"
		corrObj1.item_in_list = False
		#corrObj1.siblings = None

		
		corrObj1.name = 'average_data'
		corrObj1.parent_name = 'average_data'
		corrObj1.parent_uqid = 'average_data'
		corrObj1.autotime = autotime
		corrObj1.autoNorm = average_out
		corrObj1.min = np.min(average_out) 
		corrObj1.max = np.max(average_out)
		corrObj1.tmin = np.min(autotime) 
		corrObj1.tmax = np.max(autotime)

		self.fill_series_list()
		
		

		

	def check_all_none(self):
		

		if self.switch_true_false == True:
			for file_id in self.root_name:
				self.root_name[file_id]['file_item'].setCheckState(QtCore.Qt.Checked)
			self.switch_true_false = False
			self.right_check_all_none.setText("check none")

		else:
			for file_id in self.root_name:
				self.root_name[file_id]['file_item'].setCheckState(QtCore.Qt.Unchecked)
			self.switch_true_false = True
			self.right_check_all_none.setText("check all")

	def load_default_profile_fn(self):
		
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
	def load_folder_fn(self):
		self.load_folder_output.showDialog()
	def save_default_profile_fn(self):
		
		self.fit_profile = {}
		self.updateParamFirst()
		self.fit_profile['param'] = copy.deepcopy(self.objId_sel.param)
		self.fit_profile['def_options'] = self.def_options
		
		self.save_default_profile_output.showDialog()
	def store_default_profile_fn(self):
		
		self.fit_profile = {}
		self.updateParamFirst()
		self.fit_profile['param'] = copy.deepcopy(self.objId_sel.param)
		self.fit_profile['def_options'] = copy.deepcopy(self.def_options)
		self.image_status_text.showMessage('Profile stored, use the \'Apply\' button to apply.')
		
	def apply_default_profile_fn(self):
		
		self.def_options = copy.deepcopy(self.fit_profile['def_options'])

		self.diffNumSpecSpin.setValue(self.def_options['Diff_species'])
		self.tripNumSpecSpin.setValue(self.def_options['Triplet_species'])
		self.objId_sel.param = copy.deepcopy(self.fit_profile['param'])


		self.diffModEqSel.setCurrentIndex(self.def_options['Diff_eq']-1)
		self.tripModEqSel.setCurrentIndex(self.def_options['Triplet_eq']-1)
		self.dimenModSel.setCurrentIndex(self.def_options['Dimen']-1)
		
		self.defineTable()
		self.updateParamFirst()
		self.image_status_text.showMessage('Profile Applied.')
	def selectAll(self):
		self.series_list_view.selectAll()

	def fitSelected_equation(self):
		
		listToFit = self.series_list_view.selectedIndexes()
		indList = self.return_obj_ind_list(listToFit)

		
		#Removes duplicates
		indList = list(set(indList))
		#Reverses order.
		indList.sort(reverse=True)
		
		c =0
		

		for indL in indList:
			if self.objIdArr[indL].toFit == True:
				c = c+1
				self.objIdArr[indL].param = copy.deepcopy(self.objId_sel.param)
				self.objIdArr[indL].fitToParameters()
				self.image_status_text.showMessage("Fitting  "+str(c)+" of "+str(indList.__len__())+" plots.")
				self.app.processEvents()
				#Context sensitive colour highlighting
				self.colour_entry(self.objIdArr[indL])
		
		self.updateFitList()
		self.on_show()
	def return_grouped_data_fn(self,indL):
			#Go through each file id.
			indList =[]
			for file_id in self.root_name:
				#Find the one with the matching item to the highlighted item.
				if self.root_name[file_id]['file_item'] == indL:
					#Get the objects in this file.
					objId_list = self.root_name[file_id]['objIdArr']
					

					#Generate a list.
					
					
					for objId in objId_list:
						if objId.series_list_id != None:
							if objId.toFit == True:

								indList.append(self.obj_hash_list[self.tree_hash_list[id(objId.series_list_id)]])

							
					
			return indList			
			

	def return_obj_ind_list(self, listToFit):
		indList =[]
		
		for v_ind in listToFit:
			item = self.series_list_model.itemFromIndex(v_ind)
			if item.hasChildren():
				indList.extend(self.return_grouped_data_fn(id(item)))
			else:
				indList.append(self.obj_hash_list[self.tree_hash_list[id(item)]])
		
		return indList

			
	def removeDataFn(self):
		"""Removes data from the displayed dataseries."""
		
		#Reads those indices which are highlighted.
		listToFit = self.series_list_view.selectedIndexes()
		indList = self.return_obj_ind_list(listToFit)

		
		#Removes duplicates
		indList = list(set(indList))
		#Reverses order.
		indList.sort(reverse=True)
		
		
		#deletes the objects
		for indL in indList:
			#Looks through the objects in objIdArr and deletes them if they match.
			if self.objIdArr[indL].toFit == True:
				del self.objIdArr[indL]
				
					

		
		#Important as rehashes the index.
		self.fill_series_list()
		self.updateFitList()
		#self.on_show()
		
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
					self.modelFitSel.objId_idx = i
					#The name was found.
					name_found = True
		#If the name wasn't found in the list, because it was filtered out. Default to first entry.      
		
		if name_found == False and self.modelFitSel.model_obj_list !=[]:
			self.modelFitSel.setCurrentIndex(0)
			self.modelFitSel.objId_ind = self.objIdArr[self.modelFitSel.currentIndex()]
		#Redraw the table
		#If the currentIndex is valid
		if self.modelFitSel.currentIndex() !=-1:
			#Update the selected entry.
			self.modelFitSel.selected_name = self.objIdArr[self.modelFitSel.currentIndex()]
		

		#Redraw the table

		self.updateTableFirst()


	def resetScaleFn(self):
		self.setAutoScale = True
		self.on_show()
		self.setAutoScale = False
	def autoScaleFn(self):
		#self.turnOffAutoScale.setFlat(True)

		if self.turnOffAutoScale.isChecked() == True:#Keep Scale on.
			self.setAutoScale = False
			self.yscale_min,self.yscale_max = self.axes.get_ylim()
			self.xscale_min,self.xscale_max = self.axes.get_xlim()
		else:
			self.setAutoScale = True

	def norm_to_one_fn(self):
		if self.norm_to_one_btn.isChecked() == True:
			self.norm_to_one = True
		else:
			self.norm_to_one =  False
		
	def copyOutputDataFn(self):

		self.saveOutputDataFn(True)
	def saveOutputDataFn(self,copy_fn=False):
		#Find highlighted indices
		listToFit = self.series_list_view.selectedIndexes()
		indList =[]
		#If no highlighted indices. Take all those which are fitted.
		if listToFit ==[]:
			indList = range(0,self.objIdArr.__len__())
		else:
			for v_ind in listToFit:
				item = self.series_list_model.itemFromIndex(v_ind)
				if item.hasChildren():
					indList.extend(self.return_grouped_data_fn(id(item)))
				else:
					indList.append(self.obj_hash_list[self.tree_hash_list[id(item)]])
		saveOutputDataFn(self,indList,copy_fn)



	def clearFits(self):
		"""If items are selected in the tree view. Clear their fit settings."""
		listToFit = self.series_list_view.selectedIndexes()
		indList = self.return_obj_ind_list(listToFit)

		
		#Removes duplicates
		indList = list(set(indList))
		#Reverses order.
		indList.sort(reverse=True)
		
		
		#deletes the objects
		for indL in indList:
			self.objIdArr[indL].fitted = False
			self.objIdArr[indL].goodFit = True
			self.objIdArr[indL].param = copy.deepcopy(self.def_param)
			self.objIdArr[indL].model_autoNorm =[]
			self.objIdArr[indL].model_autotime = []
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
			f.write('Time (ms)'+',')
		


		listToFit = self.series_list_view.selectedIndexes()
		indList = self.return_obj_ind_list(listToFit)
		
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
				#exec("self."+paraTxt+"_label = QLabel()")
				
				
				exec("self."+paraTxt+"_value = QDoubleSpinBox()")
				exec("self."+paraTxt+"_value.setDecimals("+str(setDec)+")")
				exec("self."+paraTxt+"_value.setSingleStep("+str(setSingStep)+")")
				exec("self."+paraTxt+"_value.setRange("+str(paraMin)+","+str(paraMax)+")")
				
				try:
					exec("self."+paraTxt+"_value.setValue(float(param[\'"+paraTxt+"\']['value']))")
				except:
					exec("self."+paraTxt+"_value.setValue(float(self.def_param[\'"+paraTxt+"\']['value']))")
				
				exec("self."+paraTxt+"_vary = QCheckBox()")
				try:
					exec("self."+paraTxt+"_vary.setChecked(param[\'"+paraTxt+"\']['vary'])")
				except:
					exec("self."+paraTxt+"_vary.setChecked(self.def_param[\'"+paraTxt+"\']['vary'])")
				exec("self."+paraTxt+"_min = QDoubleSpinBox()")
				exec("self."+paraTxt+"_min.setDecimals("+str(setDec)+")")
				exec("self."+paraTxt+"_min.setSingleStep("+str(setSingStep)+")")
				exec("self."+paraTxt+"_min.setRange("+str(paraMin)+","+str(paraMax)+")")
				
				try:
					exec("self."+paraTxt+"_min.setValue(float(param[\'"+paraTxt+"\']['minv']))")
				except:
					exec("self."+paraTxt+"_min.setValue(float(self.def_param[\'"+paraTxt+"\']['minv']))")
				exec("self."+paraTxt+"_max = QDoubleSpinBox()")
				exec("self."+paraTxt+"_max.setDecimals("+str(setDec)+")")
				exec("self."+paraTxt+"_max.setSingleStep("+str(setSingStep)+")")
				exec("self."+paraTxt+"_max.setRange("+str(paraMin)+","+str(paraMax)+")")
				exec("self."+paraTxt+"_label = QLabel()")
				try:
					exec("self."+paraTxt+"_max.setValue(float(param[\'"+paraTxt+"\']['maxv']))")
				except:
					 exec("self."+paraTxt+"_max.setValue(float(self.def_param[\'"+paraTxt+"\']['maxv']))")
				
				#exec("self.fitTable.setCellWidget(row, 0, self."+paraTxt+"_label)")
				exec("self.fitTable.setCellWidget(row, 0, self."+paraTxt+"_value)")
				
			   
				
				exec("self.fitTable.setCellWidget(row, 1, self."+paraTxt+"_vary)")
				exec("self.fitTable.setCellWidget(row, 2, self."+paraTxt+"_min)")
				exec("self.fitTable.setCellWidget(row, 3, self."+paraTxt+"_max)")
	def defineTable(self):
			"""Creates all the fields on the parameter table"""
			self.fitTable.setCurrentCell(0,0)
			self.fitTable.setRowCount(30)
			self.fitTable.setColumnCount(4)
			self.fitTable.setHorizontalHeaderLabels(["Init","Vary","Min","Max", "", "", ""])
			
			
			self.fitTable.setColumnWidth(0,75)
			self.fitTable.setColumnWidth(1,32)
			self.fitTable.setColumnWidth(2,75)
			self.fitTable.setColumnWidth(3,75)
			row = 0
			self.fitTable.repaint()
			self.fitTable.reset()
			self.labelArray =[]

			
			
			#If data is present in the array.
			if self.objIdArr != []:
				#Finds the active data set from the combo box.
				if  self.modelFitSel.model_obj_list != []:
					self.objId_sel = self.modelFitSel.model_obj_list[self.modelFitSel.currentIndex()]
					if self.def_options['Diff_eq'] == 5: 
						PB.decide_which_to_show(self)
						PB.calc_param_fcs(self,self.objId_sel)
					elif self.def_options['Diff_eq'] == 4: 
						VD.decide_which_to_show(self)
						VD.calc_param_fcs(self,self.objId_sel)
					elif self.def_options['Diff_eq'] == 3: 
						GS.decide_which_to_show(self)
						GS.calc_param_fcs(self,self.objId_sel)
					else:
						SE.decide_which_to_show(self)
						SE.calc_param_fcs(self,self.objId_sel)
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
						self.paramFactory(paraTxt=item, setDec=6 ,paraMin=-1.0, paraMax=100000, setSingStep=0.01, row=row, param=param)
						self.labelArray.append(' '+param[item]['alias'])
						row +=1
					else:
						if col == 0:
							label = QLabel(' '+str(np.round(param[item]['value'],3)))
							
							self.fitTable.setCellWidget(row, 0, label)
							self.labelArray.append(' '+param[item]['alias'])

							
							col = 2
							row +=1
							continue
						if col ==2:
							label = QLabel(' '+str(np.round(param[item]['value'],3)))
							#label.setToolTip('test'+str(item))
							#self.fitTable.horizontalHeader().Item[0].setToolTip("header 0")

							label_2 = QLabel(str(' '+param[item]['alias']))
							self.fitTable.setCellWidget(row-1, 3, label)
							self.fitTable.setCellWidget(row-1, 2,label_2)
							#self.fitTable.verticalHeaderItem(row-1).setToolTip("Column 1 ")
							
							col = 0

			self.fitTable.setVerticalHeaderLabels(self.labelArray)
			self.fitTable.setRowCount(row)

	

	def add_actions(self, target, actions):
		for action in actions:
			if action is None:
				target.addSeparator()
			else:
				target.addAction(action)

	

	
				
	def updateParam(self):
		#Update the parameters.
		if self.def_options['Diff_eq'] == 5:
			PB.update_param_fcs(self)
		elif self.def_options['Diff_eq'] == 4:
			VD.update_param_fcs(self)
		elif self.def_options['Diff_eq'] == 3:
			GS.update_param_fcs(self)
		else:
			SE.update_param_fcs(self)
	def update_calc(self,objId):
		if self.def_options['Diff_eq'] == 5:
			PB.calc_param_fcs(self,objId)
		elif self.def_options['Diff_eq'] == 4:
			VD.calc_param_fcs(self,objId)
		elif self.def_options['Diff_eq'] == 3:
			GS.calc_param_fcs(self,objId)
		else:
			SE.calc_param_fcs(self,objId)
		
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
			#self.fill_series_list()
			self.on_show()
			self.updateFitList()
			#Context sensitive colour highlighting
			self.colour_entry(self.objId_sel)


	def fitAll_equation(self):
		"""Take the active parameters and applies them to all the other data which is not filtered"""
		#Make sure all table properties are stored
		self.updateParamFirst()

		c = 0
		import time

		for Id, objId in enumerate(self.objIdArr):
			t0 = time.time()
			#Preflight fit.
			#This will fit the selected curve once before using those generated parameters to initialise all the other curves before fitting them in bulk.
			#This was done accidently in the standalone versions, but made subsequent fits much faster and so is included here as an option.
			#Makes a big difference if the parameters are not well chosen by the user or defaults are used, as it prevents lots of badly conditioned fits.
			if objId.toFit == True:
				c = c+1
				if objId != self.objId_sel:
					#objId.param = Parameters()
					objId.param = copy.deepcopy(self.objId_sel.param)
				
				objId.fitToParameters()
				#self.update_calc(objId)
				self.image_status_text.showMessage("Fitting  "+str(c)+" of "+str(self.modelFitSel.model_obj_ind_list.__len__())+" curves.")
				self.app.processEvents()

					
				#Context sensitive colour highlighting
				self.colour_entry(objId)
			print('time',time.time()-t0)		


		
		
		self.on_show()
		self.updateFitList() 
		#self.fill_series_list()


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
		if self.parent.mpl_toolbar._active == "PAN" or self.parent.mpl_toolbar._active == "ZOOM": return
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
class comboBoxSp2(QComboBox):
	"""class which is used for multiple dynamic drop-down lists.
	including the model parameter selection."""
	def __init__(self, parent=None):
		QComboBox.__init__(self, parent)
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
		if self.type == 'Diff_eq':
			
			if self.parent.def_options['Diff_eq'] == 5:
				self.parent.order_list = ['offset','GN0','txy1','bA','Kz']
			elif self.parent.def_options['Diff_eq'] == 4:
				self.parent.order_list = ['offset','GN0','ves_radius','FWHM','D']
			elif self.parent.def_options['Diff_eq'] == 3:
				#GS.initialise_fcs(self.parent)
				self.parent.order_list = ['offset','GN0','Y','A1','A2','A3','tdiff1','tdiff2','tdiff3','B1','B2','B3','T1','T2','T3','tauT1','tauT2','tauT3']
			else:
				self.parent.order_list = ['offset','GN0','N_FCS','cpm','A1','A2','A3','txy1','txy2','txy3','tz1','tz2','tz3','alpha1','alpha2','alpha3','AR1','AR2','AR3','B1','B2','B3','T1','T2','T3','tauT1','tauT2','tauT3','N_mom','bri','CV','f0','overtb','ACAC','ACCC','above_zero','s2n']

				
		if self.parent.def_options['Diff_eq'] == 5:
			VD.decide_which_to_show(self.parent)
		elif self.parent.def_options['Diff_eq'] == 4:
			VD.decide_which_to_show(self.parent)
		elif self.parent.def_options['Diff_eq'] == 3:
			GS.decide_which_to_show(self.parent)
		else:
			SE.decide_which_to_show(self.parent)
		self.parent.defineTable()
		
class spinBoxSp3(QDoubleSpinBox):
	def __init__(self,parent):
		QDoubleSpinBox.__init__(self,parent)
		self.setDecimals(5)
		self.setMaximum(90000)
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
		return QAbstractSpinBox.StepUpEnabled | QAbstractSpinBox.StepDownEnabled 
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


if __name__ == "__main__":
	app = QApplication(sys.argv)
	form = Form()
	form.show()
	app.exec_()
	
	
	
	
	
	 