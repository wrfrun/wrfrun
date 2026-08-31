"""
wrfrun.model.plugins
####################

Define model plugin information here.
"""

from importlib import import_module

from wrfrun.core.plugin import PluginProtocol

# Module path of model plugins
PLUGIN_MAP = {
    "wrf": "wrfrun.model.wrf.plugin:WRFPlugin",
    "arps": "wrfrun.model.arps.plugin:ARPSPlugin",
}


def load_model_plugin(model_name: str) -> PluginProtocol:
    """
    Load specified model plugin.

    :param model_name: Model plugin name.
    :type model_name: str
    :raises ValueError: model_name not found in PLUGIN_MAP.
    :raises RuntimeError: Plugin loaded, but its name mismatches model_name.
    :return: Loaded plugin.
    :rtype: PluginProtocol
    """
    try:
        import_path = PLUGIN_MAP[model_name]
    except KeyError as exc:
        supported = ", ".join(sorted(PLUGIN_MAP))
        raise ValueError(f"Unsupported model '{model_name}'. Supported models: {supported}") from exc

    module_name, class_name = import_path.split(":", maxsplit=1)
    module = import_module(module_name)
    plugin_class = getattr(module, class_name)

    plugin = plugin_class()

    if plugin.name != model_name:
        raise RuntimeError(f"Plugin mismatch: config requested '{model_name}', but plugin declares '{plugin.name}'.")

    return plugin


__all__ = ["load_model_plugin"]
