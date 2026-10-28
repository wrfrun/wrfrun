"""
wrfrun.model.arps.arpstrn
#########################

Implementation of ``arpstrn`` submodel.

.. autosummary::
    :toctree: generated/

    ARPSTrn
"""

import logging

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import apply_component_namelist_updates, load_component_namelist

LOGGER = logging.getLogger("wrfrun")


def _prepare_namelist():
    global_config = WRFRUN_NEW.config.get_model_config("arps")
    model_config: dict = global_config.get("arpstrn", {})

    if len(model_config) == 0:
        LOGGER.error("Config for [magenta]arpstrn[/magenta] not found in your TOML, check it.")
        raise KeyError("Config for arpstrn not found in your TOML, check it.")

    dir_terrain_data = model_config["dir_terrain_data"]
    load_component_namelist("arpstrn", "arpstrn.nml")

    update_value = {
        "jobname": {"runname": "wrfrun"},
        "dem_trn": {"dir_trndata": dir_terrain_data},
        "trn_output": {"dirname": "./outputs"},
    }
    WRFRUN_NEW.namelist.update_namelist(update_value, "arpstrn")

    apply_component_namelist_updates("arpstrn", "arpstrn.nml")


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

        _prepare_namelist()

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
        """Write the prepared namelist before running ``arpstrn``."""
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
        """Archive ``arpstrn`` outputs and its runtime namelist."""
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


__all__ = ["ARPSTrn"]
