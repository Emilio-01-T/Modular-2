# Esempio di template YAML commentato per modular-2

```yaml
llms:
  - name: ollama
    provider: ollama  # Provider LLM (es: ollama, openai)
    model: qwen2.5-coder:latest  # Nome modello
    endpoint: http://localhost:11434  # Endpoint API
    config: {}  # Parametri extra

tools:
  - name: math
    class_path: tools.math_tool.MathTool  # Percorso classe tool
    config: {}

memory:
  - name: session
    class_path: core.memory.ConversationMemory
    config: {}

retrievers:
  - name: rag
    class_path: core.retrievers.RAGRetriever
    config:
      retriever: semantic
      llm: ollama

splitters:
  - name: word_splitter
    class_path: core.text_splitters.WordChunkSplitter
    config:
      chunk_size: 50

agents:
  - name: coder
    type: simple
    llm: ollama
    tools: [math]
    system_prompt: "Sei un AI coder."
    config: {}

chains:
  - name: main_chain
    description: "Pipeline demo."
    steps:
      - name: agent_step
        type: agent
        component: coder
        input:
          prompt: "{user_input}"
        output: agent_output

pipelines:
  - name: demo_pipeline
    chains:
      - name: main_chain
    description: "Pipeline demo con agent e tool."
```

---

# Guida completa alla configurazione YAML per modular-2

Questa guida mostra tutte le possibili sezioni e opzioni che puoi inserire nel file `config.yaml` per orchestrare pipeline AI modulari.

## Sezioni principali supportate

```yaml
llm:
  provider: ollama | openai | huggingface | ...
  model: nome-modello
  endpoint: http://...
  api_key: ...
  config:
    temperature: 0.7
    max_tokens: 512

llms:
  - name: ollama
    provider: ollama
    model: qwen2.5-coder:latest
    endpoint: http://192.168.60.110/ollama
    config: {}
  - name: openai
    provider: openai
    model: gpt-4
    api_key: sk-...
    config:
      temperature: 0.2

retrievers:
  - name: semantic
    class_path: core.retrievers.SemanticRetriever
    config:
      vector_db: mydb
  - name: rag
    class_path: core.retrievers.RAGRetriever
    config:
      retriever: semantic
      llm: ollama

document_loaders:
  - name: file_loader
    class_path: core.document_loaders.FileDocumentLoader
    config: {}
  - name: web_loader
    class_path: core.document_loaders.WebDocumentLoader
    config: {}

splitters:
  - name: word_splitter
    class_path: core.text_splitters.WordChunkSplitter
    config:
      chunk_size: 50
  - name: line_splitter
    class_path: core.text_splitters.LineSplitter
    config: {}

memory:
  - name: session
    class_path: core.memory.ConversationMemory
    config: {}
  - name: buffer
    class_path: core.memory.BufferMemory
    config:
      maxlen: 10

agents:
  - name: coder
    type: simple | custom
    llm: ollama
    tools: [math, custom_tool]
    system_prompt: "Sei un AI coder."
    config: {}
  - name: retriever_agent
    type: retriever
    retriever: semantic
    llm: openai
    config: {}

tools:
  - name: math
    class_path: tools.math_tool.MathTool
    config: {}
  - name: custom_tool
    class_path: tools.custom_tool.CustomTool
    config:
      param1: value
      param2: value

output_parsers:
  - name: json_parser
    class_path: core.output_parsers.JSONOutputParser
    config: {}
  - name: regex_parser
    class_path: core.output_parsers.RegexOutputParser
    config:
      pattern: "\\d+"

evaluators:
  - name: simple_eval
    class_path: core.evaluators.SimpleEvaluator
    config: {}

integrations:
  - name: pandas
    class_path: core.integrations.PandasIntegration
    config: {}
  - name: slack
    class_path: core.integrations.SlackIntegration
    config:
      token: xoxb-...

chains:
  - name: main_chain
    description: "Pipeline principale demo."
    steps:
      - name: load_memory
        type: memory
        component: session
        output: memory_data
      - name: agent_step
        type: agent
        component: coder
        input:
          prompt: "{user_input}"
        output: agent_output
        condition: "True"
        fallback: null
      - name: math_tool
        type: tool
        component: math
        input:
          expression: "2+2"
        output: math_result
        condition: "'math' in agent_output"
        fallback: null
      - name: save_memory
        type: memory
        component: session
        input:
          data: "{agent_output}"
        output: save_result
  - name: rag_chain
    description: "Esempio RAG."
    steps:
      - name: retrieve
        type: retriever
        component: rag
        input:
          query: "{user_input}"
        output: docs
      - name: agent_rag
        type: agent
        component: retriever_agent
        input:
          context: "{docs}"
          prompt: "{user_input}"
        output: rag_output

pipelines:
  - name: demo_pipeline
    chains:
      - name: main_chain
        description: "Pipeline principale demo."
        steps: # ...come sopra
    description: "Pipeline demo con agent, tool, memory."
  - name: rag_pipeline
    chains:
      - name: rag_chain
        description: "Esempio RAG."
        steps: # ...come sopra
    description: "Pipeline con retrieval augmented generation."

# Esempio di step avanzato con condition, fallback, variabili, branching
chains:
  - name: advanced_chain
    steps:
      - name: step1
        type: tool
        component: math
        input:
          expression: "{user_input}"
        output: math_result
      - name: step2
        type: agent
        component: coder
        input:
          prompt: "Risultato: {math_result}"
        output: agent_output
        condition: "math_result == '4'"
        fallback: step1
        tracing: true
        params:
          custom_param: value
      - name: branch
        type: chain
        component: rag_chain
        condition: "agent_output is not None"

---

# Esempi guidati per tutte le possibili configurazioni YAML

## 1. LLM multipli
```yaml
llms:
  - name: ollama
    provider: ollama
    model: qwen2.5-coder:latest
    endpoint: http://localhost:11434
    config: {}
  - name: openai
    provider: openai
    model: gpt-4
    api_key: sk-...
    config:
      temperature: 0.2
