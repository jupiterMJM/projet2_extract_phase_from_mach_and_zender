"""
programme permettant la configuration de l'extraction de la phase via interféromètre de Mach-Zender
:auteur: Maxence BARRE
:date: 26/02
:comment: ce programme a pour but d'etre utilisé en production; mais n'est pas censé être appelé
    par un programme maitre
TODO: mieux gérer les fichiers hdf5 - en particulier ne pas tout charger en mémoire comme un bourrin
TODO: régler le problème de la caméra zelux
TODO: enregistrer les paramètres de la ROI
TODO: utiliser la ROI pour accélérer les prises des photos de la zelux
TODO: placer un axe de lecture de la phase - et ajouter le graphe de la phase
TODO: utiliser les docker (cf prg de rafael)
TODO: configurer les boutons de lancement d'enregistrement, d'arret et de sauvegarde
TODO: affichage d'un label indiquant la fréquence choisie par le cursor (et le domaine de couleur correspondant, approche un peu théorique à faire)
TODO: commenter les fonctions!!!!
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
import h5py
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
        self.what_to_use_for_picture = "camera"         # choisir entre camera et video
        self.phase_vector = []
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

        # création de la ROI
        self.roi = pg.LineROI([0, 60], [20, 80], width=5, pen="r")
        self.plotView.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update_roi)

        # GUI pour l'affichage de la ROI
        self.graphicsView2 = pg.ImageView()
        self.graphicsView2.ui.roiBtn.hide()
        self.graphicsView2.ui.menuBtn.hide()
        self.graphicsView2.ui.histogram.hide()
        grid.addWidget(self.graphicsView2, 1, 0)

        
        # plotting de la "somme"/moyenne de l'image
        self.plotView2 = pg.PlotWidget()
        grid.addWidget(self.plotView2, 2, 0)

        # plotting du spectre de la fft
        self.plotView3 = pg.PlotWidget()
        self.plotFourier = pg.PlotDataItem()
        self.cursor = pg.InfiniteLine(pos=0,angle=90,movable=True,pen="g")           # on utilise ce pic pour lire la phase
        self.plotView3.addItem(self.cursor)
        self.plotView3.addItem(self.plotFourier)
        grid.addWidget(self.plotView3, 0, 1)

        # plotting du graphe de la phase
        self.plotView4 = pg.PlotWidget()
        grid.addWidget(self.plotView4, 1, 1)

    def config_video(self):
        print("[INFO] Sélection d'une vidéo ou d'un fichier h5 comme outil de travail")
        self.what_to_use_for_picture = "video"
        self.take_photo_cam = False
        dlg = qt.QFileDialog()
        dlg.setFileMode(qt.QFileDialog.AnyFile)

            
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) > 1:
                print("[WARNING] Un seul fichier maximum")
                self.what_to_use_for_picture = "camera"
            else:
                with h5py.File(filenames[0], 'r') as file:
                    self.images_from_video = np.array(file['RawData/Scan000/Detector001/Data2D/CH00/EnlData00'])
                    self.index_image_in_video = -1      # oui, oui c'est bien -1
                    print("[INFO] Images extraites avec succès")
                    print("taille", self.images_from_video.shape, type(self.images_from_video))
        
        self.take_photo_cam = True
        
    def update_frame(self):
        # print("begin update")
        if self.take_photo_cam:
            if self.what_to_use_for_picture == "camera":
                if self.cam_zelux:
                    self.current_frame = np.rot90(self.cam.snap())
                else:
                    ret, self.current_frame = self.cam.read()
                    # print('r', ret)
                    self.current_frame = np.rot90(np.rot90(np.rot90(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))))
            elif self.what_to_use_for_picture == "video":
                self.current_frame = self.video_get_next_frame()
            else:
                print("[ERROR] l'argument self.what_to_use_for_picture n'est pas reconnu pas le programme")
            self.graphicsView.setImage(self.current_frame)
            self.update_roi()
        # print("end update")

        if use_webcam:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR, PyQtGraph uses RGB
                self.graphicsView2.setImage(np.rot90(frame))


    def update_roi(self):
        # print("updating roi")
        image_roi = np.rot90(self.roi.getArrayRegion(self.current_frame, self.graphicsView))
        self.graphicsView2.setImage(image_roi)
        self.graphicsView2.autoRange()
        self.update_graph_sum(image_roi)

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

    def update_graph_spectre_fft(self, image_sommee):
        # on fait d'abord la fft
        freq = np.fft.fftfreq(image_sommee.shape[0])
        sp = np.fft.fft(image_sommee)[freq >= 0]
        freq = freq[freq >= 0]
        
        # affichage du module de la fft
        self.plotFourier.clear()
        self.plotFourier.setData(y=np.abs(sp))

        # affichage de la phase de la fft
        pic_position = int(self.cursor.value())
        # print(pic_position)
        phase = np.angle(sp[pic_position])
        if len(self.phase_vector) == 0:
            self.phase_vector.append(phase)
        else:
            self.phase_vector.append(np.unwrap([self.phase_vector[-1], phase])[-1])  # l'opération unwrap permet d'éviter les "sauts de phases entre +pi et -pi"
        self.plotView4.clear()
        self.plotView4.plot(self.phase_vector)

    

    def video_get_next_frame(self):
        self.index_image_in_video += 1
        return self.images_from_video[self.index_image_in_video]


    



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
