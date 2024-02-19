"""
programme d'extraction de phase et autres infos depuis une image d'interférences
:auteur: Maxence BARRE
:date: 19/02/2024
:comment: toutes les infos sur la fft2 sont issues de: https://users.polytech.unice.fr/~leroux/crim2.pdf
"""

# importation des modules nécessaires
import numpy as np


# fonctions secondaires
def calculate_2dft(input):
    ft = np.fft.ifftshift(input)
    ft = np.fft.fft2(ft)
    return np.fft.fftshift(ft)


# fonction primaire
def extract_all_infos(image_base, bool_filtre=True, reconstruct_picture=False):
    """
    :param: image_base: np.array: la photo des interférences (prise avec une photo zelux pex; voire la ROI de la photo)
    :param: bool_filtre: bool: indique si l'on ignore les "pics du centre" qui correspondent au fond continu (ou qui varie très lentement)
    :param: reconstruct_picture: bool: indique si l'on souhaite retourner plus d'informations, comme la reconstruction des interférences ou bien le spectre de la ff2
    :return: un tuple assez long
        si not reconstruct_picture: return (phase, frequence, slope)
        si reconstruct_picture: return (phase, frequence, slope, u, v, ft, interf_reco)
    :comment: temps d'exécution: 
        moyenne sans reconstruction: 1.66e-1 seconde
        moyenne avec reconstruction: 4.21e-1 seconde
    """
    image = image_base[:, :, :3].mean(axis=2)                   # Convert to grayscale
    ft = calculate_2dft(image)                                  # on fait la fft2
    # on essaye d'appliquer un filtre passe-haut pour effacer les variations lentes
    if bool_filtre:
        U = np.fft.fftshift(np.fft.fftfreq(ft.shape[0]))
        V = np.fft.fftshift(np.fft.fftfreq(ft.shape[1]))
        r_u = (np.abs(U) >= 0.05).reshape(U.size, 1)            # on souhaite conserver uniquement les frequences spatiales >= 0.05 (peut etre modifié selon les besoins)
        r_v = (np.abs(V) >= 0.05).reshape(1, V.size)            # idem
        filtre = np.array(np.meshgrid(r_v, r_u))
        filtre = np.logical_or(filtre[0, :, :], filtre[1, :, :])    # création du filtre
        ft = ft*filtre                                          # application du filtre

    # on trouve automatiquement les pics dans la FFT2
    index = np.transpose(np.where(np.abs(ft) == np.max(np.abs(ft))))  # attention: risque d'erreur ici, si le contraste n'est pas assez bon
    phase = np.angle(ft[np.where(np.abs(ft) == np.max(np.abs(ft)))])
    u = U[index[0, 0]]
    v = V[index[0, 1]]
    frequence_ortho = np.sqrt(u**2 + v**2)

    if reconstruct_picture:
        # reconstruction des interferences
        ft_reco = np.zeros(ft.shape, dtype=np.complex128)
        ft_reco[index[:, 0], index[:, 1]] = ft[index[:, 0], index[:, 1]]
        # reconstruction et affichage des interférences (pour vérifier la cohérence des résultats)
        interf_reco = np.fft.ifftshift(ft_reco)
        interf_reco = np.fft.ifft2(interf_reco)
        interf_reco = np.fft.fftshift(interf_reco)
        interf_reco = interf_reco.real
        return phase, frequence_ortho, -v/u, u, v, ft, interf_reco
    
    return phase, frequence_ortho, -v/u

if __name__ == "__main__":
    import time as t
    import matplotlib.pyplot as plt
    image_test = "image4.png"
    image = plt.imread(image_test)
    tps_ttl = 0
    for i in range(10):
        deb = t.time()
        extract_all_infos(image)
        tps_ttl += t.time() - deb
    print(f"Moyenne sans reconstruction: {tps_ttl/10:2e}s")

    for i in range(10):
        deb = t.time()
        extract_all_infos(image, reconstruct_picture=True)
        tps_ttl += t.time() - deb
    print(f"Moyenne avec reconstruction: {tps_ttl/10:2e}s")
        