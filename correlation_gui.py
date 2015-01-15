import struct
import numpy as np
#import scipy.weave as weave
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys, csv, os

from PyQt4 import QtGui, QtCore
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.transforms import ScaledTranslation
import random
import errno
import os.path

from scipy.special import _ufuncs_cxx
import cPickle as pickle
from correlation_objects import *

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
class folderOutput(QtGui.QMainWindow):
    
    def __init__(self,parent):
        super(folderOutput, self).__init__()
       
        self.initUI()
        self.parent = parent
        self.parent.config ={}
        
        try:
            self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ));
            self.filepath = self.parent.config['output_corr_filepath']
        except:
            self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
            try:
                os.makedirs(self.filepath)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
        
        
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

        if self.type == 'output_corr_dir':
            #folderSelect = QtGui.QFileDialog()
            #folderSelect.setDirectory(self.filepath);
            tfilepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
            
            if tfilepath !='':
                self.filepath = tfilepath
            #Save to the config file.
                self.parent.config['output_corr_filepath'] = str(tfilepath)
                pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "w" ))
            

class Annotate():
    def __init__(self,win_obj,par_obj,scrollBox):
        self.ax = plt.gca()
        
        self.x0 = []
        self.par_obj = par_obj
        self.win_obj = win_obj
        self.scrollBox = scrollBox
        
        self.pickerSelect = False;
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        

    def on_press(self, event):
        self.ax.figure.canvas.draw()
        self.x0 = event.xdata
        

    def on_release(self, event):
        #self.rect.remove()
        self.x1 = event.xdata
        
        if(self.x0 <0): self.x0 =0
        if(self.x1 <0): self.x1 =0
        if(self.x0 >self.x1): self.x1b =self.x0;self.x0=self.x1;self.x0=self.x1b
       

        self.scrollBox.rect.append(plt.axvspan(self.x0, self.x1, facecolor=self.par_obj.colors[self.scrollBox.rect.__len__() % len(self.par_obj.colors)], alpha=0.5,picker=True))
        self.ax.figure.canvas.draw()
        #Saves regions to series of arrays. Opted not to make class for this. Not sure why :-)
        self.scrollBox.x0.append(self.x0)
        self.scrollBox.x1.append(self.x1)
        self.scrollBox.color = self.par_obj.colors[self.scrollBox.rect.__len__()]
        self.scrollBox.TGid.append(self.par_obj.TGnumOfRgn)
        self.scrollBox.facecolor.append(self.par_obj.colors[self.par_obj.TGnumOfRgn])
        self.par_obj.TGnumOfRgn = self.par_obj.TGnumOfRgn + 1
        self.scrollBox.generateList()
        #refreshTable()
    def freshDraw(self):
            self.scrollBox.rect =[]
            for i in range(0,self.scrollBox.x0.__len__()):
                
                self.scrollBox.rect.append(plt.axvspan(self.scrollBox.x0[i], self.scrollBox.x1[i], facecolor=self.par_obj.colors[i % len(self.par_obj.colors)], alpha=0.5,picker=True))
            self.win_obj.canvas5.draw() 
    def redraw(self):
            
            for i in range(0,self.scrollBox.rect.__len__()):
                self.scrollBox.rect[i].remove()
            self.scrollBox.rect =[]
            for i in range(0,self.scrollBox.x0.__len__()):
                
                self.scrollBox.rect.append(plt.axvspan(self.scrollBox.x0[i], self.scrollBox.x1[i], facecolor=self.par_obj.colors[i % len(self.par_obj.colors)], alpha=0.5,picker=True))
            self.win_obj.canvas5.draw() 

    
class baseList(QtGui.QLabel):
    def __init__(self):
        super(baseList, self).__init__()
        self.listId=0
    def mousePressEvent(self,ev):
        print self.listId

