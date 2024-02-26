"""
programme permettant la configuration de l'extraction de la phase via interféromètre de Mach-Zender
:auteur: Maxence BARRE
:date: 26/02
:comment: ce programme a pour but d'etre utilisé en production; mais n'est pas censé être appelé
    par un programme maitre
"""


# une petite variable de test:
use_webcam = False

# importation des modules
print("[INFO] Importation des modules")
import sys
from pylablib.devices import Thorlabs
import PyQt5.QtWidgets as qt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import cv2
print("[INFO] Modules importés avec succès")


# création de la fen^tre graphique principale
class MainWindow(qt.QMainWindow):
    """
    fenetre de configuration principale
    """
    def __init__(self):
        """
        initialisation de la classe
        """
        super().__init__()

        self.setupUI()

        # Initialize webcam
        print("[INFO] Recherche des caméras disponibles")
        ad_serial = Thorlabs.list_cameras_tlcam()  # affiche normalement la liste des caméras connectées
        print(f"[INFO] Adresses trouvées: {ad_serial}")
        self.cam = Thorlabs.ThorlabsTLCamera(serial=ad_serial[0])
        self.cam.set_exposure(10E-3)
        print(f"[INFO] Caméra {ad_serial[0]} connectée")

        if use_webcam:
            self.cap = cv2.VideoCapture(0)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) 

    def setupUI(self):
        """
        setup de la fenetre graphique
        """
        self.setWindowTitle("Webcam Viewer")

        # Create a central widget
        self.centralWidget = qt.QWidget()
        self.setCentralWidget(self.centralWidget)

        # Create a layout for the central widget
        grid = qt.QGridLayout()
        self.centralWidget.setLayout(grid)

        # Create a graphics view widget to display the image
        self.plotView = pg.PlotWidget()
        self.graphicsView = pg.ImageItem()
        self.plotView.addItem(self.graphicsView)
        grid.addWidget(self.plotView, 0, 0)

        # Create a graphics view widget to display the image
        self.graphicsView2 = pg.ImageView()
        self.graphicsView2.ui.roiBtn.hide()
        self.graphicsView2.ui.menuBtn.hide()
        self.graphicsView2.ui.histogram.hide()
        grid.addWidget(self.graphicsView2, 0, 1)

        
        # création de la ROI
        self.roi = pg.LineROI([0, 60], [20, 80], width=5, pen="r")
        self.plotView.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update_roi)


    
    def update_roi(self):
        print("updating roi")
        image_roi = self.roi.getArrayRegion(self.current_frame, self.graphicsView)
        self.graphicsView2.setImage(image_roi)
        self.graphicsView2.autoRange()


    def update_frame(self):
        print("begin update")
        self.current_frame = self.cam.snap()
        self.graphicsView.setImage(np.rot90(self.current_frame))
        print("end update")

        if use_webcam:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR, PyQtGraph uses RGB
                self.graphicsView2.setImage(np.rot90(frame))



    def closeEvent(self, event):
        self.cam.close()
        if use_webcam:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
