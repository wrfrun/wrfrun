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

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

LOGGER = logging.getLogger("wrfrun")


def _check_and_prepare_namelist():
    WRFRUNConfig = WRFRUN_NEW.config
    global_config = WRFRUN_NEW.config.get_model_config("arps")
    model_config: dict = global_config.get("arpstrn", {})

    if len(model_config) == 0:
        LOGGER.error("Config for [magenta]arpstrn[/magenta] not found in your TOML, check it.")
        raise KeyError("Config for arpstrn not found in your TOML, check it.")

    dir_terrain_data = model_config["dir_terrain_data"]
    user_namelist = model_config["user_namelist"]
    run_name = "wrfrun"

    if not WRFRUN_NEW.namelist.check_namelist_id("arpstrn"):
        WRFRUN_NEW.namelist.register_namelist_id("arpstrn")

    WRFRUN_NEW.namelist.read_namelist(user_namelist, "arpstrn")

    # User's namelist should have the highest priority.
    return
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

        work_path = ResourceRef("workspace_arps", "arpstrn")
        self.namelist_path = work_path / "arpstrn.nml"

        super().__init__(
            "arpstrn",
            "./arpstrn",
            work_path,
            stdin_file=self.namelist_path,
            mpi_use=mpi_use,
            mpi_cmd=mpi_cmd,
            mpi_core_num=mpi_core_num,
        )

        _check_and_prepare_namelist()

    def generate_custom_config(self):
        """
        Store custom configs, including:

        * Namelist settings.
        """
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arpstrn")})

    def load_custom_config(self):
        """
        Load custom configs, including:

        * Namelist settings.
        """
        if not WRFRUN_NEW.namelist.check_namelist_id("arpstrn"):
            WRFRUN_NEW.namelist.register_namelist_id("arpstrn")

        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arpstrn")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arpstrn"

        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")

        WRFRUN_NEW.namelist.update_namelist(
            {
                "jobname": {"runname": self.name},
                "trn_output": {"dirname": "./outputs"},
            },
            "arpstrn",
        )

        WRFRUN_NEW.namelist.write_namelist(
            self.namelist_path,
            "arpstrn",
        )

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                startswith=f"{self.name}.trndata",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )

            # also save namelist files.
            self.add_output_files(
                filenames="arpstrn.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


def arpstrn():
    """
    Function interface for :class:`ARPSTrn`.

    Parameters needed to initialize :class:`ARPSTrn` is read from global variable :doc:`WRFRUN </api/core.core>`.
    """
    ARPSTrn()()


__all__ = ["ARPSTrn", "arpstrn"]