class FileDialog(QtGui.QMainWindow):
    
    def __init__(self, win_obj, par_obj, fit_obj):
        super(FileDialog, self).__init__()
       
        
        self.initUI()
        self.par_obj = par_obj
        self.fit_obj = fit_obj
        self.win_obj = win_obj

        
        
    def initUI(self):      

        self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)       
        
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle('File dialog')
        #self.show()
        
    def showDialog(self):
        #Intialise Dialog.
        fileInt = QtGui.QFileDialog()
        try:
            #Try and read the default location for a file.
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'r')
            self.loadpath =f.readline()
            f.close() 
        except:
            #If not default will do.
            self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'

        
        #Create loop which opens dialog box and allows selection of files.

        self.win_obj.update_correlation_parameters()
        for filename in fileInt.getOpenFileNames(self, 'Open a data file',self.loadpath, 'pt3 files (*.pt3);;All Files (*.*)'):
            picoObject(filename,self.par_obj,self.fit_obj);
            self.loadpath = str(QtCore.QFileInfo(filename).absolutePath())
            self.par_obj.numOfLoaded = self.par_obj.numOfLoaded+1
            self.win_obj.label.generateList()
            self.win_obj.TGScrollBoxObj.generateList()
            self.win_obj.updateCombo()
            self.win_obj.cbx.setCurrentIndex(self.par_obj.numOfLoaded-1)
            self.win_obj.plot_PhotonCount(self.par_obj.numOfLoaded-1)
        self.win_obj.plotDataQueueFn()
        try:
            
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'w')

            f.write(self.loadpath)
            f.close()
            
        except:
            print 'nofile'



        #Update listing:
        #main.label.remakeList()

    
