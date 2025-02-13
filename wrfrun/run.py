"""
``wrfrun.run`` module.
"""

import sys
import threading
from datetime import datetime
from os.path import abspath, dirname, exists
from typing import Optional, Tuple, Union

from .core import WRFRUNConfig, WRFRUNConstants, WRFRunServer, WRFRunServerHandler, save_config, stop_server
from .data import prepare_wps_input_data
from .model.namelist import prepare_wps_namelist, prepare_wrf_namelist, prepare_wrfda_namelist
from .model.plot import plot_domain_area
from .model.utils import clear_wps_logs, clear_wrf_logs
from .pbs import in_pbs, prepare_pbs_script
from .utils import call_subprocess, check_path, logger, logger_add_file_handler
from .workspace import prepare_workspace


def confirm_model_area():
    """
    Ask user to check domain area.

    """
    plot_domain_area()

    if not in_pbs():
        # ask user
        logger.warning(f"Check the domain image, is it right?")
        answer = input("Is it right? [y/N]: ")

        answer = answer.lower()

        if answer not in ["y", "yes"]:
            logger.error(f"Change your domain setting and run again")
            exit(1)


class WRFRun:
    """
    ``WRFRun`` is a context class to use all functions in ``wrfrun`` package.

    """
    def __init__(self, config_file: str, init_workspace=True, start_server=True, pbs_mode=True, prepare_wps_data=False, wps_data_area: Optional[Tuple[int, int, int, int]] = None):
        """
        WRFRun, a context class to achieve some goals before and after running WRF, like save a copy of config file, start and close WRFRunServer.

        :param config_file: ``wrfrun`` config file's path.
        :param init_workspace: If True, clean old files in workspace and re-create it.
        :param start_server: Whether to start WRFRunServer, defaults to True.
        :param pbs_mode: If commit this task to the PBS system, defaults to True.
        :param prepare_wps_data: If True, download input datas for WPS first.
        :param wps_data_area: If ``prepare_wps_data==True``, you need to give the area range of input data so download function can download data from ERA5.
        :return:
        """
        # variables for running WRFRunServer
        self.start_server = start_server
        self.wrfrun_server: Union[WRFRunServer, None] = None
        self.wrfrun_server_thread: Union[threading.Thread, None] = None
        self.ip = ""
        self.port = -1
        self.pbs_mode = pbs_mode
        self.init_workspace = init_workspace
        self.prepare_wps_data = prepare_wps_data
        self.wps_data_area = wps_data_area
        self.entry_file_path = abspath(sys.argv[0])
        self.entry_file_dir_path = dirname(self.entry_file_path)

        # make sure we can read the config file, because sometimes the user may run the Python script in a different path.
        abs_config_path = f"{self.entry_file_dir_path}/{config_file}"
        WRFRUNConfig.load_config(abs_config_path)

    def __enter__(self):
        # check workspace
        for _path in [WRFRUNConstants.get_work_path("wps"), WRFRUNConstants.get_work_path("wrf"), WRFRUNConstants.get_work_path("wrfda")]:
            if not exists(_path) and not self.init_workspace:
                logger.info(f"Force re-create workspace because it is broken.")
                self.init_workspace = True
                break

        prepare_wps_namelist()
        prepare_wrf_namelist()
        prepare_wrfda_namelist()

        # here is the condition we need to initialize workspace:
        # 1. pbs_mode = True and init_workspace = True, do prepare_workspace before committing the task to the PBS system.
        # 2. pbs_mode = False and init_workspace = True, do prepare_workspace.
        if self.pbs_mode and not in_pbs():
            if self.init_workspace:
                prepare_workspace()

            # ask user before commit the task
            confirm_model_area()

            prepare_pbs_script(self.entry_file_path)

            call_subprocess(["qsub", f"{self.entry_file_dir_path}/run.sh"])
            logger.info(f"Work has been submit to PBS system")
            exit(0)

        elif not self.pbs_mode:
            if self.init_workspace:
                prepare_workspace()

            confirm_model_area()

        # save a copy of config to the output path
        output_save_path = WRFRUNConfig.get_output_path()
        # check the path
        check_path(output_save_path)

        save_config(f"{output_save_path}/config.yaml")

        # check if we need to start a server
        if self.start_server:
            # start server
            self._start_wrfrun_server()

        # change status
        WRFRUNConstants.set_wrfrun_context(True)

        logger_add_file_handler(WRFRUNConfig.get_log_path())

        if self.prepare_wps_data:
            if self.wps_data_area is None:
                logger.error(f"If you want wrfrun preparing data, you need to give `wps_data_area`")
                raise ValueError(f"If you want wrfrun preparing data, you need to give `wps_data_area`")
            else:
                prepare_wps_input_data(self.wps_data_area)

        logger.info(r"Enter wrfrun context")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # stop thread if needed
        if self.start_server:
            stop_server(self.ip, self.port)     # type: ignore

        # change status
        WRFRUNConstants.set_wrfrun_context(False)

        clear_wps_logs()
        clear_wrf_logs()

        logger.info(r"Exit wrfrun context")

    def _start_wrfrun_server(self):
        """
        Start a WRFRunServer.
        """
        # read ip and port settings from config
        socket_ip, socket_port = WRFRUNConfig.get_socket_server_config()

        # get simulate settings
        start_date = datetime.strptime(
            WRFRUNConfig.get_wrf_config()["time"]["start_date"], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(
            WRFRUNConfig.get_wrf_config()["time"]["end_date"], "%Y-%m-%d %H:%M:%S")

        # calculate simulate seconds
        time_delta = end_date - start_date
        simulate_seconds = time_delta.days * 24 * 60 * 60 + time_delta.seconds

        # init server
        self.wrfrun_server = WRFRunServer(
            start_date, simulate_seconds, (socket_ip, socket_port),
            WRFRunServerHandler
        )

        # get ip and port from instance, because the port may change
        self.ip, self.port = self.wrfrun_server.server_address

        logger.info(f"Start socket server on {self.ip}:{self.port}")

        # start server thread
        self.wrfrun_server_thread = threading.Thread(
            target=self.wrfrun_server.serve_forever
        )
        self.wrfrun_server_thread.daemon = True
        self.wrfrun_server_thread.start()


__all__ = ["WRFRun"]
