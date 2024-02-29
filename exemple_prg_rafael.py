
import pyqtgraph as pg
import numpy as np
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.Qt import QtWidgets
import scipy.fft as fft
import scipy.signal.windows as windows
from collections import deque
import h5py
from pyqtgraph.Qt import QtCore
import os


##Path for the saved datas
# path = "C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\23012024\\" 
# file_name = "Scan_20231218_15_51_56.h5"

path = r"C:\Users\maxen\Desktop\centrale_supelec_1A\parcours_recherche\data_a_supprimer_si_plus_de_place"
file_name = r"\Scan_20240123_16_25_59.h5"
##Path of this script (to save ROI)
path_script = r"C:\Users\maxen\Desktop\centrale_supelec_1A\parcours_recherche\data_a_supprimer_si_plus_de_place"

with h5py.File(path + file_name ,'r') as file:
    images = np.array(file['RawData/Scan000/Detector001/Data2D/CH00/EnlData00'])

image=images[0]

app = pg.mkQApp("DockArea Example")
win = QtWidgets.QMainWindow()
win.resize(1500,780)
area = DockArea()
win.setCentralWidget(area)

d1=Dock("Dock1" ,size=(10,30), closable=True)
d2=Dock("Dock2",closable=True )
d3=Dock("Dock3")
d4=Dock("Dock4")
d5=Dock("Dock5")

area.addDock(d1,"left")
area.addDock(d2,"right")
area.addDock(d3,"bottom",d2)
area.addDock(d4,"bottom",d3)
area.addDock(d5,"bottom",d4)


w1=pg.PlotWidget()
img=pg.ImageItem()
img.setImage(image)
w1.addItem(img)

#Loaing ROI parameters
path_loads = path_script
if os.path.isfile(path_loads + "pos_roi.npy"):
    pos_loaded = np.load(path_loads + "pos_roi.npy")
else:
    pos_loaded = [0,0]

if os.path.isfile(path_loads + "angle_roi.npy"):
    angle_loaded = np.load(path_loads + "angle_roi.npy")
else:
    angle_loaded = 90

if  os.path.isfile(path_loads + "size_roi.npy"):
    size_loaded = np.load(path_loads + "size_roi.npy")
else:
    size_loaded = [200,200]



roi=pg.RectROI(pos=pos_loaded,angle=angle_loaded,size=size_loaded,pen=(5,30))
roi.addRotateHandle([1,0],[0.5,0.5])
# print(roi.pos())
# print(roi.angle())
print(roi.size())
w1.addItem(roi)
d1.addWidget(w1)


w2=pg.PlotWidget(title="fringes")
#w2.plot(np.mean(roi.getArrayRegion(image,img),axis=0))
d2.addWidget(w2)

w3=pg.PlotWidget(title="Fourier transform")
fourier = pg.PlotDataItem()
cursor = pg.InfiniteLine(pos=0,angle=90,movable=True,pen="g",label='Lire phase ici',span=(-100,100))
# cursor_value_loaded = np.load("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\cursor_position.npy")
# cursor = pg.InfiniteLine(pos=cursor_value_loaded,angle=90,movable=True)
w3.addItem(cursor)
w3.addItem(fourier)
d3.addWidget(w3)


phase_vector = deque(maxlen=len(images))

w4=pg.PlotWidget(title="Phase on ROI peak")
phase_plot = pg.PlotDataItem()
d4.addWidget(w4)

save_phases_Btn = QtWidgets.QPushButton('Save phase vector for this ROI')
save_ROI_Btn = QtWidgets.QPushButton('Save this ROI')
d5.addWidget(save_phases_Btn)
d5.addWidget(save_ROI_Btn)



phase_actual = 0
phase_old=0

N_images = len(images)
i=0
def updatePlot():
    global fringes,images,img,w2,w3,phase_old,phase_actual,i
    if i == N_images:
        i=0
    image = images[i]
    i+=1
    img.setImage(image)

    

    fringes_data=np.mean(roi.getArrayRegion(image,img),axis=0)
    fringes_window = fringes_data*windows.hamming(len(fringes_data))
    w2.clear()
    w2.plot().setData(y=fringes_data)
    w2.plot().setData(y=fringes_window,pen='r')
    #fft_signal = fft.fft(fringes_data)
    fft_signal_window=fft.fft(fringes_window)
    #fft_signal = fft_signal[:int(len(fft_signal)/2)]
    fft_signal_window = fft_signal_window[:int(len(fft_signal_window)/2)]

    fourier.clear()
    #fourier.setData(y=np.abs(fft_signal))
    fourier.setData(y=np.abs(fft_signal_window),pen='r')


    w4.clear()
    pic_position = int(cursor.value())
    #print(pic_position)
    phase = np.angle(fft_signal_window[pic_position])
    phase_actual = np.unwrap([phase_old,phase])[-1]
    phase_old=phase_actual
    phase_vector.append(phase_actual)
    w4.plot().setData(phase_vector)






def save_phases():
    global images,img,roi,cursor
    i=0
    phase_actual = 0
    phase_old=0
    N_images = len(images)
    phase_vector = np.zeros(N_images)
    print(N_images)
    for i in range(N_images):  
         image = images[i]
         fringes_data=np.mean(roi.getArrayRegion(image,img),axis=0)
         fringes_window = fringes_data*windows.hamming(len(fringes_data))
         fft_signal_window=fft.fft(fringes_window)
         fft_signal_window = fft_signal_window[:int(len(fft_signal_window)/2)]
         pic_position = int(cursor.value())
         phase = np.angle(fft_signal_window[pic_position])
         phase_actual = np.unwrap([phase_old,phase])[-1]
         phase_old=phase_actual
         phase_vector[i] = phase_actual
    #print(phase_vector)
    print("Phase vector saved")
    np.save("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\phases_referencing",phase_vector)

def saveROI():
    global roi,cursor
    pos = roi.pos()
    angle = roi.angle()
    size = roi.size()
    np.save("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\pos_roi",pos)
    np.save("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\angle_roi",angle)
    np.save("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\size_roi",size)
    cursor_pos = cursor.value()
    np.save("C:\\Users\\rm270258\\Documents\\Python Scripts\\referencing\\cursor_position",cursor_pos)


save_phases_Btn.clicked.connect(save_phases)
save_ROI_Btn.clicked.connect(saveROI)



# roi.sigRegionChanged.connect(updatePlot)
# #roi.sigRegionChangeFinished.connect(updatePlot)
# updatePlot()
    
    
timer = QtCore.QTimer()
timer.timeout.connect(updatePlot)
timer.start(50)

win.show()
if __name__ == '__main__':
    pg.exec()