from fitting_gui import Form
from correlation_gui import *
   
if __name__ == '__main__':
    """ Initialises the gui. """
    app = QtGui.QApplication(sys.argv)
    par_obj = ParameterClass()
    win_tab = QtGui.QTabWidget()
    fit_obj = Form()
    corr_tab = Window(par_obj, fit_obj)
    win_tab.addTab(corr_tab, "Load TCSPC")
    win_tab.addTab(fit_obj, "Fit Function")
    win_tab.resize(1200,800)
    win_tab.show()
    sys.exit(app.exec_())