class Window(QtGui.QWidget):
    def __init__(self, par_obj, fit_obj):
        super(Window, self).__init__()
        self.fit_obj = fit_obj
        self.par_obj = par_obj
        self.generateWindow()
    def generateWindow(self):
        # a figure instance to plot on
        self.figure1 = plt.figure(figsize=(10,8))


        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1 = FigureCanvas(self.figure1)
        self.figure1.patch.set_facecolor('white')
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar1 = NavigationToolbar(self.canvas1, self)

        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)
        
        #self.toolbar2 = NavigationToolbar(self.canvas2, self)

        self.figure3 = plt.figure()
        self.canvas3 = FigureCanvas(self.figure3)
        #self.toolbar3 = NavigationToolbar(self.canvas3, self)

        self.figure4 = plt.figure(figsize=(7,3))
        self.canvas4 = FigureCanvas(self.figure4)
        self.figure4.patch.set_facecolor('white')
        #self.toolbar4 = NavigationToolbar(self.canvas4, self)

        self.figure5 = plt.figure(figsize=(4,3))
        self.canvas5 = FigureCanvas(self.figure5)
        self.figure5.patch.set_facecolor('white')
        #Tself.toolbar5 = NavigationToolbar(self.canvas5, self)


        self.ex = FileDialog(self, self.par_obj, self.fit_obj)

        self.folderOutput = folderOutput(self.par_obj)
        self.folderOutput.type = 'output_corr_dir'

        # Just some button connected to `plot` method
        self.openFile = QtGui.QPushButton('Open File')
        self.openFile.clicked.connect(self.ex.showDialog)
        self.replot_btn = QtGui.QPushButton('Replot Data')
        self.replot_btn.clicked.connect(self.plotDataQueueFn)
        self.replot_btn2 = QtGui.QPushButton('Replot Data')
        self.replot_btn2.clicked.connect(self.plotDataQueueFn)
        self.saveAll_btn = QtGui.QPushButton('Save All')
        self.saveAll_btn.clicked.connect(self.saveDataQueue)

        self.normPlot = QtGui.QCheckBox('Normalise')
        self.normPlot.setChecked(False)
        #self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        #self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        # set the layout
        self.spacer = QtGui.QLabel()
        main_layout = QtGui.QHBoxLayout()
        self.globalText = QtGui.QLabel()
        self.globalText.setText('Correlation Para:')
        self.reprocess_btn = QtGui.QPushButton('reprocess data')
        self.reprocess_btn.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn2 = QtGui.QPushButton('reprocess data')
        self.reprocess_btn2.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn3 = QtGui.QPushButton('reprocess data')
        self.reprocess_btn3.clicked.connect(self.reprocessDataFn)
        
        self.NsubText = QtGui.QLabel('Nsub:')
        self.NsubText.resize(50,40)
        self.NsubEdit =lineEditSp('6',self)
        self.NsubEdit.type ='nsub'
        
        self.NcascStartText = QtGui.QLabel('Ncasc Start:')
        self.NcascStartEdit = lineEditSp('0',self)
        self.NcascStartEdit.parentId = self
        self.NcascStartEdit.type = 'ncasc'
        self.NcascEndText = QtGui.QLabel('Ncasc End:')
        self.NcascEndEdit = lineEditSp('25',self)
        self.NcascEndEdit.type = 'ncascEnd'
        self.NcascEndEdit.parentId = self
        
        self.winIntText = QtGui.QLabel('Bin Size (CH):')

        self.winIntEdit = lineEditSp('10',self)
        self.winIntEdit.type = 'winInt'
        self.winIntEdit.parObj = self
        self.folderSelect_btn = QtGui.QPushButton('Output Folder')
        self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

        
        #Adds an all option to the combobox.lfkk

        

        
        
        #grid1.addWidget(self.folderSelect_btn,11,0)
       
        
        #grid1.addWidget(self.spacer,12,0,20,0)
        
        

        self.label =scrollBox(self,self.par_obj)
        self.TGScrollBoxObj =TGscrollBox(self,self.par_obj)

        #The table which shows the details of the time-gating.
        self.modelTab = QtGui.QTableWidget(self)
        self.modelTab.setRowCount(0)
        self.modelTab.setColumnCount(7)
        
        
        self.modelTab.setColumnWidth(0,20);
        self.modelTab.setColumnWidth(1,40);
        self.modelTab.setColumnWidth(2,20);
        self.modelTab.setColumnWidth(3,40);
        self.modelTab.setColumnWidth(4,85);
        self.modelTab.setColumnWidth(5,70);
        self.modelTab.setColumnWidth(6,20);
        self.modelTab.horizontalHeader().setStretchLastSection(True)
        self.modelTab.setMinimumSize(350,200)
        self.modelTab.setHorizontalHeaderLabels(QtCore.QString(",From: , ,To: ,Apply to:, , , , ").split(","))

        #The table which shows the details of each correlated file. 
        self.modelTab2 = QtGui.QTableWidget(self)
        self.modelTab2.setRowCount(0)
        self.modelTab2.setColumnCount(5)
        self.modelTab2.setColumnWidth(0,80);
        self.modelTab2.setColumnWidth(1,140);
        self.modelTab2.setColumnWidth(2,30);
        self.modelTab2.setColumnWidth(3,100);
        self.modelTab2.setColumnWidth(4,100);
        self.modelTab2.setColumnWidth(5,100);
        self.modelTab2.horizontalHeader().setStretchLastSection(True)
        self.modelTab2.resize(800,400)
        self.modelTab2.setHorizontalHeaderLabels(QtCore.QString(",data name,plot,,file name").split(","))

        tableAndBtns =  QtGui.QVBoxLayout()
        correlationBtns =  QtGui.QHBoxLayout()
        #self.label.setText('<HTML><H3>DATA file: </H3><P>'+str(6)+' Click here to load in this sample and what happens if I make it too long.</P></HTML>')
        #self.label.listId = 6
        self.fileDialog = QtGui.QFileDialog()
        self.centre_panel = QtGui.QVBoxLayout()
        
        
        
    
        self.right_panel = QtGui.QVBoxLayout()
        #Adds the main graph components to the top panel
       

        #LEFT PANEL
        self.left_panel = QtGui.QVBoxLayout()
        self.left_panel.addWidget(self.canvas4)
        
        #LEFT PANEL TOP
        self.left_panel_top_btns= QtGui.QHBoxLayout()
        self.plotText =QtGui.QLabel()
        self.plotText.setText('Plot: ')
        self.left_panel_top_btns.addWidget(self.plotText)
        self.photonCountText =QtGui.QLabel()
        self.photonCountText.setText('Bin Size: ')
        self.photonCountEdit = lineEditSp('25',self)
        self.photonCountEdit.parObj = self
        self.photonCountEdit.resize(40,50)

    

        self.cbx = comboBoxSp(self)
        self.cbx.type ='PhotonCount'
        self.updateCombo()
        self.left_panel_top_btns.addWidget(self.cbx)
        self.left_panel_top_btns.addWidget(self.photonCountText)
        self.left_panel_top_btns.addWidget(self.photonCountEdit)
        self.left_panel_top_btns.addWidget(self.reprocess_btn3)
        self.left_panel_top_btns.addStretch()

        self.left_panel.addLayout(self.left_panel_top_btns)


        #LEFT PANEL centre
        self.left_panel_centre = QtGui.QHBoxLayout()

        #LEFT PANEL centre right
        self.left_panel_centre_right = QtGui.QVBoxLayout()
        
        self.left_panel.addLayout(self.left_panel_centre)
        
        self.left_panel_centre.addWidget(self.modelTab)
        self.left_panel_centre.addLayout(self.left_panel_centre_right)
        
        #LEFT PANEL bottom
        self.left_panel_bottom = QtGui.QVBoxLayout()
        self.left_panel_bottom.addWidget(self.canvas5)
        
        self.left_panel.addLayout(self.left_panel_bottom)
        #LEFT PANEL bottom buttons
        self.left_panel_bottom_btns = QtGui.QHBoxLayout()
        self.left_panel_bottom.addLayout(self.left_panel_bottom_btns)
        self.left_panel_bottom_btns.addWidget(self.normPlot)
        self.left_panel_bottom_btns.addWidget(self.replot_btn2)
        self.left_panel_bottom_btns.addWidget(self.winIntText)

        self.left_panel_bottom_btns.addWidget(self.winIntEdit)
        self.left_panel_bottom_btns.addWidget(self.reprocess_btn2)
        #

        self.left_panel_bottom_btns.addStretch()


        self.left_panel_centre_right.setSpacing(2)
        self.left_panel_centre_right.addWidget(self.openFile)
        
        self.left_panel_centre_right.addWidget(self.globalText)
        
        self.left_panel_centre_right.addWidget(self.NsubText)
        self.left_panel_centre_right.addWidget(self.NsubEdit)
        self.left_panel_centre_right.addWidget(self.NcascStartText)
        self.left_panel_centre_right.addWidget(self.NcascStartEdit)
        self.left_panel_centre_right.addWidget(self.NcascEndText)
        self.left_panel_centre_right.addWidget(self.NcascEndEdit)
        self.left_panel_centre_right.addWidget(self.reprocess_btn)
        
        self.left_panel_centre_right.setAlignment(QtCore.Qt.AlignTop)
        self.right_panel.addWidget(self.canvas1)
        self.right_panel.addLayout(correlationBtns)
        self.right_panel.addWidget(self.modelTab2)

        
        
        correlationBtns.addWidget(self.replot_btn)
        correlationBtns.addWidget(self.folderSelect_btn)
        correlationBtns.addWidget(self.saveAll_btn)
        correlationBtns.addWidget(self.toolbar1)
        correlationBtns.setAlignment(QtCore.Qt.AlignLeft)
        tableAndBtns.addWidget(self.modelTab2)
        
        self.setLayout(main_layout)
        main_layout.addLayout(self.left_panel)
        #main_layout.addLayout(self.centre_panel)
        main_layout.addLayout(self.right_panel)
        #main_layout.addLayout(self.right_panel)


        

        self.plt1= self.figure1.add_subplot(311)
        self.plt2= self.figure1.add_subplot(312)
        self.plt3= self.figure1.add_subplot(313)
        self.plt4= self.figure4.add_subplot(111)
        self.plt5= self.figure5.add_subplot(111)

        
   

        self.figure1.suptitle('Correlation', fontsize=20)
        self.figure4.suptitle('Photon Count', fontsize=12)
        self.figure5.suptitle('TCSPC', fontsize=12)
        self.plt5.a = Annotate(self,self.par_obj,self.TGScrollBoxObj)
    def update_correlation_parameters(self):
        self.par_obj.NcascStart = int(self.NcascStartEdit.text())
        self.par_obj.NcascEnd = int(self.NcascEndEdit.text())
        self.par_obj.Nsub = int(self.NsubEdit.text())
        self.par_obj.winInt = float(self.winIntEdit.text())
        self.par_obj.photonCountBin = float(self.photonCountEdit.text())
        
    def plotDataQueueFn(self):
        self.plt1.cla()
        self.plt2.cla()
        self.plt3.cla()
        
        
        self.plt5.clear()
        self.canvas1.draw()
        
        self.canvas5.draw()
        for x in range(0, self.par_obj.numOfLoaded):
            if(self.label.objCheck[x].isChecked() == True):
                
                self.plot(self.par_obj.objectRef[x])
        for y in range(0, self.par_obj.subNum):

            if(self.label.objCheck[y+x+1].isChecked() == True):
                
                self.plot(self.par_obj.subObjectRef[y])
        self.plt5.ax = plt.gca()
        self.plt5.a.freshDraw()
    def reprocessDataFn(self):

        for i in range(0, self.label.numOfLoaded):
                    self.objectRef[i].processData()
        for i in range(0, self.label.subNum):
                    self.subObjectRef[i].processData()

        self.plotDataQueueFn();
        self.plot_PhotonCount(self.label.numOfLoaded-1)
    def updateCombo(self):
        """Updates photon counting combox box"""
        self.cbx.clear()
        #Populates comboBox with datafiles to which to apply the time-gating.
        for b in range(0,self.par_obj.numOfLoaded):
                self.cbx.addItem("Data: "+str(b), b)
    def plot_PhotonCount(self,index):
        """Plots the photon counting"""
        object = self.par_obj.objectRef[index]
        self.plt4.clear()
        self.canvas4.draw()
        
        self.plt4.bar(np.array(object.timeSeriesScale1),np.array(object.timeSeries1), float(object.photonCountBin), color=object.color,linewidth=0)
        if object.numOfCH ==  2:
            self.plt4.bar(np.array(object.timeSeriesScale2),-1*np.array(object.timeSeries2).astype(np.float32),float(object.photonCountBin),color="grey",linewidth=0,edgecolor = None)
       
        self.figure4.subplots_adjust(left=0.15,bottom=0.25)
        self.plt4.set_xlim(0,object.timeSeriesScale1[-1])
        self.plt4.set_xlabel('Time (ms)', fontsize=12)
        self.plt4.set_ylabel('Photon counts', fontsize=12)
        self.plt4.xaxis.grid(True,'minor')
        self.plt4.xaxis.grid(True,'major')
        self.plt4.yaxis.grid(True,'minor')
        self.plt4.yaxis.grid(True,'major')
        self.canvas4.draw()

            
    def plot(self,object):
        ''' plot some random stuff '''

        autotime = object.autotime
        
        auto = object.autoNorm
        corrText = 'Auto-correlation'
        
        
        subDTimeMax = object.subDTimeMax
        subDTimeMin = object.subDTimeMin
        
        
        self.plt1.plot(autotime,auto[:,0,0],object.color)
        self.plt1.set_xscale('log')
        self.plt1.set_xlim([0, np.max(autotime)])
        self.plt1.set_xlabel('Tau (ms)', fontsize=12)
        self.plt1.set_ylabel(corrText+' CH0', fontsize=12)
        self.plt1.xaxis.grid(True,'minor')
        self.plt1.xaxis.grid(True,'major')
        self.plt1.yaxis.grid(True,'minor')
        self.plt1.yaxis.grid(True,'major')
        if object.numOfCH ==  2:
            self.plt2.plot(autotime,auto[:,1,1],object.color)
            self.plt2.set_xscale('log')
            self.plt2.set_xlim([0, np.max(autotime)])
            self.plt2.set_xlabel('Tau (ms)', fontsize=12)
            self.plt2.set_ylabel(corrText+' CH1', fontsize=12)
            self.plt2.xaxis.grid(True,'minor')
            self.plt2.xaxis.grid(True,'major')
            self.plt2.yaxis.grid(True,'minor')
            self.plt2.yaxis.grid(True,'major')
            
            self.plt3.plot(autotime,auto[:,0,1],object.color)
            self.figure3.subplots_adjust()
            self.plt3.set_xscale('log')
            self.plt3.set_xlim([0, np.max(autotime)])
            self.plt3.set_xlabel('Tau (ms)', fontsize=12)
            self.plt3.set_ylabel('Cross-correlation', fontsize=12)
            self.plt3.xaxis.grid(True,'minor')
            self.plt3.xaxis.grid(True,'major')
            self.plt3.yaxis.grid(True,'minor')
            self.plt3.yaxis.grid(True,'major')
            
            

        if object.type == 'mainObject':
            decayScale1 = object.decayScale1
            if object.numOfCH ==  2:
                decayScale2 = object.decayScale2
            if self.normPlot.isChecked() == True:
                photonDecayCh1 = object.photonDecayCh1Norm
                if object.numOfCH ==  2:
                    photonDecayCh2 = object.photonDecayCh2Norm
                axisText = 'No. of photons (Norm)'
            else:
                photonDecayCh1 = object.photonDecayCh1
                if object.numOfCH ==  2:
                    photonDecayCh2 = object.photonDecayCh2
                axisText = 'No. of photons '
            self.plt5.plot(decayScale1, photonDecayCh1,object.color)
            if object.numOfCH ==  2:
                self.plt5.plot(decayScale2, photonDecayCh2,object.color,linestyle='dashed')
            self.figure5.subplots_adjust(left=0.15,right=0.95, bottom=0.30,top=0.90)
            self.plt5.set_xlabel('Channels (1 ='+str(np.round(object.resolution,4))+' ns)', fontsize=12)
            self.plt5.set_ylabel(axisText, fontsize=8)
            self.plt5.xaxis.grid(True,'minor')
            self.plt5.xaxis.grid(True,'major')
            self.plt5.yaxis.grid(True,'minor')
            self.plt5.yaxis.grid(True,'major')
            self.canvas5.draw()
        # refresh canvas
        self.canvas1.draw()
        
        
    def saveDataQueue(self):
       
        
        for obj in self.par_obj.objectRef:
            self.saveFile(obj)
        for obj in self.par_obj.subObjectRef:
            self.saveFile(obj)
    def saveFile(self,obj):
        """Save files as .csv"""
        print obj.name,'saved'

        f = open(self.folderOutput.filepath+'/'+obj.name+'_CH1_Auto_Corr.csv', 'w')
        f.write('# Time (ns)\tCH1 Auto-Correlation\n')
        for x in range(0,obj.autotime.shape[0]):
            f.write(str(obj.autotime[x][0])+','+str(obj.autoNorm[x,0,0])+ '\n')
        if obj.numOfCH ==2:
            f = open(self.folderOutput.filepath+'/'+obj.name+'_CH2_Auto_Corr.csv', 'w')
            f.write('# Time (ns)\tCH2 Auto-Correlation\n')
            for x in range(0,obj.autotime.shape[0]):
                f.write(str(obj.autotime[x][0])+','+str(obj.autoNorm[x,1,1])+ '\n')
        
            f = open(self.folderOutput.filepath+'/'+obj.name+'_CH1_Cross_Corr.csv', 'w')
            f.write('# Time (ns)\tCH1 Cross-Correlation\n')
            for x in range(0,obj.autotime.shape[0]):
                f.write(str(obj.autotime[x][0])+','+str(obj.autoNorm[x,0,1])+ '\n')
            
            f = open(self.folderOutput.filepath+'/'+obj.name+'_CH2_Cross_Corr.csv', 'w')
            f.write('# Time (ns)\tCH2 Cross-Correlation\n')
            for x in range(0,obj.autotime.shape[0]):
                f.write(str(obj.autotime[x][0])+','+str(obj.autoNorm[x,1,0])+ '\n')
        print 'file Saved'



        

        
        

        
