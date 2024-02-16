"""
prise en main des fonctions de fft2 (FFT en 2D)
:auteur: Maxence BARRE
:date: 16/02/2024
:comment: ce programme n'a pas vocation à être appelé par un programme parent
:comment: le site https://users.polytech.unice.fr/~leroux/crim2.pdf est extrèmement utile!!!
"""

# importation des modules
import numpy as np
import matplotlib.pyplot as plt

# reconstruction des interferences
ft_reco = np.zeros((1081, 1441))
point0 = (1081//2, 1441//2)
point_quart_haut_droit = (point0[0]+97, point0[1]+187)
point_quart_bas_gauche = (2*point0[0]-point_quart_haut_droit[0], 2 * point0[1] - point_quart_haut_droit[1])
print(point_quart_haut_droit)
print(point_quart_bas_gauche)
ft_reco[point_quart_haut_droit] = 1000
ft_reco[point_quart_bas_gauche] = 1000
u = np.fft.fftshift(np.fft.fftfreq(1081))[point_quart_haut_droit[0]]
v = np.fft.fftshift(np.fft.fftfreq(1441))[point_quart_haut_droit[1]]
print(u, v)

# Calculate the inverse Fourier transform of 
# the Fourier transform
coord = np.where(np.log(abs(ft_reco)) > 0)
# coord = [(coord[0][i], coord[1][i]) for i in range(coord[0].shape[0])]


plt.subplot(121)
# plt.imshow(np.log(abs(ft_reco)))
plt.scatter(coord[0], coord[1])




ift = np.fft.ifftshift(ft_reco)
ift = np.fft.ifft2(ift)
ift = np.fft.fftshift(ift)
ift = ift.real  # Take only the real part
plt.subplot(122)
plt.imshow(ift)
plt.title("Interférences extraites")
plt.set_cmap("grey")
plt.xlim([750, 1000])
plt.ylim([800, 400])
plt.axline((900, 600), slope=-v/u)



plt.show()