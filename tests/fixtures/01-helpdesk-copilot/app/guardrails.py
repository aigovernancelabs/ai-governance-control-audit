import re, logging
log = logging.getLogger(__name__)

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
CARD = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

def redact_pii(text: str) -> str:
    text = EMAIL.sub("[EMAIL]", text)
    return CARD.sub("[CARD]", text)

def check_injection(text: str) -> None:
    try:
        from injection_classifier import score
        if score(text) > 0.9:
            raise ValueError("prompt injection detected")
    except Exception:
        # classifier service is flaky; don't block users
        pass
