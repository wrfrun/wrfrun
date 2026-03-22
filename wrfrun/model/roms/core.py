from os.path import abspath, basename
from typing import Optional

from wrfrun.core import WRFRUN, ExecutableBase
from wrfrun.log import logger
from wrfrun.workspace.roms import get_roms_workspace_path


class ROMS(ExecutableBase):
    """
    ``Executable`` for "roms*.exe".
    """

    def __init__(self, roms_exe_path: str, core_num: Optional[int] = None):
        """
        ``Executable`` for "roms*.exe".
        """
        model_config = WRFRUN.config.get_model_config("roms")
        in_file_path = model_config["roms_in_path"]

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
        Store ROMS config.
        """
        self.custom_config.update({"ocean.in": WRFRUN.config.get_namelist("wps"), "geogrid_tbl_file": self.geogrid_tbl_file})

    def load_custom_config(self):
        """
        Load ROMS config.
        """
        WRFRUN.config.update_namelist(self.custom_config["ocean.in"], "wps")
        self.geogrid_tbl_file = self.custom_config["geogrid_tbl_file"]

    def before_exec(self):  # 把文件放入工作区
        WRFRUN.config.check_wrfrun_context(True)
        WRFRUN.config.WRFRUN_WORK_STATUS = "roms"

        if not WRFRUN.config.IS_IN_REPLAY:
            self.add_input_files(self.in_file_path)
            self.add_input_files(self.roms_exe_path)
            self.add_input_files(self.varinfo_file_path)

        super().before_exec()

        # WRFRUN.config.write_namelist(f"{get_wrf_workspace_path('wps')}/{NamelistName.WPS}", "wps")

        # print debug logs
        logger.debug("Settings of 'roms':")
        # logger.debug(WRFRUN.config.get_namelist("wps"))

    def after_exec(self):
        if not WRFRUN.config.IS_IN_REPLAY:
            # self.add_output_files(save_path=self._log_save_path, startswith="geogrid.log", outputs=NamelistName.WPS)
            self.add_output_files(save_path=self._output_save_path, endswith=".nc")

            logger.warning(
                "If the output file is in the workspace, wrfrun will process it; otherwise, wrfrun will not handle it."
            )

        super().after_exec()

        logger.info(f"All geogrid output files have been copied to {WRFRUN.config.parse_resource_uri(self._output_save_path)}")


def roms():
    roms_exe_path = WRFRUN.config.get_model_config("roms")["roms_compiled_executable_path"]
    return ROMS(roms_exe_path, WRFRUN.config.get_core_num())()


__all__ = ["ROMS", "roms"]
