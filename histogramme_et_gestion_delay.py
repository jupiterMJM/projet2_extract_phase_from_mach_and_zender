from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import PyQt5.QtWidgets as qt

class FenetreHisto(qt.QMainWindow):
    def __init__(self, histo_vide):
        super().__init__()
        self.setupUI(histo_vide)

    def setupUI(self, histo_vide):
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
        self.histogramme_view = pg.PlotWidget()
        y, x = histo_vide.items()
        self.histo = pg.BarGraphItem(x=x, width=1/2, height=y, pen='w', brush=(0,0,255,150))
        self.histogramme_view.addItem(self.histo)
        grid.addWidget(self.histogramme_view)

    def update_histo(self, histo):
        print("hey mates")
        y, x = histo.items()
        print(y)
        self.histo.setOpts(height=y)


class monHisto:
    def __init__(self, borne_inf, borne_sup, nb_bin=None, largeur_bin = None):
        """
        n'admet que des bins de taille égale (modulo le dernier)
        ne spécifier que nb_bin OU largeur_bin, pas les 2
        """
        assert not (nb_bin and largeur_bin)
        if nb_bin:
            self.bins = np.linspace(borne_inf, borne_sup, nb_bin)
        else:
            self.bins = np.arange(borne_inf, borne_sup, largeur_bin)
        self.occurence = np.zeros(self.bins.shape)
    
    def append(self, terme):
        assert terme >= self.bins[0] and terme <= self.bins[-1]
        for i in range(1, self.bins.shape[0]):
            if terme < self.bins[i]:
                self.occurence[i-1] += 1
                break
        return self.occurence, self.bins
    
    def shape(self):
        return sum(self.occurence)

    def items(self):
        return self.occurence, self.bins

if __name__ == "__main__":
    import sys
    import time as t
    app = qt.QApplication(sys.argv)
    mainWindow = FenetreHisto()
    mainWindow.show()
    mainWindow.update_histo([1, 2, 3])
    sys.exit(app.exec_())
    

        