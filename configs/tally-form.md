# Formulário Tally - Candidatura RH

## Objetivo
Capturar a candidatura e disparar o webhook do n8n.

## Campos do form

| Label no Tally | Tipo | Obrigatório | Mapeamento n8n |
|----------------|------|-------------|----------------|
| Nome completo | Short text | Sim | `nome` |
| E-mail | Email | Sim | `email` |
| Vaga de interesse | Dropdown | Sim | `vaga` |
| LinkedIn | URL / Short text | Não | `linkedin` |
| Conte um pouco da sua experiência | Long text | Sim | `resumo` |
| Currículo (PDF) | File upload | Sim | `curriculo` (URL/arquivo) |

### Opções do dropdown `Vaga de interesse` (exemplo)
- Analista de Dados
- Desenvolvedor Full Stack
- Assistente de RH
- Product Designer

## Integração com n8n
1. Publique o formulário no Tally.
2. Em **Integrations → Webhooks**, cole a URL de produção do nó Webhook do n8n  
   Ex.: `https://SEU-TUNEL/webhook/tally-candidatura`
3. Envie uma resposta de teste para o n8n capturar o payload.
4. Alternativa: use o nó **Tally Trigger** no n8n com API key (também free).

## Validação pelo professor
- Link público do form no README / vídeo
- Print da aba Integrations com o webhook configurado (`docs/images/print-tally-webhook.png`)
- Submissão de teste durante a demo
