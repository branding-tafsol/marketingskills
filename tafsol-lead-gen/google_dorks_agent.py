import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── GOOGLE DORK QUERIES — Highest Buying Intent ──────────────────────────────
# These find companies actively looking to hire / outsource development
# Grouped by intent level (Priority 1 = hottest)

DORK_QUERIES = [
    # ── PRIORITY 1: Direct outsourcing intent ─────────────────────────────────
    '"looking for software development company" USA',
    '"looking for development agency" site:linkedin.com OR site:reddit.com',
    '"need a development partner" startup OR company',
    '"looking for offshore developers" USA site:linkedin.com',
    '"dedicated development team" "looking for" OR "need"',
    '"software outsourcing partner" USA OR "United States"',
    '"IT staff augmentation" "looking for" OR "need" USA',
    '"white-label development" "looking for" agency',
    '"CTO as a Service" "looking for" OR "need" startup',
    '"outsource software development" "partner" USA 2025',

    # ── PRIORITY 2: Startup / MVP signals ─────────────────────────────────────
    '"looking for technical cofounder" startup site:linkedin.com OR site:reddit.com',
    '"startup needs developers" OR "startup looking for developers"',
    '"build MVP" "need developer" OR "looking for developer" site:reddit.com OR site:linkedin.com',
    '"MVP development" "need" OR "looking for" startup USA',
    '"launch SaaS" "need developers" site:linkedin.com OR site:reddit.com',
    '"startup" "need CTO" OR "looking for CTO" site:linkedin.com',

    # ── PRIORITY 3: AI & Automation (booming 2025) ────────────────────────────
    '"ChatGPT integration" "need developer" OR "looking for" site:linkedin.com OR site:reddit.com',
    '"OpenAI integration" "hire" OR "need developer" 2025',
    '"AI automation" "need software" OR "looking for developer" USA',
    '"workflow automation" "need developer" OR "software company" site:linkedin.com',
    '"AI agent" "build" "looking for developer" OR "need developer"',
    '"LLM application" "need developer" OR "hire developer"',
    '"document AI" OR "voice AI" "need developer" startup',

    # ── PRIORITY 4: Custom software platforms ─────────────────────────────────
    '"custom CRM development" "looking for" OR "need"',
    '"custom ERP development" "looking for" OR "need"',
    '"marketplace development" "need developer" OR "looking for company"',
    '"web application development" "looking for company" USA',
    '"mobile app development" "need" OR "looking for" company USA 2025',
    '"SaaS development" "need developers" OR "looking for dev team"',
    '"build internal tool" "need developer" OR "looking for"',

    # ── PRIORITY 5: Industry + development (high-value verticals) ─────────────
    '"healthcare app development" "need" OR "looking for" company USA',
    '"dental software" "looking for" OR "need developer"',
    '"real estate app development" "need developer" OR "looking for company"',
    '"law firm software" "need developer" OR "looking for"',
    '"fintech development" "need developers" OR "looking for team"',
    '"construction ERP" "need developer" OR "looking for software"',
    '"logistics automation" "need developer" OR "looking for software company"',
    '"e-commerce custom development" "need" OR "looking for" USA',
    '"restaurant POS" "custom" "need developer" OR "looking for"',
    '"insurance software" "need developer" OR "looking for company"',

    # ── PRIORITY 6: Job boards (companies hiring = potential outsource clients) ─
    'site:wellfound.com "MERN" OR "React" OR "Node.js" developer hiring',
    'site:builtin.com "full stack developer" hiring "Series A" OR "Series B" OR "startup"',
    'site:indeed.com "contract developer" OR "freelance developer" MERN OR React OR Node',
    'site:remoteok.com "MERN" OR "Laravel" OR "React Native" developer',
    'site:weworkremotely.com "full stack developer" OR "React developer" 2025',

    # ── PRIORITY 7: Reddit high-intent threads ────────────────────────────────
    'site:reddit.com "looking for software development company" -site:reddit.com/r/forhire',
    'site:reddit.com "recommend software company" OR "recommend dev agency"',
    'site:reddit.com "need a developer" "app" OR "website" OR "software" -job -jobs',
    'site:reddit.com "who can build my app" OR "who can develop my software"',
    'site:reddit.com "startup" "need developers" "recommendation" OR "recommend"',

    # ── PRIORITY 8: Quora high-intent ─────────────────────────────────────────
    'site:quora.com "best software development company" USA',
    'site:quora.com "how to find software development company"',
    'site:quora.com "how to outsource software development"',
    'site:quora.com "startup" "how to find developers"',
    'site:quora.com "how to hire dedicated developers"',
]

