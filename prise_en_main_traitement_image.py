"""
prise en main des traitements de l'image
:auteur: Maxence BARRE
:date: 16/02/2024
:comment: ce programme n'a pas vocation à être appelé par un programme parent
"""

# importation des modules
import numpy as np
import matplotlib.pyplot as plt


# fonction secondaire
def calculate_2dft(input):
    ft = np.fft.ifftshift(input)
    ft = np.fft.fft2(ft)
    return np.fft.fftshift(ft)


# ouverture du fichier
image_filename = "image1.png"


# Processing de l'image
image = plt.imread(image_filename)
image = image[:, :, :3].mean(axis=2)  # Convert to grayscale
ft = calculate_2dft(image)

# on essaye d'appliquer un filtre passe-haut pour effacer les variations lentes
U = np.fft.fftshift(np.fft.fftfreq(ft.shape[0]))
print("U", U)
V = np.fft.fftshift(np.fft.fftfreq(ft.shape[1]))
r_u = (np.abs(U) >= 0.05).reshape(U.size, 1)
r_v = (np.abs(V) >= 0.05).reshape(1, V.size)
filtre = np.array(np.meshgrid(r_v, r_u))
filtre = np.logical_or(filtre[0, :, :], filtre[1, :, :])
# filtre = np.logical_or(filtre[:, :, 0], filtre[:, :, 1])
print(filtre.shape)
print(ft.shape)
ft = ft*filtre
print(filtre)


index = np.transpose(np.where(np.abs(ft) == np.max(np.abs(ft))))
phase = np.angle(ft[np.where(np.abs(ft) == np.max(np.abs(ft)))])
print("phase", phase)
u = U[499]  # il faut encore trouver automatiquement ces pics!
v = V[885]  # idem
print(u, v)


# reconstruction des interferences
ft_reco = np.zeros((1080, 1440))
ft_reco[499, 885] = ft[499, 885]
ft_reco[581, 555] = ft[581, 555]


# plotting et affichage graphique
fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
plt.set_cmap("gray")
ax1.imshow(image)
ax1.set_title("Image initiale")
ax1.axline((900, 600), slope=-v/u)
ax1.set_xlim([750, 1000])
ax1.set_ylim([800, 400])


plt.set_cmap("Oranges")

# im = ax2.imshow(np.log(abs(ft)), extent=(U[0], U[-1], V[-1], V[0]))
print(ft)
im = ax2.imshow(np.log(abs(ft)), extent=(U[0], U[-1], V[-1], V[0]))
ax2.scatter(V[index[:, 1]], U[index[:, 0]], marker = "x")
fig.colorbar(im)
# print(np.max(np.log(abs(ft))))
# print(np.where(np.log(abs(ft)) >= 8))
# print(ft[499, 885])
# print(ft[581, 555])
# print(ft.shape)
ax2.set_title("Fft2")





# Calculate the inverse Fourier transform of 
# the Fourier transform

ift = np.fft.ifftshift(ft_reco)
ift = np.fft.ifft2(ift)
ift = np.fft.fftshift(ift)
ift = ift.real  # Take only the real part
plt.subplot(133)
plt.imshow(ift)
plt.title("Interférences extraites")
plt.set_cmap("grey")
plt.axline((900, 600), slope=-v/u)
plt.xlim([750, 1000])
plt.ylim([800, 400])


fig.suptitle(f"Extraction des informations de l'image: {image_filename}\nFréquence spatiale: {np.sqrt(u**2 + v**2):.2E} et phase spatiale: {phase[0]:.2}")

plt.show()