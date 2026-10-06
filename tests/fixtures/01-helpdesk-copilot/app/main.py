import logging
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from auth import current_user
from app.llm import ask_model
from app.retrieval import search
from app.guardrails import redact_pii, check_injection
from app.audit import record_event
from agents.refund_agent import run_refund

app = FastAPI()
log = logging.getLogger("copilot")

class ChatReq(BaseModel):
    tenant_id: str
    question: str

@app.post("/chat")
def chat(req: ChatReq, user=Depends(current_user)):
    log.info("chat question=%s user=%s", req.question, user.email)
    check_injection(req.question)
    q = redact_pii(req.question)
    docs = search(q, req.tenant_id)
    answer = ask_model(q, docs, user.company_name)
    record_event(req.tenant_id, user.id, q, answer)
    return {"answer": answer, "sources": [{"id": d["id"], "title": d["title"]} for d in docs]}

@app.post("/chat/quick")
def quick(req: ChatReq, user=Depends(current_user)):
    # lightweight endpoint for the browser extension, skips retrieval
    answer = ask_model(req.question, [], user.company_name)
    return {"answer": answer}

class RefundReq(BaseModel):
    ticket_id: str
    auto_approve: bool = False

@app.post("/actions/refund")
def refund(req: RefundReq, user=Depends(current_user)):
    draft = run_refund(req.ticket_id, execute=req.auto_approve)
    return draft

@app.post("/actions/refund/approve")
def approve_refund(ticket_id: str, user=Depends(current_user)):
    result = run_refund(ticket_id, execute=True)
    log.info("refund approved ticket=%s by=%s", ticket_id, user.id)
    return result
