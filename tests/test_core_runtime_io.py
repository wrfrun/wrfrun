import pytest

from wrfrun.core.type import ResourceRef


def test_io_service_links_copies_and_moves_files(runtime):
    source = runtime.project / "source.txt"
    source.parent.mkdir(parents=True)
    source.write_text("content")

    link = runtime.project / "links/source.txt"
    runtime.io.symlink(file_path=source, save_path=link)
    assert link.is_symlink()
    assert link.read_text() == "content"

    copied = runtime.project / "copies/source.txt"
    runtime.io.copy(file_path=source, save_path=copied)
    assert copied.read_text() == "content"
    assert source.exists()

    moved = runtime.project / "moved/source.txt"
    runtime.io.move(file_path=copied, save_path=moved)
    assert moved.read_text() == "content"
    assert not copied.exists()


def test_io_service_resolves_resource_refs_and_refuses_unrequested_overwrite(runtime):
    source = runtime.project / "source.txt"
    source.parent.mkdir(parents=True)
    source.write_text("first")
    target = runtime.project / "target.txt"

    runtime.io.copy(
        file_path=ResourceRef("project", "source.txt"),
        save_path=ResourceRef("project", "target.txt"),
    )
    with pytest.raises(FileExistsError):
        runtime.io.copy(file_path=source, save_path=target)

    source.write_text("second")
    runtime.io.copy(file_path=source, save_path=target, overwrite=True)
    assert target.read_text() == "second"


def test_io_service_reports_missing_source(runtime):
    with pytest.raises(FileNotFoundError):
        runtime.io.copy(file_path=runtime.project / "missing.txt", save_path=runtime.project / "target.txt")