class checkBoxSp(QtGui.QCheckBox):
    def __init__(self):
        QtGui.QCheckBox.__init__(self)
        self.obj = []
        self.type = []
        self.name =[]
    def updateChecked(self):
            
                self.obj.plotOn = self.isChecked()
class checkBoxSp2(QtGui.QCheckBox):
    def __init__(self, win_obj, par_obj):
        QtGui.QCheckBox.__init__(self, parent)
        self.obj = []
        self.type = []
        self.name =[]
        self.stateChanged.connect(self.__changed)
    def __changed(self,state):
        
        if state == 2:
            if self.obj.carpetDisplay == 0:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 1:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 2:
                self.obj.CH01CrossFn()
        if state == 0:
            if self.obj.carpetDisplay == 3:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 4:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 5:
                self.obj.CH01CrossFn()
            


            #plotDataQueueFn()
class lineEditSp(QtGui.QLineEdit):
    def __init__(self, txt, win_obj):
        QtGui.QLineEdit.__init__(self, txt)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.obj = []
        self.type = []
        self.TGid =[]
        self.win_obj = win_obj
        
    def __handleEditingFinished(self):
        
        if(self.type == 'tgt0' ):
            self.win_obj.TGScrollBoxObj.x0[self.TGid] = float(self.text())
            self.win_obj.plt5.a.redraw()
            #plotDataQueueFn()
        if(self.type == 'tgt1' ):
            self.win_obj.TGScrollBoxObj.x1[self.TGid] = float(self.text())
            self.win_obj.plt5.a.redraw()
        if(self.type == 'name' ):
            self.obj.name = str(self.text())

           
            
      


            
