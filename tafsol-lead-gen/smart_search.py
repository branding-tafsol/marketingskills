"""
TAFSOL — SMART KEYWORD SEARCH
Reads my_keywords.txt → searches Reddit (live) + LinkedIn (web)
Run: python smart_search.py
"""

import sys
import io
import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

KEYWORDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_keywords.txt")
OUTPUT_DIR    = os.path.dirname(os.path.abspath(__file__))

REDDIT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) tafsol-lead-gen/1.0"
}

HIGH_INTENT = [
    "need a developer", "looking for developer", "need software", "hire developer",
    "looking for software company", "need development team", "build an app",
    "build MVP", "need chatbot", "need ai", "outsource", "offshore", "ghosted",
    "developer quit", "replace developer", "technical cofounder", "need backend",
    "need frontend", "need full stack", "need mobile", "need to build",
]

# ─── READ KEYWORDS ────────────────────────────────────────────────────────────

def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"ERROR: {KEYWORDS_FILE} nahi mila!", flush=True)
        sys.exit(1)
    keywords = []
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                keywords.append(line)
    return keywords

# ─── SCORING ──────────────────────────────────────────────────────────────────

def score(title, body):
    c = (title + " " + body).lower()
    if any(k in c for k in HIGH_INTENT):
        return "HIGH"
    return "MEDIUM"

def detect_industry(t, b):
    c = (t + b).lower()
    for kw, ind in [
        (["healthcare","medical","dental"],    "Healthcare"),
        (["real estate","property","realty"],  "Real Estate"),
        (["fintech","finance","banking"],       "Finance"),
        (["legal","law","attorney"],            "Legal"),
        (["construction","contractor"],         "Construction"),
        (["logistics","shipping"],              "Logistics"),
        (["ecommerce","shopify","retail"],      "E-commerce"),
        (["saas","startup","mvp"],              "SaaS/Startup"),
        (["restaurant","food"],                 "Hospitality"),
        (["education","edtech","school"],       "Education"),
        (["marketing","agency","branding"],     "Agency"),
    ]:
        if any(k in c for k in kw): return ind
    return "General"

# ─── REDDIT LIVE SEARCH ───────────────────────────────────────────────────────

