"""
main.py - Entrypoint principale del framework modular-2

- Avvia la CLI/chat loop e la pipeline principale.
- Carica la configurazione YAML e orchestra l'esecuzione tramite i moduli core.
- Tutta la logica di orchestrazione, logging e tracing parte da qui.

Consulta la documentazione inline nei moduli core per dettagli su builder, runner, registry, ecc.
"""

import logging
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from core.config_validator import validate_config
from core.factory import load_class_from_key, LLM_CLASSES
from core.document_loaders import FileDocumentLoader
from managers.agent_manager import create_agents
from core.registry import component_registry

try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# All'avvio, auto-discover e registra i plugin
component_registry.discover_and_register_plugins()

logger = logging.getLogger("modular-2")  # Logger centralizzato

def main():
    logger.debug("🔧 Avvio funzione main()")

    # 1. Validazione configurazione
    try:
        config = validate_config()
        logger.info("✅ Configurazione YAML caricata correttamente.")
        logger.debug(f"📦 Configurazione: {config}")
    except Exception as e:
        logger.critical(f"❌ Errore critico nella validazione della configurazione: {e}", exc_info=True)
        return

    # 2. Creazione LLM (multi-provider)
    llms = getattr(config, 'llms', None)
    llm_cfg = None
    llm = None
    if llms:
        # Se ci sono più provider, scegli il primo come default (o implementa selezione dinamica)
        llm_cfg = llms[0]
        logger.info(f"🔍 Multi-provider LLM: {[l.provider for l in llms]}")
    elif hasattr(config, 'llm') and config.llm:
        llm_cfg = config.llm
        logger.info(f"🔍 LLM config: provider={llm_cfg.provider}, model={llm_cfg.model}")
    else:
        logger.error("❌ Nessun provider LLM configurato.")
        return
    try:
        LLMClass = load_class_from_key(LLM_CLASSES, llm_cfg.provider)
        llm = LLMClass(
            model=llm_cfg.model,
            endpoint=str(llm_cfg.endpoint) if llm_cfg.endpoint else None,
            api_key=llm_cfg.api_key
        )
        logger.info(f"🧠 LLM '{llm_cfg.provider}' inizializzato correttamente.")
    except Exception as e:
        logger.error(f"❌ Errore nella creazione del LLM: {e}", exc_info=True)
        return

    # 3. Creazione agenti (opzionale)
    agents = create_agents(config.agents, llm) if config.agents else []
    if not agents:
        logger.warning("⚠️ Nessun agente configurato. Uso diretto del LLM.")
    else:
        logger.info(f"👥 {len(agents)} agente/i inizializzati.")
        logger.debug(f"👥 Dettagli agenti: {[a.name for a in agents]}")

    # 4. Chat loop streaming classica
    file_content = None  # Variabile globale per il contesto file caricato
    try:
        while True:
            try:
                prompt = input("📝 Inserisci il prompt: ")
            except KeyboardInterrupt:
                print("\n👋 Chat terminata.")
                break
            if prompt.strip().startswith("/upload"):
                # --- FILE PICKER ---
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(title="Seleziona un file", filetypes=[("Tutti i file", "*.*")])
                if not file_path:
                    print("❌ Nessun file selezionato.")
                    continue
                ext = os.path.splitext(file_path)[1].lower()
                try:
                    if ext == ".pdf" and PDF_SUPPORT:
                        with open(file_path, "rb") as f:
                            reader = PdfReader(f)
                            file_content = "\n".join(page.extract_text() or "" for page in reader.pages)
                    elif ext == ".txt" or ext == "":
                        file_content = FileDocumentLoader().load(file_path)
                    else:
                        print(f"❌ Formato file non supportato: {ext}")
                        continue
                    print(f"✅ File '{os.path.basename(file_path)}' caricato. Variabile {{file_content}} aggiornata.")
                except Exception as e:
                    print(f"❌ Errore nel caricamento file: {e}")
                continue
            # --- SOSTITUZIONE VARIABILE file_content NEL PROMPT ---
            prompt_with_file = prompt
            if file_content is not None:
                prompt_with_file = prompt_with_file.replace("{file_content}", file_content)
            if agents:
                for agent in agents:
                    logger.info(f"🤖 Esecuzione agente: {agent.name}")
                    try:
                        output = agent.run(prompt_with_file)
                        print(f"\n🧠 {agent.name}:\n{output}")
                    except Exception as e:
                        logger.error(f"❌ Errore nell'esecuzione dell'agente '{agent.name}': {e}", exc_info=True)
            else:
                try:
                    if hasattr(llm, "stream_generate"):
                        print("🧠 Risposta (stream):\n", end="", flush=True)
                        full_response = ""
                        for chunk in llm.stream_generate(prompt_with_file):
                            # --- INIZIO: ricezione di un chunk dal modello ---
                            start = len(full_response)
                            full_response += chunk
                            new_text = full_response[start:]
                            # --- FINE: ricezione di un chunk dal modello ---
                            # --- INIZIO: stampa carattere per carattere con delay per effetto "umano" ---
                            for char in new_text:
                                print(char, end="", flush=True)
                                time.sleep(0.015)  # Delay per effetto "umano"
                            # --- FINE: stampa carattere per carattere con delay ---
                        print()  # Vai a capo alla fine
                    else:
                        output = llm.generate(prompt_with_file)
                        print("🧠 Risposta:\n", output)
                except Exception as e:
                    logger.error(f"❌ Errore durante la generazione del LLM: {e}", exc_info=True)
    except KeyboardInterrupt:
        print("\n👋 Chat terminata.")
        logger.info("⛔ Chat terminata dall'utente.")

    # TODO: Orchestrazione avanzata:
    # - Parsing chain/agent/tool da YAML
    # - Integrazione PipelineBuilder/Runner
    # - Supporto memory, retrievers, evaluators, output parsers
    # - Esecuzione chain step-by-step
