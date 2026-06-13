"""
wrfrun.model.arps.arpstrn
#########################

Implementation of ``arpstrn`` submodel.

.. autosummary::
    :toctree: generated/

    ARPSTrn
    arpstrn
"""

import logging
from os import makedirs
from os.path import exists

from wrfrun.core import WRFRUN, ExecutableBase, ExecutableDB
from wrfrun.workspace.arps import get_arps_workspace_path

LOGGER = logging.getLogger("wrfrun")


def _check_and_prepare_namelist():
    WRFRUNConfig = WRFRUN.config
    model_config: dict = WRFRUNConfig.get_model_config("arps").get("arpstrn", {})

    dir_terrain_data = model_config["dir_terrain_data"]
    user_namelist = model_config["user_namelist"]
    run_name = model_config["run_name"]

    if len(model_config) == 0:
        LOGGER.error("Config for [magenta]arpstrn[/magenta] not found in your TOML, check it.")
        raise KeyError("Config for arpstrn not found in your TOML, check it.")

    if not WRFRUNConfig.check_namelist_id("arpstrn"):
        WRFRUNConfig.register_namelist_id("arpstrn")

    WRFRUNConfig.read_namelist(user_namelist, "arpstrn")

    update_value = {
        "jobname": {"runname": run_name},
        "dem_trn": {"dir_trndata": dir_terrain_data},
        "trn_output": {"dirname": "./outputs"},
    }

    WRFRUNConfig.update_namelist(update_value, "arpstrn")


class ARPSTrn(ExecutableBase):
    """
    ``Executable`` for ``arpstrn``.
    """

    def __init__(self):
        """
        ``Executable`` for ``arpstrn``.
        """
        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        self.namelist_file_name = "wrfrun.input"
        self.log_file_name = "arpstrn.log"

        cmd = f"./arpstrn < {self.namelist_file_name} > {self.log_file_name} 2>&1"

        super().__init__(
            "arpstrn",
            cmd,
            f"{get_arps_workspace_path()}/arpstrn",
            mpi_use,
            mpi_cmd,
            mpi_core_num,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN.config.get_namelist("arpstrn")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUNConfig = WRFRUN.config
        if not WRFRUNConfig.check_namelist_id("arpstrn"):
            WRFRUNConfig.register_namelist_id("arpstrn")

        WRFRUNConfig.update_namelist(self.custom_config["namelist"], "arpstrn")

    def before_exec(self):
        WRFRUNConfig = WRFRUN.config
        WRFRUNConfig.check_wrfrun_context(True)
        WRFRUNConfig.WRFRUN_WORK_STATUS = "arpstrn"

        arpstrn_workspace_path = WRFRUNConfig.parse_resource_uri(f"{get_arps_workspace_path()}/arpstrn")

        if not exists(f"{arpstrn_workspace_path}/outputs"):
            makedirs(f"{arpstrn_workspace_path}/outputs")

        WRFRUNConfig.write_namelist(
            f"{arpstrn_workspace_path}/wrfrun.input",
            "arpstrn",
        )

        super().before_exec()

    def after_exec(self):
        if not WRFRUN.config.IS_IN_REPLAY:
            run_name = WRFRUN.config.get_model_config("arps")["arpstrn"]["run_name"]

            self.add_output_files(
                outputs=f"{run_name}.trndata",
                output_dir=f"{get_arps_workspace_path()}/arpstrn/outputs",
                save_path=f"{self._output_save_path}",
            )

            # also save namelist files.
            self.add_output_files(
                outputs=self.log_file_name,
                output_dir=f"{get_arps_workspace_path()}/arpstrn",
                save_path=f"{self._output_save_path}/logs",
            )

            # also save namelist files.
            self.add_output_files(
                outputs="wrfrun.input",
                output_dir=f"{get_arps_workspace_path()}/arpstrn",
                save_path=f"{self._output_save_path}/logs",
            )

        super().after_exec()

        LOGGER.info(f"All arpstrn output files have been copied to {WRFRUN.config.parse_resource_uri(self._output_save_path)}")


def arpstrn():
    """
    Function interface for :class:`ARPSTrn`.

    Parameters needed to initialize :class:`ARPSTrn` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    ARPSTrn()()


def _exec_register_func(exec_db: ExecutableDB):
    """
    Function to register ``Executable``.

    :param exec_db: ``ExecutableDB`` instance.
    :type exec_db: ExecutableDB
    """
    class_list = [ARPSTrn]
    class_id_list = ["arpstrn"]

    for _class, _id in zip(class_list, class_id_list):
        if not exec_db.is_registered(_id):
            exec_db.register_exec(_id, _class)


WRFRUN.set_exec_db_register_func(_exec_register_func)


__all__ = ["ARPSTrn", "arpstrn"]
