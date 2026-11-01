from pathlib import Path

from wrfrun.core import ResultSource
from wrfrun.core.core import WRFRUN_NEW, create_wrfrun_session
from wrfrun.model.arps.core.arps import ARPS, ARPSInputsRules


def test_arps_stages_history_from_another_experiment(tmp_path: Path):
    token = create_wrfrun_session()
    try:
        project = tmp_path / "project"
        WRFRUN_NEW.resource.register_default_providers(project, project / ".wrfrun", "v01", "run-1")
        WRFRUN_NEW.namelist.register_namelist_id("arps")

        result_path = project / "data/outputs/v02/run-0/ext2arps"
        result_path.mkdir(parents=True)
        for name in ("ext2arps.hdfgrdbas", "ext2arps.hdf000000"):
            (result_path / name).touch()

        executable = ARPS.__new__(ARPS)
        executable.history_source = ResultSource("ext2arps", "v02", "run-0")
        staged = []
        executable.add_input_files = staged.extend
        ARPSInputsRules._stage_histories(
            executable,
            {"initialization": {"inigbf": "ext2arps.hdfgrdbas", "inifile": "ext2arps.hdf000000"}},
        )

        assert staged == [
            WRFRUN_NEW.resource.get_result_ref(source=executable.history_source) / "ext2arps.hdfgrdbas",
            WRFRUN_NEW.resource.get_result_ref(source=executable.history_source) / "ext2arps.hdf000000",
        ]
    finally:
        WRFRUN_NEW.reset_session(token)
