"""
wrfrun.core.runtime.workspace
#############################

Workspace service.

.. autosummary::
    :toctree: generated/


"""

import logging
from typing import Callable

from .io import IOService
from .resource import ResourceCatalog

LOGGER = logging.getLogger("wrfrun")


class WorkspaceService:
    def __init__(self, resource: ResourceCatalog) -> None:
        self._resource = resource

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
