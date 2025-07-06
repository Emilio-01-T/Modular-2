import click
import logging
from main import main as run_chat
from core.logger import setup_logger
from core.registry import list_registered_modules, component_registry
from config.yaml_parser import load_and_validate_config
import os
import yaml

@click.group()
def cli():
    """
    modular-2: AI Coding Framework CLI (OpenCode style)
    """
    pass

@cli.command()
def run():
    """Avvia la chat/pipeline interattiva stile opencode."""
    from core.logger import setup_logger
    import datetime
    import json
    import readline
    from config.yaml_parser import load_and_validate_config
    from core.factory import load_class_from_key, LLM_CLASSES
    from core.registry import component_registry
    from plugins.plugin_manager import discover_plugins
    import os

    setup_logger()
    session_log = []
    session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_content = None
    selected_llm = None
    history = []
    click.secho(f"[modular-2] Sessione: {session_id} | /help per comandi rapidi", fg="cyan")
    while True:
        try:
            prompt = input("\n📝 Prompt > ").strip()
        except (KeyboardInterrupt, EOFError):
            click.secho("\n👋 Chat terminata.", fg="yellow")
            break
        if not prompt:
            continue
        if prompt.startswith("/"):
            if prompt == "/help":
                click.secho("\n[HELP] Comandi rapidi:\n"
                    "  /help           Mostra questo help\n"
                    "  /exit           Esci dalla chat\n"
                    "  /clear          Pulisci la schermata\n"
                    "  /history        Mostra la cronologia dei prompt\n"
                    "  /log            Mostra il logfile\n"
                    "  /llm <nome>     Seleziona provider LLM\n"
                    "  /upload         Carica un file e usa {file_content} nei prompt\n"
                    "  /save           Salva la sessione\n"
                    "  /replay         Replay sessione\n"
                    "  /plugins        Elenca i plugin caricati\n"
                    "  /plugin <nome> [arg=val ...]  Esegui un plugin\n", fg="cyan")
            elif prompt == "/exit":
                click.secho("👋 Uscita.", fg="yellow")
                break
            elif prompt == "/clear":
                os.system("clear")
            elif prompt == "/history":
                if history:
                    click.secho("\n".join(history), fg="white")
                else:
                    click.secho("[Nessuna cronologia]", fg="yellow")
            elif prompt == "/log":
                try:
                    with open("logfile.log") as f:
                        click.secho(f.read(), fg="white")
                except FileNotFoundError:
                    click.secho("[LOG] Nessun file di log trovato.", fg="yellow")
            elif prompt.startswith("/llm"):
                parts = prompt.split()
                if len(parts) == 2:
                    selected_llm = parts[1]
                    click.secho(f"[LLM] Provider selezionato: {selected_llm}", fg="cyan")
                else:
                    click.secho("Usa: /llm <nome_provider>", fg="yellow")
            elif prompt == "/upload":
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    file_path = filedialog.askopenfilename(title="Seleziona un file", filetypes=[("Tutti i file", "*.*")])
                    if not file_path:
                        click.secho("[Nessun file selezionato]", fg="yellow")
                        continue
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == ".txt" or ext == "":
                        with open(file_path, "r") as f:
                            file_content = f.read()
                    else:
                        file_content = f"[File {os.path.basename(file_path)} caricato, formato non testuale]"
                    click.secho(f"[File '{os.path.basename(file_path)}' caricato. Usa {{file_content}} nei prompt]", fg="green")
                except Exception as e:
                    click.secho(f"[Errore upload file: {e}]", fg="red")
            elif prompt == "/save":
                fname = f"session_{session_id}.json"
                with open(fname, "w") as f:
                    json.dump(session_log, f, indent=2)
                click.secho(f"[Sessione salvata in {fname}]", fg="green")
            elif prompt == "/replay":
                if not session_log:
                    click.secho("[Nessuna sessione da riprodurre]", fg="yellow")
                    continue
                click.secho("[Replay sessione]", fg="cyan")
                for entry in session_log:
                    click.secho(f"\nPrompt: {entry.get('prompt')}\nRisposta: {entry.get('response')}", fg="white")
            elif prompt == "/plugins":
                plugins = component_registry._registry.get('plugin', {})
                if plugins:
                    click.secho("[PLUGIN] Plugin caricati:", fg="cyan")
                    for name in plugins:
                        click.secho(f"  - {name}", fg="white")
                else:
                    click.secho("[Nessun plugin caricato]", fg="yellow")
            elif prompt.startswith("/plugin "):
                parts = prompt.split()
                if len(parts) >= 2:
                    plugin_name = parts[1]
                    args = {}
                    for arg in parts[2:]:
                        if "=" in arg:
                            k, v = arg.split("=", 1)
                            args[k] = v
                    plugin_cls = component_registry.get('plugin', plugin_name)
                    if not plugin_cls:
                        click.secho(f"[Plugin '{plugin_name}' non trovato]", fg="red")
                        continue
                    try:
                        plugin = plugin_cls()
                        result = plugin.run(**args)
                        click.secho(f"[PLUGIN '{plugin_name}'] {result}", fg="magenta")
                        session_log.append({"plugin": plugin_name, "args": args, "result": result, "timestamp": datetime.datetime.now().isoformat()})
                    except Exception as e:
                        click.secho(f"[Errore plugin '{plugin_name}': {e}]", fg="red")
                else:
                    click.secho("Usa: /plugin <nome> [arg=val ...]", fg="yellow")
            else:
                click.secho(f"[Comando sconosciuto: {prompt}]", fg="red")
            continue
        # Sostituzione variabile file_content
        user_prompt = prompt
        if file_content:
            user_prompt = user_prompt.replace("{file_content}", file_content)
        history.append(user_prompt)
        # --- Invocazione reale LLM/agent ---
        try:
            config = load_and_validate_config()
            llms = getattr(config, 'llms', None)
            llm_cfg = None
            if selected_llm and llms:
                llm_cfg = next((l for l in llms if l.name == selected_llm), None)
            if not llm_cfg and llms:
                llm_cfg = llms[0]
            if not llm_cfg and hasattr(config, 'llm'):
                llm_cfg = config.llm
            if not llm_cfg:
                click.secho("[Nessun provider LLM configurato]", fg="red")
                continue
            LLMClass = load_class_from_key(LLM_CLASSES, llm_cfg.provider)
            llm = LLMClass(
                model=llm_cfg.model,
                endpoint=str(llm_cfg.endpoint) if llm_cfg.endpoint else None,
                api_key=llm_cfg.api_key
            )
            response = llm.generate(user_prompt)
            click.secho(f"\n[LLM] Risposta:\n", fg="blue")
            click.secho(response, fg="white")
            session_log.append({"prompt": user_prompt, "response": response, "llm": llm_cfg.name or llm_cfg.provider, "timestamp": datetime.datetime.now().isoformat()})
        except Exception as e:
            click.secho(f"[Errore LLM/agent: {e}]", fg="red")

