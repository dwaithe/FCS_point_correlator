from PyQt4 import QtGui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pyperclip
class TableFilterBox(QtGui.QTableWidget):
	
	def __init__(self,int_obj):
		QtGui.QTableWidget.__init__(self,int_obj)
		#self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		self.setShowGrid(False);

		self.verticalHeader().setVisible(False)
		self.horizontalHeader().setVisible(False)
		
		self.setRowCount(1)
		self.setColumnCount(4)
		self.setColumnWidth(0,20);
		self.setColumnWidth(1,100);
		self.setColumnWidth(2,65);
		self.setColumnWidth(3,30);
		



		self.int_obj = int_obj
		self.filter_list = []
		#self.filter_add_fn()




	def filter_add_fn(self):
		
		filter_select_txt = self.int_obj.filter_select.currentText()
		less_than_txt = self.int_obj.filter_lessthan.currentText()
		filter_value = self.int_obj.filter_value.text()
		try: 
			filter_float = float(filter_value)
		except:
			return;
		#if lessthan_txt =='>':
		#	less_than_op = True
		#else:
		#	less_than_op =False
		self.filter_list.append([str(filter_select_txt),str(less_than_txt),str(filter_float),1])
		self.filter_generate_list()

	def filter_generate_list(self):
		print 'how often'
		self.setRowCount(1)
		self.reset()
		for ind, filt in enumerate(self.filter_list):
			
			item = QtGui.QLabel(' '+str(filt[0])+' '+str(filt[1])+' '+str(filt[2]))
			#item.setCheckState(QtCore.Qt.Checked)
			curr_row = self.rowCount()
			self.setRowCount(curr_row + 1)
			
			x_btn = self.XBtn('',self,ind)

			checkbox = QtGui.QCheckBox()
			checkbox.setChecked(True)
			
			
			
			self.toggle_btn = self.ToggleBtn('',self,ind)
		
			
			self.setCellWidget(curr_row-1,0,checkbox)
			self.setCellWidget(curr_row-1,1,item)
			self.setCellWidget(curr_row-1,2,self.toggle_btn)
			self.setCellWidget(curr_row-1,3,x_btn)
		self.int_obj.fill_series_list()
	class XBtn(QtGui.QPushButton):
	
		def __init__(self,txt,table,ind):
			QtGui.QPushButton.__init__(self)
			self.setIcon(QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_TitleBarCloseButton))
			self.table = table
			self.ind = ind
			self.clicked.connect(self.remove_row)
			self.repaint()
			
		def remove_row(self):
			
			self.table.reset()
			self.table.filter_list.pop(self.ind)
			self.table.setRowCount(0)
			self.table.filter_generate_list()
	class ToggleBtn(QtGui.QPushButton):
	
		def __init__(self,txt,table,ind):
			QtGui.QPushButton.__init__(self)
			self.switch = {0:'off',1:'show',2:'apply'}
			self.table = table
			self.ind = ind
			#self.tog = tog
			self.clicked.connect(self.toggle)
			self.setText(self.switch[self.table.filter_list[self.ind][3]])
			
		def toggle(self):
			if self.table.filter_list[self.ind][3] == 0:
				self.table.filter_list[self.ind][3] = 1
				self.table.int_obj.fill_series_list()
				self.setText(self.switch[ self.table.filter_list[self.ind][3]])
				self.repaint()
				return
				
			if  self.table.filter_list[self.ind][3] ==1:
				self.table.filter_list[self.ind][3] = 2
				self.table.int_obj.fill_series_list()
				self.setText(self.switch[ self.table.filter_list[self.ind][3]])
				self.repaint()
				return
				
			if  self.table.filter_list[self.ind][3] == 2:
				self.table.filter_list[self.ind][3] = 0
				self.table.int_obj.fill_series_list()
				self.setText(self.switch[ self.table.filter_list[self.ind][3]])
				self.repaint()
				return

