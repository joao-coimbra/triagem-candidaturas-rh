# Prompt: montar e testar o cenário via chat de IA

Use isto num agente com acesso ao repo (idealmente Cursor Agent na pasta do projeto).

## Antes de colar o prompt

Confirme:

- [ ] Docker Desktop rodando
- [ ] Este repositório aberto como workspace
- [ ] Contas Tally, Airtable, Gemini (AI Studio), Slack e Gmail disponíveis
- [ ] Você consegue criar um túnel público para a porta `5678` (se for testar Tally de verdade)

Sem isso o agente só chega até o checklist do que falta.

## Prompt completo

```text
Contexto: repositório UniFECAF "Triagem Inteligente de Candidaturas RH".
Stack travada: Tally -> n8n (Docker) -> Airtable -> Gemini -> Slack HITL -> Gmail.

Leia primeiro:
- README.md
- n8n/SETUP-WORKFLOW.md
- n8n/triagem-candidaturas.json (só para entender nós/credenciais)
- configs/airtable-schema.md
- configs/tally-form.md
- configs/gemini-prompt.md
- .env.example
- n8n/payload-teste-tally.json

Missão: deixar o ambiente pronto para eu testar (ou o mais perto possível), sem inventar secrets.

Passos obrigatórios:
1. Checar Docker e subir `docker compose up -d`. Confirmar http://localhost:5678.
2. Garantir `.env` a partir de `.env.example` com placeholders claros do que eu preciso preencher.
3. Me passar um checklist objetivo do que criar nas UIs externas (Airtable base/tabela, form Tally + webhook, Slack bot/canal, Gmail OAuth, GEMINI_API_KEY) com a ordem certa.
4. Se o n8n estiver no ar, orientar import do workflow `n8n/triagem-candidaturas.json` e quais nós pedem credencial.
5. Explicar túnel (Cloudflare Tunnel ou ngrok): WEBHOOK_URL apontando para /webhook/tally-candidatura.
6. Preparar os 3 testes:
   - T1 perfil bom (deve ir ao Slack e, com approve, mandar Gmail)
   - T2 perfil fraco (Auto_Rejected)
   - T3 IA quebrada (HITL + Error / Error_Detail)
   Inclua texto de exemplo para colar no Tally e/ou curl usando payload-teste-tally.json.
7. Critérios de aceite: workflow ativo, webhook alcançável, um registro aparece no Airtable, ramo HITL ou rejeição automática observado.
8. Não commitar secrets. Não reescrever o README a menos que eu peça.
9. Resposta final em 3 blocos curtos: (A) status atual (B) o que falta eu fazer na mão (C) próximo comando único.
```



## Depois que o agente terminar

1. Complete as contas/chaves que ele listou.
2. Rode T1 e salve os prints nos caminhos do README (`docs/print-*.png`) para a parte teórica.
3. No Slack, use os links **Aprovar** / **Reprovar** (webhook `hitl-decisao`). Não há Wait nem resume URL no n8n.

