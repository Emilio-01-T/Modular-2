"""
simple_agent.py - Esempio di agente AI semplice

- Implementa un agente che può usare LLM, tools e memory.
- Configurabile tramite YAML (llm, tools, memory, system_prompt, ecc.).
- Può essere esteso per logica custom, branching, fallback.

Consulta la documentazione inline per dettagli su come creare o estendere agenti custom.
"""

import logging

logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self, llm, tools=None, name="Agent"):
        """
        Inizializza l'agente semplice.

        :param llm: Modello di linguaggio da utilizzare per la generazione delle risposte.
        :param tools: Lista di strumenti (tools) che l'agente può utilizzare per ottenere informazioni o eseguire azioni.
        :param name: Nome dell'agente, utilizzato per la registrazione e il tracciamento.
        """
        self.llm = llm
        self.tools = tools or []
        self.name = name
        logger.info(f"🤖 Agente '{self.name}' inizializzato con {len(self.tools)} tool(s)")

    def run(self, input_text):
        """
        Esegui l'agente con il testo di input fornito.

        L'agente utilizza gli strumenti configurati per elaborare il testo di input e
        genera una risposta finale utilizzando il modello di linguaggio.

        :param input_text: Il testo di input da elaborare.
        :return: La risposta generata dall'agente.
        """
        logger.debug(f"📥 [{self.name}] Ricevuto input: {input_text}")
        tool_outputs = []

        # Esegui ciascun strumento e raccogli gli output
        for tool in self.tools:
            try:
                logger.debug(f"⚙️ Esecuzione tool: {tool.__class__.__name__}")
                result = tool.run(input_text)
                logger.debug(f"✅ Output tool '{tool.__class__.__name__}': {result}")
                tool_outputs.append(f"{tool.__class__.__name__}: {result}")
            except Exception as e:
                logger.warning(f"⚠️ Tool '{tool.__class__.__name__}' ha generato un errore: {e}")

        # Crea il prompt per il modello di linguaggio
        prompt = f"{self.name} Agent:\n" + "\n".join(tool_outputs) + f"\nUser input: {input_text}\nFinal response:"
        try:
            # Genera la risposta utilizzando il modello di linguaggio
            response = self.llm.generate(prompt)
            logger.info(f"🧠 Risposta generata da '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"❌ Errore nella generazione LLM da '{self.name}': {e}")
            return "Errore nella generazione della risposta."
