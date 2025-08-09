"""
wrfrun.core.error
#################

This module defines all exceptions used in ``wrfrun``.

.. autosummary::
    :toctree: generated/

    WRFRunBasicError
    ConfigError
    WRFRunContextError
    CommandError
    OutputFileError
    ResourceURIError
    InputFileError
    NamelistError
    NamelistIDError
    ExecRegisterError
    GetExecClassError
    ModelNameError
"""


class WRFRunBasicError(Exception):
    """
    Basic exception class of ``wrfrun``. New exception **MUST** inherit this class.
    """
    pass


class ConfigError(WRFRunBasicError):
    """
    Exception indicates the config of ``wrfrun`` or NWP model can't be used.
    """
    pass


class WRFRunContextError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` is running out of the ``wrfrun`` context.
    """
    pass


class CommandError(WRFRunBasicError):
    """
    Exception indicates the command of ``Executable`` can't be executed successfully.
    """
    pass


class OutputFileError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't find any output files with the given rules.
    """
    pass


class ResourceURIError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't parse the URI.
    """
    pass


class InputFileError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't find specified input files.
    """
    pass


class NamelistError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't find the namelist user want to use.
    """
    pass


class NamelistIDError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't register the specified namelist id.
    """
    pass


class ExecRegisterError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't register the specified ``Executable``.
    """
    pass


class GetExecClassError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't find the specified ``Executable``.
    """
    pass


class ModelNameError(WRFRunBasicError):
    """
    Exception indicates ``wrfrun`` can't find config of the specified NWP model in the config file.
    """
    pass


__all__ = ["WRFRunBasicError", "ConfigError", "WRFRunContextError", "CommandError", "OutputFileError", "ResourceURIError", "InputFileError",
           "NamelistError", "ExecRegisterError", "GetExecClassError", "ModelNameError", "NamelistIDError"]
