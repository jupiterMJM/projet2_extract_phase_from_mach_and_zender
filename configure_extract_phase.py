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
        self.take_photo_cam = True
        # Initialize webcam
        print("[INFO] Recherche des caméras disponibles")
        ad_serial = Thorlabs.list_cameras_tlcam()  # affiche normalement la liste des caméras connectées
        if len(ad_serial) != 0:
            self.cam_zelux = True
            print(f"[INFO] Adresses trouvées: {ad_serial}")
            self.cam = Thorlabs.ThorlabsTLCamera(serial=ad_serial[0])
            self.cam.set_exposure(10E-3)
            print(f"[INFO] Caméra {ad_serial[0]} connectée")
        else:
            self.cam_zelux = False
            print("[WARNING] Caméra Zelux non trouvée, Ouverture de la caméra par défaut")
            self.cam = cv2.VideoCapture(0)

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

        # create menuBar for selection
        menuBar = self.menuBar()
        choix_source = menuBar.addMenu('Source')
        video = qt.QAction("Vidéo", self)
        choix_source.addAction(video)
        video.triggered.connect(self.config_video)
        choix_source.addAction("Caméra")
        action = menuBar.addMenu('Action')
        action.addAction('Lancer Traitement')
        action.addAction('Sauvegarder Data')
        


        # Create a layout for the central widget
        grid = qt.QGridLayout()
        self.centralWidget.setLayout(grid)

        # Create a graphics view widget to display the image
        self.plotView = pg.PlotWidget()
        self.graphicsView = pg.ImageItem()
        self.plotView.addItem(self.graphicsView)
        self.plotView.setAspectLocked()
        grid.addWidget(self.plotView, 0, 0)

        # Create a graphics view widget to display the image
        self.graphicsView2 = pg.ImageView()
        self.graphicsView2.ui.roiBtn.hide()
        self.graphicsView2.ui.menuBtn.hide()
        self.graphicsView2.ui.histogram.hide()
        grid.addWidget(self.graphicsView2, 1, 0)

        
        # création de la ROI
        self.roi = pg.LineROI([0, 60], [20, 80], width=5, pen="r")
        self.plotView.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update_roi)

        # plotting de la "somme"/moyenne de l'image
        self.plotView2 = pg.PlotWidget()
        grid.addWidget(self.plotView2, 0, 1)

        # plotting du spectre de la fft
        self.plotView3 = pg.PlotWidget()
        grid.addWidget(self.plotView3, 1, 1)

    def config_video(self):
        print("[INFO] Sélection d'une vidéo ou d'un fichier h5 comme outil de travail")
        self.take_photo_cam = False
        dlg = qt.QFileDialog()
        dlg.setFileMode(qt.QFileDialog.AnyFile)

            
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) > 1:
                print("[WARNING] Un seul fichier maximum")
                filenames = self.config_video()
        self.take_photo_cam = True
        return filenames

    def update_graph_spectre_fft(self, image_sommee):
        # on fait d'abord la fft
        freq = np.fft.fftfreq(image_sommee.shape[0])
        sp = np.fft.fft(image_sommee)[freq >= 0]
        freq = freq[freq >= 0]
        
        # print("sp", sp.shape, "freq", freq.shape)
        self.plotView3.clear()
        self.plotView3.plot(freq, np.abs(sp))


    def update_graph_sum(self, image_roi):
        # print(image_roi.shape)
        if len(image_roi.shape) == 3: # image en couleur
            sommation = np.sum(image_roi[:, :, 0], axis=1)
        else:
            sommation = np.sum(image_roi, axis=1)
        # print(sommation.shape)
        self.plotView2.clear()
        self.plotView2.plot(sommation)
        self.update_graph_spectre_fft(sommation)
    
    def update_roi(self):
        # print("updating roi")
        image_roi = np.rot90(self.roi.getArrayRegion(self.current_frame, self.graphicsView))
        self.graphicsView2.setImage(image_roi)
        self.graphicsView2.autoRange()
        self.update_graph_sum(image_roi)


    def update_frame(self):
        # print("begin update")
        if self.take_photo_cam:
            if self.cam_zelux:
                self.current_frame = np.rot90(self.cam.snap())
            else:
                ret, self.current_frame = self.cam.read()
                # print('r', ret)
                self.current_frame = np.rot90(np.rot90(np.rot90(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))))
            self.graphicsView.setImage(self.current_frame)
            self.update_roi()
        # print("end update")

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
