"""
TAFSOL — MASTER LEAD GEN LAUNCHER
One command → all agents → one combined Excel file
Run: python launch_all.py
"""

import sys
import io
import os
import time
import random
import pandas as pd
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── SETTINGS ─────────────────────────────────────────────────────────────────
TIMELIMIT  = "d"          # "d" = last 24 hours | "w" = last week | "m" = last month
MAX_RESULTS = 8           # per query
OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
MASTER_FILE = os.path.join(OUTPUT_DIR, f"MASTER_LEADS_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")

# ─── SEARCH QUERY BANKS ───────────────────────────────────────────────────────

LINKEDIN_QUERIES = [
    'site:linkedin.com "looking for software development company"',
    'site:linkedin.com "looking for development agency"',
    'site:linkedin.com "need a development partner"',
    'site:linkedin.com "dedicated development team" "looking" OR "need"',
    'site:linkedin.com "staff augmentation" "software" "looking" OR "need"',
    'site:linkedin.com "build MVP" "need developer" OR "looking for"',
    'site:linkedin.com "ChatGPT integration" "need developer" OR "looking for"',
    'site:linkedin.com "AI automation" "need developer" OR "looking for company"',
    'site:linkedin.com "hiring MERN developer" OR "hiring React developer" USA',
    'site:linkedin.com "hiring full stack developer" "remote" OR "contract" USA',
    'site:linkedin.com "looking for" "MERN developer" "hire" OR "need" OR "urgent"',
    'site:linkedin.com "need a" "Laravel developer" "project" OR "urgent" OR "hire"',
    'site:linkedin.com "startup" "looking for technical cofounder"',
    'site:linkedin.com "CRM development" OR "ERP development" "looking" OR "need"',
    'site:linkedin.com "real estate" "need website" OR "need app" OR "chatbot"',
]

REDDIT_QUERIES = [
    'site:reddit.com "looking for software development company"',
    'site:reddit.com "looking for development agency"',
    'site:reddit.com "recommend software development company"',
    'site:reddit.com startup "looking for developers" OR "need developers"',
    'site:reddit.com "build MVP" "need developer" OR "hire developer"',
    'site:reddit.com "ChatGPT integration" business "need developer"',
    'site:reddit.com "need a developer" OR "need software team"',
    'site:reddit.com "who can build my app" OR "who can develop"',
    'site:reddit.com "looking for development partner" OR "need development partner"',
    'site:reddit.com smallbusiness "website not converting" OR "no leads from website"',
]

QUORA_QUERIES = [
    'site:quora.com best software development company USA',
    'site:quora.com how to find software development company',
    'site:quora.com how to hire dedicated developers',
    'site:quora.com how to build MVP startup',
    'site:quora.com ChatGPT integration business website',
    'site:quora.com AI automation for small business',
    'site:quora.com how to get clients software development company',
    'site:quora.com how to build custom CRM software',
]

GOOGLE_DORK_QUERIES = [
    '"looking for software development company" USA',
    '"looking for development agency" site:linkedin.com OR site:reddit.com',
    '"need a development partner" startup OR company',
    '"dedicated development team" "looking for" OR "need"',
    '"software outsourcing partner" USA OR "United States"',
    '"build MVP" "need developer" OR "looking for developer" site:reddit.com OR site:linkedin.com',
    '"ChatGPT integration" "need developer" OR "looking for" site:linkedin.com OR site:reddit.com',
    '"AI automation" "need software" OR "looking for developer" USA',
    '"custom CRM development" "looking for" OR "need"',
    '"startup" "looking for technical cofounder" site:linkedin.com OR site:reddit.com',
    '"looking for offshore developers" USA site:linkedin.com',
    '"MVP development" "need" OR "looking for" startup USA',
    'site:wellfound.com "MERN" OR "React" OR "Node.js" developer hiring',
    'site:reddit.com "need developers" "recommendation" OR "recommend" startup',
    '"healthcare app development" "need" OR "looking for" company USA',
    '"real estate app development" "need developer" OR "looking for company"',
    '"fintech development" "need developers" OR "looking for team"',
]

DEV_LEADS_QUERIES = [
    'site:linkedin.com "looking for software development company"',
    'site:linkedin.com "startup" "looking for technical cofounder" OR "need CTO"',
    'site:linkedin.com "build MVP" "need developer" OR "looking for"',
    'site:linkedin.com "ChatGPT integration" "need developer" OR "looking for"',
    'site:linkedin.com "AI automation" "need developer" OR "looking for company"',
    'site:linkedin.com "looking for" "MERN developer" "hire" OR "need" OR "urgent"',
    'site:linkedin.com "need a" "Laravel developer" "project" OR "urgent" OR "hire"',
    'site:linkedin.com "hiring Flutter developer" OR "hiring React Native developer"',
    'site:linkedin.com "hiring Python developer" OR "hiring AI developer" remote',
    'site:linkedin.com "CRM development" OR "ERP development" "looking" OR "need"',
]

