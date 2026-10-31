"""Fix workflow (Resume + Gemini) and run strong/weak E2E tests for pitch readiness."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF_ID = "ce2om0zBMKs75XON"
TABLE = "tblbzeyF946ZBbVSJ"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


NORM_JS = r"""// Normaliza payload do Tally (webhook FORM_RESPONSE)
const body = $input.first().json.body ?? $input.first().json;
const data = body.data ?? body;
const fields = data.fields ?? [];

const JOBS = [
  'Full Stack Developer',
  'Data Analyst',
  'HR Assistant',
  'Product Designer',
];

function resolveOption(field, raw) {
  if (raw == null) return null;
  if (typeof raw === 'object') {
    return raw.text ?? raw.label ?? raw.name ?? raw.value ?? null;
  }
  const s = String(raw);
  const opts = field.options || field.fieldOptions || [];
  const hit = opts.find((o) => o.id === s || o.uuid === s || o.value === s || o.text === s);
  if (hit) return hit.text ?? hit.label ?? hit.name ?? hit.value ?? s;
  if (/^[0-9a-f-]{36}$/i.test(s)) return null;
  return s;
}

function fieldRaw(labelOrKey) {
  return fields.find(
    (x) =>
      (x.label && String(x.label).toLowerCase() === String(labelOrKey).toLowerCase()) ||
      x.key === labelOrKey ||
      (x.title && String(x.title).toLowerCase() === String(labelOrKey).toLowerCase())
  );
}

function fieldValue(labelOrKey) {
  const f = fieldRaw(labelOrKey);
  if (!f) return null;
  if (Array.isArray(f.value)) {
    if (f.value[0]?.url) return f.value;
    return f.value
      .map((v) => resolveOption(f, v))
      .filter((x) => x != null && x !== '')
      .join(', ');
  }
  return resolveOption(f, f.value);
}

function extractResume(files) {
  const out = [];
  const arr = Array.isArray(files) ? files : files ? [files] : [];
  for (const f of arr) {
    if (!f) continue;
    if (typeof f === 'string' && f.startsWith('http')) {
      out.push({ url: f, filename: 'curriculo.pdf' });
      continue;
    }
    const url = f.url || f.downloadUrl || f.href;
    if (!url) continue;
    const filename =
      f.name ||
      f.filename ||
      f.originalName ||
      String(url).split('?')[0].split('/').pop() ||
      'curriculo.pdf';
    out.push({ url, filename });
  }
  return out;
}

const nome = fieldValue('Nome completo') ?? fieldValue('Nome') ?? data.nome ?? 'Sem nome';
const email = fieldValue('E-mail') ?? fieldValue('Email') ?? data.email ?? '';
let vaga = fieldValue('Vaga de interesse') ?? fieldValue('Vaga') ?? data.vaga ?? '';
if (!vaga || /^[0-9a-f-]{36}$/i.test(String(vaga))) {
  vaga = JOBS.includes(String(vaga)) ? vaga : 'Full Stack Developer';
}
if (!JOBS.includes(vaga)) {
  const approx = JOBS.find((j) => String(vaga).toLowerCase().includes(j.toLowerCase().split(' ')[0]));
  vaga = approx || 'Full Stack Developer';
}
const linkedin = fieldValue('LinkedIn') ?? '';
const resumo = fieldValue('Conte um pouco da sua experiência') ?? fieldValue('Resumo') ?? '';
const curriculoRaw = fieldValue('Currículo (PDF)') ?? fieldValue('Currículo') ?? [];
const resume = extractResume(curriculoRaw);

const submissionId = data.responseId ?? data.submissionId ?? body.eventId ?? $execution.id;

