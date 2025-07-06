import importlib
import os
import sys
from plugins.plugin_base import PluginBase

def discover_plugins(plugins_dir="plugins"):
    """
    Auto-discover and import all plugins in the plugins/ directory.
    Returns a dict {plugin_name: plugin_class}.
    """
    plugins = {}
    plugins_path = os.path.abspath(plugins_dir)
    sys.path.insert(0, plugins_path)
    for fname in os.listdir(plugins_path):
        if fname.endswith(".py") and not fname.startswith("_") and fname != "plugin_base.py":
            mod_name = fname[:-3]
            mod = importlib.import_module(mod_name)
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                    plugins[obj.name] = obj
    sys.path.pop(0)
    return plugins
