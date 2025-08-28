import os
import sys
import csv
from collections import defaultdict, Counter
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address

# Input columns expected (case-insensitive match by normalized keys):
# IP Address, Timestamp, Timezone, Method, URL, Protocol, Status Code, Response Size,
# Referrer, User Agent, Crawler Name, Extra Info

KNOWN_LLM_PATTERNS = [
    ("gptbot", "OpenAI GPTBot"),
    ("openai", "OpenAI (UA)"),
    ("claudebot", "Anthropic ClaudeBot"),
    ("anthropic", "Anthropic (UA)"),
    ("perplexitybot", "PerplexityBot"),
    ("perplexity", "Perplexity (UA)"),
    ("facebookbot", "Meta (FacebookBot)"),
    ("meta-ai", "Meta AI"),
    ("meta llama", "Meta Llama"),
    ("llama", "Meta Llama"),
    ("google-extended", "Google (Extended)"),
    ("googleother", "GoogleOther (LLM)"),
    ("google ai", "Google AI"),
    ("bard", "Google Bard"),
    ("duckassist", "DuckDuckGo (DuckAssist)"),
    ("bingbot", "Microsoft Bing"),  # search bot, sometimes tied with AI features
    ("msnbot", "Microsoft (msnbot)"),
    ("bytespider", "ByteDance (ByteSpider)"),
    # Newly added vendors per user request
    ("grok", "xAI Grok"),
    ("xai", "xAI (UA)"),
    ("cohere", "Cohere"),
    ("cohere-ai", "Cohere"),
    ("mistral", "Mistral"),
    ("mistralai", "Mistral"),
]

NON_LLM_EXCLUDE = [
    "ccbot",  # Common Crawl
    "semrush", "ahrefs", "moz", "yandex", "baidu", "sogou",
    "petalbot", "seznambot", "exabot", "dotbot", "megaindex",
]


