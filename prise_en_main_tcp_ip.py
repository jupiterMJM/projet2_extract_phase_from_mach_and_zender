import socket
import time as t
import random as rd
from pymodaq.utils.tcp_ip.serializer import Serializer, DeSerializer

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('localhost', 15555))
to_send = 0
try:
    while True:
            socket.listen(5)
            client, address = socket.accept()
            print("{} connected".format( address ))
            reponse = client.recv(255).decode()
            print(reponse)
            if reponse == "launch_acquisition":
                while True:
                    print("[INFO] J'essaye d'envoyer qch")
                    to_send = (to_send + 1) % 10
                    print(f"sending: {to_send}")
                    client.send((str(to_send) + ";").encode())
finally:
    print("Close")
    client.close()