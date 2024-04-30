"""
programme permettant la configuration de l'extraction de la phase via interféromètre de Mach-Zender
:auteur: Maxence BARRE
:date: 26/02
:comment: ce programme a pour but d'etre utilisé en production; mais n'est pas censé être appelé
    par un programme maitre
TODO: régler le problème de la caméra zelux
TODO: enregistrer les paramètres de la ROI
TODO: utiliser la ROI pour accélérer les prises des photos de la zelux
TODO: utiliser les docker (cf prg de rafael)
TODO: configurer les boutons de lancement d'enregistrement, d'arret et de sauvegarde
TODO: affichage d'un label indiquant le delay associé
TODO: commenter les fonctions!!!!
TODO: proposer une aide à la "verticalisation" de la ROI
TODO: pouvoir changer le temps d'ouverture plus facilement
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
import os
import pickle
from histogramme_et_gestion_delay import * 
# from connexion_tcpip_avec_pymodaq import *
from threading import Thread    # no worry, only used when setting up the connection to pymodaq
import socket              
from collections import deque 
print("[INFO] Modules importés avec succès")


# création de la fen^tre graphique principale a
class MainWindow(qt.QMainWindow):
    """
    fenetre de configuration principale
    """
    def __init__(self):
        """
        initialisation de la classe
        """
        super().__init__()
        print("im here")
        self.take_photo_cam = True
        self.connection_set_up = False
        self.what_to_use_for_picture = "camera"         # choisir entre camera et video
        self.phase_vector = deque(maxlen=100)           # changer le paramètre maxlen pour augmenter le nombre de données affichées
        self.taille_des_blocs = 1000 # en images
        self.image_from_hdf5_to_use = list()
        self.histo_phase_sent_to_pymodaq = monHisto(borne_inf=-8, borne_sup=8, nb_bin=40, largeur_bin=None)

        # Initialize webcam
        print("[INFO] Recherche des caméras disponibles")
        ad_serial = Thorlabs.list_cameras_tlcam()  # affiche normalement la liste des caméras connectées
        if len(ad_serial) != 0:
            self.cam_zelux = True
            print(f"[INFO] Adresses trouvées: {ad_serial}")
            self.cam = Thorlabs.ThorlabsTLCamera(serial=ad_serial[0])

            # reset the ROI
            hlim, vlim = self.cam.get_roi_limits()
            self.cam.set_roi(0, hlim.max, 0, vlim.max)

            self.cam.set_exposure(0.5E-3)
            self.cam.start_acquisition()
            print(f"[INFO] Caméra {ad_serial[0]} connectée")
        else:
            self.cam_zelux = False
            print("[WARNING] Caméra Zelux non trouvée, Ouverture de la caméra par défaut")
            self.cam = cv2.VideoCapture(0)

        if use_webcam:
            self.cap = cv2.VideoCapture(0)

        self.setupUI()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
         

    def setupUI(self):
        """
        setup de la fenetre graphique
        """
        self.setWindowTitle("Webcam Viewer")
        pg.setConfigOptions(antialias=True)
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
        get_roi = qt.QAction("Utiliser ROI sauvegardée", self)
        action.addAction(get_roi)
        get_roi.triggered.connect(self.get_roi_from_file)
        send_roi_action = qt.QAction("Send ROI to cam", self)
        action.addAction(send_roi_action)
        send_roi_action.triggered.connect(self.send_ROI_to_cam)

        sauvegarde = menuBar.addMenu('Sauvegarde')
        sauvegarde.addAction('Sauvegarder Data')
        save_roi = qt.QAction("Sauvegarder ROI", self)
        sauvegarde.addAction(save_roi)
        save_roi.triggered.connect(self.save_roi)

        # config_roi = menuBar.addMenu("ROI")
        # auto = qt.QAction("AutoConfig", self)
        # config_roi.addAction(auto)
        # auto.triggered.connect(self.auto_roi)

        # Create a layout for the central widget
        grid = qt.QGridLayout()
        self.centralWidget.setLayout(grid)

        # Create a graphics view widget to display the image
        self.plotView = pg.PlotWidget()             # Warning: le plotwidget est obligé pour pouvoir utiliser une roi par la suite
        self.plotView.getAxis("bottom").setStyle(showValues=True)
        self.plotView.getAxis("left").setStyle(showValues=True)
        self.graphicsView = pg.ImageItem()
        self.plotView.addItem(self.graphicsView)
        self.plotView.setAspectLocked()
        grid.addWidget(self.plotView, 0, 0)

        # création de la ROI
        ex_image = self.take_photo_with_cam()
        self.roi = pg.RectROI(pos = [(50+12.5)/100 * ex_image.shape[0], (50-37.5)/100 * ex_image.shape[1]], size = [75/100 * ex_image.shape[1], 25/100 * ex_image.shape[0]] ,angle = 90, pen = (0, 9))
        self.roi.addRotateHandle([1, 0], [0.5, 0.5])
        self.plotView.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update_roi)

        # test passager:
        x_to_plot = (0, ex_image.shape[0], ex_image.shape[0], 0)
        y_to_plot = (0, 0, ex_image.shape[1],ex_image.shape[1])
        self.plotView.plot(x_to_plot, y_to_plot, color="green")

        # GUI pour l'affichage de la ROI
        self.graphicsView2 = pg.ImageView()
        self.graphicsView2.ui.roiBtn.hide()
        self.graphicsView2.ui.menuBtn.hide()
        self.graphicsView2.ui.histogram.hide()
        grid.addWidget(self.graphicsView2, 1, 0)

        
        # plotting de la "somme"/moyenne de l'image
        self.plotView2 = pg.PlotWidget()
        self.plotView2.setTitle("Somme sur la ROI")
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

        # création des boutons en bas à droite de la page
        groupBox = qt.QGroupBox("Boutons Utiles")
        grid_for_box = qt.QVBoxLayout()
        b1 = qt.QPushButton("Connexion à Pymodaq")
        grid_for_box.addWidget(b1)
        b1.clicked.connect(self.connect_to_pymodaq)
        self.b1 = b1
        
        b2 = qt.QPushButton("Lancement acquisition")
        grid_for_box.addWidget(b2)
        b2.clicked.connect(self.launch_acquisition)
        self.b2 = b2

        b3 = qt.QPushButton("Sauvegarder les données")
        grid_for_box.addWidget(b3)

        groupBox.setLayout(grid_for_box)
        grid.addWidget(groupBox, 2, 1)

        # a enlever!!!!!
        self.plotView.plot((0, 50), (0, 100), color="red") 
        
    def config_video(self):
        print("[INFO] Sélection d'une vidéo ou d'un fichier h5 comme outil de travail")
        self.what_to_use_for_picture = "video"
        self.take_photo_cam = False
        dlg = qt.QFileDialog()
        dlg.setFileMode(qt.QFileDialog.AnyFile)
        self.index_of_chunk = -1

            
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) > 1:
                print("[WARNING] Un seul fichier maximum")
                self.what_to_use_for_picture = "camera"
            else:
                # le fait d'utiliser with ... as ... nous oblige à extraire TOUTES les données d'un coup.
                # on décide donc de ne pas l'utiliser afin de ne pas saturer la mémoire
                file = h5py.File(filenames[0], 'r')
                self.huge_data_h5py = file['RawData/Scan000/Detector001/Data2D/CH00/EnlData00']
                self.index_image_in_video = -1      # oui, oui c'est bien -1
                # with h5py.File(filenames[0], 'r') as file:
                #     self.images_from_video = np.array(file['RawData/Scan000/Detector001/Data2D/CH00/EnlData00'])
                #     print("[INFO] Images extraites avec succès")
                #     print("taille", self.images_from_video.shape, type(self.images_from_video))
                ex_image = self.huge_data_h5py[0]
                self.roi.setPos(pos = [(50+12.5)/100 * ex_image.shape[0], (50-37.5)/100 * ex_image.shape[1]])
                self.roi.setSize(size = [75/100 * ex_image.shape[1], 25/100 * ex_image.shape[0]])
        self.take_photo_cam = True
        
    def take_photo_with_cam(self):
        if self.cam_zelux:
            frame = self.cam.read_newest_image()
            # frame = np.rot90(self.cam.snap())
        else:
            ret, frame = self.cam.read()
            # print('r', ret)
            frame = np.rot90(np.rot90(np.rot90(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))))
        return frame
    
    def update_frame(self):
        # print("begin update")
        if self.take_photo_cam:
            if self.what_to_use_for_picture == "camera":
                self.current_frame = self.take_photo_with_cam()
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

        # print(self.current_frame.shape) 

        


    def update_roi(self):
        # print("updating roi")
        image_roi = self.roi.getArrayRegion(self.current_frame, self.graphicsView)
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
        self.histo_phase_sent_to_pymodaq.append(phase)
        if len(self.phase_vector) == 0:
            self.phase_vector.append(phase)
        else:
            phase = np.unwrap([self.phase_vector[-1], phase])[-1]
            self.phase_vector.append(phase)  # l'opération unwrap permet d'éviter les "sauts de phases entre +pi et -pi"
        if self.connection_set_up:
            # print("[INFO] J'essaye d'envoyer qch:", phase, type(phase))
            to_send = str(phase) + ";"
            self.client.send(str(to_send).encode())
        
        if self.histo_phase_sent_to_pymodaq.shape() % 10 == 0:
            print("asking for renew histo")
            self.w2.update_histo(histo=self.histo_phase_sent_to_pymodaq)
        

        self.plotView4.clear()
        self.plotView4.plot(self.phase_vector)

    

    def video_get_next_frame(self):
        """
        :comment: à l'init: self.index_image_in_video = - 1
                            self.infex_of_chunk = -1
        """
        self.index_image_in_video = (self.index_image_in_video + 1) % self.taille_des_blocs


        # création des chunks à load en mémoire (on "découpe" les fichiers que l'on extrait)
        if self.index_image_in_video == 0 and self.index_of_chunk*self.taille_des_blocs < len(self.huge_data_h5py):  # on doit créer un new chunk
            self.index_of_chunk += 1
            self.image_from_hdf5_to_use = self.huge_data_h5py[self.index_of_chunk * self.taille_des_blocs : min(len(self.huge_data_h5py), (self.index_of_chunk + 1)*self.taille_des_blocs)]


        # print(self.index_image_in_video)
        return self.image_from_hdf5_to_use[self.index_image_in_video]


    def save_roi(self):
        print("[INFO] Sauvegarde de la ROI dans le fichier: ")
        state = self.roi.saveState()
        path_for_save = os.getcwd() + r'\ROI_do_not_erase'
        print(path_for_save)
        with open(path_for_save, 'wb') as f_save:
            pickle.dump(state, f_save)
        print("[INFO] ROI sauvegardée!")

    def get_roi_from_file(self):
        print("[INFO] Extraction de la ROI dans le fichier: ")
        path_for_roi = os.getcwd() + r'\ROI_do_not_erase'
        if os.path.isfile(path_for_roi):
            with open(path_for_roi, 'rb') as f_roi:
                state = pickle.load(f_roi)
            print(state)
            self.roi.setState(state)
            print("[INFO] ROI mise à jour!")
        else:
            print("[ERROR] Le fichier demandé n'existe pas. Il faut refaire la ROI à la main.")


    def launch_acquisition(self):
        if self.b2.text() == "Lancement acquisition":
            self.timer.start(30)
            self.b2.setText("Arrêt acquisition")
            self.w2 = FenetreHisto(self.histo_phase_sent_to_pymodaq)
            self.w2.show()
        else:
            self.timer.stop()
            self.b2.setText("Lancement acquisition")    

    def connect_to_pymodaq(self):
        print("[INFO] Ouverture du serveur pour connexion du client Pymodaq")
        # self.tcpclient = TCPClient_all_in_one("localhost", 6341, "GRABBER")
        # t = Thread(target=self.tcpclient.init_connection)
        # t.start()
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind(('localhost', 15555))
        serveur.listen(5)
        print("[INFO] Serveur ouvert, attente de la connexion")
        client, address = serveur.accept()
        self.client = client
        print("{} connected".format( address ))
        self.connection_set_up = True
        print("[INFO] Fonction de connexion éxécutée")
        print("[WARNING] Attention, cela ne signifie pas que le programme est bien connecté en client au serveur Pymodaq")

    def send_ROI_to_cam(self):
        # info_on_roi = self.roi.getState()
        pos_x, pos_y = self.roi.pos()
        angle = self.roi.angle()
        size_x, size_y = self.roi.size()

        # Calculate the corner coordinates
        corner1 = [pos_x, pos_y]
        corner2 = [pos_x + size_x * np.cos(np.radians(angle)), pos_y + size_x * np.sin(np.radians(angle))]
        corner3 = [corner2[0] + size_y * np.cos(np.radians(angle + 90)), corner2[1] + size_y * np.sin(np.radians(angle + 90))]
        corner4 = [corner1[0] + size_y * np.cos(np.radians(angle + 90)), corner1[1] + size_y * np.sin(np.radians(angle + 90))]

        x_abs = [corner1[0], corner2[0],corner3[0], corner4[0]]
        y_abs = [corner1[1], corner2[1],corner3[1], corner4[1]]
        self.plotView.plot(x_abs, y_abs)  # to check if the corners calculated are the right corners
        
        x_bound_roi_to_cam = (min(x_abs), max(x_abs))
        y_bound_roi_to_cam = (min(y_abs), max(y_abs))
        # self.plotView.plot(x_bound_roi_to_cam, y_bound_roi_to_cam)

        print("[INFO] Sending ROI info to cam")
        self.cam.set_roi(vstart=min(x_abs), vend=max(x_abs), hstart=min(y_abs), hend=max(y_abs))  # bon ici c'est un peu bizarre, il faut echanger l'horizontal avec le vertical pour que ca fonctionne. pk jsp trop! tjrs est il que ca fonctionne!
        
        # il faut mtnt remettre la roi au bon endroit
        print(size_x, size_y)
        # self.roi.setAngle(90)
        self.roi.setPos((np.sin(np.radians(angle)) * size_y, 0))

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
