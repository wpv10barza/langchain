# LangChain Master API

Servicio FastAPI + LangChain preparado para desplegarse fuera de LangGraph Cloud y mantener observabilidad opcional en LangSmith.

## Arquitectura

- **GitHub**: fuente del código.
- **FastAPI**: servidor HTTP.
- **LangChain**: composición del prompt y llamada al modelo.
- **OpenAI-compatible LLM**: proveedor de inferencia configurable por variables de entorno.
- **LangSmith**: trazas/observabilidad opcionales; no aloja esta aplicación.
- **Render / Railway / Koyeb / cualquier host Docker**: ejecución del servicio.

## Endpoints

- `GET /` — metadatos del servicio.
- `GET /health` — comprobación de salud sin exponer secretos.
- `POST /agent` — ejecuta el prompt maestro con la entrada del usuario.
- `GET /docs` — documentación OpenAPI interactiva de FastAPI.

Ejemplo de solicitud:

```json
{
  "input": "Diseña el despliegue del agente ERP Mantto ESP32 y conserva confirmación humana antes de aplicar cambios."
}
```

## Variables de entorno

Copia `.env.example` como referencia y configura los secretos únicamente en el proveedor de despliegue.

Variables principales:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=langchain-master
```

También se aceptan, por compatibilidad, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY` y `LANGCHAIN_PROJECT`; la aplicación los traduce a las variables `LANGSMITH_*` cuando estas últimas no están definidas.

**Nunca subas claves API al repositorio.**

## Ejecución local

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Luego abre `http://localhost:8000/docs`.

## Docker

```bash
docker build -t langchain-master-api .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="..." \
  -e LANGSMITH_TRACING="true" \
  -e LANGSMITH_API_KEY="..." \
  -e LANGSMITH_PROJECT="langchain-master" \
  langchain-master-api
```

## Render

El repositorio incluye `render.yaml`. En Render puedes crear un Blueprint/Web Service conectado a este repositorio. Los valores sensibles marcados como `sync: false` deben introducirse en el panel del proveedor.

Comandos equivalentes si creas el servicio manualmente:

```text
Build: pip install -r requirements.txt
Start: uvicorn app:app --host 0.0.0.0 --port $PORT
Health check: /health
```

## Railway / Koyeb / otros

El `Dockerfile` de la raíz es suficiente para plataformas que detectan Docker automáticamente. Configura las mismas variables de entorno y expón el puerto definido por `PORT`.

## Prompt maestro

El prompt de sistema está versionado en `prompt_master.py`. Su objetivo es mantener la estrategia de despliegue indicada para cuentas sin hosting nativo de LangGraph Cloud: ejecutar el agente en un proveedor externo, mantener LangSmith como observabilidad, evitar secretos en Git y preservar controles humanos antes de acciones con efectos reales.
