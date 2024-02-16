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


# Read and process image
image = plt.imread(image_filename)
image = image[:, :, :3].mean(axis=2)  # Convert to grayscale
print("i.shape", image.shape)
ft = calculate_2dft(image)
plt.subplot(131)
plt.imshow(image)
plt.set_cmap("gray")
plt.title("Image initiale")
plt.xlim([750, 1000])
plt.ylim([800, 400])

plt.subplot(132)

plt.imshow(np.log(abs(ft)))
plt.colorbar()
print(np.max(np.log(abs(ft))))
print(np.where(np.log(abs(ft)) >= 8))
print(ft[499, 885])
print(ft[581, 555])
print(ft.shape)
plt.title("Fft2")
plt.set_cmap("Oranges")

# reconstruction des interferences
ft_reco = np.zeros((1080, 1440))
ft_reco[499, 885] = ft[499, 885]
ft_reco[581, 555] = ft[581, 555]

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
plt.xlim([750, 1000])
plt.ylim([800, 400])



plt.show()