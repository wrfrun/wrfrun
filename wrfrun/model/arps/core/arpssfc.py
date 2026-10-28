"""
ARPS surface-data executable.

.. autosummary::
    :toctree: generated/

    ARPSSFC
"""

from wrfrun.core import WRFRUN_NEW, ExecutableBase, ResourceRef

from ._common import prepare_arps_namelist


class ARPSSFC(ExecutableBase):
    """Prepare ARPS surface data with ``arpssfc``."""

    def __init__(self):
        """Create an ``arpssfc`` executable."""
        work_path = ResourceRef("workspace_arps", "arpssfc")
        self.namelist_path = work_path / "arpssfc.nml"

        super().__init__(
            name="arpssfc",
            cmd="./arpssfc",
            work_path=work_path,
            stdin_file=self.namelist_path,
        )

        prepare_arps_namelist("arpssfc")

    def generate_custom_config(self):
        """Store the ARPS namelist for replay."""
        self.custom_config.update({"namelist": WRFRUN_NEW.namelist.get_namelist("arpssfc")})

    def load_custom_config(self):
        """Restore the ARPS namelist for replay."""
        WRFRUN_NEW.namelist.update_namelist(self.custom_config["namelist"], "arpssfc")

    def before_exec(self):
        WRFRUN_NEW.states.check_wrfrun_context(True)
        WRFRUN_NEW.states.WRFRUN_WORK_STATUS = "arpssfc"

        WRFRUN_NEW.resource.mkdir(self.work_path / "outputs")
        WRFRUN_NEW.namelist.update_namelist({"jobname": {"runname": self.name}}, "arpssfc")
        WRFRUN_NEW.namelist.write_namelist(self.namelist_path, "arpssfc")

        super().before_exec()

    def after_exec(self):
        if not WRFRUN_NEW.states.IS_IN_REPLAY:
            self.add_output_files(
                filenames=f"{self.name}.sfcdata",
                output_dir=self.work_path / "outputs",
                save_path=self._output_save_path,
            )
            self.add_output_files(
                filenames="arpssfc.nml",
                output_dir=self.work_path,
                save_path=self._output_save_path / "logs",
            )

        super().after_exec()


__all__ = ["ARPSSFC"]
