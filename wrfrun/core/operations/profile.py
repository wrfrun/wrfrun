"""
wrfrun.core.operations.profile
###############################

Save and load reusable experiment configuration profiles.

.. autosummary::
    :toctree: generated/

    ProfileInfo
    save_profile
    load_profile
    list_profiles
    remove_global_profile
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

import tomli
import tomli_w
from platformdirs import user_config_dir

from ..runtime.resource import PROJECT_TREE

MANIFEST_FILE = "manifest.toml"


@dataclass(frozen=True)
class ProfileInfo:
    """Describe one saved configuration profile."""

    name: str
    experiment: str
    models: tuple[str, ...]
    created_at: str


def _global_profile_path(name: str) -> Path:
    if Path(name).name != name or name in (".", ".."):
        raise ValueError("Profile name must be a single file name.")

    return Path(user_config_dir("wrfrun")) / "profiles" / f"{name}.zip"


def _read_manifest(archive_path: Path) -> dict:
    with ZipFile(archive_path) as archive:
        with archive.open(MANIFEST_FILE) as manifest_file:
            return tomli.loads(manifest_file.read().decode())


def save_profile(config_path: str | Path, experiment: str, archive_path: str | Path):
    """Save one project's configuration and experiment overrides to a ZIP file."""
    config_file = Path(config_path).resolve()
    project_path = config_file.parent
    archive_file = Path(archive_path).resolve()

    if archive_file.exists():
        raise FileExistsError(archive_file)

    if experiment != "common" and (Path(experiment).name != experiment or experiment in (".", "..")):
        raise ValueError("Experiment name must be a single directory name.")

    with open(config_file, "rb") as config_handle:
        config = tomli.load(config_handle)

    enabled_models = tuple(
        name for name, model_config in config["model"].items() if isinstance(model_config, dict) and model_config.get("use")
    )
    manifest = {
        "format_version": 1,
        "experiment": experiment,
        "models": list(enabled_models),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config_file": config_file.name,
    }

    files = [config_file]
    files.extend((project_path / "configs").glob("*.toml"))
    for directory in ("configs/namelists/templates", "configs/namelists/user", "configs/scheduler"):
        source_dir = project_path / directory
        if source_dir.is_dir():
            files.extend(path for path in source_dir.rglob("*") if path.is_file())

    if experiment != "common":
        experiment_dir = project_path / "configs/experiments" / experiment
        if not experiment_dir.is_dir():
            raise FileNotFoundError(experiment_dir)
        files.extend(path for path in experiment_dir.rglob("*") if path.is_file())

    archive_file.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_file, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(MANIFEST_FILE, tomli_w.dumps(manifest))
        for source_file in files:
            archive.write(source_file, source_file.relative_to(project_path).as_posix())


def load_profile(archive_path: str | Path, project_path: str | Path):
    """Create a new project from a saved profile ZIP file."""
    archive_file = Path(archive_path).resolve()
    target_path = Path(project_path).resolve()

    if target_path.exists():
        raise FileExistsError(target_path)

    manifest = _read_manifest(archive_file)
    allowed_files = {MANIFEST_FILE, manifest["config_file"]}

    with ZipFile(archive_file) as archive:
        for item in archive.infolist():
            path = PurePosixPath(item.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Unsafe path in profile: {item.filename}")
            if not path.parts or (item.filename not in allowed_files and path.parts[0] != "configs"):
                raise ValueError(f"Unexpected file in profile: {item.filename}")

        target_path.mkdir(parents=True)
        for item in archive.infolist():
            if item.filename != MANIFEST_FILE:
                archive.extract(item, target_path)

    for directory in PROJECT_TREE:
        (target_path / directory).mkdir(parents=True, exist_ok=True)

    if manifest["experiment"] != "common":
        (target_path / "configs/experiments" / manifest["experiment"] / "scheduler").mkdir(parents=True, exist_ok=True)


def get_global_profile_path(name: str) -> Path:
    """Return the ZIP path for one global profile name."""
    return _global_profile_path(name)


def remove_global_profile(name: str):
    """Remove one profile from the local configuration library."""
    get_global_profile_path(name).unlink()


def list_profiles() -> list[ProfileInfo]:
    """List profiles stored in the local configuration library."""
    profile_dir = Path(user_config_dir("wrfrun")) / "profiles"
    if not profile_dir.is_dir():
        return []

    profiles = []
    for archive_path in sorted(profile_dir.glob("*.zip")):
        manifest = _read_manifest(archive_path)
        profiles.append(
            ProfileInfo(
                name=archive_path.stem,
                experiment=manifest["experiment"],
                models=tuple(manifest["models"]),
                created_at=manifest["created_at"],
            )
        )

    return profiles


__all__ = [
    "ProfileInfo",
    "get_global_profile_path",
    "list_profiles",
    "load_profile",
    "remove_global_profile",
    "save_profile",
]
