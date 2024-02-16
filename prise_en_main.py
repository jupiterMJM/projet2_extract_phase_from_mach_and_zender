"""
fichier de prise en main de la caméra thorlabs
:auteur: Maxence BARRE
:date: 15/02/2024
:comment: ce programme n'a pas vocation à être insérer dans un programme parent (ni même être appelé)
"""

# importation des modules
print("[INFO] Importation des modules")
from pylablib.devices import Thorlabs
import numpy as np
print("[INFO] Modules importés avec succès")

# import pylablib as pll
# pll.par["devices/dlls/thorlabs_tlcam"] = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Thorlabs\Scientific Imaging\ThorCam"


# recherche des caméras accessibles
print("[INFO] Recherche des caméras disponibles")
print(Thorlabs.list_cameras_tlcam())  # affiche normalement la liste des caméras connectées


# # un essai d'ouverture de caméra
print("[INFO] Ouverture de la caméra")
ad_serial = Thorlabs.list_cameras_tlcam()
print(ad_serial, type(ad_serial))
cam1 = Thorlabs.TLCamera.ThorlabsTLCamera(ad_serial)
print("ehejej")
cam1.close()
# with Thorlabs.ThorlabsTLCamera(serial=ad_serial) as cam1:
#     print("[INFO] Caméra ouverte!")
#     cam1.snap()