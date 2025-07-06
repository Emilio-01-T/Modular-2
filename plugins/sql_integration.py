from plugins.plugin_base import PluginBase
import logging
logger = logging.getLogger("modular-2")

class SQLIntegrationPlugin(PluginBase):
    name = "sql_integration"
    description = "Esempio di integrazione SQL come plugin."

    def run(self, query, conn):
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"[Plugin] SQL error: {e}")
            return None