OUTPUT_FILE = "google_dorks_leads.xlsx"

# ─── CONFIDENCE SCORING ───────────────────────────────────────────────────────

HIGH_INTENT_KEYWORDS = [
    "looking for software development company", "looking for development agency",
    "need a development partner", "offshore developers", "dedicated development team",
    "staff augmentation", "software outsourcing", "white-label development",
    "CTO as a Service", "build MVP", "ChatGPT integration", "OpenAI integration",
    "AI automation", "custom CRM", "custom ERP", "looking for developer",
    "need developers", "hire dedicated", "technical cofounder",
]

MEDIUM_INTENT_KEYWORDS = [
    "hiring MERN", "hiring React", "hiring Node", "hiring Flutter", "hiring Python",
    "hiring Laravel", "contract developer", "freelance developer", "remote developer",
    "web application development", "mobile app development", "SaaS development",
]

def score_lead(title, body):
    combined = (title + " " + body).lower()
    if any(k.lower() in combined for k in HIGH_INTENT_KEYWORDS):
        return "High"
    elif any(k.lower() in combined for k in MEDIUM_INTENT_KEYWORDS):
        return "Medium"
    return "Low"

def detect_industry(title, body):
    combined = (title + " " + body).lower()
    if any(k in combined for k in ["healthcare", "medical", "dental", "health"]):
        return "Healthcare"
    elif any(k in combined for k in ["real estate", "property", "realty"]):
        return "Real Estate"
    elif any(k in combined for k in ["fintech", "finance", "banking", "insurance"]):
        return "Finance/Fintech"
    elif any(k in combined for k in ["legal", "law firm", "attorney"]):
        return "Legal"
    elif any(k in combined for k in ["construction", "contractor", "building"]):
        return "Construction"
    elif any(k in combined for k in ["logistics", "shipping", "transport"]):
        return "Logistics"
    elif any(k in combined for k in ["ecommerce", "e-commerce", "shopify", "retail"]):
        return "E-commerce"
    elif any(k in combined for k in ["saas", "startup", "mvp"]):
        return "SaaS/Startup"
    elif any(k in combined for k in ["restaurant", "food", "hospitality"]):
        return "Hospitality"
    elif any(k in combined for k in ["education", "edtech", "school", "university"]):
        return "Education"
    elif any(k in combined for k in ["marketing agency", "digital agency"]):
        return "Marketing Agency"
    return "General"

def detect_tech_need(title, body):
    combined = (title + " " + body).lower()
    needs = []
    if any(k in combined for k in ["mern", "react", "node.js", "mongodb"]): needs.append("MERN Stack")
    if any(k in combined for k in ["laravel", "php"]): needs.append("Laravel/PHP")
    if any(k in combined for k in ["python", "fastapi", "django"]): needs.append("Python")
    if any(k in combined for k in ["flutter", "react native", "mobile app"]): needs.append("Mobile")
    if any(k in combined for k in ["ai", "chatgpt", "openai", "llm", "automation"]): needs.append("AI/Automation")
    if any(k in combined for k in ["crm", "erp", "enterprise"]): needs.append("Enterprise Software")
    if any(k in combined for k in ["saas", "web app", "web application"]): needs.append("Web App/SaaS")
    if any(k in combined for k in [".net", "c#", "asp.net"]): needs.append(".NET")
    if not needs: needs.append("General Software")
    return ", ".join(needs)

# ─── SUGGESTED OUTREACH ───────────────────────────────────────────────────────

OUTREACH_MESSAGES = [
    "Hi {name}, I saw you're looking for a software development partner — at Tafsol Technologies we specialize in exactly this for US companies. We have dedicated MERN/Laravel/AI developers available immediately. Would love to share our work and discuss your project.",

    "Hi {name}, noticed you're searching for a development agency. Tafsol Technologies builds custom software, web apps, mobile apps, and AI solutions for US businesses — fixed-cost, clear timelines, NDA protected. Happy to share relevant case studies. Can we connect?",

    "Hi {name}, your post/question caught my attention — we help companies like yours with dedicated offshore development teams at US-quality standards. Tafsol has delivered 50+ projects for clients in California, Texas, Florida & New York. Would a 15-min call work?",

    "Hi {name}, at Tafsol Technologies we specialize in custom software development for US businesses — MERN stack, AI automation, mobile apps, CRM/ERP. Our clients typically launch their MVP in 8-12 weeks. Would you be open to a quick call to discuss your requirements?",
]


