"""
Minimal example of a TCP client connecting to a TCP server instrument class plugin (type 0D) and
sending to it 0D data in a row representing a sinus.
:comment: Program modified by Maxence BARRE to provide a single class to send the data in just one line.
Provide better readability in the code.
:comment: this program has not been tested deeply. Therefore it may not work for every configuration possible.
:comment: be careful, it is not because this client sends data that the connection is well established. Sometimes,
    the client "has the impression" of being connected but it is not!!!
:comment: this example is based on the file you can find in the 4.2.x_dev github branch pymodaq>examples>tcp_client.py
    however all the function that seem not to work have been removed

To execute all this:

* start a Daq_Viewer from the console, select DAQ0D and TCP_Server, set the IP to localhost, then init
* execute this script

You should see the TCP server printing the sinus in its 0D data viewer

"""


import numpy as np

from pymodaq.utils.tcp_ip.tcp_server_client import TCPClientTemplate
from pymodaq.utils.data import DataToExport, DataRaw
# from pymodaq.utils.tcp_ip.serializer import Serializer


class TCPClient_all_in_one(TCPClientTemplate):
    """
    this class enables you to setup the connection with the pymodaq server, sends the data you want
    and close the connexion whenever you want.
    You don't need to look at the encryption of the data. This class permits operations like
    my_tcp = TCPclient_all_in_one(my_ip, my_port)
    my_tcp.send_data(4) # plot 4 at the screen
    my_tcp.close() # close the connexion
    :comment: for now, the program has only been tested (and works) in the following conditions:
        -> in localhost, this program as a client, and sends only 0D data
    :comment: to close a connexion, you just need to enter my_tcp.close(). this function inherits from the super class
    """
    def __init__(self, ipaddress="localhost", port=6341, client_type="GRABBER"):
        """
        initiate the connexion with the server
        :param: information for connexion to Pymodaq (Pymodaq is the server, this prg is the client)
        :comment: idk if the client_type variable is just the name to print on the deck or does it have other uses
            after some tests: the use of something else than "GRABBER" leads to error "[WinError 10053]"
        :comment: be careful with the function super().__init__ the first arguments of the function are not ipadress, port, and client_type
        """
        print(f"[INFO] Connecting to {ipaddress} on port {port} as a {client_type}")
        super().__init__(ipaddress=ipaddress, port=port, client_type=client_type)      # init the connexion and says to pymodaq that the prg is a grabber

    def post_init(self, extra_commands=[]):
        """
        check if the connexion is well setup?
        should not be used by the user?
        """
        self.socket.check_sended_with_serializer(self.client_type)


    def send_data(self, data: int | str | float | np.float_):
        """
        the function you want to know
        :param: int | str | float: the type of the parameter in only due to the fact that other dimensions/type (such as np.array) has not been tested
        :comment: you don't need to take care of the serialization/encoding or stuff like that. This class aims to send the data as easy as possible.
        """
        if type(data) not in (int, str, float, np.float_):
            raise Warning(f"Sending {type(data)} has not been tested yet.")
        print([np.array([data])])
        dwa0D = DataRaw('dwa0D', data=[np.array([data])])                       # works when try to send 0D data. may not be the best solution/optimization possible
        dwa = DataToExport('mydata', data=[dwa0D], plot=True)
        if self.socket is not None:
            self.socket.check_sended_with_serializer('Done')
            self.socket.check_sended_with_serializer(dwa)


    def process_error_in_polling(self, e: Exception):
        """
        the class should work with this function but it would give an error (notImplemented)
        seems to be used as the very beginning and never after
        should not be used by the user?
        """
        print("[INFO] Use of the function process_error_in_polling")
        print(e)


if __name__ == '__main__':
    from threading import Thread
    from time import sleep

    tcpclient = TCPClient_all_in_one("localhost", 6341, "my_own_test")
    t = Thread(target=tcpclient.init_connection)
    t.start()
    sleep(1)

    for ind in range(10):
        tcpclient.send_data(np.sin(ind*.2))
        sleep(1)

        

    tcpclient.close()