# ─── SCORING ──────────────────────────────────────────────────────────────────

HIGH_INTENT = [
    "looking for software development company", "looking for development agency",
    "need a development partner", "offshore developers", "dedicated development team",
    "staff augmentation", "software outsourcing", "build MVP", "ChatGPT integration",
    "OpenAI integration", "custom CRM", "technical cofounder", "looking for developer",
    "need developers", "CTO as a Service",
]

def score(title, body):
    c = (title + " " + body).lower()
    if any(k.lower() in c for k in HIGH_INTENT): return "HIGH"
    return "MEDIUM"

def detect_platform(url):
    if "linkedin.com" in url:    return "LinkedIn"
    if "reddit.com" in url:      return "Reddit"
    if "quora.com" in url:       return "Quora"
    if "wellfound.com" in url:   return "Wellfound"
    if "indeed.com" in url:      return "Indeed"
    if "facebook.com" in url:    return "Facebook"
    return "Web"

def detect_industry(t, b):
    c = (t + b).lower()
    for kw, ind in [
        (["healthcare","medical","dental"],"Healthcare"),
        (["real estate","property","realty"],"Real Estate"),
        (["fintech","finance","banking"],"Finance"),
        (["legal","law firm","attorney"],"Legal"),
        (["construction","contractor"],"Construction"),
        (["logistics","shipping"],"Logistics"),
        (["ecommerce","shopify","retail"],"E-commerce"),
        (["saas","startup","mvp"],"SaaS/Startup"),
        (["restaurant","food"],"Hospitality"),
        (["education","edtech"],"Education"),
        (["marketing agency","digital agency"],"Agency"),
    ]:
        if any(k in c for k in kw): return ind
    return "General"

def detect_tech(t, b):
    c = (t + b).lower()
    tech = []
    if any(k in c for k in ["mern","react","node"]): tech.append("MERN/React")
    if any(k in c for k in ["laravel","php"]): tech.append("Laravel")
    if any(k in c for k in ["python","fastapi","django"]): tech.append("Python")
    if any(k in c for k in ["flutter","react native","mobile"]): tech.append("Mobile")
    if any(k in c for k in ["ai","chatgpt","openai","llm","automation"]): tech.append("AI/Automation")
    if any(k in c for k in ["crm","erp","enterprise"]): tech.append("Enterprise")
    if any(k in c for k in ["saas","web app"]): tech.append("SaaS/Web")
    return ", ".join(tech) if tech else "General"

OUTREACH = [
    "Hi {name}, I saw you're looking for a software development partner — Tafsol Technologies specializes in exactly this for US companies. We have dedicated MERN/Laravel/AI developers available immediately. Can we connect?",
    "Hi {name}, noticed you're searching for a dev agency. Tafsol builds custom software, web apps, mobile apps, and AI solutions for US businesses — fixed-cost, clear timelines, NDA protected. Happy to share case studies.",
    "Hi {name}, your post caught my attention. Tafsol Technologies helps companies like yours with dedicated offshore teams at US-quality standards. 50+ projects delivered for US clients. Quick call this week?",
]

# ─── SEARCH ENGINE ────────────────────────────────────────────────────────────

