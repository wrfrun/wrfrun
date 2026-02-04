"""
wrfrun.run
##########

.. autosummary::
    :toctree: generated/

    confirm_model_area
    WRFRun

This module defines class and function used by ``wrfrun`` to run simulations.

Use ``WRFRun`` to control simulations better
********************************************

:class:`WRFRun` provides many useful features:

* Set log files.
* Load config and namelist from files.
* Clear and prepare ``wrfrun`` workspace.
* Download background data from ERA5.
* Commit simulation to job schedulers.
* Record and replay simulations.
* Start socket server.

Though you can do same things manually, why bother yourself while :class:`WRFRun` is easy to use:

.. code-block:: python
    :caption: main.py

    from wrfrun.run import WRFRun

    config_file = "./config.toml"

    with WRFRun(config_file) as wrf_run:
        # do something
        ...
"""

import sys
import threading
from collections.abc import Generator
from os.path import abspath, dirname
from typing import Optional, Tuple, Union

from wrfrun.core.base import ExecutableBase

from .core import WRFRunBasicError, WRFRunServer, WRFRunServerHandler, call_subprocess, replay_config_generator, stop_server
from .core._record import ExecutableRecorder
from .core.core import WRFRUN
from .data import prepare_wps_input_data
from .log import logger, logger_add_file_handler
from .model import clear_model_logs, generate_domain_area
from .scheduler import in_job_scheduler, prepare_scheduler_script
from .workspace import check_workspace, prepare_workspace


def confirm_model_area():
    """
    Ask user to check domain area.

    """
    flag = generate_domain_area()

    if not in_job_scheduler() and flag:
        # ask user
        logger.warning("Check the domain image, is it right?")
        answer = input("Is it right? [y/N]: ")

        answer = answer.lower()

        if answer not in ["y", "yes"]:
            logger.error("Change your domain setting and run again")
            exit(1)


