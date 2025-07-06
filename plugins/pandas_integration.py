from plugins.plugin_base import PluginBase
import logging
logger = logging.getLogger("modular-2")

class PandasIntegrationPlugin(PluginBase):
    name = "pandas_integration"
    description = "Esempio di integrazione con Pandas come plugin."

    def run(self, code, df=None):
        import pandas as pd
        try:
            local_vars = {'df': df, 'pd': pd}
            exec(code, {}, local_vars)
            return local_vars.get('df', None)
        except Exception as e:
            logger.error(f"[Plugin] Pandas error: {e}")
            return None