class visualScatter(QtGui.QMainWindow):
	def __init__(self,parObj):
		QtGui.QMainWindow.__init__(self)
		self.parObj = parObj
	def create_main_frame(self):
		
		#self.trace_idx = self.parObj.clickedS1

		page = QtGui.QWidget()        
		hbox_main = QtGui.QHBoxLayout()
		vbox1 = QtGui.QVBoxLayout()
		vbox0 = QtGui.QVBoxLayout()
		self.setWindowTitle("Data Visualisation")
		self.figure1 = plt.figure(figsize=(10,4))
		self.figure1.patch.set_facecolor('white')
		self.canvas1 = FigureCanvas(self.figure1)

		
		self.plt1 = self.figure1.add_subplot(1,1,1)
		self.plt1.set_ylabel('frequency')
		self.plt1.set_xlabel('bins')

		
		
		
		
		self.generate_scatter_btn = QtGui.QPushButton('Generate Scatter')
		
		self.visual_param_select_1_panel = QtGui.QHBoxLayout()
		self.visual_param_select_1 = QtGui.QComboBox();
		self.visual_param_select_1_check = QtGui.QCheckBox('norm',self)
		self.visual_param_select_1_panel.addWidget(self.visual_param_select_1)
		self.visual_param_select_1_panel.addWidget(self.visual_param_select_1_check)

		self.visual_param_select_2_panel = QtGui.QHBoxLayout()
		self.visual_param_select_2 = QtGui.QComboBox();
		self.visual_param_select_2_check = QtGui.QCheckBox('norm',self)
		self.visual_param_select_2_panel.addWidget(self.visual_param_select_2)
		self.visual_param_select_2_panel.addWidget(self.visual_param_select_2_check)

		

		self.generate_menu(self.visual_param_select_1)
		self.generate_menu(self.visual_param_select_2) 
		
		self.generate_scatter_btn.clicked.connect(self.generate_scatter)
		
		copy_data_btn = QtGui.QPushButton('Copy to clipboard')
		copy_data_btn.clicked.connect(self.copy_to_clipboard)
		save_data_btn = QtGui.QPushButton('Save to file')
		save_data_btn.clicked.connect(self.save_to_file)
		hbox_main.addLayout(vbox0)
		hbox_main.addLayout(vbox1)
		
		
		
	
		
		vbox0.addLayout(self.visual_param_select_1_panel)
		vbox0.addLayout(self.visual_param_select_2_panel)
		

		
		
		vbox0.addWidget(self.generate_scatter_btn)
		vbox0.addWidget(copy_data_btn)
		vbox0.addWidget(save_data_btn)
		vbox0.addStretch();
		vbox1.addWidget(self.canvas1)
		
		page.setLayout(hbox_main)
		self.setCentralWidget(page)
		self.show()
		

	def generate_scatter(self):
		self.data_1 = []
		indList = range(0,self.parObj.objIdArr.__len__())
		for v_ind in indList:
			if self.parObj.objIdArr[v_ind].toFit == True:
				if self.parObj.objIdArr[v_ind].fitted == True:
					for art in self.parObj.objIdArr[v_ind].param:
						if art == self.visual_param_select_1.currentText():
							self.data_1.append(self.parObj.objIdArr[v_ind].param[art]['value'])
		self.data_2 = []
		indList = range(0,self.parObj.objIdArr.__len__())
		for v_ind in indList:
			if self.parObj.objIdArr[v_ind].toFit == True:
				if self.parObj.objIdArr[v_ind].fitted == True:
					for art in self.parObj.objIdArr[v_ind].param:
						if art == self.visual_param_select_2.currentText():
							self.data_2.append(self.parObj.objIdArr[v_ind].param[art]['value'])
		

		if self.data_1 !=[] and self.data_2 !=[]:
			if self.visual_param_select_1_check.isChecked():
				self.data_1 = list(np.array(self.data_1)/np.median(self.data_1))
			if self.visual_param_select_2_check.isChecked():
				self.data_2 = list(np.array(self.data_2)/np.median(self.data_2))

			self.plt1.cla();
			self.plt1.scatter(np.array(self.data_1).astype(np.float64), np.array(self.data_2).astype(np.float64), facecolor='green', alpha=0.75)
			
			self.plt1.set_xlim(np.min(self.data_1)*0.8,np.max(self.data_1)*1.2)
			self.plt1.set_ylim(np.min(self.data_2)*0.8,np.max(self.data_2)*1.2)
			
			self.title_1 = self.visual_param_select_1.currentText()
			self.title_2 = self.visual_param_select_2.currentText()
			self.plt1.set_xlabel(self.title_1)
			self.plt1.set_ylabel(self.title_2)
			self.canvas1.draw()
			
	def copy_to_clipboard(self):
		
		copyStr = ""
		copyStr += str(self.title_1)+"\t"+str(self.title_2) +"\n"
		for i in range(0,self.data_1.__len__()):
			copyStr += str(self.data_1[i])+"\t"+ str(self.data_2[i]) +"\n"
		
		pyperclip.copy(copyStr)
		self.parObj.image_status_text.showMessage("Data copied to the system clipboard.")
				
	def save_to_file(self):
		outPath = self.parObj.folderOutput.filepath
		filenameTxt = str(self.parObj.fileNameText.text())
		filenamePth = outPath+'/'+filenameTxt+'_scatter_data.csv'
		f = open(filenamePth, 'w')
		f.write(str(self.title_1)+","+str(self.title_2) +"\n")
		for i in range(0,self.data_1.__len__()):
			f.write(str(self.data_1[i])+","+ str(self.data_2[i]) +"\n")
		self.parObj.image_status_text.showMessage("Data save to the path: "+outPath+'/'+filenameTxt+'_scatter_data.csv')


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
			for art in self.parObj.objIdArr[v_ind].param:
				if self.parObj.objIdArr[v_ind].param[art]['to_show'] !=False:
					combo.addItem(art)
			
