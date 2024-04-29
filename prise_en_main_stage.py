"""
prise en main de la stage de l'experience, precision au 10nm
:auteur: Maxence
:remarque: pour que le prg fonctionne, il faut utiliser un MSC2 (et non pas un mSC-3C). C'est obligatoire!!!!!!!!!!!!
"""

import pylablib as pll
pll.par["devices/dlls/smaract_mcs2"] = r"C:\SmarAct\MCS\Programs"

from pylablib.devices import SmarAct
devices = SmarAct.list_msc2_devices()

with SmarAct.MCS2(devices[0]) as stage:
    print("hello")
    print(stage.get_position())
    stage.move_by(1e-2)
    print(stage.get_position())