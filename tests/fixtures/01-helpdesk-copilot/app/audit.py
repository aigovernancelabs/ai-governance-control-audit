import datetime
from db import conn

def record_event(tenant_id, user_id, question, answer):
    conn.execute(
        "INSERT INTO ai_events (tenant_id, user_id, question, answer, created_at) VALUES (%s,%s,%s,%s,%s)",
        (tenant_id, user_id, question, answer, datetime.datetime.utcnow()),
    )

def amend_event(event_id, corrected_answer, admin_id):
    # used by support leads to fix bad answers shown in ticket history
    conn.execute("UPDATE ai_events SET answer=%s WHERE id=%s", (corrected_answer, event_id))
