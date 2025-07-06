from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Log, Static, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from rich.markdown import Markdown
from core.registry import list_registered_modules, component_registry
from config.yaml_parser import load_and_validate_config
from core.factory import load_class_from_key, LLM_CLASSES
from core.logger import setup_logger
from plugins.plugin_manager import discover_plugins
import logging
import datetime
import json
import os

logger = setup_logger()

class NameInputDialog(ModalScreen):
    def __init__(self, title, callback):
        super().__init__()
        self.title = title
        self.callback = callback

    def compose(self):
        yield Static(self.title)
        yield Input(placeholder="Nome", id="name_input")
        yield Button("Crea", id="create_btn")
        yield Button("Annulla", id="cancel_btn")

    def on_button_pressed(self, event):
        if event.button.id == "create_btn":
            name = self.query_one("#name_input", Input).value.strip()
            if name:
                self.dismiss()
                self.callback(name)
        elif event.button.id == "cancel_btn":
            self.dismiss()

class Modular2TUI(App):
    CSS_PATH = None
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("f1", "help", "Help"),
        ("f2", "show_agents", "Agents"),
        ("f3", "show_tools", "Tools"),
        ("f4", "show_plugins", "Plugins"),
        ("f5", "show_config", "Config"),
        ("f6", "show_log", "Log"),
        ("f7", "show_history", "History"),
        ("f8", "upload_file", "Upload"),
    ]
    session_log = []
    session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_content = None
    selected_llm = None
    history = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Home"):
                yield self._main_panel()
            with TabPane("Agents"):
                yield self._agents_panel()
            with TabPane("Tools"):
                yield self._tools_panel()
            with TabPane("Plugins"):
                yield self._plugins_panel()
            with TabPane("Config"):
                yield self._config_panel()
            with TabPane("Log"):
                yield self._log_panel()
            with TabPane("History"):
                yield self._history_panel()
        yield Input(placeholder="Scrivi un prompt o un comando...", id="input")
        yield Footer()

    def _main_panel(self):
        panel = Vertical(
            Button("Avvia pipeline YAML", id="run_pipeline_btn"),
            Button("Cambia tema (dark/light)", id="toggle_theme_btn"),
            Log(id="output_home")
        )
        return panel
    def _agents_panel(self):
        panel = Vertical(
            Button("Crea nuovo agente", id="create_agent_btn"),
            Log(id="output_agents")
        )
        return panel
    def _tools_panel(self):
        panel = Vertical(
            Button("Crea nuovo tool", id="create_tool_btn"),
            Log(id="output_tools")
        )
        return panel
    def _plugins_panel(self):
        panel = Vertical(
            Button("Crea nuovo plugin", id="create_plugin_btn"),
            Log(id="output_plugins")
        )
        return panel
    def _config_panel(self):
        panel = Vertical(
            Button("Quickstart pipeline YAML", id="quickstart_btn"),
            Log(id="output_config")
        )
        return panel
    def _log_panel(self):
        return Log(id="output_log")
    def _history_panel(self):
        return Log(id="output_history")

    def on_mount(self):
        self.title = "modular-2 | AI Coding Framework"
        self.query_one("#output_home", Log).write(f"[b cyan]Benvenuto in modular-2![/b cyan] Sessione: {self.session_id} | Premi F1 per help.")
        self.show_help()
        self.refresh_all_tabs()
        # Focus automatico sull'input
        self.query_one("#input", Input).focus()
        self.set_interval(1, self.refresh_log_tab)

    def refresh_log_tab(self):
        self.show_log()

    def refresh_all_tabs(self):
        self.show_agents()
        self.show_tools()
        self.show_plugins()
        self.show_config()
        self.show_log()
        self.show_history()

    def show_help(self):
        self.query_one("#output_home", Log).write("""[b]Comandi:[/b] /help, /exit, /clear, /list, /config, /log, /history, /llm <nome>, /upload, /save, /replay, /scaffold agent|tool|plugin Nome, /quickstart, /run_pipeline NomePipeline\nScorciatoie: F2=Agents, F3=Tools, F4=Plugins, F5=Config, F6=Log, F7=History, F8=Upload""")

    def show_agents(self):
        agents = list_registered_modules().get('agents', [])
        self.query_one("#output_agents", Log).clear()
        self.query_one("#output_agents", Log).write("[b]Agents:[/b] " + (", ".join(agents) if agents else "Nessuno"))
        self.query_one("#output_agents", Log).write("[dim]Premi il pulsante sopra o usa /scaffold agent Nome per crearne uno nuovo.[/dim]")
    def show_tools(self):
        tools = list_registered_modules().get('tools', [])
        self.query_one("#output_tools", Log).clear()
        self.query_one("#output_tools", Log).write("[b]Tools:[/b] " + (", ".join(tools) if tools else "Nessuno"))
        self.query_one("#output_tools", Log).write("[dim]Premi il pulsante sopra o usa /scaffold tool Nome per crearne uno nuovo.[/dim]")
    def show_plugins(self):
        plugins = list_registered_modules().get('plugins', [])
        self.query_one("#output_plugins", Log).clear()
        self.query_one("#output_plugins", Log).write("[b]Plugins:[/b] " + (", ".join(plugins) if plugins else "Nessuno"))
        self.query_one("#output_plugins", Log).write("[dim]Premi il pulsante sopra o usa /scaffold plugin Nome per crearne uno nuovo.[/dim]")
    def show_config(self):
        try:
            with open("config.yaml") as f:
                self.query_one("#output_config", Log).clear()
                self.query_one("#output_config", Log).write(f.read())
        except Exception:
            self.query_one("#output_config", Log).write("[yellow]Nessun config.yaml trovato.[/yellow]")

    def show_log(self):
        try:
            with open("logfile.log") as f:
                self.query_one("#output_log", Log).clear()
                self.query_one("#output_log", Log).write(f.read())
        except FileNotFoundError:
            self.query_one("#output_log", Log).write("[yellow]Nessun file di log trovato.[/yellow]")

    def show_history(self):
        self.query_one("#output_history", Log).clear()
        if self.history:
            self.query_one("#output_history", Log).write("[b]Cronologia prompt:[/b]\n" + "\n".join(self.history))
        else:
            self.query_one("#output_history", Log).write("[yellow]Nessuna cronologia disponibile.[/yellow]")
        self.query_one("#output_history", Log).write("[dim]Usa /history o scorciatoia F7 per accedere rapidamente.\nPremi su un prompt per riutilizzarlo.[/dim]")

    def on_button_pressed(self, event):
        if event.button.id == "help_btn":
            self.show_help()
        elif event.button.id == "agents_btn":
            self.list_agents()
        elif event.button.id == "tools_btn":
            self.list_tools()
        elif event.button.id == "plugins_btn":
            self.list_plugins()
        elif event.button.id == "config_btn":
            self.show_config()
        elif event.button.id == "log_btn":
            self.show_log()
        elif event.button.id == "history_btn":
            self.show_history()
        elif event.button.id == "upload_btn":
            self.upload_file()
        elif event.button.id == "create_agent_btn":
            self.push_screen(NameInputDialog("Nome nuovo agente", self.create_agent))
        elif event.button.id == "create_tool_btn":
            self.push_screen(NameInputDialog("Nome nuovo tool", self.create_tool))
        elif event.button.id == "create_plugin_btn":
            self.push_screen(NameInputDialog("Nome nuovo plugin", self.create_plugin))
        elif event.button.id == "quickstart_btn":
            self.quickstart_yaml()
        elif event.button.id == "run_pipeline_btn":
            self.run_pipeline_dialog()
        elif event.button.id == "toggle_theme_btn":
            self.toggle_theme()

    def on_input_submitted(self, event):
        text = event.value.strip()
        output = self.query_one("#output_home", Log)
        if text.startswith("/"):
            if text == "/help":
                self.show_help()
            elif text == "/exit":
                self.exit()
            elif text == "/clear":
                output.clear()
            elif text == "/list":
                self.list_all()
            elif text == "/config":
                self.show_config()
            elif text == "/log":
                self.show_log()
            elif text == "/history":
                self.show_history()
            elif text.startswith("/llm"):
                parts = text.split()
                if len(parts) == 2:
                    self.selected_llm = parts[1]
                    output.write(f"[cyan]Provider LLM selezionato:[/cyan] {self.selected_llm}")
                else:
                    output.write("[yellow]Usa: /llm <nome_provider> (es. /llm openai)[/yellow]")
            elif text == "/upload":
                self.upload_file()
            elif text == "/save":
                self.save_session()
            elif text == "/replay":
                self.replay_session()
            elif text == "/plugins":
                self.list_plugins()
            elif text.startswith("/plugin "):
                # Invocazione plugin: /plugin nome_plugin arg1=val1 arg2=val2
                parts = text.split()
                if len(parts) >= 2:
                    plugin_name = parts[1]
                    args = {}
                    for arg in parts[2:]:
                        if "=" in arg:
                            k, v = arg.split("=", 1)
                            args[k] = v
                    plugin_cls = component_registry.get('plugin', plugin_name)
                    if not plugin_cls:
                        output.write(f"[red]Plugin '{plugin_name}' non trovato.[/red]")
                        return
                    try:
                        plugin = plugin_cls()
                        result = plugin.run(**args)
                        output.write(f"[b magenta]Plugin '{plugin_name}':[/b magenta] {result}")
                        self.session_log.append({"plugin": plugin_name, "args": args, "result": result, "timestamp": datetime.datetime.now().isoformat()})
                    except Exception as e:
                        output.write(f"[red]Errore plugin '{plugin_name}': {e}[/red]")
                else:
                    output.write("[yellow]Usa: /plugin <nome> [arg1=val1 ...]")
            elif text.startswith("/scaffold "):
                # /scaffold agent|tool|plugin Nome
                parts = text.split()
                if len(parts) == 3:
                    kind, name = parts[1], parts[2]
                    if kind == "agent":
                        self.create_agent(name)
                    elif kind == "tool":
                        self.create_tool(name)
                    elif kind == "plugin":
                        self.create_plugin(name)
                    else:
                        output.write("[yellow]Usa: /scaffold agent|tool|plugin Nome[/yellow]")
                else:
                    output.write("[yellow]Usa: /scaffold agent|tool|plugin Nome[/yellow]")
            elif text == "/quickstart":
                self.quickstart_yaml()
            elif text.startswith("/run_pipeline"):
                # /run_pipeline NomePipeline
                parts = text.split()
                if len(parts) == 2:
                    self.run_pipeline(parts[1])
                else:
                    output.write("[yellow]Usa: /run_pipeline NomePipeline[/yellow]")
            else:
                output.write(f"[red]Comando sconosciuto:[/red] {text}")
        elif text:
            # Sostituzione variabile file_content
            prompt = text
            if self.file_content:
                prompt = prompt.replace("{file_content}", self.file_content)
            output.write(f"[b green]Prompt:[/b green] {prompt}")
            self.history.append(prompt)
            # --- Invocazione reale LLM/agent ---
            try:
                config = load_and_validate_config()
                llms = getattr(config, 'llms', None)
                llm_cfg = None
                if self.selected_llm and llms:
                    llm_cfg = next((l for l in llms if l.name == self.selected_llm), None)
                if not llm_cfg and llms:
                    llm_cfg = llms[0]
                if not llm_cfg and hasattr(config, 'llm'):
                    llm_cfg = config.llm
                if not llm_cfg:
                    output.write("[red]Nessun provider LLM configurato.[/red]")
                    return
                LLMClass = load_class_from_key(LLM_CLASSES, llm_cfg.provider)
                llm = LLMClass(
                    model=llm_cfg.model,
                    endpoint=str(llm_cfg.endpoint) if llm_cfg.endpoint else None,
                    api_key=llm_cfg.api_key
                )
                response = llm.generate(prompt)
                output.write(f"[b blue]Risposta LLM:[/b blue]\n{response}")
                self.session_log.append({"prompt": prompt, "response": response, "llm": llm_cfg.name or llm_cfg.provider, "timestamp": datetime.datetime.now().isoformat()})
            except Exception as e:
                logger.error(f"❌ Errore LLM/agent: {e}")
                output.write(f"[red]Errore LLM/agent:[/red] {e}")
        event.input.value = ""

    def notify(self, message, color="green"):
        from textual.widgets import Notification
        self.mount(Notification(message, style=f"bold {color}"))

    def upload_file(self):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Seleziona un file", filetypes=[("Tutti i file", "*.*")])
        if not file_path:
            self.query_one("#output", Log).write("[yellow]Nessun file selezionato.[/yellow]")
            return
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".txt" or ext == "":
                with open(file_path, "r") as f:
                    self.file_content = f.read()
            else:
                self.file_content = f"[File {os.path.basename(file_path)} caricato, formato non testuale]"
            self.query_one("#output", Log).write(f"[green]File '{os.path.basename(file_path)}' caricato. Usa {{file_content}} nei prompt.[/green]")
        except Exception as e:
            self.query_one("#output", Log).write(f"[red]Errore nel caricamento file: {e}[/red]")

    def save_session(self):
        fname = f"session_{self.session_id}.json"
        with open(fname, "w") as f:
            json.dump(self.session_log, f, indent=2)
        self.query_one("#output", Log).write(f"[green]Sessione salvata in {fname}[/green]")

    def replay_session(self):
        if not self.session_log:
            self.query_one("#output", Log).write("[yellow]Nessuna sessione da riprodurre.[/yellow]")
            return
        self.query_one("#output", Log).write("[b]Replay sessione:[/b]")
        for entry in self.session_log:
            self.query_one("#output", Log).write(f"[b green]Prompt:[/b green] {entry['prompt']}\n[b blue]Risposta:[/b blue] {entry['response']}")

    def create_agent(self, name):
        fname = f"agents/{name.lower()}_agent.py"
        template = f'''# Agent template: {name}\nclass {name.capitalize()}Agent:\n    def run(self, input):\n        # TODO: implementa la logica\n        return input\n'''
        try:
            os.makedirs("agents", exist_ok=True)
            with open(fname, "w") as f:
                f.write(template)
            self.query_one("#output_agents", Log).write(f"[green]Agent '{fname}' creato.[/green]")
            self.notify(f"Agent '{name}' creato!", color="green")
            self.show_agents()
        except Exception as e:
            self.query_one("#output_agents", Log).write(f"[red]Errore creazione agent: {e}[/red]")
            self.notify(f"Errore creazione agent: {e}", color="red")

    def create_tool(self, name):
        fname = f"tools/{name.lower()}_tool.py"
        template = f'''# Tool template: {name}\nclass {name.capitalize()}Tool:\n    def run(self, input):\n        # TODO: implementa la logica\n        return input\n'''
        try:
            os.makedirs("tools", exist_ok=True)
            with open(fname, "w") as f:
                f.write(template)
            self.query_one("#output_tools", Log).write(f"[green]Tool '{fname}' creato.[/green]")
            self.notify(f"Tool '{name}' creato!", color="green")
            self.show_tools()
        except Exception as e:
            self.query_one("#output_tools", Log).write(f"[red]Errore creazione tool: {e}[/red]")
            self.notify(f"Errore creazione tool: {e}", color="red")
    def create_plugin(self, name):
        fname = f"plugins/{name.lower()}_plugin.py"
        template = f'''from plugins.plugin_base import PluginBase\n\nclass {name.capitalize()}Plugin(PluginBase):\n    name = "{name.lower()}"\n    description = "Plugin {name}"\n    def run(self, *args, **kwargs):\n        # TODO: implementa la logica\n        return "Hello from {name.capitalize()}Plugin"\n'''
        try:
            os.makedirs("plugins", exist_ok=True)
            with open(fname, "w") as f:
                f.write(template)
            self.query_one("#output_plugins", Log).write(f"[green]Plugin '{fname}' creato.[/green]")
            self.notify(f"Plugin '{name}' creato!", color="green")
            self.show_plugins()
        except Exception as e:
            self.query_one("#output_plugins", Log).write(f"[red]Errore creazione plugin: {e}[/red]")
            self.notify(f"Errore creazione plugin: {e}", color="red")

    def quickstart_yaml(self):
        example = '''llm:\n  provider: ollama\n  model: qwen2.5-coder:latest\n  endpoint: http://localhost:11434\n\ntools:\n  - name: math\n    class_path: tools.math_tool.MathTool\n    config: {}\n\nagents:\n  - name: coder\n    type: simple\n    llm: ollama\n    tools: [math]\n    system_prompt: "Sei un AI coder."\n\npipelines:\n  - name: demo_pipeline\n    chains:\n      - name: main_chain\n        steps:\n          - name: agent_step\n            type: agent\n            component: coder\n            input:\n              prompt: "{user_input}"\n            output: agent_output\n    description: "Pipeline demo con agent."\n'''
        try:
            with open("quickstart.yaml", "w") as f:
                f.write(example)
            self.query_one("#output_config", Log).write("[green]File 'quickstart.yaml' generato.[/green]")
            self.notify("Quickstart YAML generato!", color="green")
        except Exception as e:
            self.query_one("#output_config", Log).write(f"[red]Errore quickstart: {e}[/red]")
            self.notify(f"Errore quickstart: {e}", color="red")

    def run_pipeline_dialog(self):
        class PipelineSelectDialog(ModalScreen):
            def __init__(self, pipelines, callback):
                super().__init__()
                self.pipelines = pipelines
                self.callback = callback
            def compose(self):
                yield Static("Seleziona pipeline da avviare:")
                for p in self.pipelines:
                    yield Button(p, id=f"pipeline_{p}")
                yield Button("Annulla", id="cancel_btn")
            def on_button_pressed(self, event):
                if event.button.id.startswith("pipeline_"):
                    name = event.button.label
                    self.dismiss()
                    self.callback(name)
                elif event.button.id == "cancel_btn":
                    self.dismiss()
        # Carica pipeline da config.yaml
        try:
            from config.yaml_parser import load_and_validate_config
            config = load_and_validate_config()
            pipelines = [p.name for p in getattr(config, 'pipelines', [])]
            if not pipelines:
                self.query_one("#output_home", Log).write("[yellow]Nessuna pipeline definita in config.yaml.[/yellow]")
                return
            self.push_screen(PipelineSelectDialog(pipelines, self.run_pipeline))
        except Exception as e:
            self.query_one("#output_home", Log).write(f"[red]Errore caricamento pipeline: {e}[/red]")
    def run_pipeline(self, pipeline_name):
        try:
            from core.builder import PipelineBuilder
            from config.yaml_parser import load_and_validate_config
            from core.runner import Runner
            import threading
            config = load_and_validate_config()
            pipeline_cfg = next((p for p in getattr(config, 'pipelines', []) if p.name == pipeline_name), None)
            if not pipeline_cfg:
                self.query_one("#output_home", Log).write(f"[red]Pipeline '{pipeline_name}' non trovata.[/red]")
                return
            builder = PipelineBuilder(pipeline_cfg)
            chains = builder.build()
            first_chain = pipeline_cfg.chains[0].name if pipeline_cfg.chains else None
            if not first_chain or first_chain not in chains:
                self.query_one("#output_home", Log).write(f"[red]Nessuna chain valida nella pipeline.[/red]")
                return
            runner = Runner(chains[first_chain])
            def run_and_update():
                try:
                    result = runner.run({"user_input": "Test pipeline dalla TUI"})
                    self.query_one("#output_home", Log).write(f"[green]Pipeline '{pipeline_name}' eseguita. Risultato:[/green]\n{result}")
                    self.notify(f"Pipeline '{pipeline_name}' eseguita!", color="green")
                except Exception as e:
                    self.query_one("#output_home", Log).write(f"[red]Errore esecuzione pipeline: {e}[/red]")
                    self.notify(f"Errore pipeline: {e}", color="red")
            threading.Thread(target=run_and_update, daemon=True).start()
        except Exception as e:
            self.query_one("#output_home", Log).write(f"[red]Errore esecuzione pipeline: {e}[/red]")
            self.notify(f"Errore pipeline: {e}", color="red")

    def toggle_theme(self):
        # Cambia tema tra dark e light (placeholder, da estendere con CSS personalizzato)
        if getattr(self, "_theme", "dark") == "dark":
            self.dark = False
            self._theme = "light"
            self.query_one("#output_home", Log).write("[cyan]Tema chiaro attivato.[/cyan]")
        else:
            self.dark = True
            self._theme = "dark"
            self.query_one("#output_home", Log).write("[cyan]Tema scuro attivato.[/cyan]")
