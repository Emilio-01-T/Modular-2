from plugins.plugin_base import PluginBase

class ExamplePlugin(PluginBase):
    name = "example"
    description = "An example plugin for modular-2."

    def run(self, *args, **kwargs):
        print("ExamplePlugin is running!")
        return "Hello from ExamplePlugin!"
