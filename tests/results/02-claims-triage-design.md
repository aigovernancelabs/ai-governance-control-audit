# AI Governance Control Audit: ClaimAssist triage copilot (Northwind Mutual)

**Defensibility: GAPS**. Tier T3, doc mode
The decision workflow is well built, but you could not yet show a policyholder or regulator which fraud model shaped an SIU referral, how long the record is kept, or that the AI was involved at all.

**Controls at required level:** 3/9 · **Claim–reality gaps:** 0 confirmed (1 possible: confirm) · **Bypasses:** 0

*Assumptions (labelled):* Tier T3, because the system proposes triage and fraud referrals on insurance claims, which are decisions about people in a regulated sector. "Tenant" (C7) is the individual claim, which matches the design's own isolation unit (§8). Doc mode caps every score at 2, so the effective required level is 2 for all nine controls. The fraud-signal service is treated as part of the AI path, because its output is shown to adjusters and stored with every decision. Reference date: 2026-10-05.

## Scorecard
| Control | Required | Actual | Evidence | Gap |
|---|---|---|---|---|
| C1 Version traceability | 3 (cap 2) | 1 | §2: LLM pinned (`vendor-large-2026-03-14`); `model_snapshot`, `prompt_sha`, `config_hash` stamped on every output. §5: fraud signals stored with no fraud-model version. | The LLM path is fully traced. The fraud-signal model, which drives SIU referrals, has no recorded version. |
| C2 Source attribution | 2 | 2 | §3: `chunk_id`s and document versions stored per output; the cited clause is shown from the same retrieval data. | Tool outputs (`get_claim_history`) are not listed as stored sources. Treated as minor. |
| C3 Immutable audit log | 3 (cap 2) | 1 | §5: separate DB, INSERT-only grant, daily hash chain; holds proposal, sources, signals, decision, adjuster ID, edit diff. | Retention is "to be confirmed with Legal" (undefined, so capped at 1). PII protection in the ledger is unspecified, and within-day records are unchained until the daily hash runs. |
| C4 Embedded explainability | 2 | 1 | §7: adjusters see cited clauses, weighted fraud signals and a low-confidence banner. | Policyholders, the affected people, are never told AI was involved. The banner relies on the model's self-reported confidence, which is uncalibrated. No AI label for adjusters is specified. |
| C5 Pipeline guardrails | 3 (cap 2) | 2 | §4: network-enforced single egress via the Gateway; PII redacted before the vendor; injection checks on notes and extracted text; output policy check; fails closed (`GUARDRAIL_UNAVAILABLE`). | **At cap: needs code evidence.** Photo handling (embedded text, PII) and tool-output scanning are not described. |
| C6 Human approval + logging | 3 (cap 2) | 2 | §6: the claims API rejects finalisation without an adjuster approval record; §5 logs the AI proposal, final decision and letter diff. | **At cap: needs code evidence.** Overriding an SIU referral needs a senior adjuster and a reason, while accepting one needs neither. That asymmetry pushes adjusters to defer to the AI. The override reason is not in the ledger field list. |
| C7 Tenant isolation + data use | 3 (cap 2) | 1 | §3, §8: per-claim namespace; vendor zero retention and no training; no fine-tuning on claims. | The retrieval path is isolated. The tool path is not: the §9 identity has read scope on the whole claims DB, with no server-side claim scoping. No policyholder-facing data-use statement exists. |
| C8 Agent identity + authority | 3 (cap 2) | 1 | §9: dedicated service identity; two read-only tools. | Credential type and lifetime are unspecified (capped at 1). Scope is DB-wide, not least privilege. No kill switch, rate limit, named owner or declared autonomy level. |
| C9 Evals + monitoring | 2 | 1 | §10: 600-claim offline eval (91% agreement); weekly QA sample; change request for model upgrades. | The eval doesn't gate model or prompt changes; prompt commits aren't gated at all. No drift, guardrail-rate or cost alerts, no runbook, no tested rollback, no SIU false-positive or fairness slice. |

