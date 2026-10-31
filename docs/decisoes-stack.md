# Decisões de stack - Etapa 1

Registro das escolhas de ferramentas para o projeto **Triagem Inteligente de Candidaturas RH**.
Essas decisões alimentam a Parte Teórica (`parte-teorica.html` / `arquitetura.md`) e o `README.md`.

| Papel | Ferramenta | Motivo |
|-------|------------|--------|
| Entrada | **Tally** | Form mais profissional que Google Forms; free; webhook e integração n8n nativos |
| Orquestração | **n8n (Docker self-host)** | Citado no PDF; Community Edition gratuita; professor replica com `docker compose` |
| Persistência | **Airtable** | Low-code alinhado ao curso; Attachment para PDF; status e auditoria |
| IA | **Google Gemini** (AI Studio) | Classifica aderência à vaga; camada gratuita com cota |
| HITL | **Slack** + link Airtable | Aprovar/Reprovar sem UI admin; RH revisa currículo no Airtable |
| Ação | **Gmail** | Convite/comunicação ao candidato após aprovação humana |
| PDF | **Airtable Attachment** | Sem R2; complexidade desnecessária para a rubrica |
| Auth no form | **Não** | Candidatura pública; identidade via nome/e-mail |

## Fora do MVP
- Google Calendar (mencionado só como evolução)
- better-t-stack / Better Auth / painel admin de RH
- Cloudflare R2 para arquivos
- n8n Cloud (sem plano free permanente; só trial)

## Fluxo resumido
`Tally → n8n → Airtable → Gemini → IF → Slack HITL → Gmail → Airtable`