class visualHisto(QtGui.QMainWindow):
	def __init__(self,parObj):
		QtGui.QMainWindow.__init__(self)
		self.parObj = parObj
	def create_main_frame(self):
		
		#self.trace_idx = self.parObj.clickedS1

		page = QtGui.QWidget()        
		hbox_main = QtGui.QHBoxLayout()
		vbox1 = QtGui.QVBoxLayout()
		vbox0 = QtGui.QVBoxLayout()
		self.setWindowTitle("Data Visualisation")
		self.figure1 = plt.figure(figsize=(10,4))
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
				#if self.parObj.objIdArr[v_ind].fitted == True:
					for art in self.parObj.objIdArr[v_ind].param:
						if art == self.visual_param_select.currentText():
							self.data.append(self.parObj.objIdArr[v_ind].param[art]['value'])

		
		
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
		copyStr = ""
		for i in range(0,self.n.__len__()):
			
			
			copyStr += str(self.bins[i])+"-"+str(self.bins[i+1])+"\t"+ str(self.n[i]) +"\n"
		
		pyperclip.copy(copyStr)
		self.parObj.image_status_text.showMessage("Data copied to the system clipboard.")
				
	def save_to_file(self):
		outPath = self.parObj.folderOutput.filepath
		filenameTxt = str(self.parObj.fileNameText.text())
		filenamePth = outPath+'/'+filenameTxt+'_histo_data.csv'
		f = open(filenamePth, 'w')
		
		
		f.write("bin"+","+str("frequency") +"\n")

		
		for i in range(0,self.n.__len__()):
			f.write(str(self.bins[i])+"-"+str(self.bins[i+1])+","+ str(self.n[i]) +"\n")
		self.parObj.image_status_text.showMessage("Data save to the path: "+outPath+'/'+filenameTxt+'_histo_data.csv')


	def generate_menu(self,combo):
		#Ensures the headings are relevant to the fit.

		
		proceed=False;
		for i in range(0,self.parObj.objIdArr.__len__()):
			if self.parObj.objIdArr[i].toFit == True:
				#if self.parObj.objIdArr[i].fitted == True:
					v_ind = i;
					proceed = True;
					break;
			
		
		if proceed == True:
			#Includes the headers for the data which is present.
			for art in self.parObj.objIdArr[v_ind].param:
				if self.parObj.objIdArr[v_ind].param[art]['to_show'] !=False:
					combo.addItem(art)
				#combo.addItem('stderr('+key+')')
				
		
				#combo.addItem('stderr('+key+')')
		
		