from app.guardrails import redact_pii

def test_redacts_email():
    assert redact_pii("mail me at a@b.com") == "mail me at [EMAIL]"
