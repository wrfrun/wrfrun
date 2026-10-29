import pytest

from wrfrun.core.error import NamelistError
from wrfrun.core.states.namelist import NamelistService


def test_namelist_service_keeps_component_ids_isolated(runtime):
    namelist = NamelistService(runtime.io)
    assert namelist.register_namelist_id("arpssfc")
    assert namelist.register_namelist_id("ext2arps")

    namelist.read_namelist({"soil": {"sfcdat": 2}}, "arpssfc")
    namelist.read_namelist({"extdfile": {"nextdfil": 3}}, "ext2arps")
    namelist.update_namelist({"soil": {"sfcdtfl": "surface.data"}}, "arpssfc")

    assert namelist.get_namelist("arpssfc") == {"soil": {"sfcdat": 2, "sfcdtfl": "surface.data"}}
    assert namelist.get_namelist("ext2arps") == {"extdfile": {"nextdfil": 3}}


def test_namelist_service_returns_a_copy_and_round_trips_files(runtime):
    namelist = NamelistService(runtime.io)
    namelist.register_namelist_id("arpssfc")
    namelist.read_namelist({"soil": {"sfcdat": 2}}, "arpssfc")

    external_copy = namelist.get_namelist("arpssfc")
    external_copy["soil"]["sfcdat"] = 1
    assert namelist.get_namelist("arpssfc")["soil"]["sfcdat"] == 2

    output = runtime.project / "arpssfc.nml"
    namelist.write_namelist(output, "arpssfc")
    reloaded = NamelistService(runtime.io)
    reloaded.register_namelist_id("arpssfc")
    reloaded.read_namelist(output.as_posix(), "arpssfc")
    assert reloaded.get_namelist("arpssfc")["soil"]["sfcdat"] == 2


def test_namelist_service_reports_unloaded_registered_id(runtime):
    namelist = NamelistService(runtime.io)
    namelist.register_namelist_id("arpssfc")

    with pytest.raises(NamelistError):
        namelist.get_namelist("arpssfc")
