"""
programme semi-maitre du projet
permet la configuration de l'extraction de la phase; les config seront sauvegardées dans un fichier
et seront réutilisées à chaque appel de la fonction
:auteur: Maxence BARRE
:date: 19/02/2024
"""

# importation des modules nécessaires
import numpy as np
import pyqtgraph as pg
from PIL import Image

# ouverture du fichier à afficher
image = np.array(Image.open("image4.png"))

# create GUI
app = pg.mkQApp("ROI Examples")
w = pg.GraphicsLayoutWidget(show=True, size=(1000,800), border=True)
w.setWindowTitle('pyqtgraph example: ROI Examples')
w1 = w.addLayout(row=0, col=0)
v1a = w1.addViewBox(row=0, col=0, lockAspect=True)
img1a = pg.ImageItem(image)
v1a.addItem(img1a)

# création de la ROI
roi = pg.LineROI([0, 60], [20, 80], width=5, pen="r")
v1a.addItem(roi)


if __name__ == '__main__':
    pg.exec()