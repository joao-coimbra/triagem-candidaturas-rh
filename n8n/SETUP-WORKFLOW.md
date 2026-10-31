# Setup do workflow n8n

## Importar
1. Suba o n8n (`docker compose up -d` na raiz do projeto).
2. Abra `http://localhost:5678`.
3. **Workflows → Import from File** → selecione `triagem-candidaturas.json`.
4. Religue as credenciais (Airtable, Slack, Gmail) nos nós marcados.

## Variáveis de ambiente recomendadas
No Docker / host, defina pelo menos:
- `GEMINI_API_KEY`
- `AIRTABLE_BASE_ID`
- `AIRTABLE_TABLE_ID` (id da tabela Candidates; o workflow usa `$env.AIRTABLE_TABLE_ID`)
- `SLACK_CHANNEL_RECRUTAMENTO` (ex.: `#rh-triagem`)
- `GEMINI_MODEL` (default `gemini-2.5-flash`)
- `SCORE_HITL_MINIMO` (default `50`)
- `WEBHOOK_URL` (URL pública se usar tunnel; também base dos links Aprovar/Reprovar)
- `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` (necessário para `$env.AIRTABLE_*` / Gemini no workflow)

No n8n: **Settings → Variables** ou env do container.

## Credenciais na UI
| Credencial | Onde obter |
|------------|------------|
| Airtable PAT | airtable.com → Developer hub → Personal access tokens (scopes: `data.records:read/write`, `schema.bases:read/write`) |
| Slack Bot | api.slack.com → Create App → `chat:write` + `channels:read`/`groups:read`; no canal privado `#rh-triagem` rode `/invite @hr_screening_bot` |
| Gmail OAuth2 | Google Cloud Console → OAuth client → n8n Gmail credential |
| Gemini | aistudio.google.com → API key (via query `key` no HTTP Request) |

## Tally → Webhook
1. Ative o workflow.
2. Copie a Production URL do nó **Webhook Tally** (`/webhook/tally-candidatura`).
3. Se estiver em localhost, publique um tunnel e use essa URL base em `WEBHOOK_URL`.
4. No Tally: form → Integrations → Webhooks → cole a URL.

## HITL (Slack → webhook)
A triagem **não espera** no n8n. Depois do Slack, a execução termina; a decisão humana é assíncrona.

1. No Slack, abra o Airtable se quiser revisar o currículo.
2. Clique em **Aprovar** ou **Reprovar** na própria mensagem (não precisa abrir o n8n).
3. Os links usam `WEBHOOK_URL` + `/webhook/hitl-decisao?recordId=...&decision=approve|reject`.
4. O webhook atualiza o Airtable (`Approved` / `HITL_Rejected`) e, se aprovado, dispara o Gmail.
5. O browser mostra “Decisão registrada: aprovado/reprovado”.

## Anexar PDF no Airtable
O webhook do Tally envia URLs de arquivo. Depois do create, você pode:
- baixar o arquivo com HTTP Request e fazer upload no campo Attachment; ou
- colar a URL no campo LinkedIn/Resumo na demo e anexar o PDF manualmente uma vez para evidência.

Para a rubrica, o importante é o Attachment existir no registro revisado no HITL.

## Teste ponta a ponta
1. Submissão Tally com score esperado alto (texto forte) → Slack → approve → Gmail + Airtable `Approved`.
2. Submissão fraca → `Auto_Rejected` sem e-mail de convite.
3. Desligar API Gemini / chave inválida → cai em HITL com `Error` / `Error_Detail`.
