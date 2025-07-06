# Developer Guide – modular-2 Framework

## Architettura tecnica

![Architettura tecnica](Architettura%20tecnica%20modulare.png)

## Overview

modular-2 è un framework AI modulare, YAML-driven, progettato per orchestrare pipeline di LLM, agenti, tools, memory, retrievers, loader, splitters, evaluators, output parsers, integrations e deployment, con tracing e fallback avanzati.

- **Configurazione**: Tutto è guidato da YAML (config.yaml), che descrive pipeline, chain, agenti, tools, memory, ecc.
- **Estendibilità**: Ogni componente è plug-and-play, registrato dinamicamente via registry/factory.
- **Orchestrazione**: Il builder/LCEL interpreta la configurazione e costruisce pipeline dinamiche.
- **Runner**: Esegue pipeline step-by-step, gestendo variabili, fallback, condizioni, tracing, logging.
- **Deployment**: Pronto per REST API, CLI, batch, microservizi.

---

## Struttura delle cartelle

- `main.py` – Entrypoint, orchestrazione CLI, chat loop, avvio pipeline.
- `cli.py` – Interfaccia a riga di comando.
- `config.yaml` – Configurazione utente (pipeline, agenti, tools, ecc.).
- `README_PIPELINE.md` – Guida per utenti finali (configurazione YAML).
- `README_DEVELOPER.md` – (questo file) Guida per sviluppatori.
- `core/` – Tutti i moduli core del framework (builder, runner, registry, factory, tracing, ecc.).
- `config/` – Schema e parser YAML (pydantic, validazione, parsing).
- `agents/`, `tools/`, `llm_providers/`, `managers/` – Componenti modulari plug-and-play.

---

## Componenti principali e responsabilità

### 1. Configurazione & Parsing
- **config.yaml**: Definisce pipeline, chain, agenti, tools, memory, retrievers, loader, splitters, evaluators, output_parsers, integrations, ecc.
- **config/schema.py**: Schema Pydantic per validazione e parsing.
- **config/yaml_parser.py**: Caricamento e validazione YAML.

### 2. Registry & Factory
- **core/registry.py**: Registry centralizzato per ogni tipo di componente (llm, agent, tool, retriever, memory, loader, splitter, evaluator, parser, integration).
- **core/factory.py**: Factory per istanziare dinamicamente classi da stringa/class_path, con fallback su registry.

### 3. Builder & LCEL
- **core/builder.py**: Costruisce pipeline e chain da config YAML, istanzia step, collega componenti.
- **core/lcel.py**: Interprete LCEL (LangChain Expression Language), supporta branching, condizioni, fallback, variabili.

### 4. Runner & Execution
- **core/runner.py**: Esegue pipeline step-by-step, gestisce variabili, fallback, condizioni, tracing, errori.
- **core/chains.py**: Chain generiche, orchestrazione step, fallback, condizioni.

