## Learned User Preferences

- Prefers n8n (local Docker) over Power Platform or Make for this automation work.
- Prefers Airtable over Google Sheets for persistence; sees Sheets as too basic for a low-code portfolio.
- Chose Tally for form intake (nicer than Google Forms); likes building custom UIs but skips heavy auth stacks for public candidacy forms.
- HITL preference: Slack Aprovar/Reprovar links (webhook) plus Airtable record link; RH must decide in Slack without opening n8n or Wait URLs; not a custom RH admin UI.
- Prefers Gemini (free AI Studio tier) for classification; cloud free tiers are always rate-limited, and Ollama is the truly free local option if needed; avoid paid LLM APIs when the rubric does not require them.
- Prefers Gmail over Resend for MVP candidate email (native n8n OAuth, fewer accounts for the professor to reproduce); candidate-facing email and Slack copy should be Portuguese.
- Prefers English for the AI JSON contract and the Airtable Candidates schema; AI_Reason and Suggested_Next_Step prose should be Portuguese for Slack/demo.
- README should stay a direct GitHub-style intro and how-to-run guide, not an academic delivery essay; TOC, topic emojis, and a single Mermaid sequence diagram are welcome; describe HITL in prose only.
- Avoid em dashes; prefer natural human Portuguese and cut AI-generic wording.
- Stack and design decisions belong in the delivery PDF / theoretical docs, not stuffed into the README.
- Theoretical docs should look authored: keep `docs/parte-teorica.html` as the written source and `docs/Arquitetura-Triagem-RH.pdf` as the delivery artifact (ABNT layout in the RadarInvest vein). Do not spotlight PDF generators in the README; avoid obvious auto-generated-doc tooling in the public story.
- Prefers locking the tool base first, then building the project part by part; minimize manual demo-prep clicks when the agent can handle them.

## Learned Workspace Facts

- This repo is a UniFECAF low-code module deliverable: intelligent RH candidature triage with AI and human-in-the-loop.
- Locked stack: Tally -> n8n (Docker Compose) -> Airtable -> Gemini -> Slack HITL -> Gmail.
- HITL is Slack Aprovar/Reprovar webhook links (not n8n Wait resume URLs); Airtable Attachment/Resume holds CV PDFs; Cloudflare R2, Google Calendar, and full RH admin UI are out of MVP.
- Workflow export lives at `n8n/triagem-candidaturas.json`; setup notes at `n8n/SETUP-WORKFLOW.md`.
- Theoretical delivery: authored HTML at `docs/parte-teorica.html`, finished PDF at `docs/Arquitetura-Triagem-RH.pdf`; narrative mirror in `docs/arquitetura.md`; prints in `docs/images/print-*.png` (canonical evidence set used by README and the theoretical HTML). No `docs/gerar_pdf.py`. Optional maintainer-only rebuild may live quietly in `scripts/build-pdf.mjs` (not README material). No separate `evidencias/` or `entrega/` folders.
- AI JSON contract and Airtable Candidates schema use English field names; `Summary` is the candidate's Tally text (not AI-generated), while the model fills Score, Classification, AI_Reason, Extracted_Skills, and Suggested_Next_Step.
- Airtable record links must use `https://airtable.com/{baseId}/{tableId}/{recordId}` (base + table + record), not base/record alone.
- Video pitch roteiro is not kept in the repo.
- Assignment guidance allows n8n/Make-class tools; Power Platform is not required despite course module titles.
- Local n8n is reachable for demos at `http://localhost:5678`; Tally webhooks need a tunnel (Cloudflare Tunnel or ngrok) from localhost.
- Public GitHub remote is https://github.com/joao-coimbra/triagem-candidaturas-rh with default branch `main`.
