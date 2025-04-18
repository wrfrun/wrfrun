import socket
import socketserver
import subprocess
from datetime import datetime
from time import time
from typing import Tuple, Optional

from .config import WRFRUNConfig
from ..utils import logger

WRFRUN_SERVER_INSTANCE = None
WRFRUN_SERVER_THREAD = None


def get_wrf_simulated_seconds(start_datetime: datetime, log_file_path: Optional[str] = None) -> int:
    """
    Get how many seconds wrf has integrated.

    :param start_datetime: WRF start datetime.
    :type start_datetime: datetime
    :param log_file_path: Absolute path of the log file to be parsed.
    :type log_file_path: str
    :return: Seconds.
    :rtype: int
    """
    # use linux cmd to get the latest line of wrf log files
    if log_file_path is None:
        log_file_path = WRFRUNConfig.parse_resource_uri(f"{WRFRUNConfig.WRF_WORK_PATH}/rsl.out.0000")
    res = subprocess.run(["tail", "-n", "1", log_file_path], capture_output=True)
    log_text = res.stdout.decode()

    if not (log_text.startswith("d01") or log_text.startswith("d02")):
        return -1

    time_string = log_text.split()[1]

    seconds = -1
    try:
        current_datetime = datetime.strptime(time_string, "%Y-%m-%d_%H:%M:%S")
        # remove timezone info so we can calculate.
        date_delta = current_datetime - start_datetime.replace(tzinfo=None)
        seconds = date_delta.days * 24 * 60 * 60 + date_delta.seconds

    except ValueError:
        seconds = -1

    finally:
        return seconds


class WRFRunServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    A socket server to report time usage.
    """

    def __init__(self, start_date: datetime, wrf_simulate_seconds: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # record the time the server starts
        self.start_timestamp = datetime.fromtimestamp(time())

        # record when the wrf start to integral
        self.start_date = start_date

        # record how many seconds the wrf will integral
        self.wrf_simulate_seconds = wrf_simulate_seconds

        # we need to parse the log file to track the simulation progress.
        self.wrf_log_path = WRFRUNConfig.parse_resource_uri(f"{WRFRUNConfig.WRF_WORK_PATH}/rsl.out.0000")
        logger.debug("WRFRun Server will try to track simulation progress with following log files:")
        logger.debug(f"WRF: {self.wrf_log_path}")

    def server_bind(self):
        """
        Bind address and port.
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

    def get_wrf_simulate_settings(self) -> Tuple[datetime, int]:
        """
        Get the start date of the case the NWP simulates and the total seconds of the simulation.

        :return: (start date, simulation seconds)
        :rtype: tuple
        """
        return self.start_date, self.wrf_simulate_seconds


class WRFRunServerHandler(socketserver.StreamRequestHandler):
    """
    Socket server handler.

    """
    def __init__(self, request, client_address, server: WRFRunServer) -> None:
        super().__init__(request, client_address, server)

        # get server
        self.server: WRFRunServer = server

    def calculate_time_usage(self) -> str:
        """Calculate time usage from server start (usually the time to run wrfrun)

        Returns:
            str: Time usage in `"%H:%M:%S"`
        """
        # get current timestamp
        current_timestamp = datetime.fromtimestamp(time())

        # get delta second
        seconds_diff = current_timestamp - self.server.get_start_time()
        seconds_diff = seconds_diff.seconds

        # calculate hours, minutes and seconds
        seconds = seconds_diff % 60
        minutes = (seconds_diff % 3600) // 60
        hours = seconds_diff // 3600

        time_usage = ":".join([
            str(hours).rjust(2, '0'),
            str(minutes).rjust(2, '0'),
            str(seconds).rjust(2, '0')
        ])

        return time_usage

    def calculate_progress(self) -> str:
        """
        Calculate the simulation progress.

        :return:
        :rtype:
        """
        start_date, simulate_seconds = self.server.get_wrf_simulate_settings()

        simulated_seconds = get_wrf_simulated_seconds(start_date, self.server.wrf_log_path)

        if simulated_seconds > 0:
            progress = simulated_seconds * 100 // simulate_seconds

        else:
            progress = 0

        status = WRFRUNConfig.WRFRUN_WORK_STATUS

        if status == "":
            status = "*"

        return f"{status}: {progress}%"

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
            start_date, simulate_seconds = self.server.get_wrf_simulate_settings()
            start_date = start_date.strftime("%Y-%m-%d %H:%M")
            
            self.wfile.write(f"{start_date}\n{simulate_seconds}\n".encode())
            
        else:
            progress = self.calculate_progress()
            time_usage = self.calculate_time_usage()

            # send the message
            self.wfile.write(f"{progress}\n{time_usage}".encode())


def stop_server(socket_ip: str, socket_port: int):
    """Try to stop server.

    Args:
        socket_ip (str): Server IP.
        socket_port (int): Server Port.
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


__all__ = ["WRFRunServer", "WRFRunServerHandler", "get_wrf_simulated_seconds", "stop_server"]