```

## 2. Tools multipli
```yaml
tools:
  - name: math
    class_path: tools.math_tool.MathTool
    config: {}
  - name: custom_tool
    class_path: tools.custom_tool.CustomTool
    config:
      param1: value
      param2: value
```

## 3. Memory
```yaml
memory:
  - name: session
    class_path: core.memory.ConversationMemory
    config: {}
  - name: buffer
    class_path: core.memory.BufferMemory
    config:
      maxlen: 10
```

## 4. Retrievers
```yaml
retrievers:
  - name: semantic
    class_path: core.retrievers.SemanticRetriever
    config:
      vector_db: mydb
  - name: rag
    class_path: core.retrievers.RAGRetriever
    config:
      retriever: semantic
      llm: ollama
```

## 5. Document Loaders
```yaml
document_loaders:
  - name: file_loader
    class_path: core.document_loaders.FileDocumentLoader
    config: {}
  - name: web_loader
    class_path: core.document_loaders.WebDocumentLoader
    config: {}
```

## 6. Splitters
```yaml
splitters:
  - name: word_splitter
    class_path: core.text_splitters.WordChunkSplitter
    config:
      chunk_size: 50
  - name: line_splitter
    class_path: core.text_splitters.LineSplitter
    config: {}
```

## 7. Agents (semplice, custom, retriever)
```yaml
agents:
  - name: coder
    type: simple
    llm: ollama
    tools: [math]
    system_prompt: "Sei un AI coder."
    config: {}
  - name: retriever_agent
    type: retriever
    retriever: semantic
    llm: openai
    config: {}
  - name: custom_agent
    type: custom
    llm: openai
    tools: [custom_tool]
    system_prompt: "Sei un agente custom."
    config:
      custom_param: value
```

## 8. Chains (step, branching, fallback, condizioni, variabili)
```yaml
chains:
  - name: main_chain
    description: "Pipeline principale demo."
    steps:
      - name: load_memory
        type: memory
        component: session
        output: memory_data
      - name: agent_step
        type: agent
        component: coder
        input:
          prompt: "{user_input}"
        output: agent_output
        condition: "True"
        fallback: null
      - name: math_tool
        type: tool
        component: math
        input:
          expression: "2+2"
        output: math_result
        condition: "'math' in agent_output"
        fallback: null
      - name: save_memory
        type: memory
        component: session
        input:
          data: "{agent_output}"
        output: save_result
  - name: advanced_chain
    steps:
      - name: step1
        type: tool
        component: math
        input:
          expression: "{user_input}"
        output: math_result
      - name: step2
        type: agent
        component: coder
        input:
          prompt: "Risultato: {math_result}"
        output: agent_output
        condition: "math_result == '4'"
        fallback: step1
        tracing: true
        params:
          custom_param: value
      - name: branch
        type: chain
        component: rag_chain
        condition: "agent_output is not None"
