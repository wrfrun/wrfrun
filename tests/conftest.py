from dataclasses import dataclass
from pathlib import Path

import pytest

from wrfrun.core.runtime.io import IOService
from wrfrun.core.runtime.resource import ResourceCatalog


@dataclass
class RuntimeFixture:
    project: Path
    resource: ResourceCatalog
    io: IOService


@pytest.fixture
def runtime(tmp_path: Path) -> RuntimeFixture:
    project = tmp_path / "project"
    resource = ResourceCatalog()
    resource.register_default_providers(project, project / ".wrfrun", "v01", "run-1")
    return RuntimeFixture(project, resource, IOService(resource))
