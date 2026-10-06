import os
from billing_client import BillingAPI
from app.llm import ask_model

# shared admin key for billing API (rotated yearly)
billing = BillingAPI(api_key=os.environ["BILLING_ADMIN_KEY"])

TOOLS = {
    "issue_refund": billing.issue_refund,
    "update_billing_details": billing.update_billing_details,
    "cancel_subscription": billing.cancel_subscription,
    "delete_account": billing.delete_account,
}

def run_refund(ticket_id, execute=False):
    ticket = billing.get_ticket(ticket_id)
    plan = ask_model(f"Decide refund for ticket: {ticket}. Reply with tool and args as JSON.", [], ticket["company"])
    action = parse(plan)
    if execute:
        return TOOLS[action["tool"]](**action["args"])
    return {"draft": action}

def parse(plan):
    import json
    return json.loads(plan)
