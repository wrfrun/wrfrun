"""
wrfrun.model.palm.core
######################

Core implementation of PALM model. All ``Executable`` and function interface of PALM model are defined here.

.. autosummary::
    :toctree: generated/

    _check_and_prepare_namelist
    PALMRun
    palmrun
"""

from os.path import exists
from typing import Optional

from wrfrun.core import WRFRUN, ExecutableBase, ExecutableDB
from wrfrun.log import logger
from wrfrun.workspace.palm import get_palm_workspace_path

from ..constants import NamelistName
from .namelist import prepare_palm_namelist


def _check_and_prepare_namelist():
    """
    Check if namelist of ``PALM`` has been loaded.
    If not, call :func:`prepare_palm_namelist <wrfrun.model.palm.namelist.prepare_palm_namelist>` to load it.
    """
    if not WRFRUN.config.check_namelist("palm"):
        prepare_palm_namelist()


class PALMRun(ExecutableBase):
    """
    ``Executable`` for bash script "palmrun".
    """

    def __init__(self, config_id: str = "default", core_num: Optional[int] = None):
        """
        ``Executable`` for bash script "palmrun".

        :param config_id: Configuration identifier of ``PALM``, defaults to "default"
        :type config_id: str, optional
        :param core_num: CPU cores to use, defaults to None
        :type core_num: Optional[int], optional
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning("`core_num` should be greater than 0")
            core_num = None

        mpi_use = False
        mpi_cmd = None
        mpi_core_num = None

        cmd = f"./palmrun -r wrfrun -c {config_id} -a d3# -X {core_num} -v"

        super().__init__("palmrun", cmd, get_palm_workspace_path(), mpi_use, mpi_cmd, mpi_core_num)

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN.config.get_namelist("palm")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN.config.update_namelist(self.custom_config["namelist"], "palm")

    def before_exec(self):
        WRFRUN.config.check_wrfrun_context(True)
        WRFRUN.config.WRFRUN_WORK_STATUS = "palm"

        config = WRFRUN.config.get_model_config("palm")

        if not WRFRUN.config.IS_IN_REPLAY:
            # check if user provides topography files
            if exists(config["topography_file"]):
                self.add_input_files(
                    {
                        "file_path": config["topography_file"],
                        "save_path": get_palm_workspace_path("input"),
                        "save_name": "palmrun.topo",
                        "is_data": True,
                        "is_output": False,
                    }
                )

        super().before_exec()

        WRFRUN.config.write_namelist(f"{get_palm_workspace_path('input')}/{NamelistName.PALM}", "palm")

        # print debug logs
        logger.debug("Namelist settings of 'palmrun':")
        logger.debug(WRFRUN.config.get_namelist("palm"))

    def after_exec(self):
        if not WRFRUN.config.IS_IN_REPLAY:
            self.add_output_files(
                output_dir=get_palm_workspace_path("output"), save_path=self._output_save_path, startswith="wrfrun_"
            )

        super().after_exec()

        logger.info(f"All PALM output files have been copied to {WRFRUN.config.parse_resource_uri(self._output_save_path)}")


def palmrun():
    """
    Function interface for :class:`PALMRun`.

    Parameters needed to initialize :class:`PALMRun` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    config = WRFRUN.config.get_model_config("palm")
    PALMRun(config["config_identifier"], WRFRUN.config.get_core_num())()


def _exec_register_func(exec_db: ExecutableDB):
    """
    Function to register ``Executable``.

    :param exec_db: ``ExecutableDB`` instance.
    :type exec_db: ExecutableDB
    """
    class_list = [PALMRun]
    class_id_list = ["palmrun"]

    for _class, _id in zip(class_list, class_id_list):
        if not exec_db.is_registered(_id):
            exec_db.register_exec(_id, _class)


WRFRUN.set_exec_db_register_func(_exec_register_func)


__all__ = ["PALMRun", "palmrun"]
