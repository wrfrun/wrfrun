"""
wrfrun.core.runtime.workspace
#############################

Workspace service.

.. autosummary::
    :toctree: generated/


"""

import logging
import uuid
from pathlib import Path
from shutil import move, rmtree
from typing import Callable

from ..error import WorkspaceResetError
from .io import IOService
from .resource import ResourceCatalog

LOGGER = logging.getLogger("wrfrun")


class WorkspaceService:
    """
    Workspace service.
    """

    def __init__(self, resource: ResourceCatalog, io: IOService) -> None:
        """
        Workspace service.

        :param resource: Resource manager.
        :type resource: ResourceCatalog
        """
        self._resource = resource
        self._io = io
        self._workspace_uuid = str(uuid.uuid1())
        self._work_path: Path | None = None

        self._workspace_init_func_map: dict[str, Callable] = {}
        self._workspace_check_func_map: dict[str, Callable[[], bool]] = {}

    def register_init_func(self, model_name: str, func: Callable):
        """
        Register a init function.

        :param model_name: Model name.
        :type model_name: str
        :param func: Init function.
        :type func: Callable
        :raises KeyError: Model name has been registered.
        """
        if model_name in self._workspace_init_func_map:
            message = f"Workspace init function has been registered for model '{model_name}'"
            LOGGER.error(message)
            raise KeyError(message)

        self._workspace_init_func_map.update({model_name: func})

    def check_init_func(self, model_name: str) -> bool:
        """
        Check if the init workspace of a model has been registered.

        :param model_name: Model name.
        :type model_name: str
        :return: True if is registered, else False.
        :rtype: bool
        """
        if model_name in self._workspace_init_func_map:
            return True

        else:
            return False

    def unregister_init_func(self, model_name: str):
        """
        Unregister a init function.

        :param model_name: Model name
        :type model_name: str
        """
        if model_name in self._workspace_init_func_map:
            self._workspace_init_func_map.pop(model_name)

    def register_check_func(self, model_name: str, func: Callable[[], bool]):
        """
        Register a workspace check function.

        :param model_name: Model name.
        :type model_name: str
        :param func: Workspace check function.
        :type func: Callable[[], bool]
        :raises KeyError: Model name has been registered.
        """
        if model_name in self._workspace_check_func_map:
            message = f"Workspace check function has been registered for model '{model_name}'"
            LOGGER.error(message)
            raise KeyError(message)

        self._workspace_check_func_map.update({model_name: func})

    def check_check_func(self, model_name: str) -> bool:
        """
        Check if the workspace check function of a model has been registered.

        :param model_name: Model name.
        :type model_name: str
        :return: True if is registered, else False.
        :rtype: bool
        """
        if model_name in self._workspace_check_func_map:
            return True

        else:
            return False

    def unregister_check_func(self, model_name: str):
        """
        Unregister a workspace check function.

        :param model_name: Model name
        :type model_name: str
        """
        if model_name in self._workspace_check_func_map:
            self._workspace_check_func_map.pop(model_name)

    def set_work_path(self, work_path: str):
        """
        Set work path of current session.

        :param work_path: Work path.
        :type work_path: str
        :raises WorkspaceResetError: Work path is set again after it being set.
        """
        if self._work_path is not None:
            message = f"Work directory is already set to '{self._work_path}', you can't change it again."
            LOGGER.error(message)
            raise WorkspaceResetError(message)

        self._work_path = Path(work_path).resolve()
        self._resource.register_provider("workspace", self._work_path / self._workspace_uuid)

    def init_model_workspace(self, model_name: str):
        """
        Initialize workspace of a model.

        :param model_name: Model name.
        :type model_name: str
        :raises KeyError: Init function not found.
        """
        if model_name in self._workspace_init_func_map:
            self._workspace_init_func_map[model_name]()

        else:
            message = f"Workspace init function of model '{model_name}' not found, use 'register_init_func' register it."
            LOGGER.error(message)
            raise KeyError(message)

    def check_model_workspace(self, model_name: str) -> bool:
        """
        Check workspace of a model.

        :param model_name: Model name.
        :type model_name: str
        :raises KeyError: Check function not found.
        """
        if model_name in self._workspace_check_func_map:
            return self._workspace_init_func_map[model_name]()

        else:
            message = f"Workspace check function of model '{model_name}' not found, use 'register_check_func' register it."
            LOGGER.error(message)
            raise KeyError(message)

    def init_workspace(self):
        """
        Initialize the whole workspace.

        Init function of all loaded model will be called too.
        """
        workspace_backup_path = None
        initialize_success = False

        wrfrun_temp_path = self._resource.get_custom_resource(self._resource.WRFRUN_TEMP_PATH)
        workspace_path = self._resource.get_custom_resource(self._resource.WRFRUN_WORKSPACE_ROOT)
        replay_work_path = self._resource.get_custom_resource(self._resource.WRFRUN_WORKSPACE_REPLAY)
        output_path = self._resource.get_custom_resource(self._resource.OUTPUT_DIR)

        if workspace_path.is_dir():
            LOGGER.info(f"Reinitialize main workspace at: '{workspace_path}'")
            # backup old workspace, so we can restore it if we failed to create new workspace.
            workspace_backup_path = workspace_path.parent / ".workspace_backup"
            move(workspace_path, workspace_backup_path)

        else:
            LOGGER.info(f"Initialize main workspace at: '{workspace_path}'")

        # check folder
        wrfrun_temp_path.mkdir(exist_ok=True, parents=True)
        replay_work_path.mkdir(exist_ok=True, parents=True)
        output_path.mkdir(exist_ok=True, parents=True)

        try:
            for model_name in self._workspace_init_func_map:
                self._workspace_init_func_map[model_name]()

            initialize_success = True

        finally:
            if initialize_success and workspace_backup_path:
                rmtree(workspace_backup_path)

            else:
                LOGGER.warning("Failed to initialize workspace.")

                if workspace_backup_path:
                    rmtree(workspace_path)
                    move(workspace_backup_path, workspace_path)
                    LOGGER.warning("Old workspace restored.")

    def check_workspace(self):
        """
        Check if workspace exists.

        :return: ``True`` if workspace exists, ``False`` otherwise.
        :rtype: bool
        """
        global CHECK_FUNC_MAP

        wrfrun_temp_path = self._resource.get_custom_resource(self._resource.WRFRUN_TEMP_PATH)
        workspace_path = self._resource.get_custom_resource(self._resource.WRFRUN_WORKSPACE_ROOT)
        replay_work_path = self._resource.get_custom_resource(self._resource.WRFRUN_WORKSPACE_REPLAY)
        output_path = self._resource.get_custom_resource(self._resource.OUTPUT_DIR)

        flag = True
        flag = flag & wrfrun_temp_path.is_dir() & replay_work_path.is_dir() & output_path.is_dir() & workspace_path.is_dir()

        for model_name in self._workspace_check_func_map:
            flag = flag & self._workspace_check_func_map[model_name]()

        return flag


__all__ = ["WorkspaceService"]
