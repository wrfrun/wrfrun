from pathlib import Path

from wrfrun.core.core import WRFRUN_NEW, create_wrfrun_session
from wrfrun.model.arps.core.arpsintrp import ARPSIntrp


def test_arpsintrp_stages_history_from_inputs_or_selected_results(tmp_path: Path):
    token = create_wrfrun_session()
    try:
        project = tmp_path / "project"
        WRFRUN_NEW.resource.register_default_providers(project, project / ".wrfrun", "v01", "run-1")
        WRFRUN_NEW.namelist.register_namelist_id("arpsintrp")

        input_ref = WRFRUN_NEW.resource.INPUT_DIR / "arpsintrp"
        input_path = WRFRUN_NEW.resource.get_custom_resource(input_ref)
        input_path.mkdir(parents=True)
        for name in ("arps.hdfgrdbas", "arps.hdf000000", "arps.hdf000060", "arps.sound"):
            (input_path / name).touch()

        executable = ARPSIntrp.__new__(ARPSIntrp)
        executable.history_executable = None
        executable.history_run_id = None
        staged = []
        executable.add_input_files = staged.extend
        executable._stage_history_data()

        assert staged == [
            input_ref / "arps.hdfgrdbas",
            input_ref / "arps.hdf000000",
            input_ref / "arps.hdf000060",
        ]
        assert WRFRUN_NEW.namelist.get_namelist("arpsintrp")["history_data"] == {
            "hdmpinopt": 2,
            "grdbasfn": "./arps.hdfgrdbas",
            "nhisfile": 2,
            "hisfile": ["./arps.hdf000000", "./arps.hdf000060"],
        }

        result_path = project / "data/outputs/v01/run-0/arps"
        result_path.mkdir(parents=True)
        for name in ("arps.h5fgrdbas", "arps.h5f000000"):
            (result_path / name).touch()

        executable.history_executable = "arps"
        executable.history_run_id = "run-0"
        staged.clear()
        executable._stage_history_data()

        assert [source.name for source in staged] == ["arps.h5fgrdbas", "arps.h5f000000"]
        assert WRFRUN_NEW.namelist.get_namelist("arpsintrp")["history_data"]["nhisfile"] == 1
    finally:
        WRFRUN_NEW.reset_session(token)
