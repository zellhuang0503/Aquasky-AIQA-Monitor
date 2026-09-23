#!/usr/bin/env python3
"""AQUASKY citation monitor. Explicit --run; every answer has a raw evidence file."""
from __future__ import annotations
import argparse
import configparser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlparse

import requests
from src.question_loader import load_question_records

ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = "請以繁體中文回答。請查詢公開網路資料並附上支持回答的來源；無法查證的資訊請明確說明，不要捏造。"
OFFICIAL_DOMAINS = ("aquaskyplus.com",)


def dump_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def official_url(url):
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in OFFICIAL_DOMAINS)


def extract_citations(raw):
    """Structured citations only. Body links/search results are not citation evidence."""
    result = []
    for item in raw.get("citations", []) or []:
        if isinstance(item, str):
            result.append({"url": item, "title": "", "source": "citations"})
        elif isinstance(item, dict) and item.get("url"):
            result.append({**item, "source": "citations"})
    choices = raw.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    for annotation in message.get("annotations", []) or []:
        if annotation.get("type") == "url_citation":
            citation = annotation.get("url_citation", annotation)
            if citation.get("url"):
                result.append({**citation, "source": "annotation"})
    unique = {}
    for item in result:
        if urlparse(item["url"]).scheme in ("http", "https"):
            unique.setdefault(item["url"], item)
    return list(unique.values())


def normalize_response(raw):
    choices = raw.get("choices") or []
    choice = choices[0] if choices else {}
    answer = choice.get("message", {}).get("content") or ""
    if not isinstance(answer, str):
        answer = "\n".join(p.get("text", "") for p in answer if isinstance(p, dict))
    answer = answer.strip()
    finish = choice.get("finish_reason")
    status = "success" if answer and finish not in ("length", "content_filter", "error") else "failed"
    if answer and finish == "length":
        status = "truncated"
    citations = extract_citations(raw)
    return {"status": status, "answer": answer, "finish_reason": finish,
            "returned_model": raw.get("model"), "provider": raw.get("provider"),
            "usage": raw.get("usage", {}), "citations": citations,
            "body_urls": list(dict.fromkeys(re.findall(r'https?://[^\s<>\[\]()]+', answer))),
            "brand_mentioned": bool(re.search(r"\baqua\s*sky\b|溢康", answer, re.I)),
            "official_cited": any(official_url(c["url"]) for c in citations),
            "citation_metadata_present": bool(citations),
            "error": "" if status == "success" else ("Output token limit reached" if status == "truncated" else "No complete answer")}


def resolve_citation_redirects(records):
    """Resolve Google citation redirects without fetching the destination sites."""
    pending = {c["url"] for r in records for c in r.get("citations", [])
               if urlparse(c["url"]).hostname == "vertexaisearch.cloud.google.com"
               and not c.get("resolved_url")}

    def resolve(url):
        try:
            response = requests.head(url, allow_redirects=False, timeout=(5, 15))
            target = response.headers.get("Location", "")
            parsed = urlparse(target)
            valid = (response.is_redirect and parsed.scheme in ("https", "http")
                     and bool(parsed.hostname) and parsed.hostname != "vertexaisearch.cloud.google.com")
            return url, {"resolved_url": target if valid else None,
                         "resolution_http_status": response.status_code,
                         "resolved_at": datetime.now().astimezone().isoformat()}
        except requests.RequestException as exc:
            return url, {"resolved_url": None, "resolution_error": type(exc).__name__}

    with ThreadPoolExecutor(max_workers=6) as pool:
        resolved = dict(pool.map(resolve, sorted(pending)))
    for record in records:
        for citation in record.get("citations", []):
            if citation["url"] in resolved:
                citation.update(resolved[citation["url"]])
        record["unresolved_citations"] = sum(
            urlparse(c["url"]).hostname == "vertexaisearch.cloud.google.com" and not c.get("resolved_url")
            for c in record.get("citations", []))
        record["official_cited"] = any(official_url(c.get("resolved_url") or c["url"])
                                        for c in record.get("citations", []))


