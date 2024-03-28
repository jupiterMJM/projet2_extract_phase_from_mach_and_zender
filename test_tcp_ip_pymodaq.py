from pymodaq.utils.tcp_ip.serializer import Serializer, DeSerializer
import time as t
import random as rd
import socket as sk

socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
socket.bind(('localhost', 15555))

try:
    while True:
            socket.listen(5)
            client, address = socket.accept()
            print("{} connected".format( address ))

            response = client.recv(255)
            # if response == b'Launch_acquisition':
            print(response)
                    
finally:
    print("Close")
    client.close()