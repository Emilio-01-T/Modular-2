"""
agent_manager.py - Gestione avanzata di agenti e orchestrazione multi-agent

- Permette di gestire, avviare e coordinare più agenti in una pipeline.
- Supporta logica di scheduling, assegnazione task, monitoraggio stato agenti.
- Utile per pipeline multi-agent, workflow distribuiti o scenari complessi.

Consulta la documentazione inline per dettagli su come estendere la logica di agent management.
"""

from core.factory import load_class_from_key, AGENT_CLASSES
import logging

logger = logging.getLogger(__name__)

def create_agents(agent_configs, llm):
    agents = []

    for cfg in agent_configs:
        logger.debug(f"🔧 Creazione agente: {cfg.name} (type={cfg.type})")
        try:
            AgentClass = load_class_from_key(AGENT_CLASSES, cfg.type)
        except Exception as e:
            logger.error(f"❌ Tipo agente non supportato '{cfg.type}': {e}")
            continue

        tools = []
        for tool_path in cfg.tools:
            logger.debug(f"🔍 Caricamento tool '{tool_path}'")
            try:
                module, cls = tool_path.rsplit(".", 1)
                mod = __import__(module, fromlist=[cls])
                ToolClass = getattr(mod, cls)
                tools.append(ToolClass())
                logger.debug(f"✅ Tool '{cls}' caricato correttamente.")
            except Exception as e:
                logger.warning(f"⚠️ Tool '{tool_path}' non caricato: {e}")

        agent = AgentClass(llm=llm, tools=tools, name=cfg.name)
        agents.append(agent)
        logger.info(f"🤖 Agente '{cfg.name}' creato con {len(tools)} tool(s).")

    logger.info(f"✅ Totale agenti creati: {len(agents)}")
    return agents
