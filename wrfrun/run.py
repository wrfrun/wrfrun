"""
``wrfrun.run`` module.
"""

import sys
import threading
from os.path import abspath, dirname, exists
from typing import Optional, Tuple, Union

from .core import ExecConfigRecorder, WRFRUNConfig, WRFRunBasicError, WRFRunServer, WRFRunServerHandler, replay_config_generator, stop_server
from .data import prepare_wps_input_data
from .model import clear_model_logs, plot_domain_area
from .pbs import in_pbs, prepare_pbs_script
from .utils import call_subprocess, logger, logger_add_file_handler
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
    _instance = None
    _initialized = False

    def __init__(self, config_file: str, init_workspace=True, start_server=False, pbs_mode=False, prepare_wps_data=False, wps_data_area: Optional[Tuple[int, int, int, int]] = None,
                 generate_replay_file: Optional[str] = None, replay_include_data=False):
        """
        WRFRun, a context class to achieve some goals before and after running WRF, like save a copy of config file, start and close WRFRunServer.

        :param config_file: ``wrfrun`` config file's path.
        :param init_workspace: If True, clean old files in workspace and re-create it.
        :param start_server: Whether to start WRFRunServer, defaults to True.
        :param pbs_mode: If commit this task to the PBS system, defaults to True.
        :param prepare_wps_data: If True, download input datas for WPS first.
        :param wps_data_area: If ``prepare_wps_data==True``, you need to give the area range of input data so download function can download data from ERA5.
        :param generate_replay_file: Provide a file path to save replay configs.
        :type generate_replay_file: str
        :param replay_include_data: If include input data in replay configs.
        :type replay_include_data: bool
        :return:
        """
        if self._initialized:
            return

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
        self._replay_configs = None

        # make sure we can read the config file, because sometimes the user may run the Python script in a different path.
        abs_config_path = f"{self.entry_file_dir_path}/{config_file}"
        WRFRUNConfig.load_wrfrun_config(abs_config_path)

        self._WRFRUNReplay = ExecConfigRecorder.reinit(save_path=generate_replay_file, include_data=replay_include_data)

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __enter__(self):
        # check workspace
        check_list = [WRFRUNConfig.WPS_WORK_PATH, WRFRUNConfig.WRF_WORK_PATH, WRFRUNConfig.WRFDA_WORK_PATH]
        check_list = [WRFRUNConfig.parse_resource_uri(x) for x in check_list]
        for _path in check_list:
            if not exists(_path) and not self.init_workspace:
                logger.info(f"Force re-create workspace because it is broken.")
                self.init_workspace = True
                break

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
        WRFRUNConfig.save_wrfrun_config(f"{WRFRUNConfig.WRFRUN_OUTPUT_PATH}/config.toml")

        # check if we need to start a server
        if self.start_server:
            # start server
            self._start_wrfrun_server()

        # change status
        WRFRUNConfig.set_wrfrun_context(True)

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

        if exc_type is None and WRFRUNConfig.IS_RECORDING:
            self._WRFRUNReplay.export_replay_file()
            self._WRFRUNReplay.clear_records()

        # change status
        WRFRUNConfig.set_wrfrun_context(False)

        clear_model_logs()

        logger.info(r"Exit wrfrun context")

    def _start_wrfrun_server(self):
        """
        Start a WRFRunServer.
        """
        # read ip and port settings from config
        socket_ip, socket_port = WRFRUNConfig.get_socket_server_config()

        # get simulate settings
        start_date = WRFRUNConfig.get_model_config("wrf")["time"]["start_date"]
        end_date = WRFRUNConfig.get_model_config("wrf")["time"]["end_date"]

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

    def replay_simulation(self, replay_file: str):
        """
        Replay the simulation without any changes.

        :param replay_file:
        :type replay_file:
        :return:
        :rtype:
        """
        WRFRUNConfig.check_wrfrun_context(True)

        if self._replay_configs is not None:
            del self._replay_configs

        self._replay_configs = replay_config_generator(replay_file)

        WRFRUNConfig.IS_IN_REPLAY = True

        try:
            for _, executable in self._replay_configs:
                executable.replay()

        except WRFRunBasicError:
            logger.error("Failed to replay the simulation")

        WRFRUNConfig.IS_IN_REPLAY = False

    def replay_executables(self, replay_file: str):
        """
        Replay the simulation without any changes.

        :param replay_file:
        :type replay_file:
        :return:
        :rtype:
        """
        WRFRUNConfig.check_wrfrun_context(True)

        if self._replay_configs is not None:
            del self._replay_configs

        self._replay_configs = replay_config_generator(replay_file)

        WRFRUNConfig.IS_IN_REPLAY = True

        for name, executable in self._replay_configs:
            yield name, executable

        WRFRUNConfig.IS_IN_REPLAY = False


__all__ = ["WRFRun"]
