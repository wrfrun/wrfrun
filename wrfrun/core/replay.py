from json import loads
from os.path import exists
from shutil import unpack_archive

from .base import ExecutableBase, ExecutableConfig
from .config import WRFRUNConfig
from .error import ExecRegisterError, GetExecClassError
from ..utils import logger

WRFRUN_REPLAY_URI = ":WRFRUN_REPLAY:"


class WRFRunExecutableRegisterCenter:
    """
    Record all executable class.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        if self._initialized:
            return

        self._exec_db = {}

        self._initialized = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def register_exec(self, unique_iq: str, cls: type):
        """
        Register an executable class.

        :param unique_iq: Unique ID.
        :type unique_iq: str
        :param cls: Class.
        :type cls: type
        :return:
        :rtype:
        """
        if unique_iq in self._exec_db:
            logger.error(f"'{unique_iq}' has been registered.")
            raise ExecRegisterError(f"'{unique_iq}' has been registered.")

        self._exec_db[unique_iq] = cls

    def is_registered(self, unique_id: str) -> bool:
        """
        Check if an executable class has been registered.

        :param unique_id: Unique ID.
        :type unique_id: str
        :return: True or False.
        :rtype: bool
        """
        if unique_id in self._exec_db:
            return True
        else:
            return False

    def get_cls(self, unique_id: str) -> type:
        """
        Get a registered executable class.

        :param unique_id: Unique ID.
        :type unique_id: str
        :return: Executable class.
        :rtype: type
        """
        if unique_id not in self._exec_db:
            logger.error(f"Executable class '{unique_id}' not found.")
            raise GetExecClassError(f"Executable class '{unique_id}' not found.")

        return self._exec_db[unique_id]


WRFRUNExecDB = WRFRunExecutableRegisterCenter()


def replay_config_generator(replay_config_file: str):
    """
    Replay the simulations.

    :param replay_config_file: Replay file path.
    :type replay_config_file: str
    :return:
    :rtype:
    """
    logger.info(f"Loading replay resources from: {replay_config_file}")
    work_path = WRFRUNConfig.parse_resource_uri(WRFRUNConfig.WRFRUN_REPLAY_WORK_PATH)

    unpack_archive(replay_config_file, work_path, "zip")

    if not exists(f"{work_path}/config.json"):
        logger.error("Can't find replay config in the provided config file.")
        raise FileNotFoundError("Can't find replay config in the provided config file.")

    with open(f"{work_path}/config.json", "r") as f:
        replay_config_list: list[ExecutableConfig] = loads(f.read())

    for _config in replay_config_list:
        args = _config["class_config"]["class_args"]
        kwargs = _config["class_config"]["class_kwargs"]
        executable: ExecutableBase = WRFRUNExecDB.get_cls(_config["name"])(*args, **kwargs)
        executable.load_config(_config)
        yield _config["name"], executable


__all__ = ["WRFRUNExecDB", "replay_config_generator"]