@cli.command()
def init():
    """Inizializza un nuovo progetto modular-2 (scaffold config, agent, tool, ecc)."""
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w") as f:
            f.write("llm:\n  provider: ollama\n  model: qwen2.5-coder:latest\n")
        click.secho("[INIT] File config.yaml creato.", fg="green")
    else:
        click.secho("[INIT] config.yaml già presente.", fg="yellow")

@cli.group()
def agent():
    """Gestione agent (list, scaffold, info)."""
    pass

@agent.command("list")
def agent_list():
    """Elenca tutti gli agent disponibili."""
    mods = list_registered_modules().get('agents', [])
    click.secho("[AGENT] Agents disponibili:", fg="cyan")
    for m in mods:
        click.secho(f"  - {m}", fg="white")

@agent.command("scaffold")
@click.argument('name')
def agent_scaffold(name):
    """Crea un nuovo agent da template."""
    fname = f"agents/{name.lower()}_agent.py"
    template = f'''# Agent template: {name}\nclass {name.capitalize()}Agent:\n    def run(self, input):\n        # TODO: implementa la logica\n        return input\n'''
    with open(fname, "w") as f:
        f.write(template)
    click.secho(f"[SCAFFOLD] Agent '{fname}' creato.", fg="green")

@cli.group()
def tool():
    """Gestione tool (list, scaffold, info)."""
    pass

@tool.command("list")
def tool_list():
    mods = list_registered_modules().get('tools', [])
    click.secho("[TOOL] Tools disponibili:", fg="cyan")
    for m in mods:
        click.secho(f"  - {m}", fg="white")

