class WRFRunBasicError(Exception):
    """
    Basic error type.
    """
    pass


class ConfigError(WRFRunBasicError):
    """
    Config cannot be used error.
    """
    pass


class WRFRunContextError(WRFRunBasicError):
    """
    Need to enter wrfrun context.
    """
    pass


class CommandError(WRFRunBasicError):
    """
    The command is wrong.
    """
    pass


class LoadConfigError(WRFRunBasicError):
    """
    Failed to load config.
    """
    pass


class OutputError(WRFRunBasicError):
    """
    No output found.
    """
    pass


__all__ = ["WRFRunBasicError", "ConfigError", "WRFRunContextError", "CommandError", "LoadConfigError", "OutputError"]