# ─── MAIN SCRAPER ─────────────────────────────────────────────────────────────

def find_leads():
    leads = []
    seen = set()
    print(f"\nSearching {len(DORK_QUERIES)} queries for high-intent leads...\n")

    with DDGS() as ddgs:
        for i, query in enumerate(DORK_QUERIES, 1):
            print(f"  [{i}/{len(DORK_QUERIES)}] {query[:70]}...")
            try:
                results = ddgs.text(query, region="us-en", max_results=8, timelimit="m")
                for r in results:
                    url   = r.get("href", "")
                    title = r.get("title", "")
                    body  = r.get("body", "")

                    if url in seen or not url:
                        continue
                    seen.add(url)

                    # Detect source platform
                    if "linkedin.com" in url:       platform = "LinkedIn"
                    elif "reddit.com" in url:        platform = "Reddit"
                    elif "quora.com" in url:         platform = "Quora"
                    elif "wellfound.com" in url:     platform = "Wellfound"
                    elif "builtin.com" in url:       platform = "Built In"
                    elif "indeed.com" in url:        platform = "Indeed"
                    elif "remoteok.com" in url:      platform = "RemoteOK"
                    elif "weworkremotely" in url:    platform = "WeWorkRemotely"
                    elif "facebook.com" in url:      platform = "Facebook"
                    else:                            platform = "Web"

                    confidence = score_lead(title, body)
                    industry   = detect_industry(title, body)
                    tech_need  = detect_tech_need(title, body)

                    name = title.split(" - ")[0].strip() if " - " in title else title.split("|")[0].strip()
                    first_name = name.split()[0] if name else "there"
                    outreach = random.choice(OUTREACH_MESSAGES).format(name=first_name)

                    leads.append({
                        "Confidence":       confidence,
                        "Platform":         platform,
                        "Industry":         industry,
                        "Tech Need":        tech_need,
                        "Title/Name":       title[:120],
                        "URL":              url,
                        "Snippet":          body[:250],
                        "Outreach Message": outreach,
                        "Status":           "Not Contacted",
                        "Contacted Date":   "",
                        "Reply":            "No",
                        "Notes":            "",
                        "Found At":         datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Search Query":     query[:80],
                    })

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(3)

    return leads


def save_to_excel(leads):
    if not leads:
        print("\nNo leads found.")
        return

    df = pd.DataFrame(leads)

    # Sort: High confidence first, then by platform
    confidence_order = {"High": 0, "Medium": 1, "Low": 2}
    df["_sort"] = df["Confidence"].map(confidence_order)
    df = df.sort_values(["_sort", "Platform"]).drop(columns=["_sort"])

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="All Leads")
        ws = writer.sheets["All Leads"]

        # Separate high-intent sheet
        df_high = df[df["Confidence"] == "High"]
        if not df_high.empty:
            df_high.to_excel(writer, index=False, sheet_name="HIGH Intent")
            ws2 = writer.sheets["HIGH Intent"]
            for col in ws2.columns:
                max_len = max((len(str(c.value or "")) for c in col), default=10)
                ws2.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
            ws2.freeze_panes = "A2"

        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
        ws.freeze_panes = "A2"

    print(f"\nSaved {len(df)} leads to {OUTPUT_FILE}")
    return df


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL GOOGLE DORKS AGENT")
    print("  High-intent leads across all platforms")
    print("=" * 60)

    leads = find_leads()

    if not leads:
        print("\nNo leads found.")
        return

    df = save_to_excel(leads)

    # Summary
    high   = len([l for l in leads if l["Confidence"] == "High"])
    medium = len([l for l in leads if l["Confidence"] == "Medium"])
    low    = len([l for l in leads if l["Confidence"] == "Low"])

    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Total leads    : {len(leads)}")
    print(f"  HIGH intent    : {high}  ← Start here")
    print(f"  MEDIUM intent  : {medium}")
    print(f"  LOW intent     : {low}")
    print(f"\n  Open {OUTPUT_FILE}")
    print(f"  → 'HIGH Intent' sheet mein sabse hot leads hain")
    print(f"  → Outreach Message copy karo, send karo")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
