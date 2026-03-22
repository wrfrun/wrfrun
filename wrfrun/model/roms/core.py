"""
wrfrun.model.roms.core
######################

Core implementation of ROMS model.

.. autosummary::
    :toctree: generated/

    ROMS
    roms
"""

from os.path import abspath, basename
from typing import Optional

from wrfrun.core import WRFRUN, ExecutableBase
from wrfrun.log import logger
from wrfrun.workspace.roms import get_roms_workspace_path


class ROMS(ExecutableBase):
    """
    ``Executable`` for ROMS.
    """

    def __init__(self, roms_exe_path: str, core_num: Optional[int] = None):
        """
        ``Executable`` for ROMS

        :param roms_exe_path: ROMS executable file path.
        :type roms_exe_path: str
        :param core_num: CPU cores to use, defaults to None
        :type core_num: Optional[int], optional
        """
        if isinstance(core_num, int) and core_num <= 0:
            logger.warning("`core_num` should be greater than 0")
            core_num = None

        if core_num is None:
            mpi_use = False
            mpi_cmd = None
            mpi_core_num = core_num

        else:
            mpi_use = True
            mpi_cmd = "mpirun"
            mpi_core_num = core_num

        model_config = WRFRUN.config.get_model_config("roms")
        in_file_path = model_config["roms_in_path"]

        super().__init__(
            name="roms",
            cmd=f"./{basename(roms_exe_path)} ./{basename(in_file_path)}",
            work_path=get_roms_workspace_path(),
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        self.roms_exe_path = abspath(roms_exe_path)
        self.in_file_path = abspath(in_file_path)
        self.varinfo_file_path = abspath(model_config["roms_varinfo_file_path"])
        logger.warning(
            "The file path in the .in file must be an absolute path; "
            "otherwise, errors may occur when running in the wrfrun workspace."
        )

    def generate_custom_config(self):
        """
        Store custom config, including:

        * ``.in`` file path.
        * varinfo.yaml file path.
        """
        self.custom_config.update({"in_file_path": self.in_file_path, "varinfo_file_path": self.varinfo_file_path})

    def load_custom_config(self):
        """
        Load custom config, including:

        * ``.in`` file path.
        * varinfo.yaml file path.
        """
        self.in_file_path = self.custom_config["in_file_path"]
        self.varinfo_file_path = self.custom_config["varinfo_file_path"]

    def before_exec(self):
        WRFRUN.config.check_wrfrun_context(True)
        WRFRUN.config.WRFRUN_WORK_STATUS = "roms"

        if not WRFRUN.config.IS_IN_REPLAY:
            self.add_input_files(self.in_file_path)
            self.add_input_files(self.roms_exe_path)
            self.add_input_files(self.varinfo_file_path)

        super().before_exec()

    def after_exec(self):
        if not WRFRUN.config.IS_IN_REPLAY:
            self.add_output_files(save_path=self._output_save_path, endswith=".nc")

            logger.warning(
                "If the output file is in the workspace, wrfrun will process it; otherwise, wrfrun will not handle it."
            )

        super().after_exec()

        logger.info(f"All ROMS output files have been copied to {WRFRUN.config.parse_resource_uri(self._output_save_path)}")


def roms():
    """
    Function interface for :class:`ROMS`.

    Parameters needed to initialize :class:`ROMS` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    roms_exe_path = WRFRUN.config.get_model_config("roms")["roms_compiled_executable_path"]
    return ROMS(roms_exe_path, WRFRUN.config.get_core_num())()


__all__ = ["ROMS", "roms"]