class comboBoxSp(QtGui.QComboBox):
    def __init__(self,win_obj):
        QtGui.QComboBox.__init__(self,parent=None)
        self.activated[str].connect(self.__activated) 
        self.obj = []
        self.TGid =[]
        self.type = []
        self.win_obj = win_obj
    def __activated(self,selected):
        
        if self.type == 'AUG':
            if self.currentIndex() == 1:
                self.obj.aug = 'PIE'
                self.obj.PIE = self.currentIndex();
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
            if self.currentIndex() == 2:
                self.obj.aug = 'PIE'
                self.obj.PIE = self.currentIndex();
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
            if self.currentIndex() == 3:
                self.obj.aug = 'rmAP'
                self.obj.processData()
                self.win_obj.plotDataQueueFn()
        if self.type == 'PhotonCount':
            self.win_obj.plot_PhotonCount(self.currentIndex());

class pushButtonSp(QtGui.QPushButton):
    def __init__(self, win_obj, par_obj):
        QtGui.QPushButton.__init__(self)
        self.clicked.connect(self.__activated)
        self.par_obj = par_obj;
        self.win_obj = win_obj;
        #Which list is should look at.
        self.objList = []
        self.xmin = []
        self.xmax =[]
        self.TGid = []
    def __activated(self):
        if self.type =='photoCrr':
            self.par_obj.clickedS1 = self.xmin
            self.par_obj.clickedS2 = self.xmax
            self.win_obj.bleachInt.create_main_frame()
        if self.type =='remove':
            self.par_obj.TGnumOfRgn -= 1
            self.win_obj.TGScrollBoxObj.rect.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.x0.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.x1.pop(self.TGid)
            self.win_obj.TGScrollBoxObj.facecolor.pop(self.TGid)
            self.win_obj.modelTab.clear()
            self.win_obj.TGScrollBoxObj.generateList()
            self.win_obj.plotDataQueueFn()
        if self.type =='create':
            self.xmin =  self.win_obj.TGScrollBoxObj.x0[self.TGid]
            self.xmax =  self.win_obj.TGScrollBoxObj.x1[self.TGid]

            if (self.objList.currentIndex() == self.par_obj.objectRef.__len__()):
                for i in range(0,self.par_obj.objectRef.__len__()):
                    picoSub = subPicoObject(self.par_obj.objectRef[i],self.xmin,self.xmax,self.TGid,self.par_obj)
                    self.win_obj.updateCombo()
                    self.par_obj.subNum = self.par_obj.subNum+1
            else:
                picoSub = subPicoObject(self.par_obj.objectRef[self.objList.currentIndex()],self.xmin,self.xmax,self.TGid,self.par_obj)          
                self.win_obj.updateCombo()
                self.par_obj.subNum = self.par_obj.subNum+1
            self.win_obj.label.generateList()
            self.win_obj.plotDataQueueFn()