def build_payload(model, question, max_tokens):
    payload = {"model": model["id"], "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question["question"]}], "max_tokens": max_tokens}
    if model["api_type"] == "openrouter":
        payload["plugins"] = [{"id": "web", "engine": model["search_engine"]}]
        if model.get("provider"):
            payload["provider"] = model["provider"]
        if model.get("reasoning_effort"):
            payload["reasoning"] = {"effort": model["reasoning_effort"]}
    return payload


class APIClient:
    def __init__(self, config_path):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(config_path, encoding="utf-8-sig")
        self.keys = {route: cfg.get("api_keys", key, fallback="").strip()
                     for route, key in [("openrouter", "openrouter_api_key"), ("perplexity", "perplexity_api_key")]}

    def query(self, model, payload):
        self.retry_responses = []
        route = model["api_type"]
        key = self.keys.get(route, "")
        if not key or key.startswith("your_"):
            return {"error": "Missing API key", "http_status": None}, True
        url = {"openrouter": "https://openrouter.ai/api/v1/chat/completions",
               "perplexity": "https://api.perplexity.ai/v1/sonar"}[route]
        for attempt in range(3):
            try:
                response = requests.post(url, headers={"Authorization": f"Bearer {key}",
                    "Content-Type": "application/json", "X-Title": "AQUASKY AIQA Monitor"},
                    json=payload, timeout=(15, 180))
                try:
                    raw = response.json()
                except ValueError:
                    raw = {"error": "Non-JSON API response"}
                if response.status_code == 200 and not raw.get("error"):
                    transient = any(
                        c.get("finish_reason") == "error"
                        and (c.get("error") or {}).get("code") in (429, 500, 502, 503, 504)
                        for c in raw.get("choices", []))
                    if transient and attempt < 2:
                        # OpenRouter can wrap provider failures inside an HTTP 200.
                        # Preserve the failed response separately from the final response.
                        self.retry_responses.append(raw)
                        time.sleep(2 ** (attempt + 1))
                        continue
                    return raw, False
                # Never persist headers, keys or arbitrary error body from a provider.
                error = {"error": f"API HTTP {response.status_code}", "http_status": response.status_code}
                if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                return error, response.status_code in (401, 402, 403, 404)
            except requests.RequestException as exc:
                # A timed-out POST may have been billed. Avoid automatic duplicate calls.
                return {"error": type(exc).__name__, "http_status": None}, False
        return {"error": "Retries exhausted", "http_status": None}, False


def summary_markdown(manifest, records):
    lines = ["# AQUASKY AI 引用監測", "", f"執行時間：{manifest['created_at']}",
             f"題庫 SHA-256：`{manifest['question_hash']}`", "",
             "本報告為模型 API 測試，不代表 ChatGPT 網頁版、Gemini App 或 Google AI Overviews。",
             "每題獨立對話；使用相同繁體中文查詢與來源要求，未限定網站，未向 A 組注入品牌名。",
             "品牌提及只是文字偵測，不等於推薦、資訊正確或完整 Share of Voice。B 組正確性仍需人工核對。",
             "引用僅計 API 結構化來源；回答內網址另存，不冒充引用。搜尋已啟用，但無引用不代表未搜尋。",
             "Google 搜尋跳轉以 HEAD 查核 Location，不抓取目標網站；原始與解析後網址均保留。",
             "同日重跑、不同題庫與不同搜尋引擎不混算；這是單次觀測，不能推論長期趨勢。", "",
             "| 模型 | 搜尋模式 | 完整回答 / 預定 | A 組品牌提及 / 完整回答 | A 組官網引用 / 完整回答 | B 組官網引用 / 完整回答 | 有來源 / 完整回答 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    if manifest.get("source_runs"):
        # Insert provenance before the comparison table, preserving each run's time.
        table_start = next(i for i, line in enumerate(lines) if line.startswith("| 模型 |"))
        provenance = ["## 本報告來源批次", "", "這是相同題庫與參數的分批測試整合，非同時發出的單一批次。", ""]
        provenance += [f"- {s['run_id']}：{s['created_at']}；模型 {', '.join(s['models'])}" for s in manifest["source_runs"]]
        lines[table_start:table_start] = provenance + [""]
    for model in manifest["models"]:
        rows = [r for r in records if r["model_key"] == model["key"]]
        good = [r for r in rows if r["status"] == "success"]
        a = [r for r in good if r["group"] == "A"]
        b = [r for r in good if r["group"] == "B"]
        def ratio(items, key):
            return f"{sum(bool(r.get(key)) for r in items)}/{len(items)}" if items else "—（無完整回答）"
        lines.append(f"| {model['name']} | {model['search_engine']} | {len(good)}/{len(manifest['questions'])} | {ratio(a, 'brand_mentioned')} | {ratio(a, 'official_cited')} | {ratio(b, 'official_cited')} | {ratio(good, 'citation_metadata_present')} |")
    bad = [r for r in records if r["status"] != "success"]
    unresolved = sum(r.get("unresolved_citations", 0) for r in records)
    if unresolved:
        lines += ["", f"注意：仍有 {unresolved} 筆 Google 引用跳轉未能解析，官網引用數為已確認下限，不能把未命中解讀為沒有引用。"]
    if bad:
        lines += ["", "## 未完成或截斷項目", ""]
        lines += [f"- {r['model_key']} / {r['question_id']}：{r['status']} — {r.get('error', '')}" for r in bad]
    lines += ["", "## 逐題回答與來源", ""]
    for r in records:
        lines += [f"### {r['model_key']} / {r['question_id']}", "", r["question"], "",
                  f"狀態：{r['status']}；回傳模型：{r.get('returned_model', '—')}", "",
                  r.get("answer", "") or r.get("error", ""), "", "API 引用來源：", ""]
        lines += [f"- [{c.get('title') or c['url']}]({c.get('resolved_url') or c['url']})" for c in r.get("citations", [])] or ["- 未取得結構化引用。"]
        lines += ["", f"原始回應：`raw/{r['model_key']}_{r['question_id']}.json`", ""]
    return "\n".join(lines)


def write_reports(run_dir, manifest, records):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    resolve_citation_redirects(records)
    dump_json(run_dir / "results.json", records)
    (run_dir / "report.md").write_text(summary_markdown(manifest, records), encoding="utf-8")
    wb = Workbook(); ws = wb.active; ws.title = "回答與引用"
    ws.append(["模型", "題號", "類別", "問句", "狀態", "回答", "API引用網址", "品牌提及", "官網引用", "總Token", "結束原因", "錯誤"])
    for r in records:
        values = [r["model_key"], r["question_id"], r["group"], r["question"], r["status"], r.get("answer", ""),
                  "\n".join(c.get("resolved_url") or c["url"] for c in r.get("citations", [])), r.get("brand_mentioned", False),
                  r.get("official_cited", False), r.get("usage", {}).get("total_tokens", 0), r.get("finish_reason"), r.get("error", "")]
        ws.append(values)
        for cell in ws[ws.max_row]:
            if isinstance(cell.value, str):
                cell.data_type = "s"
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF");c.fill = PatternFill("solid", fgColor="183C55")
    ws.freeze_panes = "E2";ws.auto_filter.ref = ws.dimensions
    for col, width in {"A":18,"B":10,"C":10,"D":55,"E":15,"F":100,"G":65,"H":12,"I":12,"J":14,"K":18,"L":28}.items():
        ws.column_dimensions[col].width = width
    wb.save(run_dir / "answers.xlsx")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=ROOT / "config/questions_20260922.md")
    parser.add_argument("--models", help="Comma-separated keys, or all; defaults to enabled models")
    parser.add_argument("--question-ids", help="Subset, e.g. A1,B1")
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--run", action="store_true", help="Send billable API requests")
    parser.add_argument("--dry-run", action="store_true", help="Validate locally without API calls")
    parser.add_argument("--resume", type=Path, help="Resume an existing run with the SAME inputs")
    parser.add_argument("--retry-failed", action="store_true", help="Explicitly retry failed/truncated records on resume")
    args = parser.parse_args(argv)
    if args.max_tokens < 1 or (args.run and args.dry_run):
        parser.error("Use positive max-tokens and choose --run OR --dry-run")
    models = json.loads((ROOT / "config/working_models.json").read_text(encoding="utf-8-sig"))
    requested = args.models.split(",") if args.models and args.models != "all" else None
    if requested and set(requested) - {m["key"] for m in models}:
        parser.error("Unknown model key")
    models = [m for m in models if (m["key"] in requested if requested else (args.models == "all" or m["enabled"]))]
    questions = load_question_records(args.questions)
    if args.question_ids:
        ids = args.question_ids.split(",")
        if set(ids) - {q["id"] for q in questions}:
            parser.error("Unknown question ID")
        questions = [q for q in questions if q["id"] in ids]
    identity = {"schema_version": 1, "models": models, "questions": questions,
                "system_prompt": SYSTEM_PROMPT, "max_tokens": args.max_tokens, "official_domains": OFFICIAL_DOMAINS}
    print(json.dumps({"questions": len(questions), "ids": [q["id"] for q in questions],
                      "models": [m["id"] for m in models], "requests": len(models) * len(questions)}, ensure_ascii=False), flush=True)
    if not args.run:
        print("DRY RUN: no API requests sent.")
        return 0
    run_dir = args.resume.resolve() if args.resume else ROOT / "outputs/runs" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if args.resume:
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("report_only"):
            parser.error("Combined reports are read-only; resume an original API run instead.")
        if manifest["run_hash"] != fingerprint(identity):
            parser.error("Resume inputs differ (questions/models/prompt/token limit). Start a new run.")
        records = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    else:
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "raw").mkdir()
        manifest = {**identity, "created_at": datetime.now().astimezone().isoformat(),
                    "question_source": str(args.questions.resolve()), "question_hash": fingerprint(questions),
                    "run_hash": fingerprint(identity)}
        dump_json(run_dir / "manifest.json", manifest)
        records = []
        dump_json(run_dir / "results.json", records)
    print(f"RUN_DIR={run_dir}", flush=True)
    client = APIClient(ROOT / "config.ini")
    blocked_routes = set()
    try:
        for model in models:
            for question in questions:
                existing = next((r for r in records if r["model_key"] == model["key"] and r["question_id"] == question["id"]), None)
                if existing and (existing["status"] == "success" or not args.retry_failed):
                    continue
                payload = build_payload(model, question, args.max_tokens)
                print(f"QUERY {model['key']} {question['id']}", flush=True)
                started = time.monotonic()
                client.retry_responses = []
                if model["api_type"] in blocked_routes:
                    raw, fatal = {"error": "Skipped: provider authentication/credit failure"}, True
                else:
                    raw, fatal = client.query(model, payload)
                if fatal and raw.get("http_status") in (401, 402, 403):
                    blocked_routes.add(model["api_type"])
                record = {"model_key": model["key"], "model_id": model["id"], "search_engine": model["search_engine"],
                          "question_id": question["id"], "group": question["group"], "question": question["question"],
                          "timestamp": datetime.now().astimezone().isoformat(), "elapsed_seconds": round(time.monotonic()-started, 2)}
                if raw.get("error"):
                    record.update(status="failed", error=raw["error"], answer="", citations=[])
                else:
                    record.update(normalize_response(raw))
                raw_path = run_dir / "raw" / f"{model['key']}_{question['id']}.json"
                if existing and raw_path.exists():
                    backup = raw_path.with_name(raw_path.stem + f"_previous_{time.time_ns()}.json")
                    backup.write_bytes(raw_path.read_bytes())
                dump_json(raw_path, {"request": payload, "response": raw,
                                     "retry_responses": client.retry_responses})
                if existing:
                    records.remove(existing)
                records.append(record)
                # Persist after EVERY response, before attempting potentially fallible exports.
                dump_json(run_dir / "results.json", records)
                print(f"RESULT {model['key']} {question['id']} {record['status']} citations={len(record.get('citations', []))}", flush=True)
    finally:
        write_reports(run_dir, manifest, records)
    good = sum(r["status"] == "success" for r in records)
    print(f"COMPLETE {good}/{len(models)*len(questions)}; {run_dir / 'report.md'}", flush=True)
    return 0 if good == len(models)*len(questions) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted; saved responses can be resumed.")
        raise SystemExit(130)
