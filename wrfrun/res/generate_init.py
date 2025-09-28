import argparse
from json import loads
from os import listdir
from os.path import dirname, exists
from typing import Union

HEADER_CODE = """from os.path import abspath, dirname

from wrfrun.core import WRFRUNConfig


RES_PATH = abspath(dirname(__file__))
WRFRUNConfig.register_resource_uri(WRFRUNConfig.WRFRUN_RESOURCE_PATH, RES_PATH)

"""

FOOT_CODE = """\nWRFRUNConfig.set_config_template_path(CONFIG_MAIN_TOML_TEMPLATE)\n"""


def _generate_init():
    parser = argparse.ArgumentParser(description="Generate __init__.py")
    parser.add_argument("--output", "-o", help="Absolute or relative path to '__init__.py'.", required=True)
    args = vars(parser.parse_args())

    target_file_path = args["output"]
    target_dir_path = dirname(target_file_path)

    total_name_list = []
    total_path_list = []
    file_name_list, file_path_list, dir_name_list, dir_path_list = _generate_name_list_in_dir(target_dir_path, "")
    total_name_list += file_name_list
    total_path_list += file_path_list

    while len(dir_name_list) > 0:
        file_name_list, file_path_list, dir_name_list, dir_path_list = _generate_name_list_in_dir(dir_path_list, dir_name_list)
        total_name_list += file_name_list
        total_path_list += file_path_list

    total_path_list = [f":WRFRUN_RESOURCE_PATH:/{x[len(target_dir_path) + 1:]}" for x in total_path_list]

    with open(target_file_path, "w") as f:
        f.write(HEADER_CODE)

        all_string = ""
        for _var_name, _file_path in zip(total_name_list, total_path_list):
            f.write(f"{_var_name} = \"{_file_path}\"\n")
            all_string += f', "{_var_name}"'

        f.write(FOOT_CODE)

        all_string = all_string.strip(", ")

        f.write(f'\n\n__all__ = [{all_string}]\n')


def _generate_name_list_in_dir(dir_path: Union[str, list[str]], dir_name: Union[str, list[str]], root=False) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Generate a variable name list for the target path.

    :param dir_path:
    :type dir_path:
    :param dir_name:
    :type dir_name:
    :param root: Root path?
    :type root: bool
    :return: (file_name_list, file_path_list, dir_name_list, dir_path_list).
    :rtype: tuple
    """
    if isinstance(dir_path, str):
        dir_path = [dir_path, ]
        dir_name = [dir_name, ]

    file_name_list = []
    file_path_list = []
    dir_name_list = []
    dir_path_list = []

    for _dir_path, _dir_name in zip(dir_path, dir_name):
        if not exists(f"{_dir_path}/name_map.json"):
            raise FileNotFoundError(f"{_dir_path}/name_map.json. Files: {listdir(_dir_path)}")

        with open(f"{_dir_path}/name_map.json", "r") as f:
            name_map_dict: dict[str, dict[str, str]] = loads(f.read())

        for file, config in name_map_dict.items():
            name = config["name"]
            file_type = config["type"]

            var_name = f"{_dir_name}_{name}"
            var_name = var_name.strip("_")

            if root:
                _path = f":WRFRUN_RESOURCE_PATH:/{file}"
            else:
                _path = f"{_dir_path}/{file}"

            if file_type == "dir":
                dir_name_list.append(var_name)
                dir_path_list.append(_path)

            else:
                file_name_list.append(var_name)
                file_path_list.append(_path)

    return file_name_list, file_path_list, dir_name_list, dir_path_list


_generate_init()