class pushButtonSp2(QtGui.QPushButton):
    """Save button"""
    def __init__(self, txt, win_obj, par_obj):
        QtGui.QPushButton.__init__(self,txt)
        self.clicked.connect(self.__clicked)
        self.win_obj = win_obj;
        self.par_obj = par_obj;
        self.corr_obj =[]
    def __clicked(self):
        self.win_obj.saveFile(self.corr_obj)





class scrollBox():
    def __init__(self, win_obj, par_obj):
        self.win_obj = win_obj
        self.par_obj = par_obj
        self.par_obj.numOfLoaded = 0
        self.par_obj.subNum =0
        self.generateList()
    def generateList(self):
        
        self.obj =[];
        self.objCheck =[];

        
        
        for i in range(0, self.par_obj.numOfLoaded):
            self.win_obj.modelTab2.setRowCount(i+1)
            #Represents each y
            self._l=QtGui.QHBoxLayout()
            self.obj.append(self._l)

            
            #HTML text
            a =baseList()
            a.listId = i
            a.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">Data '+str(i)+': </p></HTML>')
            

            self.win_obj.modelTab2.setCellWidget(i, 0, a)

            #Line edit for each entry in the file list
            lb = lineEditSp(self.win_obj, self.par_obj)
            
            lb.type ='name'
            lb.obj = self.par_obj.objectRef[i]
            lb.setText(self.par_obj.objectRef[i].name);
            self.win_obj.modelTab2.setCellWidget(i, 1, lb)

            
            

            cb = checkBoxSp()
            cb.setChecked(self.par_obj.objectRef[i].plotOn)
            cb.obj = self.par_obj.objectRef[i]
            cb.stateChanged.connect(cb.updateChecked)
            self.win_obj.modelTab2.setCellWidget(i, 2, cb)


            #cbx = comboBoxSp(self.win_obj)
            #Populates comboBox with datafiles to which to apply the time-gating.
            
            #cbx.addItem("norm", 0)
            #cbx.addItem("PIE-CH-0", 1)
            #cbx.addItem("PIE-CH-1", 2)
            #cbx.addItem("rm AfterPulse", 3)
            #cbx.obj = self.par_obj.objectRef[i]
            #cbx.type = 'AUG'
            #Adds an all option to the combobox.lfkk
            
            #cbx.TGid = i
            #self.win_obj.modelTab2.setCellWidget(i, 3, cbx)

            
            #Adds save button to the file.
            sb = pushButtonSp2('save file', self.win_obj, self.par_obj)
            sb.obj = self.par_obj.objectRef[i]
            self.win_obj.modelTab2.setCellWidget(i, 3, sb)

            b = baseList()
            b.setText('<HTML><p style="margin-top:0">pt3 file :'+str(self.par_obj.data[i])+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i, 4, b)
            
            
            self.win_obj.label.objCheck.append(cb)
            j = i+1
        for i in range(0,self.par_obj.subNum):
            self.win_obj.modelTab2.setRowCount(j+i+1)
            print i
            a =baseList()
            a.listId = i
            a.setText('<HTML><p style="color:'+str(self.par_obj.subObjectRef[i].color)+';margin-top:0">TG-'+str(self.par_obj.subObjectRef[i].TGid)+': Data:'+str(self.par_obj.subObjectRef[i].parentUnqID)+'-xmin:'+str(round(self.par_obj.subObjectRef[i].xmin,1))+'-xmax:'+str(round(self.par_obj.subObjectRef[i].xmax,1))+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i+j, 0, a)
            
            #Line edit for each entry in the file list
            lb =lineEditSp(self.win_obj, self.par_obj)
            lb.type ='name'
            lb.obj = self.par_obj.subObjectRef[i]
            lb.setText(self.par_obj.subObjectRef[i].name);
            self.win_obj.modelTab2.setCellWidget(i+j, 1, lb)
            #Main text for file menu.


            #Adds the plot checkBox:
            cb = checkBoxSp()
            cb.setChecked(self.par_obj.subObjectRef[i].plotOn)
            cb.obj = self.par_obj.subObjectRef[i]
            cb.stateChanged.connect(cb.updateChecked)
            self.win_obj.modelTab2.setCellWidget(i+j, 2, cb)

            
            #Adds save button to the file.
            sb = pushButtonSp2('save file', self.win_obj, self.par_obj)
            sb.obj = self.par_obj.subObjectRef[i]
            
            self.win_obj.modelTab2.setCellWidget(i+j, 3, sb)

            b = baseList()
            b.setText('<HTML><p style="margin-top:0">pt3 file :'+str(self.par_obj.subObjectRef[i].filepath)+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i+j, 4, b)

            #Adds the checkBox to a list.
            self.objCheck.append(cb)
        

