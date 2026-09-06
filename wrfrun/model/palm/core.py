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

from os import listdir
from os.path import abspath, exists
from pathlib import Path
from typing import Literal, Optional

from wrfrun.core import WRFRUN_NEW, ExecutableBase
from wrfrun.log import logger

from ...core.type import ResourceRef
from .config import prepare_palm_config, write_palm_config
from .namelist import check_palm_namelist_settings, get_namelist_save_name, prepare_palm_namelist
from .utils import get_input_postfix


def _check_and_prepare_namelist(workspace_root: ResourceRef):
    """
    Check if namelist of ``PALM`` has been loaded.
    If not, call :func:`prepare_palm_namelist <wrfrun.model.palm.namelist.prepare_palm_namelist>` to load it.
    """
    if not WRFRUN_NEW.namelist.check_namelist("palm"):
        prepare_palm_namelist()
        check_palm_namelist_settings()

    if not WRFRUN_NEW.namelist.check_namelist("palm_config"):
        prepare_palm_config(workspace_root)

    if not WRFRUN_NEW.namelist.check_namelist("palm_config"):
        prepare_palm_config(workspace_root)


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

        config = WRFRUN_NEW.config.get_model_config("palm")
        job_name = config["job_name"]
        simulation_type = config["simulation_type"]
        cmd = ["./palmrun", "-r", job_name, "-c", config_id, "-a", simulation_type, "-X", str(core_num), "-v"]

        super().__init__(
            "palmrun",
            cmd,
            ResourceRef("workspace_palm", ""),
            mpi_use,
            mpi_cmd,
            mpi_core_num,
        )

        _check_and_prepare_namelist(self._get_workspace_path())

    def _get_workspace_path(self, node: Literal["root", "job", "input", "output"] = "root") -> Path | ResourceRef:
        """
        Get workspace of PALM model.

        :param node: Which dir.
        :type node: str
        :return: Workspace path.
        :rtype: str
        """
        job_name = WRFRUN_NEW.config.get_model_config("palm")["job_name"]

        match node:
            case "root":
                return self.work_path

            case "job":
                return self.work_path / "job"

            case "input":
                return self.work_path / f"job/{job_name}/INPUT"

            case "output":
                return self.work_path / f"job/{job_name}/OUTPUT"

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("palm")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "palm")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "palm"

        config = WRFRUN_NEW.config.get_model_config("palm")
        job_name = config["job_name"]
        config_id = config["config_identifier"]

        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            palm_workspace_input_path = self._get_workspace_path("input")

            # check if user provides topography files
            topography_file = config["topography_file"]
            topography_file = abspath(topography_file)
            if exists(topography_file):
                self.add_input_files(
                    {
                        "file_path": topography_file,
                        "save_path": palm_workspace_input_path,
                        "save_name": "palmrun_topo",
                        "is_data": True,
                        "is_output": False,
                    }
                )

            palm_data_dir = config["data_dir_path"]
            palm_data_dir = abspath(palm_data_dir)
            if exists(palm_data_dir):
                logger.info(f"Read datas in '{palm_data_dir}'.")
                for data in listdir(palm_data_dir):
                    _palm_postfix = get_input_postfix(data)

                    if _palm_postfix:
                        save_name = f"{job_name}{_palm_postfix}"
                        self.add_input_files(
                            {
                                "file_path": f"{palm_data_dir}/{data}",
                                "save_path": palm_workspace_input_path,
                                "save_name": save_name,
                                "is_data": True,
                                "is_output": False,
                            }
                        )

                    else:
                        logger.error(f"Your data have unknown postfix string: '{data}'.")
                        raise ValueError(f"Your data have unknown postfix string: '{data}'.")

        WRFRUN_NEW.namelist.write_namelist(
            f"{self._get_workspace_path('input')}/{get_namelist_save_name()}",
            "palm",
        )

        write_palm_config(f"{self._get_workspace_path()}/.palm.config.{config_id}")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            job_name = WRFRUN_NEW.config.get_model_config("palm")["job_name"]

            self.add_output_files(
                output_dir=self._get_workspace_path("output"),
                save_path=f"{self._output_save_path}/{job_name}",
                startswith=job_name,
            )

            # also save namelist files.
            self.add_output_files(
                output_dir=self._get_workspace_path("input"),
                save_path=f"{self._output_save_path}/{job_name}/logs",
                filenames=get_namelist_save_name(),
            )

        super().after_exec()


def palmrun():
    """
    Function interface for :class:`PALMRun`.

    Parameters needed to initialize :class:`PALMRun` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    config = WRFRUN_NEW.config.get_model_config("palm")
    PALMRun(config["config_identifier"], WRFRUN_NEW.config.get_core_num())()


__all__ = ["PALMRun", "palmrun"]