class WRFRun:
    """
    ``WRFRun`` is a context class to use all functions in ``wrfrun`` package.
    """

    def __init__(
        self,
        config_file: str,
        init_workspace=True,
        start_server=False,
        submit_job=False,
        prepare_wps_data=False,
        wps_data_area: Optional[Tuple[int, int, int, int]] = None,
        skip_domain_confirm=False,
    ):
        """
        Context class to achieve some goals before and after running WRF,
        like saving a copy of config file, starting and closing WRFRunServer.

        :param config_file: ``wrfrun`` config file's path.
        :type config_file: str
        :param init_workspace: If True, clean old files in workspace and re-create it.
        :type init_workspace: bool
        :param start_server: Whether to start WRFRunServer, defaults to True.
        :type start_server: bool
        :param submit_job: If commit this task to the PBS system, defaults to True.
        :type submit_job: bool
        :param prepare_wps_data: If True, download input datas for WPS first.
        :type prepare_wps_data: bool
        :param wps_data_area: If ``prepare_wps_data==True``, you need to give the area range of input data,
                              so download function can download data from ERA5.
        :type wps_data_area: tuple
        :param skip_domain_confirm: If ``True``, skip domain confirm.
        :type skip_domain_confirm: bool
        :return:
        """
        # variables for running WRFRunServer
        self._start_server = start_server
        self._wrfrun_server: Union[WRFRunServer, None] = None
        self._wrfrun_server_thread: Union[threading.Thread, None] = None
        self._ip = ""
        self._port = -1

        self._submit_job = submit_job
        self._init_workspace = init_workspace
        self._prepare_wps_data = prepare_wps_data
        self._wps_data_area = wps_data_area
        self._skip_domain_confirm = skip_domain_confirm
        self._entry_file_path = abspath(sys.argv[0])
        self._entry_file_dir_path = dirname(self._entry_file_path)
        self._replay_configs = None

        # make sure we can read the config file,
        # because sometimes the user may run the Python script in a different path.
        abs_config_path = f"{self._entry_file_dir_path}/{config_file}"
        WRFRUN.init_wrfrun_config(abs_config_path)

        self._WRFRUNReplay: Optional[ExecutableRecorder] = None

    def __enter__(self):
        # check workspace
        if not check_workspace():
            logger.info("Force re-create workspace because it is broken.")
            self._init_workspace = True

        # here is the condition we need to initialize workspace:
        # 1. submit_job = True and init_workspace = True,
        #    do prepare_workspace before submitting the task to job scheduler.
        # 2. submit_job = False and init_workspace = True, do prepare_workspace.
        if self._submit_job and not in_job_scheduler():
            if self._init_workspace:
                prepare_workspace()

            # ask user before commit the task
            if not self._skip_domain_confirm:
                confirm_model_area()

            prepare_scheduler_script(self._entry_file_path)

            call_subprocess(["qsub", f"{self._entry_file_dir_path}/run.sh"])
            logger.info("Work has been submit to PBS system")
            exit(0)

        elif not self._submit_job:
            if self._init_workspace:
                prepare_workspace()

            if not self._skip_domain_confirm:
                confirm_model_area()

        # save a copy of config to the output path
        WRFRUN.config.save_wrfrun_config(f"{WRFRUN.config.WRFRUN_OUTPUT_PATH}/config.toml")

        # check if we need to start a server
        if self._start_server:
            # start server
            self._start_wrfrun_server()

        # change status
        WRFRUN.config.set_wrfrun_context(True)

        logger_add_file_handler(WRFRUN.config.get_log_path())

        if self._prepare_wps_data:
            if self._wps_data_area is None:
                logger.error("If you want wrfrun preparing data, you need to give `wps_data_area`")
                raise ValueError("If you want wrfrun preparing data, you need to give `wps_data_area`")
            else:
                prepare_wps_input_data(self._wps_data_area)

        logger.debug(r"Enter wrfrun context")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # stop thread if needed
        if self._start_server:
            stop_server(self._ip, self._port)  # type: ignore

        if exc_type is None and self._WRFRUNReplay is not None:
            self._WRFRUNReplay.export_replay_file()
            self._WRFRUNReplay.clear_records()

        # change status
        WRFRUN.config.set_wrfrun_context(False)

        clear_model_logs()

        logger.debug(r"Exit wrfrun context")

    def _start_wrfrun_server(self):
        """
        Start a WRFRunServer to report simulation progress.
        """
        # read ip and port settings from config
        socket_ip, socket_port = WRFRUN.config.get_socket_server_config()

        # get simulate settings
        start_date = WRFRUN.config.get_model_config("wrf")["time"]["start_date"]
        end_date = WRFRUN.config.get_model_config("wrf")["time"]["end_date"]

        start_date = start_date[0] if isinstance(start_date, list) else start_date
        end_date = end_date[0] if isinstance(end_date, list) else end_date

        # calculate simulate seconds
        time_delta = end_date - start_date
        simulate_seconds = time_delta.days * 24 * 60 * 60 + time_delta.seconds

        # init server
        self._wrfrun_server = WRFRunServer(start_date, simulate_seconds, (socket_ip, socket_port), WRFRunServerHandler)

        # get ip and port from instance, because the port may change
        self._ip, self._port = self._wrfrun_server.server_address  # type: ignore

        logger.info(f"Start socket server on {self._ip}:{self._port}")

        # start server thread
        self._wrfrun_server_thread = threading.Thread(target=self._wrfrun_server.serve_forever)
        self._wrfrun_server_thread.daemon = True
        self._wrfrun_server_thread.start()

    def record_simulation(self, output_path: str, include_data=False):
        """
        Start to record simulation. Simulation parts before this function call will not be recorded.

        :param output_path: Output file path.
        :type output_path: str
        :param include_data: If includes data.
        :type include_data: bool
        """
        WRFRUN.init_recorder(output_path, include_data)
        WRFRUN.config.IS_RECORDING = True
        self._WRFRUNReplay = WRFRUN.record

    def replay_simulation(self, replay_file: str):
        """
        Replay the whole simulation with settings from the ``replay_file``.

        :param replay_file: ``.replay`` file path.
        :type replay_file: str
        """
        WRFRUN.config.check_wrfrun_context(True)

        if self._replay_configs is not None:
            del self._replay_configs

        self._replay_configs = replay_config_generator(replay_file)

        WRFRUN.config.IS_IN_REPLAY = True

        try:
            for _, executable in self._replay_configs:
                executable.replay()

        except WRFRunBasicError:
            logger.error("Failed to replay the simulation")

        WRFRUN.config.IS_IN_REPLAY = False

    def replay_executables(self, replay_file: str) -> Generator[tuple[str, ExecutableBase], None, None]:
        """
        Read settings from the ``replay_file``, and yield ``Executable`` name and instance in order.

        >>> with WRFRun("config.toml") as wrf_run:
        >>>     for name, _exec in wrf_run.replay_executables("example.replay"):
        >>>         _exec()

        :param replay_file: ``.replay`` file path.
        :type replay_file: str
        :return: Generator that yields ``Executable`` name and instance.
        :rtype: Generator[tuple[str, ExecutableBase]]
        """
        WRFRUN.config.check_wrfrun_context(True)

        if self._replay_configs is not None:
            del self._replay_configs

        self._replay_configs = replay_config_generator(replay_file)

        WRFRUN.config.IS_IN_REPLAY = True

        for name, executable in self._replay_configs:
            yield name, executable

        WRFRUN.config.IS_IN_REPLAY = False


__all__ = ["WRFRun"]