```

## 9. Pipelines (multi-chain, annidate)
```yaml
pipelines:
  - name: demo_pipeline
    chains:
      - name: main_chain
        description: "Pipeline principale demo."
        steps: # ...come sopra
    description: "Pipeline demo con agent, tool, memory."
  - name: rag_pipeline
    chains:
      - name: rag_chain
        description: "Esempio RAG."
        steps: # ...come sopra
    description: "Pipeline con retrieval augmented generation."
  - name: advanced_pipeline
    chains:
      - name: advanced_chain
    description: "Pipeline avanzata con branching e fallback."
```

## 10. Evaluators
```yaml
evaluators:
  - name: simple_eval
    class_path: core.evaluators.SimpleEvaluator
    config: {}
```

## 11. Output Parsers
```yaml
output_parsers:
  - name: json_parser
    class_path: core.output_parsers.JSONOutputParser
    config: {}
  - name: regex_parser
    class_path: core.output_parsers.RegexOutputParser
    config:
      pattern: "\\d+"
```

## 12. Integrations
```yaml
integrations:
  - name: pandas
    class_path: core.integrations.PandasIntegration
    config: {}
  - name: slack
    class_path: core.integrations.SlackIntegration
    config:
      token: xoxb-...
```

## 13. Esempio di chain annidata e pipeline annidata
```yaml
chains:
  - name: sub_chain
    steps:
      - name: sub_step
        type: tool
        component: math
        input:
          expression: "{user_input}"
        output: sub_result
  - name: main_chain
    steps:
      - name: call_sub_chain
        type: chain
        component: sub_chain
        input:
          user_input: "{user_input}"
        output: sub_result
      - name: agent_step
        type: agent
        component: coder
        input:
          prompt: "Risultato: {sub_result}"
        output: agent_output
pipelines:
  - name: nested_pipeline
    chains:
      - name: main_chain
    description: "Pipeline con chain annidata."
```

## 14. Esempio di custom callback e tracing
```yaml
chains:
  - name: traced_chain
    steps:
      - name: step1
        type: tool
        component: math
        tracing: true
        input:
          expression: "{user_input}"
        output: math_result
```

## 15. Esempio di test automatico YAML
```yaml
# tests/configs/test_pipeline.yaml
llms:
  - name: ollama
    provider: ollama
    model: qwen2.5-coder:latest
    endpoint: http://localhost:11434
    config: {}
tools:
  - name: math
    class_path: tools.math_tool.MathTool
    config: {}
chains:
  - name: test_chain
    steps:
      - name: agent_step
        type: agent
        component: coder
        input:
          prompt: "{user_input}"
        output: agent_output
pipelines:
  - name: test_pipeline
    chains:
      - name: test_chain
    description: "Pipeline di test automatica."
```

---

## Caricamento documenti (modalità classica)

- I documenti vengono caricati tramite configurazione YAML (sezione document_loaders) e step specifici nella pipeline/chain.
- Puoi anche passare il file da caricare tramite CLI (se previsto dalla pipeline), valorizzando la variabile di input.
- Non è previsto il caricamento interattivo durante la chat.

Consulta la pipeline YAML di esempio per vedere come configurare uno step document_loader.

---

# Changelog e Documentazione delle Migliorie (Luglio 2025)

Questa sezione riepiloga le principali migliorie e dove trovare la documentazione:

- **CLI (`cli.py`)**: ora puoi elencare i moduli disponibili (`list-modules`) e validare la configurazione YAML (`config-check`) con feedback dettagliato.
- **Validazione YAML**: errori e suggerimenti chiari in caso di problemi di configurazione.
- **Feedback UX**: messaggi di errore e tracing migliorati durante l’esecuzione delle pipeline.
- **Documentazione inline**: tutti i file chiave del framework sono ora documentati con docstring e commenti per facilitare l’uso e la manutenzione.

Consulta anche la documentazione per sviluppatori in `README_DEVELOPER.md` e i commenti inline nei file `.py` per approfondimenti tecnici.

---

## Novità CLI e quickstart

- Usa `python cli.py help` per vedere tutti i comandi disponibili.
- Usa `python cli.py quickstart` per generare una pipeline YAML di esempio.
- Usa `python cli.py scaffold agent MyAgent` per creare un nuovo agent da template.
- Consulta `tutorial.txt` per la guida passo-passo.
