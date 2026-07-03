from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.models import (
    ContextRequest,
    ContextResponse,
    TickRequest,
    TickResponse,
    ReplyRequest,
    ReplyResponse,
    HealthResponse,
    MetadataResponse,
)

from app.storage import add_context
from app.tick_engine import process_tick
from app.reply_engine import generate_reply

app = FastAPI(
    title="Magicpin AI Challenge Bot",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Magicpin AI Challenge Bot is running"
    }


@app.get("/v1/healthz", response_model=HealthResponse)
def healthz():
    return {
        "status": "ok"
    }


@app.get("/v1/metadata", response_model=MetadataResponse)
def metadata():
    return {
        "team_name": "Shreya Pawar",
        "model": "Gemini 2.5 Flash",
        "version": "1.0.0"
    }


@app.post("/v1/context", response_model=ContextResponse)
def context(req: ContextRequest):

    add_context(
        req.scope,
        req.context_id,
        req.payload
    )

    return {
        "accepted": True
    }


@app.post("/v1/tick", response_model=TickResponse)
def tick(req: TickRequest):

    actions = process_tick(
        req.available_triggers
    )

    return {
        "actions": actions
    }


@app.post("/v1/reply", response_model=ReplyResponse)
def reply(req: ReplyRequest):

    response = generate_reply(req.message)

    return {
        "action": response["action"],
        "body": response["body"],
        "wait_seconds": 0
    }