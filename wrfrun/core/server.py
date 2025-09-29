"""
wrfrun.core.server
##################

Currently, ``wrfrun`` provides the method to reads log file of WRF and calculates simulation progress.
In order to report the progress to user, ``wrfrun`` provides :class:`WRFRunServer` to set up a socket server.

.. autosummary::
    :toctree: generated/

    WRFRunServer
    WRFRunServerHandler
    stop_server
"""

import socket
import socketserver
from collections.abc import Callable
from datetime import datetime
from json import dumps
from time import time
from typing import Tuple

from .config import WRFRUNConfig
from ..utils import logger

WRFRUN_SERVER_INSTANCE = None
WRFRUN_SERVER_THREAD = None


class WRFRunServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    A socket server to report time usage.

    If you want to use the socket server, you need to give four arguments: ``start_date``,
    ``wrf_simulate_seconds``, ``socket_address_port`` and ``WRFRunServerHandler``.

    >>> start_date = datetime(2021, 3, 25, 8)
    >>> simulate_seconds = 60 * 60 * 72
    >>> socket_address_port = ("0.0.0.0", 54321)
    >>> _wrfrun_server = WRFRunServer(start_date, simulate_seconds, socket_address_port, WRFRunServerHandler)

    Usually you don't need to create socket server manually, because :class:`WRFRun` will handle this.

    .. py:attribute:: start_timestamp
        :type: datetime

        The time the socket server start.

    .. py:attribute:: start_date
        :type: datetime

        The simulation's start date.

    .. py:attribute:: wrf_simulate_seconds
        :type: int

        The total seconds the simulation will integrate.

    .. py:attribute:: wrf_log_path
        :type: str

        Path of the log file the server will read.
    """

    def __init__(self, start_date: datetime, total_simulate_seconds: int, *args, **kwargs) -> None:
        """

        :param start_date: The simulation's start date.
        :type start_date: datetime
        :param total_simulate_seconds: The total seconds the simulation will integrate.
        :type total_simulate_seconds: int
        :param args: Other positional arguments passed to parent class.
        :type args:
        :param kwargs: Other keyword arguments passed to parent class.
        :type kwargs:
        """
        super().__init__(*args, **kwargs)

        # record the time the server starts
        self.start_timestamp = datetime.fromtimestamp(time())

        # record when the wrf start to integral
        self.start_date = start_date

        # record how many seconds the wrf will integral
        self.total_simulate_seconds = total_simulate_seconds

    def server_bind(self):
        """
        Bind and listen on the address and port.
        """
        # reuse address and port to prevent the error `Address already in use`
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def get_start_time(self) -> datetime:
        """
        Get the start time of the socket.
        As the socket server should start with NWP, it is also regarded as the start time of NWP.

        :return: Start datetime.
        :rtype: datetime
        """
        return self.start_timestamp

    def get_model_simulate_settings(self) -> Tuple[datetime, int]:
        """
        Get the start date of the case the NWP simulates and the total seconds of the simulation.

        :return: (start date, simulation seconds)
        :rtype: tuple
        """
        return self.start_date, self.total_simulate_seconds


class WRFRunServerHandler(socketserver.StreamRequestHandler):
    """
    :class:`WRFRunServer` handler.

    This handler can report time usage and simulation progress of the running model, simulation settings, and stop the server:

    1. If this handler receives ``"stop"``, it stops the server.
    2. If this handler receives ``"debug"``, it returns the simulation settings in JSON.
    3. It returns time usage and simulation progress in JSON when receiving any other messages.

    **On receiving "stop"**

    This handler will stop the server, and return a plain message ``Server stop``.

    **On receiving "debug"**

    This handler will return simulation settings in a JSON string like:

    .. code-block:: json

        {
            "start_date": "2021-03-25 00:00",
            "total_simulate_seconds": 360000,
        }

    **On receiving any other messages**

    This handler will return time usage and simulation progress in a JSON string like:

    .. code-block:: json

        {
            "usage": 3600,
            "status": "geogrid",
            "progress": 35,
        }

    where ``usage`` represents the seconds ``wrfrun`` has spent running the NWP model,
    ``status`` represents work status,
    ``progress`` represents simulation progress of the status in percentage.
    """
    def __init__(self, request, client_address, server: WRFRunServer, log_parse_func: Callable[[datetime], int] | None) -> None:
        """
        :class:`WRFRunServer` handler.

        :param request:
        :type request:
        :param client_address:
        :type client_address:
        :param server: :class:`WRFRunServer` instance.
        :type server: WRFRunServer
        :param log_parse_func: Function used to get simulated seconds from model's log file.
                               If the function can't parse the simulated seconds, it should return ``-1``.
        :type log_parse_func: Callable[[datetime], int]
        """
        super().__init__(request, client_address, server)

        # get server
        self.server: WRFRunServer = server
        self.log_parse_func = log_parse_func

    def calculate_time_usage(self) -> int:
        """
        Calculate the duration from the server's start time to the present,
        which represents the time ``wrfrun`` has spent running the NWP model.

        :return: Seconds.
        :rtype: int
        """
        # get current timestamp
        current_timestamp = datetime.fromtimestamp(time())

        # get delta second
        seconds_diff = current_timestamp - self.server.get_start_time()
        seconds_diff = seconds_diff.seconds

        return seconds_diff

    def calculate_progress(self) -> tuple[str, int]:
        """
        Read the log file and calculate the simulation progress.

        :return: ``(status, progress)``. ``status`` represents work status,
                 ``progress`` represents simulation progress of the status in percentage.
        :rtype: tuple[str, int]
        """
        start_date, simulate_seconds = self.server.get_model_simulate_settings()

        if self.log_parse_func is None:
            simulated_seconds = -1
        else:
            simulated_seconds = self.log_parse_func(start_date)

        if simulated_seconds > 0:
            progress = simulated_seconds * 100 // simulate_seconds
        else:
            progress = -1

        status = WRFRUNConfig.WRFRUN_WORK_STATUS

        if status == "":
            status = "*"

        return status, progress

    def handle(self) -> None:
        """
        Request handler.
        """

        # check if we will to stop server
        msg = self.rfile.readline().decode().split('\n')[0]

        if msg == "stop":
            self.server.shutdown()
            self.wfile.write(f"Server stop\n".encode())
        
        elif msg == "debug":
            start_date, simulate_seconds = self.server.get_model_simulate_settings()
            start_date = start_date.strftime("%Y-%m-%d %H:%M")
            
            self.wfile.write(dumps({"start_date": start_date, "total_seconds": simulate_seconds}).encode())
            
        else:
            status, progress = self.calculate_progress()
            time_usage = self.calculate_time_usage()

            # send the message
            self.wfile.write(dumps({"usage": time_usage, "status": status, "progress": progress}).encode())


def stop_server(socket_ip: str, socket_port: int):
    """
    Stop the socket server.

    :param socket_ip: Server address.
    :param socket_port: Server port.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((socket_ip, socket_port))

        # send msg to server
        sock.sendall("stop\n".encode())

        # receive the message
        msg = sock.recv(1024).decode().split('\n')[0]

        logger.info(f"WRFRunServer: {msg}")

    except (ConnectionRefusedError, ConnectionResetError):
        logger.warning("Fail to stop WRFRunServer, maybe it doesn't start at all.")


__all__ = ["WRFRunServer", "WRFRunServerHandler", "stop_server"]
