import subprocess
import socket
import socketserver
import threading
from time import time
from typing import Tuple
from datetime import datetime

from wrfrun.utils import logger
from wrfrun.core.constant import WRFRUNConstants


WRFRUN_SERVER_INSTANCE = None
WRFRUN_SERVER_THREAD = None


def get_wrf_simulated_seconds(start_datetime: datetime) -> int:
    """Get how many seconds wrf has integrated.

    Args:
        start_datetime (datetime): WRF start datetime.

    Returns:
        int: Seconds.
    """
    # use linux cmd to get the latest line of wrf log files
    res = subprocess.run(
        ["tail", "-n", "1", f"{WRFRUNConstants.get_work_path('wrf')}/rsl.out.0000"], capture_output=True)
    log_text = res.stdout.decode()

    # parse log text
    if not (log_text.startswith("d01") or log_text.startswith("d02")):
        return -1

    time_string = log_text.split()[1]

    # try to parse
    try:
        current_datetime = datetime.strptime(time_string, "%Y-%m-%d_%H:%M:%S")
        date_delta = current_datetime - start_datetime
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

    def server_bind(self):
        # reuse address and port to prevent the error `Address already in use`
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def get_start_time(self) -> datetime:
        return self.start_timestamp
    
    def get_wrf_start_date(self) -> datetime:
        return self.start_date

    def get_wrf_simulate_settings(self) -> Tuple[datetime, int]:
        return self.start_date, self.wrf_simulate_seconds


class WRFRunServerHandler(socketserver.StreamRequestHandler):
    """
    Socket server handler.

    """
    def __init__(self, request, client_address, server: WRFRunServer, *args, **kwargs) -> None:
        super().__init__(request, client_address, server, *args, **kwargs)

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
        # get wrf simulate settings
        start_date, simulate_seconds = self.server.get_wrf_simulate_settings()

        # get wrf simulated seconds
        simulated_seconds = get_wrf_simulated_seconds(start_date)

        if simulated_seconds > 0:
            progress = simulated_seconds * 100 // simulate_seconds

        else:
            progress = 0

        # get work status
        status = WRFRUNConstants.get_wrf_status()

        if status == "":
            status = "*"

        return f"{status}: {progress}%"

    def handle(self) -> None:
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
            # get message to be sent
            progress = self.calculate_progress()
            time_usage = self.calculate_time_usage()

            # send
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

        # receive message
        msg = sock.recv(1024).decode().split('\n')[0]

        logger.info(f"WRFRunServer: {msg}")

    except (ConnectionRefusedError, ConnectionResetError):
        logger.warning(
            f"Fail to stop WRFRunServer, maybe it doesn't start at all.")


__all__ = ["WRFRunServer", "WRFRunServerHandler", "get_wrf_simulated_seconds", "stop_server"]