def normalize_key(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


# Optional GeoIP resolver (uses local MaxMind DB if available)
class GeoIPResolver:
    def __init__(self, base_dir: str) -> None:
        self.country_reader = None
        self.asn_reader = None
        self.enabled = False
        try:
            # Prefer env vars; fallback to project data directory
            country_db = os.environ.get("GEOIP_COUNTRY_DB") or os.path.join(base_dir, "data", "GeoLite2-Country.mmdb")
            asn_db = os.environ.get("GEOIP_ASN_DB") or os.path.join(base_dir, "data", "GeoLite2-ASN.mmdb")
            if os.path.exists(country_db) or os.path.exists(asn_db):
                try:
                    import geoip2.database  # type: ignore
                except Exception:
                    # geoip2 not installed; keep disabled
                    return
                if os.path.exists(country_db):
                    self.country_reader = geoip2.database.Reader(country_db)
                if os.path.exists(asn_db):
                    self.asn_reader = geoip2.database.Reader(asn_db)
                self.enabled = True
        except Exception:
            self.enabled = False

    def close(self) -> None:
        try:
            if self.country_reader:
                self.country_reader.close()
            if self.asn_reader:
                self.asn_reader.close()
        except Exception:
            pass

    def resolve(self, ip: str) -> Tuple[str, str, str]:
        if not self.enabled:
            return "", "", ""
        try:
            _ = ip_address(ip)
        except Exception:
            return "", "", ""
        country_iso = ""
        asn = ""
        as_org = ""
        try:
            if self.country_reader:
                r = self.country_reader.country(ip)
                country_iso = (r.country.iso_code or "")
        except Exception:
            country_iso = ""
        try:
            if self.asn_reader:
                r = self.asn_reader.asn(ip)
                asn = str(r.autonomous_system_number or "")
                as_org = (r.autonomous_system_organization or "")
        except Exception:
            asn = asn or ""
            as_org = as_org or ""
        return country_iso or "", asn or "", as_org or ""


BOT_FAMILY_MAP: Dict[str, str] = {
    "gptbot": "GPTBot",
    "openai": "OpenAI",
    "claudebot": "ClaudeBot",
    "anthropic": "Anthropic",
    "perplexitybot": "PerplexityBot",
    "perplexity": "Perplexity",
    "facebookbot": "FacebookBot",
    "meta-ai": "Meta-AI",
    "meta llama": "Llama",
    "llama": "Llama",
    "google-extended": "Google-Extended",
    "googleother": "GoogleOther",
    "google ai": "Google-AI",
    "bard": "Bard",
    "duckassist": "DuckAssist",
    "bingbot": "BingBot",
    "msnbot": "msnbot",
    "bytespider": "ByteSpider",
    "grok": "Grok",
    "xai": "xAI",
    "cohere": "Cohere",
    "cohere-ai": "Cohere",
    "mistral": "Mistral",
    "mistralai": "Mistral",
}


def detect_llm(crawler_name: str, user_agent: str) -> Tuple[bool, str, str, str, str]:
    ua = (user_agent or "").lower()
    cn = (crawler_name or "").lower()

    # Exclude known non-LLM crawlers
    for bad in NON_LLM_EXCLUDE:
        if bad in ua or bad in cn:
            return False, "Non-LLM crawler", "", "", ""

    for pat, vendor in KNOWN_LLM_PATTERNS:
        if pat in ua or pat in cn:
            matched = pat
            source = "user_agent" if pat in ua else "crawler_name"
            bot_family = BOT_FAMILY_MAP.get(pat, matched)
            return True, vendor, matched, source, bot_family

    return False, "Unknown", "", "", ""


def is_success(status_code: str, response_size: str) -> bool:
    try:
        sc = int(str(status_code).strip())
    except Exception:
        return False
    try:
        rs = int(str(response_size).strip())
    except Exception:
        rs = 0
    return (200 <= sc < 300) and (rs > 0)


def load_rows(csv_path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return rows, fieldnames


def analyze(csv_path: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    rows, fieldnames = load_rows(csv_path)
    norm_map = {normalize_key(k): k for k in fieldnames}

    def get(row, key, default=""):
        src = norm_map.get(key)
        return row.get(src, default) if src else default

    analyzed: List[Dict[str, Any]] = []

    # Prepare GeoIP resolver (base_dir = project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geo = GeoIPResolver(project_root)

    for r in rows:
        ip = get(r, "ip_address")
        ts = get(r, "timestamp")
        tz = get(r, "timezone")
        method = get(r, "method")
        url = get(r, "url")
        proto = get(r, "protocol")
        status = get(r, "status_code")
        size = get(r, "response_size")
        ref = get(r, "referrer")
        ua = get(r, "user_agent")
        crawler = get(r, "crawler_name")
        extra = get(r, "extra_info")

        is_llm, vendor, matched, evidence_src, bot_family = detect_llm(crawler, ua)
        success = is_success(status, size)

        # status class
        try:
            sc_int = int(str(status).strip())
            status_class = f"{sc_int // 100}xx"
        except Exception:
            status_class = "unknown"

        # hour bucket: derive from timestamp + timezone like 30/Jun/2025:05:10:41 and -0700
        hour_bucket = ""
        ts_str = (ts or "").strip()
        tz_str = (tz or "").strip()
        try:
            dt_naive = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S")
            if tz_str and len(tz_str) == 5 and (tz_str.startswith("+") or tz_str.startswith("-")):
                sign = 1 if tz_str[0] == "+" else -1
                hours = int(tz_str[1:3])
                mins = int(tz_str[3:5])
                offset = timedelta(hours=hours, minutes=mins) * sign
                dt = dt_naive.replace(tzinfo=timezone(offset))
                hour_bucket = dt.strftime("%Y-%m-%d %H:00 %z")
            else:
                hour_bucket = dt_naive.strftime("%Y-%m-%d %H:00")
        except Exception:
            hour_bucket = ""

        # GeoIP lookup (optional)
        country_iso, asn, as_org = geo.resolve(ip or "")

        analyzed.append({
            "timestamp": ts,
            "timezone": tz,
            "ip": ip,
            "method": method,
            "url": url,
            "protocol": proto,
            "status_code": status,
            "response_size": size,
            "referrer": ref,
            "user_agent": ua,
            "crawler_name": crawler,
            "extra_info": extra,
            "is_llm_bot": is_llm,
            "llm_vendor": vendor,
            "pattern_matched": matched,
            "vendor_evidence": evidence_src,  # user_agent / crawler_name
            "bot_family": bot_family,
            "status_class": status_class,
            "hour_bucket": hour_bucket,
            "note": ("DuckAssist Q&A crawler" if ("duckassist" in (ua or "")) else ""),
            "country_iso": country_iso,
            "asn": asn,
            "as_org": as_org,
            "success": success,
        })

    # Write detailed filtered LLM requests
    detail_path = os.path.join(out_dir, "llm_bot_requests.csv")
    with open(detail_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(analyzed[0].keys()) if analyzed else [])
        if analyzed:
            writer.writeheader()
            writer.writerows([x for x in analyzed if x["is_llm_bot"]])

    # Aggregate by vendor
    agg: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "requests": 0,
        "success": 0,
        "unique_ips": set(),
        "unique_urls": set(),
    })

    for x in analyzed:
        if not x["is_llm_bot"]:
            continue
        v = x["llm_vendor"]
        agg[v]["requests"] += 1
        if x["success"]:
            agg[v]["success"] += 1
        agg[v]["unique_ips"].add(x["ip"])
        agg[v]["unique_urls"].add(x["url"])

    summary_rows = []
    for v, d in agg.items():
        req = d["requests"]
        succ = d["success"]
        sr = round(succ / req, 4) if req else 0.0
        summary_rows.append({
            "llm_vendor": v,
            "requests": req,
            "success": succ,
            "success_rate": sr,
            "unique_ips": len(d["unique_ips"]),
            "unique_urls": len(d["unique_urls"]),
        })

    summary_path = os.path.join(out_dir, "llm_bot_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "llm_vendor", "requests", "success", "success_rate", "unique_ips", "unique_urls"
        ])
        writer.writeheader()
        writer.writerows(sorted(summary_rows, key=lambda r: r["requests"], reverse=True))

    # Top URLs by vendor
    top_urls: Dict[str, Counter] = defaultdict(Counter)
    for x in analyzed:
        if x["is_llm_bot"]:
            top_urls[x["llm_vendor"]][x["url"]] += 1

    # Helper to make safe filenames per vendor
    def safe_name(name: str) -> str:
        return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (name or "unknown"))

    # Write per-vendor Top URL CSVs (all URLs with counts, sorted desc)
    for vendor, counter in top_urls.items():
        rows = [{"url": url, "count": cnt} for url, cnt in counter.most_common()]
        path = os.path.join(out_dir, f"llm_bot_top_urls_{safe_name(vendor)}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["url", "count"])
            writer.writeheader()
            writer.writerows(rows)

    # Build trends: hourly and daily per vendor
    trend_hourly: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(lambda: {"requests": 0, "success": 0})
    trend_daily: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(lambda: {"requests": 0, "success": 0})

    for x in analyzed:
        if not x["is_llm_bot"]:
            continue
        vendor = x["llm_vendor"]
        hb = x.get("hour_bucket") or ""
        # daily from timestamp string (fallback to first 10 chars after parsing format)
        ts_str = (x.get("timestamp") or "").strip()
        day = ""
        try:
            dt = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S")
            day = dt.strftime("%Y-%m-%d")
        except Exception:
            day = ts_str[:10]

        trend_hourly[(vendor, hb)]["requests"] += 1
        if x.get("success"):
            trend_hourly[(vendor, hb)]["success"] += 1

        trend_daily[(vendor, day)]["requests"] += 1
        if x.get("success"):
            trend_daily[(vendor, day)]["success"] += 1

    # Write trend hourly CSV
    hourly_path = os.path.join(out_dir, "llm_bot_trend_hourly.csv")
    with open(hourly_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["llm_vendor", "hour_bucket", "requests", "success", "success_rate"])
        writer.writeheader()
        for (vendor, hb), d in sorted(trend_hourly.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            req = d["requests"]
            suc = d["success"]
            sr = round(suc / req, 4) if req else 0.0
            writer.writerow({
                "llm_vendor": vendor,
                "hour_bucket": hb,
                "requests": req,
                "success": suc,
                "success_rate": sr,
            })

    # Also write per-vendor hourly trend CSVs
    per_vendor_hourly: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for (vendor, hb), d in sorted(trend_hourly.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        req = d["requests"]
        suc = d["success"]
        sr = round(suc / req, 4) if req else 0.0
        per_vendor_hourly[vendor].append({
            "hour_bucket": hb,
            "requests": req,
            "success": suc,
            "success_rate": sr,
        })
    for vendor, rows in per_vendor_hourly.items():
        path = os.path.join(out_dir, f"llm_bot_trend_hourly_{safe_name(vendor)}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["hour_bucket", "requests", "success", "success_rate"])
            writer.writeheader()
            writer.writerows(rows)

    # Write trend daily CSV
    daily_path = os.path.join(out_dir, "llm_bot_trend_daily.csv")
    with open(daily_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["llm_vendor", "date", "requests", "success", "success_rate"])
        writer.writeheader()
        for (vendor, day), d in sorted(trend_daily.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            req = d["requests"]
            suc = d["success"]
            sr = round(suc / req, 4) if req else 0.0
            writer.writerow({
                "llm_vendor": vendor,
                "date": day,
                "requests": req,
                "success": suc,
                "success_rate": sr,
            })

    # Also write per-vendor daily trend CSVs
    per_vendor_daily: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for (vendor, day), d in sorted(trend_daily.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        req = d["requests"]
        suc = d["success"]
        sr = round(suc / req, 4) if req else 0.0
        per_vendor_daily[vendor].append({
            "date": day,
            "requests": req,
            "success": suc,
            "success_rate": sr,
        })
    for vendor, rows in per_vendor_daily.items():
        path = os.path.join(out_dir, f"llm_bot_trend_daily_{safe_name(vendor)}.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "requests", "success", "success_rate"])
            writer.writeheader()
            writer.writerows(rows)

    # Write markdown report
    report_md = os.path.join(out_dir, "report.md")
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("# LLM Bot 抓取行為分析報告\n\n")
        f.write(f"資料來源: {os.path.basename(csv_path)}\n\n")
        total_llm = sum(r["requests"] for r in summary_rows)
        f.write(f"- 總計 LLM Bot 請求數: {total_llm}\n\n")
        f.write("## 各廠商摘要\n\n")
        for r in sorted(summary_rows, key=lambda r: r["requests"], reverse=True):
            f.write(f"- {r['llm_vendor']}: {r['requests']} 次，成功 {r['success']} 次，成功率 {r['success_rate']*100:.1f}% ，IP {r['unique_ips']} 個，URL {r['unique_urls']} 個\n")
        f.write("\n## 各廠商熱門抓取 URL (前 10)\n\n")
        for vendor, counter in top_urls.items():
            f.write(f"### {vendor}\n")
            for url, cnt in counter.most_common(10):
                f.write(f"- {url} ({cnt})\n")
            f.write("\n")

    print("[SUCCESS] 分析完成。輸出：")
    print(" - ", summary_path)
    print(" - ", detail_path)
    print(" - ", report_md)
    print(" - ", hourly_path)
    print(" - ", daily_path)
    try:
        geo.close()
    except Exception:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_server_logs.py '<path_to_log_csv>'")
        sys.exit(1)
    input_csv = sys.argv[1]
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "outputs", "log_analysis")
    analyze(input_csv, out_dir)
