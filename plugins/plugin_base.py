class PluginBase:
    """
    Base class for all plugins in modular-2.
    Plugins should inherit from this class and implement the required methods.
    """
    name = "base"
    description = "Base plugin class."

    def activate(self, **kwargs):
        """Activate the plugin (optional)."""
        pass

    def deactivate(self, **kwargs):
        """Deactivate the plugin (optional)."""
        pass

    def run(self, *args, **kwargs):
        """Main entry point for the plugin."""
        raise NotImplementedError("Plugin must implement the run method.")
