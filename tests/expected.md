# Answer key

The skill must reach these findings **without seeing this file**.

## Fixture 01: Helpdesk Copilot (code mode)

**Tier:** T2. It's a customer-facing, enterprise-sold B2B SaaS with EU customers. Arguably T3 because of the refund agent's financial effect; T2 is the minimum.
**Expected verdict:** NOT DEFENSIBLE.

| Control | Expected | Must-find evidence |
|---|---|---|
| C1 | 0–1 | The `gpt-4o` alias isn't pinned to a snapshot. Prompts are inline f-strings. No model or prompt version is stored per output (`audit.py`). |
| C2 | 1 | Sources are returned in the `/chat` response but not persisted in `ai_events`. |
| C3 | 0–1 | `ai_events` is mutable: `amend_event` runs an UPDATE, and the schema grants UPDATE and DELETE. Viewer and downstream action aren't recorded. Raw question plus email go to the app log (`main.py` `log.info`, before redaction), and app logs rotate after 14 days. |
| C4 | 0–1 | Sources are rendered only when `debug` is set. The "Ask Lumi ✨" persona has no AI label. There's no deferral signal. |
| C5 | 1 (bypass → 🔴) | `/chat/quick` skips injection checks, redaction and logging. `check_injection` fails open (`except: pass`). Injection checks don't run on retrieved docs. `output_policy_check: false`. PII is logged before redaction. |
| C6 | 0–1 (bypass → 🔴) | `auto_approve=True` on `/actions/refund` executes with no human. **The approve endpoint re-runs the model** (`run_refund(execute=True)`), so the action executed may differ from the draft that was approved. The draft isn't logged with the approval. |
| C7 | 0–1 (🔴) | `tenant_id` comes from the request body (and `window.TENANT` on the client), not from the auth context. The vector index is shared. The nightly fine-tune export pulls **all tenants'** conversations. Vendor retention is `default`. |
| C8 | 0 (🔴) | The refund agent uses a shared, long-lived `BILLING_ADMIN_KEY`. The tool list includes `delete_account` and `cancel_subscription`. The model chooses the tool. No kill switch, no limits, no owner. |
| C9 | 0 | Evals are a manual notebook from March and aren't in CI (CI runs lint and unit tests only). No monitoring, no rollback (no pinned version to roll back to). |

**Claim–reality gaps (all must be found):**
1. "Every AI output is logged immutably": the table is mutable, and `/chat/quick` doesn't log at all.
2. "A human approves every refund": the `auto_approve` bypass, and approval re-runs the model.
3. "Your data is never used to train AI models": the nightly fine-tune export, plus vendor retention left at default.
4. "Strictly isolated": a client-supplied tenant ID on a shared index, and a cross-tenant export.
5. "All AI answers show sources": sources only appear in debug mode.

**Reconstruction test:** mostly **No**.

## Fixture 02: ClaimAssist design doc (doc mode)

**Tier:** T3. Insurance claims decisions about people, including fraud referral. Within EU AI Act scope for Ireland: the Annex III insurance category covers risk assessment and pricing for life and health insurance, so P&C claims triage is arguably *not* Annex III. A good audit sets T3 on consequential-decision grounds either way.
**Expected verdict:** GAPS. Doc mode caps every control at 2, so nothing can reach the required 3. The report must say that code evidence is needed to reach Proven, and must not call the system NOT DEFENSIBLE just because of the cap.

| Control | Expected (doc max 2) | Key points |
|---|---|---|
| C1 | 2 | Pinned snapshot; prompt SHA, model snapshot and config hash stamped on every output. |
| C2 | 2 | Chunk IDs and document versions stored and shown. |
| C3 | 1–2 | Strong design (INSERT-only, hash chain, captures decision and diff), but **retention is undefined**. Score 1, or 2 with a 🟡 retention gap. |
| C4 | 1 | Strong for adjusters, but **policyholders aren't told AI was involved**. Self-reported model confidence is a weak signal. |
| C5 | 2 | Network-enforced Gateway; fails closed. Scans both input and document text. |
| C6 | 2 | Enforced by the server-side API; SIU override needs a reason. |
| C7 | 2 | Per-claim namespace, zero retention, no fine-tuning. |
| C8 | 1 | Dedicated identity and read-only tools are good; **credential type and lifetime undefined**; no kill switch or owner named. |
| C9 | 1 | One-off offline eval; weekly manual sample; **no eval gate on model or prompt changes**, no drift monitoring, no rollback described. |

**Valid extra finding:** `get_claim_history` runs with read scope on the *whole* claims DB, which sits uneasily with "cross-claim retrieval isn't possible". It is legitimate as a *possible* claim–reality gap (🟡, confirm), because reading the same policyholder's prior claims is normal fraud practice.

**Valid extra finding:** the fraud-signal model's version isn't recorded alongside the LLM's (§2 stamps only the LLM snapshot). That makes C1 = 1 defensible.

**Must NOT:** invent code-level bypasses; score anything 3; fail the system only because of the doc-mode cap.
