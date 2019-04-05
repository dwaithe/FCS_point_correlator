from fitting_gui import Form
from correlation_gui import *
import sys


   
if __name__ == '__main__':
    """ Initialises the gui. """
    app = QtWidgets.QApplication(sys.argv)
    par_obj = ParameterClass()
    win_tab = QtWidgets.QTabWidget()
    fit_obj = Form('point')
    #Ensures the the fit tab can refresh the display, for status updates.
    fit_obj.app = app


    corr_tab = Window(par_obj, fit_obj)
    win_tab.addTab(corr_tab, "Load TCSPC")
    win_tab.addTab(fit_obj, "Fit Function")
    win_tab.resize(1200,1000)
    win_tab.show()
    sys.exit(app.exec_())