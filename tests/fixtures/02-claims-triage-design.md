# System Design: ClaimAssist triage copilot

*Invented test fixture. Not a real company.*

**Company:** Northwind Mutual, a property & casualty insurer operating in Ontario, Quebec and Ireland.
**Feature:** an AI copilot that reads incoming home-insurance claims (first notice of loss, photos, adjuster notes), proposes a triage category (fast-track payout ≤ €5,000 / standard / refer to Special Investigations Unit for fraud review), and drafts the customer letter.
**Users:** about 140 claims adjusters. The people affected are policyholders.

## 1. Architecture

```
Claims portal → Intake API → ClaimAssist Orchestrator → Guardrail Gateway → LLM (vendor, EU region)
                                     │                         │
                                     ├─ Retrieval (policy wording, per-policy docs)
                                     ├─ Fraud-signal service (internal ML model)
                                     └─ Decision Ledger (append-only)
```

## 2. Models and prompts
- Primary model: `vendor-large-2026-03-14`, pinned by snapshot ID in `claimassist.config`. Upgrades go through a change request.
- Prompts live in `prompts/` and are versioned by git SHA. The orchestrator stamps `model_snapshot`, `prompt_sha` and `config_hash` on every output record.

## 3. Retrieval
- Policy wordings are indexed per product line. Policyholder documents are indexed in a **per-claim namespace** that's created when the claim is opened and deleted when it closes plus the retention period.
- Every output stores the `chunk_id`s and document versions used. Adjusters see the cited policy clause next to the proposed triage.

## 4. Guardrail Gateway
- Every model call goes through the Gateway. There is no direct vendor access, and egress to the vendor is blocked at the network layer for every service except the Gateway.
- The Gateway redacts policyholder PII (names, policy numbers, bank details) before sending, and re-inserts it in the response.
- It runs injection detection on adjuster notes and on extracted document text, and checks outputs for prohibited content (for example, references to protected characteristics in fraud rationale).
- **Failure mode:** if the Gateway can't complete its checks, the request returns `GUARDRAIL_UNAVAILABLE` and the adjuster proceeds manually.

## 5. Decision Ledger
- An append-only table in a separate database. The application role has INSERT-only grants. Records are hash-chained daily.
- Each record holds: the AI proposal, the cited sources, the fraud signals, the adjuster's final decision, the adjuster ID, the time from proposal to decision, and any edits to the letter (as a diff).
- Retention: to be confirmed with Legal.

## 6. Human decision
- ClaimAssist **never** finalises a claim. Every triage category and every customer letter needs the adjuster to approve it in the claims portal, and the claims system's API rejects a finalisation without an adjuster approval record.
- An SIU referral can be overridden only by a senior adjuster, and the override needs a written reason.

## 7. Explainability to users
- Adjusters see the cited clauses, the fraud signals (with their weights), and a "low confidence — review fully" banner when the model's self-reported confidence is below threshold.
- Policyholders receive the final letter. It doesn't mention AI involvement.

## 8. Data use
- The vendor contract has zero data retention and no training on inputs.
- We don't fine-tune on claims data.
- Each claim's namespace is isolated. Cross-claim retrieval isn't possible.

## 9. Agents and tools
- The orchestrator can call two read-only tools, `get_policy` and `get_claim_history`, using a dedicated service identity with read scope on the claims DB.
- The credential type and lifetime aren't specified yet.

## 10. Quality
- Before launch we ran a 600-claim offline evaluation: triage agreement with senior adjusters was 91%.
- Post-launch: a weekly sample review by the claims QA team.
- Model upgrades go through a change request, approved by the Head of Claims.