class TGscrollBox():
    #Generates scroll box for time-gating data.
    def __init__(self, win_obj, par_obj):
        
        self.win_obj = win_obj
        self.par_obj = par_obj
        self.par_obj.TGnumOfRgn = 0
        self.x0 =[]
        self.x1 =[]
        self.facecolor =[]
        self.TGid = []
        self.rect =[]

    def generateList(self):
        print 'here'
        for i in range(0, self.par_obj.TGnumOfRgn):
            self.win_obj.modelTab.setRowCount(i+1)
            print 'loaded'
            
            txt2 = QtGui.QLabel()
            txt2.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">t0:</p></HTML>')
            self.win_obj.modelTab.setCellWidget(i, 0, txt2)


            lb1 = lineEditSp('', self.win_obj)
            lb1.setMaxLength(5)
            lb1.setFixedWidth(40)
            lb1.setText(str(self.win_obj.TGScrollBoxObj.x0[i]))
            lb1.type = 'tgt0'
            lb1.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 1, lb1)

            txt3 = QtGui.QLabel()
            txt3.setText('<HTML><p style="color:'+str(self.par_obj.colors[i % len(self.par_obj.colors)])+';margin-top:0">t1:</p></HTML>')
            self.win_obj.modelTab.setCellWidget(i, 2, txt3)
            
            

            lb2 = lineEditSp('', self.win_obj)
            lb2.setMaxLength(5)
            lb2.setFixedWidth(40)
            lb2.setText(str(self.win_obj.TGScrollBoxObj.x1[i]))
            lb2.type = 'tgt1'
            lb2.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 3, lb2)
            

            cbx = comboBoxSp(self.win_obj)
            #Populates comboBox with datafiles to which to apply the time-gating.
            for b in range(0,self.par_obj.numOfLoaded):
                cbx.addItem("Data: "+str(b), b)
            #Adds an all option to the combobox.lfkk
            cbx.addItem("All",b+1)
            cbx.TGid = i
            self.win_obj.modelTab.setCellWidget(i, 4, cbx)
            
            cbtn = pushButtonSp(self.win_obj, self.par_obj)
            cbtn.setText('Create')
            cbtn.type ='create'
            cbtn.TGid = i
            cbtn.xmin = self.win_obj.TGScrollBoxObj.x0[i]
            cbtn.xmax = self.win_obj.TGScrollBoxObj.x1[i]
            self.win_obj.modelTab.setCellWidget(i, 5, cbtn)
            #Make sure the btn knows which list it is connected to.
            cbtn.objList = cbx

            rmbtn = pushButtonSp(self.win_obj, self.par_obj)
            rmbtn.setText('X')
            rmbtn.TGid = i
            rmbtn.type = 'remove'
            self.win_obj.modelTab.setCellWidget(i, 6, rmbtn)

class ParameterClass():
    def __init__(self):
        
        #Where the data is stored.
        self.data = []
        self.objectRef =[]
        self.subObjectRef =[]
        self.colors = ['blue','green','red','cyan','magenta','yellow','black']