## Claim–reality gaps
No confirmed gaps.

🟡 **Possible claim–reality gap: confirm.** §8 says "Each claim's namespace is isolated. Cross-claim retrieval isn't possible." §9 gives the orchestrator `get_claim_history` under a service identity with read scope on the **whole claims DB**. A claim-history tool reads other claims by definition. If the model chooses the claim or policyholder parameter, it could pull unrelated policyholders' claims into the context. This holds only if (a) "claim history" spans claims beyond the current one and (b) the parameter isn't fixed by the server, so it is left out of the verdict. If confirmed, it becomes a 🔴 gap and a C7 bypass, and the verdict moves to NOT DEFENSIBLE.

## Reconstruction test
Scenario: ClaimAssist proposes an SIU referral on a €4,200 water-damage claim, the adjuster approves, and the payout is delayed. 90 days later the policyholder files an access request and a complaint.

| Question | Answerable? | From where |
|---|---|---|
| Which model and prompt version produced it? | Partly: LLM snapshot and prompt SHA, yes; fraud-model version, no | C1 |
| What sources or data did it use? | Partly: chunk IDs and document versions, yes; claim-history tool output, not stored | C2 |
| Who saw it, and what happened next? | Yes, if the record is still retained (retention undefined) | C3 |
| What was the user shown as the basis? | Partly: adjuster view inferable; banner state not logged; policyholder told nothing about AI | C4 |
| Which guardrails ran, and what did they catch? | No: Gateway results are not written to the ledger | C5 |
| Who approved the action, and what did they change? | Yes: adjuster ID, decision, letter diff. Override reason not logged | C6 |
| Did any other claim's data contribute? | Partly: namespace isolated; tool reads are DB-wide and unlogged | C7 |
| Which identity executed the action, and with what permissions? | Partly: one shared service identity; tool calls not logged per claim | C8 |
| Had this model and prompt version passed evals? | No: only the launch version was evaluated | C9 |

**You could reconstruct the human decision, but not the full basis of the AI's fraud recommendation.**

## Top gaps
| # | Gap | Severity | Consequence | Obligation/expectation it fails |
|---|---|---|---|---|
| 1 | Tool identity has DB-wide read scope, with no claim scoping, owner, kill switch or credential lifetime (C7, C8) | 🟡 (🔴 if the possible gap is confirmed) | Another policyholder's claim history could enter a fraud rationale. Also contradicts the published isolation claim | GDPR Art. 5(1)(b), Art. 32; PIPEDA safeguards; Law 25 purpose limitation; "Is our data isolated? What can your agents access?" |
| 2 | Fraud-model version not recorded; eval doesn't gate changes; no monitoring (C1, C9) | 🟡 | A fraud-model or prompt change silently shifts SIU referral rates, and you can't say which version flagged whom | GDPR Art. 5(2) accountability, Art. 35 DPIA review; NIST AI RMF Measure/Manage; ISO/IEC 42001 monitoring |
| 3 | Ledger retention undefined; PII handling in the ledger unspecified (C3) | 🟡 | Records may be purged before a complaint or litigation, or kept longer than lawful | GDPR Art. 5(1)(e)/(f), Art. 30; "Immutable logs? For how long?" |
| 4 | Policyholders not told AI shaped triage; confidence signal uncalibrated (C4) | 🟡 | Policyholder complaints and regulator inquiries on fraud referrals, and over-trust of a self-reported score | GDPR Art. 13/14, Art. 15; NIST AI RMF transparency; Law 25 s. 12.1 only if a decision becomes exclusively automated |

## Tickets

**1. [C7, C8] Scope the orchestrator tool identity to the active claim and give it an owner and kill switch**
Why: closes the possible §8 contradiction and answers "what can your agents access?"
Change: `get_claim_history` takes its claim and policyholder from the server-side session, not from model arguments. Use a short-lived credential (≤1h) with row-level scope. Log every tool call to the Decision Ledger. Add a kill-switch flag, rate limits and a named owner.
Acceptance: a test requesting another policyholder's claim history is denied; flipping the flag disables tools within 1 minute.
Effort: M   Owner: Platform/Security lead

