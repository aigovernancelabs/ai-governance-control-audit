# AI Governance Control Audit: Ledgerly Helpdesk Copilot + Refund Agent

**Defensibility: NOT DEFENSIBLE**. Tier T2 (T3 on the refund-agent path), code mode
Any logged-in user can make the refund agent move money, or delete an account, with no human approval, while the published Trust-page policy promises the opposite.

**Controls at required level:** 0/9 · **Claim–reality gaps:** 5 · **Bypasses:** 7

**Tier assumption (labelled):** B2B invoicing SaaS, ~1,100 business customers, EU + North America (README.md:3), so T2. The refund agent can issue refunds, cancel subscriptions and delete accounts (agents/refund_agent.py:8-13), which are autonomous actions with financial effect. That path is T3, so C1, C3, C5, C6 and C8 are held to level 3.

## Scorecard
| Control | Required | Actual | Evidence | Gap |
|---|---|---|---|---|
| C1 Version traceability | 3 | 0 | Model is the alias `gpt-4o`, "tracks latest" (config.yaml:3). Prompts are inline f-strings (app/llm.py:9, agents/refund_agent.py:17). No model or prompt ID stored per output (app/audit.py:6). | 3 🔴 |
| C2 Source attribution | 2 | 1 | Source IDs come from the retrieval layer and go into the response (app/main.py:26), but they're never persisted (app/audit.py:4) and have no document versions. /chat/quick has no grounding (main.py:31). | 1 🟡 |
| C3 Immutable audit log | 3 | 0 | `ai_events` is a mutable table: `GRANT ... UPDATE, DELETE` (db/schema.sql:9), and `amend_event` rewrites answers (app/audit.py:10-12). There's no viewer, no action and no retention. /chat/quick and refunds aren't recorded. | 3 🔴 |
| C4 Embedded explainability | 2 | 0 | Sources render only when `debug` is set (web/ChatPanel.tsx:17). The "Ask Lumi ✨" header (line 12) isn't a clear AI label. There's no deferral or uncertainty state. | 2 🔴 |
| C5 Pipeline guardrails | 3 | 1 | `redact_pii` runs before the model on /chat (main.py:22). Injection check fails open (guardrails.py:16-18). /chat/quick and the refund agent skip all guardrails. Retrieved docs aren't scanned. Output check is off (config.yaml:10). Raw question and email are logged before redaction (main.py:20). | 2 🔴 |
| C6 Human approval + logging | 3 | 0 | `auto_approve=true` executes directly (main.py:36,40). /approve re-runs the model and executes a new plan, with no stored draft or approval record (main.py:43-45). Only an app-log line is written, rotated after 14 days. | 3 🔴 |
| C7 Tenant isolation + data use | 3 | 0 | Shared index (retrieval.py:3) filtered by a `tenant_id` from the request body (main.py:15,23; retrieval.py:6; ChatPanel.tsx:6). A nightly job exports all tenants' conversations for fine-tuning (jobs/nightly_finetune_export.py:10-12). Vendor retention is `default` (config.yaml:5). | 3 🔴 |
| C8 Agent identity + authority | 3 | 0 | Shared `BILLING_ADMIN_KEY`, rotated yearly (refund_agent.py:5-6). The model picks any tool, including `delete_account` (lines 8-13, 20). No allowlist enforcement, limits, kill switch, owner or autonomy level. | 3 🔴 |
| C9 Evals + monitoring | 2 | 0 | Manual 40-ticket notebook run in March (evals/notebook_notes.md:2-3). CI runs only ruff and pytest (.github_workflow_ci.yml:5-6). No monitoring, alerting, runbook or rollback. | 2 🔴 |

## Claim–reality gaps
All five claims are in docs/AI_POLICY.md, which is published on the Trust page (README.md:10).
1. 🔴 **"Every AI output is logged immutably and retained for 2 years"** (line 3). The log table is updatable and deletable (db/schema.sql:9), `amend_event` overwrites answers (app/audit.py:12), no retention is defined, and /chat/quick (main.py:28-32) and refund actions aren't logged at all.
2. 🔴 **"A human approves every refund before any money moves"** (line 4). `auto_approve=true` executes with no human (main.py:40), and /approve executes a plan the human never saw (main.py:45).
3. 🔴 **"Your data is never used to train AI models"** (line 5). `nightly_finetune_export.py` exports yesterday's conversations "for fine-tuning a cheaper model" to s3://ledgerly-ml/finetune/, and it's enabled (config.yaml:16).
4. 🔴 **"Each customer's data is strictly isolated"** (line 6). One shared index is filtered by a client-supplied `tenant_id` (retrieval.py:6, ChatPanel.tsx:6), and the fine-tune export pools every tenant's data into one file.
5. 🔴 **"All AI answers show the help-centre sources they are based on"** (line 7). Sources are hidden unless `debug` is set (ChatPanel.tsx:17), and /chat/quick returns no sources (main.py:32).

