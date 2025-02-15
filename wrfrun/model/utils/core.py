from os import listdir, makedirs
from os.path import basename, exists
from shutil import copyfile, move
from typing import Tuple, Union, List, Iterable

from wrfrun.utils import logger

REGISTERED_CUSTOM_FILES = {}


def register_custom_files(file_path: Union[str, List[str]], exec_name: str):
    """
    Register custom files which will be used during simulating.

    :param file_path: Custom files' path.
    :type file_path: str | list[str]
    :param exec_name: The name of the executable, valid values: ``["geogrid", "ungrib", "metgrid", "real", "wrf", "dfi"]``.
    :type exec_name: str
    :return:
    :rtype:
    """
    global REGISTERED_CUSTOM_FILES

    if isinstance(file_path, str):
        file_path = [file_path, ]

    if exec_name in REGISTERED_CUSTOM_FILES:
        logger.debug(f"Found registered files of {exec_name}, merge them")
        values = REGISTERED_CUSTOM_FILES[exec_name]
        values = list(set(values + file_path))
        REGISTERED_CUSTOM_FILES[exec_name] = values
    else:
        logger.debug(f"Register files: {file_path} for {exec_name}")
        REGISTERED_CUSTOM_FILES[exec_name] = file_path


def model_preprocess(exec_name: str, work_path: str):
    """
    Do all things that should be done before call model part.
    This function will copy the custom necessary files to the workspace.
    
    :param exec_name: The name of the executable, valid values: ``["geogrid", "ungrib", "metgrid", "real", "wrf", "dfi"]``.
    :type exec_name: str
    :param work_path: Work path of the ``exec_name``.
    :type work_path: str
    :return:
    :rtype:
    """
    global REGISTERED_CUSTOM_FILES

    # copy registered files
    if exec_name in REGISTERED_CUSTOM_FILES:
        file_list = REGISTERED_CUSTOM_FILES.pop(exec_name)
        logger.debug(f"Found registered file for {exec_name}: {file_list}")
        for _file in file_list:
            filename = basename(_file)
            copyfile(_file, f"{work_path}/{filename}")


def model_postprocess(output_dir: str, save_path: str, startswith: Union[None, str, Tuple[str, ...]] = None, endswith: Union[None, str, Tuple[str, ...]] = None,
                      outputs: Union[None, str, List[str]] = None, copy_only=True):
    """
    Save the results and logs from the model.

    :param output_dir: Output dir path of the model.
    :type output_dir: str
    :param save_path: Save path.
    :type save_path: str
    :param startswith: Prefix string or prefix list of output files.
    :type startswith: None | str | list[str]
    :param endswith: Postfix string or Postfix list of output files.
    :type endswith: None | str | list[str]
    :param outputs: Files name list. All files in the list will be saved.
    :type outputs: None | str | list[str]
    :param copy_only: If ``False``, move the file instead of copying it.
    :type copy_only: bool
    :return:
    :rtype:
    """
    if not exists(save_path):
        makedirs(save_path)

    file_list = listdir(output_dir)
    save_file_list = []

    if startswith is not None:
        _list = []
        for _file in file_list:
            if _file.startswith(startswith):
                _list.append(_file)
        save_file_list += _list
                
        logger.debug(f"Collect files match `startswith`: {_list}")

    if endswith is not None:
        _list = []
        for _file in file_list:
            if _file.endswith(endswith):
                _list.append(_file)
        save_file_list += _list
                
        logger.debug(f"Collect files match `endswith`: {_list}")

    if outputs is not None:
        if isinstance(outputs, str) and outputs in file_list:
            save_file_list.append(outputs)
        else:
            outputs = [x for x in outputs if x in file_list]
            save_file_list += outputs

    if len(save_file_list) < 1:
        return

    save_file_list = list(set(save_file_list))
    logger.debug(f"Files to be processed: {save_file_list}")

    for _file in save_file_list:
        if copy_only:
            copyfile(f"{output_dir}/{_file}", f"{save_path}/{_file}")
        else:
            move(f"{output_dir}/{_file}", f"{save_path}/{_file}")


__all__ = ["register_custom_files", "model_preprocess", "model_postprocess"]
