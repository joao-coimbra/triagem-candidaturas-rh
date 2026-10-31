"""Publish the RH candidature Tally form (Portuguese labels matching n8n Parse)."""
from __future__ import annotations

import json
import uuid
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def req(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    )
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} -> {e.code}: {err}") from e


def uid() -> str:
    return str(uuid.uuid4())


def q_title(html: str) -> dict:
    return {
        "uuid": uid(),
        "type": "TITLE",
        "groupUuid": uid(),
        "groupType": "QUESTION",
        "payload": {"html": html},
    }


def main() -> None:
    env = load_env()
    token = env["TALLY_API_KEY"]
    form_id = env.get("TALLY_FORM_ID", "PRpzKx")

    jobs = [
        "Full Stack Developer",
        "Data Analyst",
        "HR Assistant",
        "Product Designer",
    ]
    job_group = uid()
    job_options = []
    for i, text in enumerate(jobs):
        job_options.append(
            {
                "uuid": uid(),
                "type": "DROPDOWN_OPTION",
                "groupUuid": job_group,
                "groupType": "DROPDOWN",
                "payload": {
                    "index": i,
                    "isFirst": i == 0,
                    "isLast": i == len(jobs) - 1,
                    "text": text,
                },
            }
        )

    blocks = [
        {
            "uuid": uid(),
            "type": "FORM_TITLE",
            "groupUuid": uid(),
            "groupType": "TEXT",
            "payload": {
                "title": "Candidatura RH — Triagem Inteligente",
                "html": "Candidatura RH — Triagem Inteligente",
            },
        },
        q_title("Nome completo"),
        {
            "uuid": uid(),
            "type": "INPUT_TEXT",
            "groupUuid": uid(),
            "groupType": "INPUT_TEXT",
            "payload": {"isRequired": True, "placeholder": "Seu nome"},
        },
        q_title("E-mail"),
        {
            "uuid": uid(),
            "type": "INPUT_EMAIL",
            "groupUuid": uid(),
            "groupType": "INPUT_EMAIL",
            "payload": {"isRequired": True, "placeholder": "voce@email.com"},
        },
        q_title("Vaga de interesse"),
        *job_options,
        q_title("LinkedIn"),
        {
            "uuid": uid(),
            "type": "INPUT_LINK",
            "groupUuid": uid(),
            "groupType": "INPUT_LINK",
            "payload": {"isRequired": False, "placeholder": "https://linkedin.com/in/..."},
        },
        q_title("Conte um pouco da sua experiência"),
        {
            "uuid": uid(),
            "type": "TEXTAREA",
            "groupUuid": uid(),
            "groupType": "TEXTAREA",
            "payload": {
                "isRequired": True,
                "placeholder": "Resumo da experiência, stack e projetos relevantes",
            },
        },
        q_title("Currículo (PDF)"),
        {
            "uuid": uid(),
            "type": "FILE_UPLOAD",
            "groupUuid": uid(),
            "groupType": "FILE_UPLOAD",
            "payload": {"isRequired": True},
        },
    ]

    updated = req(
        "PATCH",
        f"https://api.tally.so/forms/{form_id}",
        token,
        {"status": "PUBLISHED", "blocks": blocks},
    )
    print("form:", updated.get("id"), updated.get("name"), updated.get("status"))
    print("public_url: https://tally.so/r/" + form_id)

    # persist id
    env_path = ROOT / ".env"
    text = env_path.read_text(encoding="utf-8")
    if "TALLY_FORM_ID=" in text:
        lines = []
        for line in text.splitlines():
            if line.startswith("TALLY_FORM_ID="):
                lines.append(f"TALLY_FORM_ID={form_id}")
            else:
                lines.append(line)
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        env_path.write_text(text.rstrip() + f"\nTALLY_FORM_ID={form_id}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
