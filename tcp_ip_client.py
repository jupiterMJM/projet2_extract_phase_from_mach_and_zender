# coding: utf-8

import socket
import time as t
from pymodaq.utils.tcp_ip.serializer import Serializer, DeSerializer

hote = "localhost"
port = 15555

servor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servor.connect((hote, port))
print("Connection on {}".format(port))
t.sleep(4)
# servor.send('Launch_acquisition'.encode())
try:
    while True:
        print("inside the boucle")
        retour = servor.recv(255).decode()
        print(retour)
        t.sleep(0.1)
    
except:
    print("Close")
    socket.close(servor)