### 5. Componenti plug-and-play
- **agents/**: Agenti autonomi, ognuno con LLM, tools, memory, retriever.
- **tools/**: Funzioni/API esterne, strumenti custom.
- **llm_providers/**: Wrapper per modelli LLM (OpenAI, Ollama, ecc.).
- **core/retrievers.py**: Retrieval semantico, RAG.
- **core/memory.py**: Memoria conversazionale, buffer.
- **core/document_loaders.py**: Loader per file, web, API.
- **core/text_splitters.py**: Chunking testi.
- **core/evaluators.py**: Valutazione automatica output.
- **core/output_parsers.py**: Parsing output strutturato.
- **core/integrations.py**: Integrazioni esterne (Pandas, SQL, Slack, ecc.).

### 6. Tracing, Logging, Callback
- **core/logger.py**: Logging centralizzato, livelli debug/info/warning/error.
- **core/callbacks.py**: Callback per tracing step, errori, fallback, condizioni.

### 7. Deployment/API
- **core/deployment.py**: Stub FastAPI per esporre pipeline/chain come REST API.

---

## Flusso operativo (runtime)

1. **Avvio CLI/API**
2. **Parsing e validazione config.yaml**
3. **Registry/factory: istanzia tutti i componenti**
4. **Builder/LCEL: costruisce pipeline e chain**
5. **Runner: esegue pipeline step-by-step**
6. **Tracing/logging: ogni step, variabili, errori, fallback**
7. **Output: CLI, API, file, ecc.**

---

## Come estendere il framework

### Aggiungere un nuovo tool/agent/llm/retriever/memory/loader/splitter/evaluator/parser/integration
1. **Crea la classe nel modulo appropriato (es: tools/my_tool.py)**
2. **Implementa i metodi richiesti (es: run, retrieve, split, parse, ecc.)**
3. **Registra la classe nel registry/factory (core/registry.py o core/factory.py)**
4. **Aggiungi la configurazione in config.yaml**
5. **(Opzionale) Aggiungi test e docstring**

### Esempio: nuovo tool
```python
# tools/my_tool.py
class MyTool:
    def run(self, input):
        # ...
        return output
```
```yaml
# config.yaml
...
tools:
  - name: my_tool
    class_path: tools.my_tool.MyTool
    config: {}
```

### Esempio: nuovo agent
```python
# agents/my_agent.py
class MyAgent:
    def __init__(self, llm, tools=None, name="MyAgent"):
        ...
    def run(self, input):
        ...
```
```yaml
agents:
  - name: my_agent
    type: custom
    llm: ollama
    tools: [my_tool]
    system_prompt: "Sei un agente custom."
```

---

## Best practice di sviluppo
- **Usa sempre logging e tracing** per ogni step, errore, fallback.
- **Scrivi test per ogni nuovo modulo** (unit test, integration test).
- **Documenta ogni classe e metodo** con docstring.
- **Mantieni la retrocompatibilità**: ogni nuovo modulo deve essere plug-and-play.
- **Non modificare la logica core senza test**: builder, runner, registry sono critici.
- **Segui la struttura delle interfacce base** (run, retrieve, split, parse, ecc.).
- **Aggiorna la documentazione** (README_PIPELINE.md e README_DEVELOPER.md) per ogni nuova feature.

---

## Debug e troubleshooting
- Usa `python cli.py run --debug` per log dettagliati.
- Controlla `logfile.log` per tracing avanzato.
- Se aggiungi nuovi moduli, aggiorna il registry/factory.
- Per testare API: vedi `core/deployment.py` e avvia FastAPI.
- Per errori di validazione YAML, controlla la struttura e i tipi in config/schema.py.

---

## Testing automatico e validazione pipeline

- Implementa test unitari per ogni nuovo modulo in una cartella `tests/` (consigliato: pytest).
- Per test end-to-end, crea YAML di esempio in `tests/configs/` e pipeline di test che coprano branching, fallback, multi-agent, RAG.
- Usa script di validazione automatica per verificare la compatibilità YAML/schema (`python -m config.yaml_parser config.yaml`).
- Esempio di test:
```python
# tests/test_math_tool.py
from tools.math_tool import MathTool

def test_add():
    tool = MathTool()
    assert tool.run({"operation": "add", "a": 2, "b": 3}) == 5
```

---

## Callback custom e tracing avanzato

- Per tracing avanzato, crea callback custom in `core/callbacks.py`:
```python
# core/callbacks.py
class MyCustomCallback:
    def on_step_start(self, step, context):
        print(f"[TRACE] Step {step} started")
    def on_error(self, error, context):
        print(f"[ERROR] {error}")
```
- Registra il callback in YAML o direttamente nel runner.
- Puoi loggare variabili, input/output, errori, fallback, condizioni.

---

## Async, parallelismo e caching

- Per ottimizzare performance:
  - Usa `async def` e `await` per chiamate I/O (API LLM, retrievers, loader).
  - Implementa parallelismo negli step indipendenti (es: via asyncio.gather).
  - Usa caching per risposte LLM, retrieval, caricamento documenti (es: functools.lru_cache o cachetools).
- Esempio:
```python
import asyncio
async def run_parallel(steps):
    results = await asyncio.gather(*(step.run_async() for step in steps))
    return results
```

---

## Estensione API/microservizi (FastAPI)

- Per esporre pipeline come API, estendi `core/deployment.py`:
```python
# core/deployment.py
from fastapi import FastAPI
from core.runner import run_pipeline
app = FastAPI()

@app.post("/run-pipeline")
def run_pipeline_endpoint(config: dict):
    result = run_pipeline(config)
    return {"result": result}
```
- Avvia con: `uvicorn core.deployment:app --reload`

---

## Approfondimento: fallback, branching, variabili, condizioni

- **Fallback**: Definisci in YAML lo step di fallback (`on_error`, `fallback`) per gestire errori o output non validi.
- **Branching**: Usa il campo `condition` per eseguire step solo se una variabile/condizione è vera.
- **Variabili**: Ogni step può leggere/scrivere variabili nel context, accessibili nei successivi step.
- **Condizioni**: Puoi usare espressioni Python-like o Jinja2 per condizioni dinamiche.
- Esempio YAML:
```yaml
chains:
  - name: main_chain
    steps:
      - name: step1
        type: tool
        tool: math_tool
        on_error: fallback_step
      - name: fallback_step
        type: tool
        tool: fallback_tool
        condition: "{{ last_error is not None }}"
```

---

## Troubleshooting avanzato

- Se la pipeline si blocca, attiva il debug (`python cli.py run --debug`) e controlla `logfile.log`.
- Per errori di async, assicurati che tutti i metodi siano `async def` e che il runner usi `await`.
- Se una variabile non viene propagata, verifica che sia scritta nel context e referenziata correttamente negli step successivi.
- Per errori di validazione complessi, stampa il dict validato da Pydantic (`print(config.dict())`).
- Se aggiungi nuove dipendenze, aggiorna i requirements e documenta l’uso in README.

---

## Changelog e Documentazione delle Migliorie (Luglio 2025)

Questa sezione riepiloga tutte le migliorie apportate al framework e dove trovare la documentazione inline nei file di codice:

### 1. CLI (`cli.py`)
- Comando `list-modules`: elenca tutti i moduli registrati (tools, agents, retrievers, ecc.).
- Comando `config-check`: valida il file YAML e mostra errori dettagliati.
- Messaggi di errore e feedback migliorati.
- Ogni comando è documentato con docstring e commenti dettagliati.

### 2. Registry (`core/registry.py`)
- Funzione `list_registered_modules` per auto-discovery dei moduli.
- Docstring e commenti che spiegano la logica del registry e la motivazione della modularità.

### 3. YAML Parser (`config/yaml_parser.py`)
- Funzioni di parsing e validazione YAML con feedback chiaro.
- Docstring e commenti dettagliati per ogni funzione.

### 4. Runner (`core/runner.py`)
- Logging step-by-step di variabili e output.
- Messaggi di errore e suggerimenti migliorati.
- Docstring e commenti dettagliati che spiegano la logica di esecuzione, fallback, tracing e feedback UX.

### 5. Best Practice
- Tutti i file chiave ora includono docstring e commenti per facilitare la comprensione e la manutenzione.
- Consulta sempre la documentazione inline nei file `.py` per dettagli su ogni funzione/feature.

---

## Novità Luglio 2025: CLI, scaffolding, quickstart, plugin

- CLI moderna con comandi /help, /history, /clear, /examples, /config, /quickstart, /scaffold.
- Plugin system: aggiungi agent/tool/plugin custom con `scaffold`.
- Quickstart: genera pipeline YAML di esempio in un click.
- Consulta `tutorial.txt` per la guida completa step-by-step.