## Bypasses (7)
1. `/chat/quick` reaches the model with no injection check, no redaction, no retrieval scoping and no audit record (main.py:28-32). Affects C5 and C3.
2. `check_injection` swallows every exception (guardrails.py:16-18), so the check fails open. Affects C5.
3. The refund agent sends raw ticket content to the model with no redaction or injection check, and the model's JSON then picks the tool (refund_agent.py:16-20). Affects C5.
4. The `auto_approve` request flag executes the action without approval (main.py:36,40). Affects C6.
5. `/actions/refund/approve` executes a freshly generated plan. No draft or approval record is required, so any user can call it directly (main.py:43-45). Affects C6.
6. The retrieval tenant filter takes the caller-controlled `tenant_id` (main.py:15,23). Affects C7.
7. The refund routes accept any `ticket_id` without checking it belongs to the caller's tenant, and execute it with the admin key (main.py:39-45; refund_agent.py:6,16). This assumes BillingAPI does no per-tenant check. Affects C7 and C8.

## Reconstruction test
Scenario: 90 days ago, the copilot told tenant A's support user to refund a customer, and the refund agent then issued the refund. The customer disputes it.

| Question | Answerable? | From where |
|---|---|---|
| Which model and prompt version produced it? | No | Alias `gpt-4o`, inline prompt, nothing stored (C1) |
| What sources or data did it use? | No | Source IDs returned, never stored (C2) |
| Who saw it, and what happened next? | Partly | `ai_events` has the user and an answer that may have been amended. It has no action link. The 14-day app log is gone (C3) |
| What was the user shown as the basis? | No | Sources hidden by default, and the UI state isn't recorded (C4) |
| Which guardrails ran, and what did they catch? | No | No guardrail results logged, and injection failures are silent (C5) |
| Who approved the action, and what did they change? | No | One app-log line, rotated after 14 days. No draft and no edits. `auto_approve` leaves nothing (C6) |
| Did any other tenant's data contribute? | No | The tenant ID came from the client, and doc IDs weren't stored (C7) |
| Which identity executed the action, and with what permissions? | No | Shared admin billing key with full scope (C8) |
| Had this model and prompt version passed evals? | No | The version is unknown, and only a March notebook exists (C9) |

**You could not reconstruct this decision.**

## Top gaps
| # | Gap | Severity | Consequence | Obligation/expectation it fails |
|---|---|---|---|---|
| 1 | Refunds and account changes execute without enforced human approval, under a shared admin key with destructive tools (C6, C8) | 🔴 bypass + claim | An injected ticket or one API flag can move money or delete a customer account, and "a human approves every refund" becomes a false statement | EU AI Act Art. 14 human oversight, Art. 15 cybersecurity (if in scope); GDPR Art. 22, Art. 32; "Can the AI take actions without approval? How do you stop an agent?" |
| 2 | Tenant scope is set by the client, and all tenants' conversations are exported for fine-tuning (C7) | 🔴 bypass + 2 claims | A cross-tenant leak, plus a "never train on your data" promise your own job contradicts. That's a deceptive-practices risk and will kill enterprise deals | GDPR Art. 5(1)(b), Art. 28, Art. 32; PIPEDA consent for new purposes; Quebec Law 25 purpose limitation; SOC 2 confidentiality |
| 3 | Guardrails are bypassable, fail open, skip retrieved content and log PII before redaction (C5) | 🔴 3 bypasses | Prompt injection and PII leakage to the vendor and to logs | EU AI Act Art. 15; GDPR Art. 25, Art. 32; OWASP LLM01/LLM02 |
| 4 | The "immutable" audit log is a mutable table with an amend function (C3) | 🔴 claim | Incident and dispute records can be rewritten, and the policy claim fails due diligence | EU AI Act Art. 12, Art. 19/26(6); GDPR Art. 5(1)(f), Art. 33; SOC 2 logging |
| 5 | No model pinning, no prompt versioning, no eval gate or monitoring (C1, C9) | 🔴 | A vendor snapshot change silently alters answers and refund decisions, and there's no rollback target | EU AI Act Art. 11/12, Art. 72; ISO/IEC 42001; NIST AI RMF Measure/Manage |
| 6 | Sources are hidden in the UI, not stored, and there's no AI label (C4, C2) | 🔴 claim | Users over-trust wrong answers, and "all answers show sources" is false | EU AI Act Art. 13, Art. 50; GDPR Art. 13/14 |

## Tickets
1. **[C6] Enforce server-side refund approval bound to a stored draft**
Why: Closes bypasses 4–5 and makes the refund claim true.
Change: Remove `auto_approve` (main.py:36) and `execute`. `/actions/refund` stores the draft. `/approve` takes the `draft_id`, executes exactly that action, and logs the approver, decision and edits (ticket 5).
Acceptance: A test proves no billing tool runs without an approval row that matches the draft hash.
Effort: M   Owner: Backend lead