return [{
  json: {
    nome,
    email,
    vaga,
    linkedin,
    resumo,
    curriculo: curriculoRaw,
    resume,
    resume_url: resume[0]?.url || '',
    resume_filename: resume[0]?.filename || 'curriculo.pdf',
    tally_submission_id: String(submissionId),
    status_inicial: 'Under_Review',
    recebido_em: new Date().toISOString()
  }
}];
"""

GEMINI_BODY = (
    "={{ JSON.stringify({ "
    "contents: [{ role: 'user', parts: [{ text: "
    "'You are an HR screening assistant. Score how well the candidate fits the job.\\n\\n' + "
    "'Job: ' + String($json.vaga || '') + '\\n' + "
    "'Name: ' + String($json.nome || '') + '\\n' + "
    "'LinkedIn: ' + String($json.linkedin || '') + '\\n' + "
    "'Experience/summary:\\n' + String($json.resumo || '') + '\\n\\n' + "
    "'Respond with ONLY valid JSON (no markdown), in this shape:\\n' + "
    "'{\\\"score\\\": number 0-100, \\\"classification\\\": \\\"High\\\"|\\\"Medium\\\"|\\\"Low\\\", "
    "\\\"reason\\\": string, \\\"skills\\\": string[], \\\"next_step\\\": string}\\n' + "
    "'Criteria: relevant experience, clarity, apparent seniority, alignment with the job title.' "
    "}] }], "
    "generationConfig: { temperature: 0.2, responseMimeType: 'application/json' } "
    "}) }}"
)

RESUME_EXPR = (
    "={{ $json.resume && $json.resume.length "
    "? $json.resume "
    ": ($json.resume_url "
    "? [{ url: $json.resume_url, filename: $json.resume_filename || 'curriculo.pdf' }] "
    ": undefined) }}"
)

SCORE_EXPR = (
    "={{ ($json.score === null || $json.score === undefined || $json.score === '') "
    "? undefined : $json.score }}"
)


class N8n:
    def __init__(self) -> None:
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def call(self, method: str, path: str, data: dict | None = None) -> dict:
        body = None if data is None else json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"http://localhost:5678{path}",
            data=body,
            method=method,
            headers={
                "browser-id": "py-pitch-001",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        with self.opener.open(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}


def airtable_get(token: str, base: str, formula: str) -> list[dict]:
    q = urllib.parse.urlencode(
        {
            "filterByFormula": formula,
            "maxRecords": 5,
        }
    )
    req = urllib.request.Request(
        f"https://api.airtable.com/v0/{base}/{TABLE}?{q}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())["records"]


def patch_export() -> dict:
    path = ROOT / "n8n" / "triagem-candidaturas.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    for n in d["nodes"]:
        if n["name"] == "Normalizar Tally":
            n["parameters"]["jsCode"] = NORM_JS
        if n["name"] == "Gemini Classificar":
            n["parameters"]["jsonBody"] = GEMINI_BODY
            n["parameters"]["url"] = (
                "=https://generativelanguage.googleapis.com/v1beta/models/"
                "{{ $env.GEMINI_MODEL || 'gemini-2.5-flash' }}:generateContent"
            )
        if n["name"] == "Airtable Criar Candidato":
            n["parameters"]["columns"]["value"]["Resume"] = RESUME_EXPR
        if n["type"] == "n8n-nodes-base.airtable" and n["parameters"].get("operation") == "update":
            n["parameters"].setdefault("columns", {})
            n["parameters"]["columns"]["matchingColumns"] = ["id"]
            vals = n["parameters"]["columns"].get("value") or {}
            if "Score" in vals:
                vals["Score"] = SCORE_EXPR
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return d


def push_live(n8n: N8n, export: dict) -> None:
    n8n.call(
        "POST",
        "/rest/login",
        {
            "emailOrLdapLoginId": "joao.coimbra.188635@a.fecaf.com.br",
            "password": "UniFECAF-n8n-2026!",
        },
    )
    wf = n8n.call("GET", f"/rest/workflows/{WF_ID}")["data"]
    by_name = {n["name"]: n for n in export["nodes"]}
    for n in wf["nodes"]:
        src = by_name.get(n["name"])
        if not src:
            continue
        if n["name"] in {"Normalizar Tally", "Gemini Classificar", "Airtable Criar Candidato"}:
            creds = n.get("credentials")
            n["parameters"] = src["parameters"]
            if creds:
                n["credentials"] = creds
        if n["type"] == "n8n-nodes-base.airtable" and n["parameters"].get("operation") == "update":
            n["parameters"].setdefault("columns", {})
            n["parameters"]["columns"]["matchingColumns"] = ["id"]
            vals = n["parameters"]["columns"].get("value") or {}
            if "Score" in vals:
                vals["Score"] = SCORE_EXPR
    patched = n8n.call(
        "PATCH",
        f"/rest/workflows/{WF_ID}",
        {
            "name": wf["name"],
            "nodes": wf["nodes"],
            "connections": wf["connections"],
            "settings": wf.get("settings") or {},
            "staticData": wf.get("staticData"),
        },
    )["data"]
    act = n8n.call(
        "POST",
        f"/rest/workflows/{WF_ID}/activate",
        {"versionId": patched["versionId"]},
    )["data"]
    print("active=", act.get("active"))
    wf2 = n8n.call("GET", f"/rest/workflows/{WF_ID}")["data"]
    create = next(x for x in wf2["nodes"] if x["name"] == "Airtable Criar Candidato")
    gem = next(x for x in wf2["nodes"] if x["name"] == "Gemini Classificar")
    print("has_Resume=", "Resume" in create["parameters"]["columns"]["value"])
    print("gemini_$json=", "$json.vaga" in gem["parameters"]["jsonBody"])


def post_webhook(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def tally_like(
    *,
    nome: str,
    email: str,
    vaga: str,
    resumo: str,
    submission_id: str,
    pdf_name: str,
    pdf_url: str,
) -> dict:
    return {
        "eventType": "FORM_RESPONSE",
        "data": {
            "responseId": submission_id,
            "submissionId": submission_id,
            "fields": [
                {"label": "Nome completo", "type": "INPUT_TEXT", "value": nome},
                {"label": "E-mail", "type": "INPUT_EMAIL", "value": email},
                {
                    "label": "Vaga de interesse",
                    "type": "DROPDOWN",
                    "value": vaga,
                    "options": [
                        {"id": "1", "text": "Full Stack Developer"},
                        {"id": "2", "text": "Data Analyst"},
                        {"id": "3", "text": "HR Assistant"},
                        {"id": "4", "text": "Product Designer"},
                    ],
                },
                {"label": "LinkedIn", "type": "INPUT_LINK", "value": "https://linkedin.com/in/teste"},
                {
                    "label": "Conte um pouco da sua experiência",
                    "type": "TEXTAREA",
                    "value": resumo,
                },
                {
                    "label": "Currículo (PDF)",
                    "type": "FILE_UPLOAD",
                    "value": [{"url": pdf_url, "name": pdf_name}],
                },
            ],
        },
    }


def wait_execution(n8n: N8n, after_ts: str | None = None, timeout: int = 90) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        results = n8n.call("GET", "/rest/executions?limit=10")["data"]["results"]
        for e in results:
            if after_ts and e["startedAt"] <= after_ts:
                continue
            if e["status"] in {"success", "error", "waiting", "crashed", "canceled"}:
                # prefer newest
                return e
        time.sleep(2)
    raise TimeoutError("no execution")


def get_execution(n8n: N8n, eid: str) -> dict:
    return n8n.call("GET", f"/rest/executions/{eid}?includeData=true")["data"]


def flatten_exec(raw: dict) -> tuple[str | None, str | None, dict]:
    """Return lastNode, errorMessage, and a shallow map of interesting values."""
    arr = json.loads(raw["data"])
    rd = arr[2]
    last = arr[int(rd["lastNodeExecuted"])] if str(rd.get("lastNodeExecuted", "")).isdigit() else rd.get(
        "lastNodeExecuted"
    )
    err = None
    if rd.get("error") is not None:
        e = arr[int(rd["error"])]
        msg = e.get("message")
        if str(msg).isdigit():
            msg = arr[int(msg)]
        err = msg
    return last, err, {"status": raw.get("status"), "waitTill": raw.get("waitTill")}


def find_waiting(n8n: N8n) -> dict | None:
    results = n8n.call("GET", "/rest/executions?limit=20&status=waiting")["data"]["results"]
    return results[0] if results else None


def resume_hitl(n8n: N8n, execution_id: str, decision: str, tunnel: str) -> None:
    # n8n waiting webhook: /webhook-waiting/<executionId>/<suffix>
    # workflow uses webhookSuffix = '/' + airtable_id
    detail = get_execution(n8n, execution_id)
    arr = json.loads(detail["data"])
    # find airtable id string like rec...
    rec = None
    for v in arr:
        if isinstance(v, str) and v.startswith("rec") and len(v) >= 14:
            rec = v
            break
    if not rec:
        raise RuntimeError("airtable id not found in waiting execution")
    urls = [
        f"{tunnel}/webhook-waiting/{execution_id}/{rec}?decision={decision}",
        f"{tunnel}/webhook-waiting/{execution_id}?decision={decision}",
    ]
    last_err = None
    for u in urls:
        try:
            req = urllib.request.Request(u, method="GET")
            with urllib.request.urlopen(req, timeout=30) as resp:
                print("resume", u, resp.status, resp.read()[:200])
                return
        except Exception as e:  # noqa: BLE001
            last_err = e
            print("resume_try_fail", u, e)
    raise RuntimeError(f"resume failed: {last_err}")


def main() -> None:
    env = load_env()
    tunnel = env["CLOUDFLARE_TUNNEL_URL"].rstrip("/")
    webhook = f"{tunnel}/webhook/tally-candidatura"
    token = env["AIRTABLE_PAT"]
    base = env["AIRTABLE_BASE_ID"]
    email = env.get("TEST_CANDIDATE_EMAIL", "joao.coimbra.188635@a.fecaf.com.br")

    # use a public PDF URL Airtable can fetch (w3c dummy) + also tally-like name
    # Prefer local file hosted? Airtable needs public URL. Use w3.org dummy for reliability,
    # filename still reflects test CV names for pitch evidence.
    pdf_public = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

    print("=== patch export + live ===")
    export = patch_export()
    n8n = N8n()
    push_live(n8n, export)

    # mark time
    before = n8n.call("GET", "/rest/executions?limit=1")["data"]["results"]
    before_ts = before[0]["startedAt"] if before else ""

    print("=== STRONG path ===")
    strong = tally_like(
        nome="Ana Beatriz Ferreira",
        email=email,
        vaga="Full Stack Developer",
        resumo=(
            "5 anos full stack com TypeScript, React, NestJS e PostgreSQL. "
            "Experiencia em OAuth, webhooks, Docker e CI/CD em SaaS B2B. "
            "Busco a vaga de Full Stack Developer."
        ),
        submission_id=f"pitch-strong-{int(time.time())}",
        pdf_name="cv-forte-fullstack.pdf",
        pdf_url=pdf_public,
    )
    print("webhook_resp", post_webhook(webhook, strong))
    time.sleep(8)
    ex = wait_execution(n8n, after_ts=before_ts, timeout=120)
    print("exec_strong", ex["id"], ex["status"], ex.get("waitTill"))
    detail = get_execution(n8n, ex["id"])
    last, err, meta = flatten_exec(detail)
    print("lastNode", last, "err", err, "meta", meta)

    # poll waiting if still running
    if ex["status"] not in {"waiting", "success", "error"}:
        time.sleep(10)
        ex = n8n.call("GET", f"/rest/executions/{ex['id']}")["data"]
        print("exec_strong2", ex.get("status"), ex.get("waitTill"))

    # if error, print and stop strong HITL
    if ex["status"] == "error" or (isinstance(ex, dict) and ex.get("status") == "error"):
        d2 = get_execution(n8n, str(ex["id"]))
        last, err, _ = flatten_exec(d2)
        print("STRONG_FAILED", last, err)
    else:
        # find waiting
        waiting = None
        for _ in range(30):
            cur = n8n.call("GET", f"/rest/executions/{ex['id']}")["data"]
            if cur.get("status") == "waiting" or cur.get("waitTill"):
                waiting = cur
                break
            if cur.get("status") in {"success", "error"}:
                print("strong finished early", cur.get("status"))
                break
            time.sleep(2)
        if waiting:
            print("HITL waiting", waiting["id"])
            resume_hitl(n8n, str(waiting["id"]), "approve", tunnel)
            time.sleep(10)
            fin = n8n.call("GET", f"/rest/executions/{waiting['id']}")["data"]
            print("after_approve", fin.get("status"))

    recs = airtable_get(token, base, "FIND('Ana Beatriz Ferreira', {Name})")
    for r in recs[:3]:
        f = r["fields"]
        print(
            "AIR_STRONG",
            r["id"],
            "job=",
            f.get("Job"),
            "score=",
            f.get("Score"),
            "class=",
            f.get("Classification"),
            "status=",
            f.get("Status"),
            "resume=",
            bool(f.get("Resume")),
            "human=",
            f.get("Human_Decision"),
        )

    before2 = n8n.call("GET", "/rest/executions?limit=1")["data"]["results"][0]["startedAt"]
    print("=== WEAK path ===")
    weak = tally_like(
        nome="Carlos Souza",
        email=email,
        vaga="Full Stack Developer",
        resumo=(
            "Trabalhei com atendimento e fiz umas paginas HTML. "
            "Quero entrar em TI, mas ainda nao tenho experiencia com React, Node ou banco de dados."
        ),
        submission_id=f"pitch-weak-{int(time.time())}",
        pdf_name="cv-fraco-fullstack.pdf",
        pdf_url=pdf_public,
    )
    print("webhook_resp", post_webhook(webhook, weak))
    time.sleep(10)
    exw = wait_execution(n8n, after_ts=before2, timeout=120)
    print("exec_weak", exw["id"], exw["status"])
    dw = get_execution(n8n, exw["id"])
    lastw, errw, _ = flatten_exec(dw)
    print("weak last", lastw, "err", errw)
    for _ in range(20):
        cur = n8n.call("GET", f"/rest/executions/{exw['id']}")["data"]
        if cur.get("status") in {"success", "error", "waiting"}:
            print("weak final", cur.get("status"))
            if cur.get("status") == "error":
                lastw, errw, _ = flatten_exec(get_execution(n8n, str(exw["id"])))
                print("WEAK_FAILED", lastw, errw)
            break
        time.sleep(2)

    recs_w = airtable_get(token, base, "FIND('Carlos Souza', {Name})")
    for r in recs_w[:3]:
        f = r["fields"]
        print(
            "AIR_WEAK",
            r["id"],
            "score=",
            f.get("Score"),
            "status=",
            f.get("Status"),
            "resume=",
            bool(f.get("Resume")),
        )


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print("HTTPError", e.code, e.read().decode("utf-8", errors="replace")[:800])
        raise
