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


class OutputFileError(WRFRunBasicError):
    """
    No output found.
    """
    pass


class ResourceURIError(WRFRunBasicError):
    """
    Error about resource namespace.
    """
    pass


class InputFileError(WRFRunBasicError):
    """
    Input file error.
    """
    pass


__all__ = ["WRFRunBasicError", "ConfigError", "WRFRunContextError", "CommandError", "LoadConfigError", "OutputFileError", "ResourceURIError", "InputFileError"]