@tool.command("scaffold")
@click.argument('name')
def tool_scaffold(name):
    fname = f"tools/{name.lower()}_tool.py"
    template = f'''# Tool template: {name}\nclass {name.capitalize()}Tool:\n    def run(self, input):\n        # TODO: implementa la logica\n        return input\n'''
    with open(fname, "w") as f:
        f.write(template)
    click.secho(f"[SCAFFOLD] Tool '{fname}' creato.", fg="green")

@cli.group()
def plugin():
    """Gestione plugin (list, scaffold, info)."""
    pass

@plugin.command("list")
def plugin_list():
    plugins = component_registry._registry.get('plugin', {})
    click.secho("[PLUGIN] Plugin caricati:", fg="cyan")
    for name in plugins:
        click.secho(f"  - {name}", fg="white")

@plugin.command("scaffold")
@click.argument('name')
def plugin_scaffold(name):
    fname = f"plugins/{name.lower()}_plugin.py"
    template = f'''from plugins.plugin_base import PluginBase\n\nclass {name.capitalize()}Plugin(PluginBase):\n    name = "{name.lower()}"\n    description = "Plugin {name}"\n    def run(self, *args, **kwargs):\n        # TODO: implementa la logica\n        return "Hello from {name.capitalize()}Plugin"\n'''
    with open(fname, "w") as f:
        f.write(template)
    click.secho(f"[SCAFFOLD] Plugin '{fname}' creato.", fg="green")

@cli.command()
def config():
    """Mostra la configurazione YAML attiva."""
    try:
        with open("config.yaml") as f:
            data = yaml.safe_load(f)
            click.secho(yaml.dump(data, allow_unicode=True), fg="white")
    except Exception as e:
        click.secho(f"[ERRORE] Impossibile leggere config.yaml: {e}", fg="red")

@cli.command()
def status():
    """Mostra lo stato del framework."""
    click.secho("[STATUS] modular-2 attivo.", fg="green")

@cli.command()
def log():
    """Visualizza il contenuto di logfile.log"""
    try:
        with open("logfile.log") as f:
            click.secho(f.read(), fg="white")
    except FileNotFoundError:
        click.secho("[LOG] Nessun file di log trovato.", fg="yellow")

@cli.command()
def quickstart():
    """Genera una pipeline YAML di esempio in 'quickstart.yaml'."""
    example = '''llm:\n  provider: ollama\n  model: qwen2.5-coder:latest\n  endpoint: http://localhost:11434\n\ntools:\n  - name: math\n    class_path: tools.math_tool.MathTool\n    config: {}\n\nagents:\n  - name: coder\n    type: simple\n    llm: ollama\n    tools: [math]\n    system_prompt: "Sei un AI coder."\n\npipelines:\n  - name: demo_pipeline\n    chains:\n      - name: main_chain\n        steps:\n          - name: agent_step\n            type: agent\n            component: coder\n            input:\n              prompt: "{user_input}"\n            output: agent_output\n    description: "Pipeline demo con agent."\n'''
    with open("quickstart.yaml", "w") as f:
        f.write(example)
    click.secho("[QUICKSTART] File 'quickstart.yaml' generato.", fg="green")

@cli.command()
def help():
    """Mostra l'help dettagliato e i comandi disponibili."""
    click.secho("\n[HELP] Comandi principali:", fg="cyan")
    click.secho("  run         Avvia la chat/pipeline", fg="white")
    click.secho("  init        Inizializza progetto", fg="white")
    click.secho("  agent       Gestione agent", fg="white")
    click.secho("  tool        Gestione tool", fg="white")
    click.secho("  plugin      Gestione plugin", fg="white")
    click.secho("  config      Mostra configurazione", fg="white")
    click.secho("  status      Mostra stato", fg="white")
    click.secho("  log         Visualizza log", fg="white")
    click.secho("  quickstart  Genera pipeline di esempio", fg="white")
    click.secho("\nPer sottocomandi: modular-2 agent --help, modular-2 tool --help, modular-2 plugin --help", fg="yellow")

@cli.command()
def tui():
    """Avvia la TUI grafica avanzata (Textual) di modular-2."""
    from tui import Modular2TUI
    Modular2TUI().run()

if __name__ == '__main__':
    cli()