**2. [C1, C9] Version the fraud model and gate every model or prompt change on evals**
Why: needed to show which version flagged a claim and that it passed testing.
Change: stamp `fraud_model_version` on each ledger record. Run the 600-claim set plus SIU false-positive and protected-attribute slices in CI on any `prompts/` or model change. Add drift, guardrail-hit and SIU-rate alerts, a runbook, and pinned-previous-version rollback.
Acceptance: CI blocks a change that drops agreement below a set threshold; a rollback drill is completed.
Effort: L   Owner: ML lead

**3. [C3] Define ledger retention and protect PII at rest**
Why: an undefined retention period fails "how long do you keep records?" and risks losing complaint evidence.
Change: Legal sets retention per jurisdiction (Ontario, Quebec, Ireland). Enforce it with object lock or a scheduled, logged purge that no app role can run. Encrypt or tokenise PII fields. Chain every record, not daily batches. Align namespace deletion (§3) with the same period.
Acceptance: retention value in config; tests show UPDATE/DELETE fail; the hash-chain verifier passes.
Effort: M   Owner: Data platform lead + Legal

**4. [C4] Disclose AI involvement to policyholders and replace self-reported confidence**
Why: the affected person currently has no notice; access requests and complaints will surface that.
Change: add AI-assistance wording to the customer letter and privacy notice, with a route to request human review. Base the review banner on calibrated scores or eval-derived thresholds, not model self-report. Label proposals "AI-generated" in the portal. Log banner state to the ledger.
Acceptance: letter template includes the disclosure; a calibration report exists.
Effort: M   Owner: Product lead (Claims) + Compliance

**5. [Verification] Provide evidence for C5, C6**
Why: the design is strong but doc mode can't prove it; T3 requires level 3.
Change: supply code or infra config for the network egress policy, Gateway fail-closed handling, photo and tool-output scanning, and the claims-API approval check. Add a ledger field for SIU override reasons.
Acceptance: tests show a vendor call outside the Gateway is blocked, a Gateway error stops the request, and finalisation without approval is rejected.
Effort: M   Owner: Engineering lead

**Backlog:** C2: store `get_claim_history` outputs as sources (covered in part by ticket 1). C6: review the SIU-override asymmetry so that declining a referral isn't harder than accepting one (automation-bias risk).
**Verification:** C5, C6 are at cap: needs code evidence.

## What's already strong
- **Single enforced egress (§4):** vendor egress is blocked at the network layer except for the Gateway, so no route can skip guardrails. The Gateway fails closed: the adjuster works manually and no model call is made.
- **Server-side approval (§6):** the claims API rejects finalisation without an adjuster approval record, and the ledger keeps the AI draft, the decision and the letter diff.
- **Tamper-resistant ledger design (§5):** a separate database, INSERT-only role and hash chaining.
- **Strong LLM traceability and attribution (§2, §3):** pinned snapshot, prompt SHA and config hash on every output, plus chunk IDs and document versions per answer.

## Audit limits
- Doc mode: no code, infrastructure or vendor contract was seen. Every score of 2 is the cap and still needs code evidence.
- The fraud-signal service (training data, features, version control, bias testing) is out of view. Its outputs bypass the Gateway's protected-characteristic check because it isn't an LLM call.
- Regulatory scope was not determined. Property insurance triage and fraud detection are likely outside EU AI Act Annex III (which names life and health insurance pricing). GDPR (Ireland), PIPEDA and Quebec Law 25 apply to the personal data processing. All citations apply only if in scope.
- Assumed: "extracted document text" covers policyholder uploads but not photos; "claim history" may span other claims.

---
*Evidence-based control audit, not legal advice or certification. Regulatory references indicate where a control provides evidence; applicability depends on scope.*
