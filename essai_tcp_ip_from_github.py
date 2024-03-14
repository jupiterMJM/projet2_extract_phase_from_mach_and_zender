"""
Minimal example of a TCP client connecting to a TCP server instrument class plugin (type 0D) and
sending to it 0D data in a row representing a sinus.

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
    my_tcp.close # close the connexion
    :comment: for now, the program has only been tested (and works) in the following conditions:
        -> in localhost, this program as a client, and sends only 0D data
    :comment: to close a connexion, you just need to enter my_tcp.close(). this function inherits from the super class
    """
    def __init__(self, ipaddress="localhost", port=6341, client_type="GRABBER"):
        print(ipaddress, port, client_type)
        super().__init__(ipaddress=ipaddress, port=port, client_type=client_type)      # init the connexion and says to pymodaq that the prg is a grabber

    def post_init(self, extra_commands=[]):
        self.socket.check_sended_with_serializer(self.client_type)


    def send_data(self, data: DataToExport):
        print("funtion in use")
        # first send 'Done' and then send the length of the list
        if not isinstance(data, DataToExport):
            raise TypeError(f'should send a DataToExport object')
        if self.socket is not None:
            self.socket.check_sended_with_serializer('Done')
            self.socket.check_sended_with_serializer(data)


    def send_data_perso(self, data: int | str | float | np.float_):
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

    def ready_to_read(self):
        message = self._deserializer.string_deserialization()
        self.get_data(message)

    def get_data(self, message: str):
        """

        Parameters
        ----------
        message

        Returns
        -------

        """
        if self.socket is not None:

            if message == 'set_info':
                path = self._deserializer.list_deserialization()
                param_xml = self._deserializer.string_deserialization()
                print(param_xml)

            elif message == 'move_abs' or message == 'move_rel':
                position = self._deserializer.dwa_deserialization()
                print(f'Position is {position}')

            else:
                print(message)

    def data_ready(self, data: DataToExport):
        self.send_data(data)

    def ready_to_write(self):
        pass

    def ready_with_error(self):
        self.connected = False

    def process_error_in_polling(self, e: Exception):
        print(e)


if __name__ == '__main__':
    from threading import Thread
    from time import sleep
    print("connecting")
    tcpclient = TCPClient_all_in_one()
    print("initializing")
    t = Thread(target=tcpclient.init_connection)
    print("i am here")
    t.start()
    print("connected")
    sleep(5)

    for ind in range(100):
        print("sending")
        tcpclient.send_data_perso(np.sin(ind*.2))
        sleep(1)
        

    tcpclient.close()