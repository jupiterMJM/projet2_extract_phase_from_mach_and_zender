from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import PyQt5.QtWidgets as qt
import pylablib as pll
pll.par["devices/dlls/smaract_mcs2"] = r"C:\SmarAct\MCS\Programs"       # modifier ce chemin pour diriger vers les .dll du MCS
from pylablib.devices import SmarAct

lambda_OEM = 450        # en nm !!!! # à vérifier
look_and_move_stage = False


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
        self.histogramme_view.plot(x, histo_vide.distribution_objectif(x))
        grid.addWidget(self.histogramme_view)

        self.cursor = pg.InfiniteLine(pos=0,angle=90,movable=True,pen="g")           # on utilise ce pic pour lire la phase
        self.histogramme_view.addItem(self.cursor)

        if look_and_move_stage:
            self.maStage = StageGestionDelay()

    def update_histo(self, histo):
        print("hey mates")
        y, x = histo.items()
        print(y)
        self.histo.setOpts(height=y)
        next_target = histo.get_least_chosen()
        self.cursor.setValue(next_target)
        if look_and_move_stage:
            self.maStage.goto_phase(next_target)



class monHisto:
    def __init__(self, borne_inf, borne_sup, nb_bin=None, largeur_bin = None):
        """
        n'admet que des bins de taille égale (modulo le dernier)
        ne spécifier que nb_bin OU largeur_bin, pas les 2
        """
        assert not (nb_bin and largeur_bin)
        if nb_bin:
            self.bins = np.linspace(borne_inf, borne_sup, nb_bin)
            self.nb_bin = nb_bin
        else:
            self.bins = np.arange(borne_inf, borne_sup, largeur_bin)
            self.nb_bin = self.bins.shape[0]
        self.occurence = np.zeros(self.bins.shape)
        self.last_append = 0

        # # pour une distribution uniforme
        # self.distribution_objectif = lambda x : 1/self.nb_bin * np.ones(self.bins.shape)

        # pour une distribution gaussienne quelconque
        sigma = 3
        mu = 0
        self.distribution_objectif = lambda x: 1/(np.sqrt(2*np.pi) * sigma) * np.exp(-1/2 * ((x-mu)/sigma)**2)
    
    def append(self, terme):
        assert terme >= self.bins[0] and terme <= self.bins[-1]
        self.last_append = terme
        for i in range(1, self.bins.shape[0]):
            if terme < self.bins[i]:
                self.occurence[i-1] += 1
                break
        self.get_least_chosen()
        return self.occurence, self.bins
    
    def shape(self):
        return sum(self.occurence)

    def items(self):
        return self.occurence/sum(self.occurence), self.bins
    
    def get_least_chosen(self):
        """
        retourne le bin qui est le plus loin de la distribution choisie.
        fonctions qui fonctionnent bien: 
        -> loi uniforme: 1/self.nb_bin * np.ones(self.bins.shape)
        -> loi gaussienne: pour mu, sigma fixé, lambda x: 1/(np.sqrt(2*np.pi) * sigma) * np.exp(-1/2 * ((x-mu)/sigma)**2)
        """
        densite = self.occurence / sum(self.occurence)
        densite_objectif = self.distribution_objectif(self.bins)
        diff_densite = densite - densite_objectif
        next_target = self.bins[diff_densite == min(diff_densite)][0]       # peut etre choisir un random ici.... (à la place du [0])
        return next_target


class StageGestionDelay:
    """
    classe permettant de gérer la stage afin de modifier le delay
    ATTENTION: pour que le programme fonctionne la stage doit OBLIGATOIREMENT etre connecté au MCS2; et non au MCS3C
    """

    def __init__(self):
        """
        fonction d'initialisation
        """
        # initialisation de la stage 
        devices = SmarAct.list_msc2_devices()
        if len(devices) == 0:
            raise Exception("No device detected")
        self.stage = SmarAct.MCS2(devices[0])
        print(f"[INFO] Connected to the first stage detected: {devices[0]}")

    def goto_phase(self, phase_to_go_to, current_phase):
        """
        fonction permettant d'aller à une phase précise et donnée par l'opérateur
        conversion pour passer d'une longeur/delay à une phase
        A vérifier 2pi radians <=> lambda/2 de longueur en plus
        """
        where_stage_now = self.stage.get_position()
        diff_phase = phase_to_go_to - current_phase
        lg_to_move = diff_phase * lambda_OEM / (4*np.pi)
        self.stage.move_by(lg_to_move)



if __name__ == "__main__":
    import sys
    import time as t
    app = qt.QApplication(sys.argv)
    mainWindow = FenetreHisto()
    mainWindow.show()
    mainWindow.update_histo([1, 2, 3])
    sys.exit(app.exec_())
    

        