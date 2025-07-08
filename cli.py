"""
CLI interface for modular-2 framework.
Provides command-line interface for running agents and managing the framework.
"""
import click
import logging
import sys
import os
from typing import Dict, Any
from main import ModularFramework
from config.yaml_parser import load_and_validate_config
from core.registry import registry

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """modular-2 Framework CLI - Sistema modulare per AI agents."""
    pass

@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path al file di configurazione')
@click.option('--agent', '-a', help='Nome dell\'agente da usare')
@click.option('--debug', is_flag=True, help='Abilita logging debug')
def run(config, agent, debug):
    """Avvia la chat interattiva con gli agenti."""
    
    # Setup logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🐛 Debug mode abilitato")
    
    try:
        # Initialize framework
        framework = ModularFramework(config)
        
        # Get available agents
        agents = framework.list_agents()
        
        if not agents:
            click.echo("❌ Nessun agente disponibile. Controlla la configurazione.")
            return
        
        # Select agent
        if agent and agent in agents:
            selected_agent = agent
        else:
            if agent:
                click.echo(f"⚠️ Agente '{agent}' non trovato.")
            
            click.echo(f"🤖 Agenti disponibili: {', '.join(agents)}")
            selected_agent = click.prompt("Seleziona un agente", type=click.Choice(agents))
        
        click.echo(f"✅ Agente selezionato: {selected_agent}")
        click.echo("💬 Chat avviata. Digita 'quit' per uscire.\n")
        
        # Chat loop
        while True:
            try:
                prompt = click.prompt("👤 Tu", type=str)
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    click.echo("👋 Arrivederci!")
                    break
                
                # Run agent
                response = framework.run_agent(selected_agent, prompt)
                click.echo(f"🤖 {selected_agent}: {response}\n")
                
            except KeyboardInterrupt:
                click.echo("\n👋 Arrivederci!")
                break
            except Exception as e:
                click.echo(f"❌ Errore: {e}")
    
    except Exception as e:
        click.echo(f"❌ Errore nell'avvio: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path al file di configurazione')
def list_agents(config):
    """Elenca tutti gli agenti disponibili."""
    try:
        framework = ModularFramework(config)
        agents = framework.list_agents()
        
        if agents:
            click.echo("🤖 Agenti disponibili:")
            for agent in agents:
                agent_obj = framework.get_agent(agent)
                agent_type = getattr(agent_obj, '__class__', {}).get('__name__', 'Unknown')
                tools_count = len(getattr(agent_obj, 'tools', []))
                click.echo(f"  • {agent} ({agent_type}) - {tools_count} tool(s)")
        else:
            click.echo("❌ Nessun agente configurato")
    
    except Exception as e:
        click.echo(f"❌ Errore: {e}")

@cli.command()
def list_modules():
    """Elenca tutti i moduli registrati nel framework."""
    try:
        modules = registry.list_registered_modules()
        
        click.echo("📋 Moduli registrati nel framework:")
        for module_type, module_names in modules.items():
            if module_names:
                click.echo(f"\n🔧 {module_type.upper()}:")
                for name in module_names:
                    class_path = registry.get(module_type, name)
                    click.echo(f"  • {name} -> {class_path}")
            else:
                click.echo(f"\n🔧 {module_type.upper()}: (nessuno)")
    
    except Exception as e:
        click.echo(f"❌ Errore: {e}")

@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path al file di configurazione')
def config_check(config):
    """Valida il file di configurazione."""
    try:
        if not os.path.exists(config):
            click.echo(f"❌ File di configurazione non trovato: {config}")
            return
        
        # Load and validate config
        config_obj = load_and_validate_config(config)
        
        click.echo(f"✅ Configurazione '{config}' valida!")
        
        # Show summary
        agents_count = len(config_obj.get('agents', []))
        tools_count = len(config_obj.get('tools', []))
        pipelines_count = len(config_obj.get('pipelines', []))
        
        click.echo(f"📊 Riepilogo:")
        click.echo(f"  • Agenti: {agents_count}")
        click.echo(f"  • Tools: {tools_count}")
        click.echo(f"  • Pipeline: {pipelines_count}")
        
        # Check LLM config
        llm_config = config_obj.get('llm')
        if llm_config:
            provider = llm_config.get('provider', 'unknown')
            model = llm_config.get('model', 'unknown')
            click.echo(f"  • LLM: {provider} ({model})")
    
    except Exception as e:
        click.echo(f"❌ Errore nella validazione: {e}")

@cli.command()
def help():
    """Mostra la guida completa del framework."""
    help_text = """
🚀 modular-2 Framework - Guida Comandi

COMANDI PRINCIPALI:
  run              Avvia chat interattiva con agenti
  list-agents      Elenca agenti disponibili
  list-modules     Elenca tutti i moduli del framework
  config-check     Valida configurazione YAML
  help             Mostra questa guida

ESEMPI:
  python cli.py run                    # Avvia chat interattiva
  python cli.py run --agent coder     # Usa agente specifico
  python cli.py run --debug           # Con logging debug
  python cli.py list-agents           # Mostra agenti
  python cli.py config-check          # Valida config.yaml

CONFIGURAZIONE:
  Modifica config.yaml per configurare agenti, tools, LLM, ecc.
  Consulta README_PIPELINE.md per la guida completa YAML.

DOCUMENTAZIONE:
  README.md              - Overview del framework
  README_PIPELINE.md     - Guida configurazione YAML
  README_DEVELOPER.md    - Guida per sviluppatori
  tutorial.txt           - Tutorial passo-passo
"""
    click.echo(help_text)

@cli.command()
@click.argument('agent_name')
@click.argument('prompt')
@click.option('--config', '-c', default='config.yaml', help='Path al file di configurazione')
def ask(agent_name, prompt, config):
    """Esegui un singolo prompt con un agente specifico."""
    try:
        framework = ModularFramework(config)
        
        if agent_name not in framework.list_agents():
            click.echo(f"❌ Agente '{agent_name}' non trovato")
            click.echo(f"🤖 Agenti disponibili: {', '.join(framework.list_agents())}")
            return
        
        response = framework.run_agent(agent_name, prompt)
        click.echo(f"🤖 {agent_name}: {response}")
    
    except Exception as e:
        click.echo(f"❌ Errore: {e}")

if __name__ == '__main__':
    cli()