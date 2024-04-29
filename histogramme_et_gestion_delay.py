from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import PyQt5.QtWidgets as qt

class FenetreHisto(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Histogramme de la répartition des données")
        pg.setConfigOptions(antialias=True)
        # Create a central widget
        self.centralWidget = qt.QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create a layout for the central widget
        grid = qt.QGridLayout()
        self.centralWidget.setLayout(grid)


        ## make interesting distribution of values
        vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])

        ## compute standard histogram
        y,x = np.histogram(vals, bins=np.linspace(-3, 8, 40))
        self.histogramme_view = pg.PlotWidget()
        bgi = pg.BarGraphItem(x0=x[:-1], x1=x[1:], height=y, pen='w', brush=(0,0,255,150))
        self.histogramme_view.addItem(bgi)
        grid.addWidget(self.histogramme_view)


if __name__ == "__main__":
    import sys
    app = qt.QApplication(sys.argv)
    mainWindow = FenetreHisto()
    mainWindow.show()
    sys.exit(app.exec_())

        