2. **[C7] Derive tenant scope from the authenticated identity**
Why: Closes bypasses 6–7 and the "strictly isolated" claim.
Change: Drop `tenant_id` from `ChatReq` and ChatPanel.tsx:6, and use `user.tenant_id`. Give each tenant its own namespace in place of `helpdesk-shared`. Check `ticket_id` belongs to the caller's tenant before `run_refund`.
Acceptance: A tenant A user asking for tenant B's ID or ticket gets a 403.
Effort: M   Owner: Platform lead

3. **[C7] Stop training on customer data**
Why: Removes a direct contradiction of "never used to train".
Change: Set `fine_tune_export: disabled` and purge s3://ledgerly-ml/finetune/. Re-enable only with per-tenant opt-in and redaction. Set vendor zero-retention or no-training terms (config.yaml:5).
Acceptance: CI fails if the export is enabled without an opt-in check. The vendor setting is documented.
Effort: S   Owner: Head of Data + Legal

4. **[C5] Make guardrails mandatory, fail-closed middleware**
Why: Closes bypasses 1–3 and answers the injection and PII question.
Change: Wrap `ask_model` so redaction, injection checks (on user input, retrieved docs and ticket text) and output checks always run. On error, `check_injection` raises. Remove or wrap `/chat/quick`. Log after redaction (main.py:20).
Acceptance: Tests show a classifier error blocks the request and every route uses the wrapper.
Effort: M   Owner: Backend lead

5. **[C3] Replace `ai_events` with an append-only ledger**
Why: Makes the "immutable, 2 years" claim true and enables reconstruction.
Change: Revoke UPDATE and DELETE (schema.sql:9) and delete `amend_event`; record corrections as new rows. Add viewer, action, model, prompt, source and guardrail fields. Hash-chain the rows, with object lock and 2-year retention. Cover /chat/quick and refunds.
Acceptance: A test proves `copilot_app` cannot UPDATE or DELETE.
Effort: M   Owner: Backend lead

6. **[C8] Give the refund agent a least-privilege identity**
Why: Limits the blast radius and answers the agent-access question.
Change: Replace `BILLING_ADMIN_KEY` with a short-lived token scoped to `issue_refund`. Remove the other tools from `TOOLS` and reject anything off the allowlist. Add an amount cap, kill switch, owner and autonomy level.
Acceptance: Model output `delete_account` is rejected in tests. The kill switch is tested.
Effort: M   Owner: Platform lead

7. **[C1, C9] Pin models, version prompts, gate on evals**
Why: Enables rollback, version answers and regression detection.
Change: Pin a dated gpt-4o snapshot (config.yaml:3). Move the prompts in llm.py:9 and refund_agent.py:17 into a versioned registry, and store `model` and `prompt_hash` per output. Automate the 40-ticket eval with refund and injection cases as a CI gate. Add drift alerts.
Acceptance: CI fails below threshold.
Effort: L   Owner: ML lead

8. **[C4, C2] Show and store citations by default**
Why: Makes "all answers show sources" true and supports AI disclosure.
Change: Always render `sources` with snippets (ChatPanel.tsx:17). Add an "AI-generated" label and a handoff state. Persist source IDs and doc versions in the ledger (ticket 5).
Acceptance: A UI test with `debug=false` shows sources and the label. The audit row has source IDs.
Effort: S   Owner: Frontend lead

**Backlog:** none beyond the tickets (C2's 🟡 is merged into ticket 8).
**Verification:** none (code mode, no mode cap applies).

## What's already strong
- PII redaction (email and card) runs before the model call on /chat (app/main.py:22) and has a unit test (tests/test_guardrails.py:3-4).
- Citations come from retrieval results, not model-generated text (app/main.py:26), so they can't be hallucinated once they're shown.
- The refund agent defaults to drafting: `execute=False` (agents/refund_agent.py:15).
- Every route requires an authenticated user (`Depends(current_user)`, main.py:19,29,39,44).

## Audit limits
- Not in the repo: `auth`, `db`, `billing_client`, `injection_classifier`, `vectordb`, the browser extension, and the actual fine-tuning job. I assumed BillingAPI and the vector DB enforce no tenant scoping of their own.
- Production DB grants, S3 bucket policies, object lock, IAM and vendor contract terms weren't visible. Runtime config may differ from config.yaml.
- `guardrails.injection_check: true` (config.yaml:9) is never read by the code, so it controls nothing.
- The tier is assumed: T2 overall, T3 on the refund path.

---
*Evidence-based control audit, not legal advice or certification. Regulatory references indicate where a control provides evidence; applicability depends on scope.*
