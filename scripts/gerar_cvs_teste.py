"""Gera CVs PDF de teste (forte e fraco) para a demo de triagem."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "test-cvs"


def build(path: Path, blocks: list[tuple[str, str]]) -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=14)
    small = ParagraphStyle("s", parent=styles["Normal"], fontSize=9, leading=12, textColor="#333333")

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    story = []
    for kind, text in blocks:
        style = {"title": title, "h2": h2, "small": small}.get(kind, body)
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 2))
    doc.build(story)
    print("wrote", path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    strong = [
        ("title", "Ana Beatriz Ferreira"),
        (
            "small",
            "Full Stack Developer | São Paulo, SP | ana.ferreira.dev@email.com | linkedin.com/in/anaferreira-fs",
        ),
        ("h2", "Resumo"),
        (
            "body",
            "Desenvolvedora full stack com 5 anos de experiência em TypeScript, React, Node.js e PostgreSQL. "
            "Atuei em produtos SaaS B2B, com entregas de APIs REST, autenticação OAuth, filas e CI/CD. "
            "Foco em código limpo, testes e automação de processos.",
        ),
        ("h2", "Experiência"),
        (
            "body",
            "<b>Nexo Digital — Full Stack Developer</b> (2022–atual)<br/>"
            "• Liderei a migração de um monolito legado para Node.js + React, reduzindo tempo de deploy em 40%.<br/>"
            "• Implementei autenticação OAuth2 e webhooks com retries idempotentes.<br/>"
            "• Modelei PostgreSQL (índices, migrations) e monitei p95 de API.<br/>"
            "• Stack: TypeScript, NestJS, Next.js, Docker, GitHub Actions, Redis.",
        ),
        (
            "body",
            "<b>Orbit Labs — Desenvolvedora Pleno</b> (2020–2022)<br/>"
            "• Construí dashboards React e APIs Express para RH e onboarding.<br/>"
            "• Integrações com Slack e Airtable via webhooks; documentação OpenAPI.<br/>"
            "• Pair programming e code review em time de 6 pessoas.",
        ),
        ("h2", "Formação"),
        ("body", "Bacharelado em Ciência da Computação — USP (2016–2020)"),
        ("h2", "Skills"),
        (
            "body",
            "TypeScript, JavaScript, React, Next.js, Node.js, NestJS, PostgreSQL, Docker, "
            "n8n, Git, testes (Jest/Playwright), CI/CD, REST, OAuth2.",
        ),
        ("h2", "Projetos"),
        (
            "body",
            "• Pipeline de triagem de candidaturas (forms → IA → HITL Slack).<br/>"
            "• Biblioteca interna de componentes React com Storybook.",
        ),
    ]

    weak = [
        ("title", "Carlos Souza"),
        ("small", "São Paulo | carlos.souza@email.com"),
        ("h2", "Objetivo"),
        ("body", "Busco uma vaga de emprego na área de informática / desenvolvimento."),
        ("h2", "Experiência"),
        (
            "body",
            "<b>Loja do Bairro — Atendente</b> (2023–2024)<br/>"
            "Atendimento ao cliente, caixa e organização de estoque.",
        ),
        (
            "body",
            "<b>Freelance</b> (2024)<br/>"
            "Fiz algumas páginas em HTML e CSS para conhecidos. Sem repositório público.",
        ),
        ("h2", "Formação"),
        ("body", "Ensino médio completo. Curso online introdutório de programação (não finalizado)."),
        ("h2", "Skills"),
        ("body", "Word, Excel, WhatsApp, HTML básico, pouco JavaScript."),
        ("h2", "Observações"),
        (
            "body",
            "Não tenho experiência com React, Node, TypeScript, bancos de dados, Docker ou APIs. "
            "Nunca trabalhei em time de produto de software.",
        ),
    ]

    build(OUT / "cv-forte-fullstack.pdf", strong)
    build(OUT / "cv-fraco-fullstack.pdf", weak)


if __name__ == "__main__":
    main()