def search_reddit(keyword, seen, timelimit="day"):
    results = []
    url = "https://www.reddit.com/search.json"
    params = {
        "q":     keyword,
        "sort":  "new",
        "t":     timelimit,   # hour / day / week / month
        "limit": 15,
        "type":  "link",
    }
    try:
        r = requests.get(url, params=params, headers=REDDIT_HEADERS, timeout=10)
        if r.status_code != 200:
            return results
        data = r.json()
        posts = data.get("data", {}).get("children", [])
        for post in posts:
            p    = post.get("data", {})
            purl = "https://www.reddit.com" + p.get("permalink", "")
            if purl in seen: continue
            seen.add(purl)
            title    = p.get("title", "")
            selftext = p.get("selftext", "")[:300]
            subreddit = p.get("subreddit", "")
            author   = p.get("author", "")
            created  = datetime.fromtimestamp(p.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M")
            results.append({
                "Confidence":       score(title, selftext),
                "Platform":         f"Reddit r/{subreddit}",
                "Keyword Used":     keyword,
                "Industry":         detect_industry(title, selftext),
                "Author":           f"u/{author}",
                "Title / Post":     title[:150],
                "URL":              purl,
                "Snippet":          selftext[:200],
                "Posted At":        created,
                "Outreach":         f"u/{author} ke post pe comment karo ya DM karo",
                "Status":           "Not Contacted",
                "Notes":            "",
            })
    except Exception as e:
        print(f"      Reddit error: {e}", flush=True)
    return results

# ─── LINKEDIN WEB SEARCH ──────────────────────────────────────────────────────

def search_linkedin(keyword, seen):
    results = []
    query = f'site:linkedin.com/posts "{keyword}"'
    try:
        with DDGS() as ddgs:
            hits = ddgs.text(query, region="us-en", max_results=8, timelimit="w")
            for r in hits:
                url   = r.get("href", "")
                title = r.get("title", "")
                body  = r.get("body", "")
                if not url or url in seen: continue
                seen.add(url)
                results.append({
                    "Confidence":   score(title, body),
                    "Platform":     "LinkedIn",
                    "Keyword Used": keyword,
                    "Industry":     detect_industry(title, body),
                    "Author":       title.split(" - ")[0].split("|")[0].strip()[:60],
                    "Title / Post": title[:150],
                    "URL":          url,
                    "Snippet":      body[:200],
                    "Posted At":    "",
                    "Outreach":     "LinkedIn pe connect request bhejo ya comment karo",
                    "Status":       "Not Contacted",
                    "Notes":        "",
                })
    except Exception as e:
        print(f"      LinkedIn error: {e}", flush=True)
    return results

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    keywords = load_keywords()
    print("=" * 65, flush=True)
    print("  TAFSOL — SMART KEYWORD SEARCH", flush=True)
    print(f"  Keywords loaded : {len(keywords)}", flush=True)
    print(f"  Platforms       : Reddit (live) + LinkedIn", flush=True)
    print(f"  Started at      : {datetime.now().strftime('%Y-%m-%d %H:%M')}", flush=True)
    print("=" * 65, flush=True)

    print("\nTimeframe select karo:")
    print("  [1] Last 1 hour   (freshest)")
    print("  [2] Last 24 hours (recommended)")
    print("  [3] Last week")
    t = input("\nChoice (1/2/3): ").strip()
    timelimit = {"1": "hour", "2": "day", "3": "week"}.get(t, "day")
    print(f"\nSearching last: {timelimit}\n", flush=True)

    all_leads = []
    seen_urls  = set()

    for i, kw in enumerate(keywords, 1):
        print(f"[{i}/{len(keywords)}] '{kw}'", flush=True)

        # Reddit
        r_leads = search_reddit(kw, seen_urls, timelimit)
        all_leads.extend(r_leads)
        print(f"   Reddit  → {len(r_leads)} posts", flush=True)
        time.sleep(random.uniform(1, 2))

        # LinkedIn
        l_leads = search_linkedin(kw, seen_urls)
        all_leads.extend(l_leads)
        print(f"   LinkedIn→ {len(l_leads)} posts", flush=True)
        time.sleep(random.uniform(1.5, 2.5))

    if not all_leads:
        print("\nKoi lead nahi mili. Timelimit 'week' karo ya keywords update karo.")
        return

    # ─── SAVE ─────────────────────────────────────────────────────────────────
    df = pd.DataFrame(all_leads)
    df["_s"] = df["Confidence"].map({"HIGH":0,"MEDIUM":1})
    df = df.sort_values(["_s","Platform"]).drop(columns=["_s"])

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    fname = os.path.join(OUTPUT_DIR, f"smart_leads_{stamp}.xlsx")

    with pd.ExcelWriter(fname, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="All Leads")
        _fmt(writer.sheets["All Leads"])

        df_h = df[df["Confidence"] == "HIGH"]
        if not df_h.empty:
            df_h.to_excel(writer, index=False, sheet_name="HIGH Intent")
            _fmt(writer.sheets["HIGH Intent"])

        for plat in df["Platform"].str.split(" ").str[0].unique():
            df_p = df[df["Platform"].str.startswith(plat)]
            sname = plat[:31]
            df_p.to_excel(writer, index=False, sheet_name=sname)
            _fmt(writer.sheets[sname])

    # ─── SUMMARY ──────────────────────────────────────────────────────────────
    high   = len(df[df["Confidence"]=="HIGH"])
    medium = len(df[df["Confidence"]=="MEDIUM"])

    print("\n" + "=" * 65, flush=True)
    print("  DONE!", flush=True)
    print(f"  Total leads  : {len(df)}", flush=True)
    print(f"  HIGH Intent  : {high}  ← yahan se shuru karo", flush=True)
    print(f"  MEDIUM       : {medium}", flush=True)
    print(f"\n  File: {os.path.basename(fname)}", flush=True)
    print(f"  → 'HIGH Intent' sheet mein hottest leads hain", flush=True)
    print("=" * 65, flush=True)


def _fmt(ws):
    from openpyxl.utils import get_column_letter
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 3, 60)
    ws.freeze_panes = "A2"


if __name__ == "__main__":
    main()