def search_all(queries, source_label, seen):
    results = []
    with DDGS() as ddgs:
        for q in queries:
            try:
                hits = ddgs.text(q, region="us-en", max_results=MAX_RESULTS, timelimit=TIMELIMIT)
                for r in hits:
                    url   = r.get("href","")
                    title = r.get("title","")
                    body  = r.get("body","")
                    if not url or url in seen: continue
                    seen.add(url)
                    name = title.split(" - ")[0].split("|")[0].strip()[:60]
                    results.append({
                        "Confidence":       score(title, body),
                        "Source Agent":     source_label,
                        "Platform":         detect_platform(url),
                        "Industry":         detect_industry(title, body),
                        "Tech Need":        detect_tech(title, body),
                        "Title / Name":     title[:120],
                        "URL":              url,
                        "Snippet":          body[:200],
                        "Outreach Message": random.choice(OUTREACH).format(name=name.split()[0] if name else "there"),
                        "Status":           "Not Contacted",
                        "Reply":            "No",
                        "Notes":            "",
                        "Found At":         datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                print(f"    Error: {e}")
                time.sleep(2)
    return results

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  TAFSOL — MASTER LEAD GEN LAUNCHER")
    print(f"  Timeframe : Last 24 hours  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)

    all_leads = []
    seen_urls  = set()

    agents = [
        ("LinkedIn",        LINKEDIN_QUERIES),
        ("Reddit",          REDDIT_QUERIES),
        ("Quora",           QUORA_QUERIES),
        ("Google Dorks",    GOOGLE_DORK_QUERIES),
        ("LinkedIn DevReq", DEV_LEADS_QUERIES),
    ]

    for label, queries in agents:
        print(f"\n[{label}] Searching {len(queries)} queries...")
        leads = search_all(queries, label, seen_urls)
        all_leads.extend(leads)
        high = sum(1 for l in leads if l["Confidence"] == "HIGH")
        print(f"  → {len(leads)} leads found  |  HIGH intent: {high}")

    if not all_leads:
        print("\nNo leads found. Try expanding timelimit to 'w' (last week).")
        print("Edit TIMELIMIT = 'w' at top of this file.")
        return

    # ─── SAVE INDIVIDUAL FILES PER AGENT ─────────────────────────────────────
    df_all = pd.DataFrame(all_leads)
    df_all["_sort"] = df_all["Confidence"].map({"HIGH":0,"MEDIUM":1})
    df_all = df_all.sort_values(["_sort","Source Agent"]).drop(columns=["_sort"])

    stamp     = datetime.now().strftime("%Y%m%d_%H%M")
    saved_files = []

    for label, _ in agents:
        df_agent = df_all[df_all["Source Agent"] == label].copy()
        if df_agent.empty:
            continue
        fname = os.path.join(OUTPUT_DIR, f"{label.replace(' ','_')}_leads_{stamp}.xlsx")
        with pd.ExcelWriter(fname, engine="openpyxl") as writer:
            df_agent.to_excel(writer, index=False, sheet_name="All Leads")
            _fmt(writer.sheets["All Leads"])
            df_h = df_agent[df_agent["Confidence"] == "HIGH"]
            if not df_h.empty:
                df_h.to_excel(writer, index=False, sheet_name="HIGH Intent")
                _fmt(writer.sheets["HIGH Intent"])
        high_n = len(df_agent[df_agent["Confidence"]=="HIGH"])
        print(f"  Saved: {os.path.basename(fname)}  ({len(df_agent)} leads, {high_n} HIGH)")
        saved_files.append(fname)

    # ─── MASTER COMBINED FILE ─────────────────────────────────────────────────
    with pd.ExcelWriter(MASTER_FILE, engine="openpyxl") as writer:
        df_all.to_excel(writer, index=False, sheet_name="All Leads")
        _fmt(writer.sheets["All Leads"])
        df_high = df_all[df_all["Confidence"] == "HIGH"]
        if not df_high.empty:
            df_high.to_excel(writer, index=False, sheet_name="HIGH Intent")
            _fmt(writer.sheets["HIGH Intent"])
        for platform in df_all["Platform"].unique():
            df_p = df_all[df_all["Platform"] == platform]
            sname = platform[:31]
            df_p.to_excel(writer, index=False, sheet_name=sname)
            _fmt(writer.sheets[sname])

    # ─── SUMMARY ──────────────────────────────────────────────────────────────
    high   = len(df_all[df_all["Confidence"]=="HIGH"])
    medium = len(df_all[df_all["Confidence"]=="MEDIUM"])

    print("\n" + "=" * 65)
    print("  RESULTS SUMMARY")
    print("=" * 65)
    print(f"  Total Leads     : {len(df_all)}")
    print(f"  HIGH Intent     : {high}   ← Start outreach from here")
    print(f"  MEDIUM Intent   : {medium}")
    print()
    print("  By Platform:")
    for p, cnt in df_all["Platform"].value_counts().items():
        print(f"    {p:<18} {cnt}")
    print()
    print("  By Industry:")
    for ind, cnt in df_all["Industry"].value_counts().head(6).items():
        print(f"    {ind:<20} {cnt}")
    print()
    print(f"  MASTER file : {os.path.basename(MASTER_FILE)}")
    print(f"  Alag files  : {len(saved_files)} agent Excel files bhi saved hain")
    print(f"  → 'HIGH Intent' sheet se outreach shuru karo")
    print("=" * 65)


def _fmt(ws):
    from openpyxl.utils import get_column_letter
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 3, 60)
    ws.freeze_panes = "A2"


if __name__ == "__main__":
    main()
