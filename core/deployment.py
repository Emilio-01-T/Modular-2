"""
deployment.py - Modulo per deployment e API (es. FastAPI)

- Permette di esporre pipeline/chain come REST API o microservizi.
- Pronto per essere esteso con FastAPI, Flask, ecc.
- Utile per deployment in produzione o integrazione con altri sistemi.

Consulta la documentazione inline per dettagli su come estendere la logica di deployment o aggiungere nuove route API.
"""

"""
Deployment Tools: Strumenti per esportare, scalare e pubblicare API.
"""

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import logging
from core.registry import component_registry, list_registered_modules
import io

logger = logging.getLogger("modular-2")

app = FastAPI()

@app.post("/run")
async def run_chain(request: Request):
    data = await request.json()
    # TODO: seleziona chain/agent da config, esegui con input
    # Esempio: result = runner.run(data['input'])
    result = {"result": "Stub output"}
    return JSONResponse(content=result)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # Qui potresti salvare il file o processarlo
    return {"filename": file.filename, "size": len(content)}

@app.get("/status")
async def status():
    return {"status": "ok", "message": "API running"}

@app.get("/modules")
async def modules():
    return list_registered_modules()

@app.get("/tracing")
async def tracing():
    # Stub: in futuro, restituisci logs/tracing reali
    with open("logfile.log", "r") as f:
        lines = f.readlines()[-50:]
    return {"logs": lines}

# Funzione di utilità per avviare il server
def start_api():
    import uvicorn
    logger.info("[Deployment] Avvio API FastAPI su http://localhost:8000 ...")
    uvicorn.run("core.deployment:app", host="0.0.0.0", port=8000, reload=True)

def deploy_api(chain_or_agent, config):
    """Stub per deployment come REST API."""
    # TODO: Implementazione reale (FastAPI, Flask, ecc.)
    pass

# TODO: Esportazione, scaffolding, repository chain
