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


class NamelistError(WRFRunBasicError):
    """
    Error about namelist.
    """
    pass


class ExecRegisterError(WRFRunBasicError):
    pass


class GetExecClassError(WRFRunBasicError):
    pass


class ModelNameError(WRFRunBasicError):
    """
    Name of the model isn't found in the config file.
    """
    pass


__all__ = ["WRFRunBasicError", "ConfigError", "WRFRunContextError", "CommandError", "LoadConfigError", "OutputFileError", "ResourceURIError", "InputFileError",
           "NamelistError", "ExecRegisterError", "GetExecClassError", "ModelNameError"]
