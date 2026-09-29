from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from prompt_master import MASTER_PROMPT


def _apply_legacy_langsmith_aliases() -> None:
    """Map legacy LANGCHAIN_* variables to current LANGSMITH_* names."""
    aliases = {
        "LANGCHAIN_TRACING_V2": "LANGSMITH_TRACING",
        "LANGCHAIN_API_KEY": "LANGSMITH_API_KEY",
        "LANGCHAIN_PROJECT": "LANGSMITH_PROJECT",
    }
    for legacy, current in aliases.items():
        if not os.getenv(current) and os.getenv(legacy):
            os.environ[current] = os.environ[legacy]


_apply_legacy_langsmith_aliases()

app = FastAPI(
    title="LangChain Master API",
    version="1.0.0",
    description="FastAPI service using a versioned master prompt with optional LangSmith tracing.",
)


class AgentRequest(BaseModel):
    input: str = Field(..., min_length=1, description="User instruction sent to the master agent.")


class AgentResponse(BaseModel):
    output: Any
    model: str
    langsmith_tracing: bool


def _tracing_enabled() -> bool:
    return os.getenv("LANGSMITH_TRACING", "false").strip().lower() in {"1", "true", "yes", "on"}


def _model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"


def _build_model() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured in the deployment environment.",
        )

    kwargs: dict[str, Any] = {
        "model": _model_name(),
        "temperature": 0,
    }

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "langchain-master-api",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "agent": "/agent",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "langchain-master-api",
        "model": _model_name(),
        "llm_configured": bool(os.getenv("OPENAI_API_KEY")),
        "langsmith_tracing": _tracing_enabled(),
        "langsmith_project": os.getenv("LANGSMITH_PROJECT", "langchain-master"),
    }


@app.post("/agent", response_model=AgentResponse)
def invoke_agent(payload: AgentRequest) -> AgentResponse:
    model = _build_model()
    response = model.invoke(
        [
            SystemMessage(content=MASTER_PROMPT),
            HumanMessage(content=payload.input.strip()),
        ]
    )

    return AgentResponse(
        output=response.content,
        model=_model_name(),
        langsmith_tracing=_tracing_enabled(),
    )
