# Airtable schema - base `HR Screening`

Create an Airtable base named **HR Screening** with the table below.

## Table: `Candidates`

| Field | Type | Notes |
|-------|------|-------|
| Name | Single line text | Primary |
| Email | Email | |
| Job | Single select | e.g. Data Analyst, Full Stack Developer, HR Assistant |
| LinkedIn | URL | Optional |
| Summary | Long text | Text from Tally |
| Resume | Attachment | PDF/DOCX from Tally (up to ~10 MB on free) |
| Score | Number | 0-100 from the AI |
| Classification | Single select | `High` / `Medium` / `Low` |
| AI_Reason | Long text | Gemini justification |
| Extracted_Skills | Long text | List or textual JSON |
| Suggested_Next_Step | Single line text | e.g. Schedule technical interview |
| Status | Single select | `New`, `Under_Review`, `Awaiting_HITL`, `Approved`, `Auto_Rejected`, `HITL_Rejected`, `Error` |
| Human_Decision | Single select | `Pending`, `Approved`, `Rejected` |
| Approved_By | Single line text | Slack user when available |
| Tally_Submission_Id | Single line text | Idempotency / tracing |
| Record_URL | URL | Direct record link (for Slack) |
| Error_Detail | Long text | Filled on failures |
| Created_At | Created time | Automatic |
| Updated_At | Last modified time | Automatic |

## Suggested views
- **HITL queue:** Status = `Awaiting_HITL`
- **Approved:** Status = `Approved`
- **Rejected:** Status in `Auto_Rejected` or `HITL_Rejected`
- **Errors:** Status = `Error`

## Sharing
Share the base as **read-only** or drop the screenshot in the README (`docs/images/print-airtable-candidato.png`).
