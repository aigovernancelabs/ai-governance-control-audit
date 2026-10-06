# AI Governance Control Audit

**A Claude skill from AI Governance Labs that audits what an AI system actually implements, not what its policy says.**

Most AI governance is paperwork: a policy PDF, a risk register, a slide that says "human in the loop". Due diligence, incidents and regulators don't test the paperwork. They ask whether you can show which model produced an answer, what it was based on, who approved the action, and whether another customer's data was involved.

This skill reads your **codebase**, **architecture doc** or **design**, and scores nine governance controls. Every score has to cite a file and line or a config key. If it can't, the score is zero. The output is a defensibility verdict, a test of whether you could reconstruct one AI decision after the fact, and engineering tickets your team can start on today.

## The nine controls

| # | Control | What good looks like |
|---|---|---|
| C1 | Model and version traceability | Every output is stamped with the pinned model version, the prompt-template ID and the config |
| C2 | Source attribution | The documents and records behind each answer are stored with it and drive the citations |
| C3 | Immutable audit log | Append-only record of each output, who saw it, and what action followed |
| C4 | Embedded explainability | Source snippets, an AI label and deferral signals in the product, including for the affected person |
| C5 | Enforced pipeline guardrails | PII redaction, injection detection and policy checks as mandatory middleware that fails closed |
| C6 | Human approval with logging | The AI drafts, a human approves consequential actions (enforced server-side), and both are logged |
| C7 | Tenant isolation and data-use transparency | Hard isolation boundaries set server-side; data-use claims match the code |
| C8 | Agent identity and authority | Per-agent identity, least-privilege short-lived credentials, a kill switch, a named owner |
| C9 | Evaluation and runtime monitoring | Evals gate model and prompt changes; drift monitoring; a tested rollback |

## What makes it different

- **Evidence ladder.** Each control scores Absent (0), Partial (1), Implemented (2) or Proven (3). Proven means a test or infrastructure enforcement would catch the control breaking. A design doc can reach Implemented at most; only code or infrastructure config can reach Proven.
- **Required level by context.** An internal tool, an enterprise-sold SaaS product and a system making consequential decisions about people need different bars. The skill sets the system's tier and scores the gap against the bar for that tier.
- **Claim–reality gaps.** When your trust page says "we never train on your data" and a nightly job exports conversations for fine-tuning, that's the first finding in the report.
- **Bypass hunting.** It looks for the unguarded endpoint, the `except: pass` around a guardrail, the `auto_approve` flag, and the tenant ID that comes from the request body.
- **Reconstruction test.** Pick one consequential output and ask nine questions about it 90 days later. Most systems can't answer them.
- **Consequence mapping.** Each gap is tied to the EU AI Act article, the GDPR and Canadian privacy obligations, the frameworks (NIST AI RMF, ISO/IEC 42001, OWASP LLM Top 10), and the enterprise questionnaire question it leaves you unable to answer.

## Sample output

From [`tests/fixtures/01-helpdesk-copilot`](tests/fixtures/01-helpdesk-copilot), an invented B2B support copilot with a refund agent:

> **Defensibility: NOT DEFENSIBLE**. Tier T2 (T3 on the refund-agent path), code mode
> Any logged-in user can make the refund agent move money, or delete an account, with no human approval, while the published Trust-page policy promises the opposite.
>
> **Controls at required level:** 0/9 · **Claim–reality gaps:** 5 · **Bypasses:** 7

From [`tests/fixtures/02-claims-triage-design.md`](tests/fixtures/02-claims-triage-design.md), an invented insurer's design doc:

> **Defensibility: GAPS**. Tier T3, doc mode
> The decision workflow is well built, but you could not yet show a policyholder or regulator which fraud model shaped an SIU referral, how long the record is kept, or that the AI was involved at all.

The full reports are in [`tests/results/`](tests/results/).

## Install

**Claude Code:**

```bash
git clone https://github.com/aigovernancelabs/ai-governance-control-audit.git
cp -r ai-governance-control-audit/skills/ai-governance-control-audit ~/.claude/skills/
```

**Claude apps:** zip the `skills/ai-governance-control-audit` folder and upload it under Skills in Claude's settings.

## Use

- **Code mode (best):** open the repo in Claude Code and ask: *"Run an AI governance control audit on this repo"* or *"Audit the support assistant path for governance controls."*
- **Doc mode:** attach an architecture doc, system design or PRD and ask for a governance control audit.
- **Interview mode:** with nothing written down, the skill asks up to eight targeted questions. Scores cap at Partial until there's evidence.

The audit is read-only. It doesn't run your code or call external services, and it never repeats secrets it finds.

## Tests

[`tests/fixtures/`](tests/fixtures/) contains a codebase seeded with gaps (bypasses, a fail-open guardrail, a mutable "audit" table, a cross-tenant fine-tuning export, and a policy that contradicts the code) and a strong design doc with subtle gaps. [`tests/expected.md`](tests/expected.md) is the answer key. Run the skill on each fixture without letting it see the answer key, then compare. Both verdicts and every seeded trap matched at v1.0.0.

## Limitations

- It sees what's in the repo or doc. Infrastructure, IAM, vendor consoles and other services are listed under "Audit limits" and not scored.
- Regulatory references show where a control provides evidence. Whether a regulation applies to you depends on scope, which this skill doesn't decide.
- It's not legal advice or a certification.

## Contributing

Issues and pull requests are welcome. They're especially useful for:
- new fixtures that catch a missed bypass pattern
- framework mappings
- language-specific evidence patterns.

## About

Published by **AI Governance Labs**, a practitioner-led lab that treats AI governance as an operational discipline: wired into the codebase, the API gateway and the runtime, not left in a PDF.

The nine controls build on AI Governance Labs' case study [What Good Governance Looks Like: An Example](https://aigovernancerisk.substack.com/p/what-good-governance-looks-like-an), published in [The AI Governance Brief](https://aigovernancerisk.substack.com), a weekly brief for B2B product and AI executives. Control 8 draws on AI Governance Labs' *Blueprint for Safe Autonomy* report.

## License

MIT. See [LICENSE](LICENSE).
