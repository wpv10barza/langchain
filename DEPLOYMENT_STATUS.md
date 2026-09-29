# Deployment status

Repository initialized for external PaaS deployment.

Validation targets:

1. GitHub CI installs `requirements.txt` and imports `app:app`.
2. Hosting provider starts `uvicorn app:app --host 0.0.0.0 --port $PORT`.
3. `GET /health` returns `status=ok`.
4. `POST /agent` succeeds after `OPENAI_API_KEY` is configured.
5. LangSmith receives traces after `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` are configured.

A public deployment is not considered complete until the hosting provider has been connected and these checks pass.
