import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── SEARCH QUERIES — people who NEED developers ──────────────────────────────

NEED_QUERIES = [
    # Priority 1: Direct outsourcing / agency intent
    'site:linkedin.com "looking for software development company"',
    'site:linkedin.com "looking for development agency"',
    'site:linkedin.com "need a development partner"',
    'site:linkedin.com "looking for offshore developers"',
    'site:linkedin.com "dedicated development team" "looking" OR "need"',
    'site:linkedin.com "staff augmentation" "software" "looking" OR "need"',
    'site:linkedin.com "software outsourcing" "partner" OR "looking"',
    'site:linkedin.com "white-label development" OR "white label software"',
    'site:linkedin.com "CTO as a Service" OR "fractional CTO" "looking"',
    # Priority 2: Startup / MVP signals
    'site:linkedin.com "startup" "looking for technical cofounder" OR "need CTO"',
    'site:linkedin.com "build MVP" "need developer" OR "looking for"',
    'site:linkedin.com "launch SaaS" "need developers" OR "looking for dev"',
    'site:linkedin.com "startup" "MVP development" "need" OR "hire"',
    'site:linkedin.com "prototype development" "looking for developer"',
    # Priority 3: AI & Automation (hot market)
    'site:linkedin.com "ChatGPT integration" "need developer" OR "looking for"',
    'site:linkedin.com "OpenAI integration" "need" OR "looking" 2025',
    'site:linkedin.com "AI automation" "need developer" OR "looking for company"',
    'site:linkedin.com "workflow automation" "need developer" OR "build"',
    'site:linkedin.com "AI agent" "looking for developer" OR "need to build"',
    'site:linkedin.com "LLM application" "need developer" OR "build"',
    # Priority 4: Custom software / platform
    'site:linkedin.com "CRM development" OR "custom CRM" "need" OR "looking for"',
    'site:linkedin.com "ERP development" OR "custom ERP" "need" OR "looking for"',
    'site:linkedin.com "marketplace development" "need developer" OR "looking for"',
    'site:linkedin.com "web application" "need developer" OR "looking for company"',
    'site:linkedin.com "mobile app development" "need" OR "looking for developer"',
    # Priority 5: Tech stack hiring (companies that may outsource)
    'site:linkedin.com "looking for" "MERN developer" "hire" OR "need" OR "urgent"',
    'site:linkedin.com "need a" "Laravel developer" "project" OR "urgent" OR "hire"',
    'site:linkedin.com "looking for" "full stack developer" "urgent" OR "immediately"',
    'site:linkedin.com "hiring" "MERN stack" developer "remote" OR "freelance"',
    'site:linkedin.com "looking for" "React Native developer" "app" "hire"',
    'site:linkedin.com "urgent requirement" developer "MERN" OR "Laravel" OR "fullstack"',
    'site:linkedin.com "hiring Flutter developer" OR "hiring React Native" USA',
    'site:linkedin.com "hiring Python developer" OR "hiring AI developer" remote',
    'site:linkedin.com "hiring Node.js developer" OR "hiring backend developer" USA',
    # Priority 6: Problem-based / asking community
    'site:linkedin.com "anyone know" "good developer" OR "good software company"',
    'site:linkedin.com "recommend" "software development company" OR "development agency"',
    'site:linkedin.com "need help" "build app" OR "build website" OR "build software"',
    'site:linkedin.com "DM me" "developer" "MERN" OR "Laravel" OR "React" "need"',
    # Priority 7: Industry + development
    'site:linkedin.com "healthcare" "app development" "need" OR "looking for"',
    'site:linkedin.com "real estate" "app" OR "software" "need developer" OR "looking"',
    'site:linkedin.com "fintech" "need developers" OR "looking for dev team"',
    'site:linkedin.com "logistics" "automation software" "need" OR "looking for"',
    'site:linkedin.com "e-commerce" "custom development" "need" OR "looking"',
    'site:linkedin.com "legal" OR "law firm" "software" "need developer" OR "looking"',
]

OUTPUT_FILE = "linkedin_dev_leads.xlsx"

# ─── OUTREACH TEMPLATES ───────────────────────────────────────────────────────

OUTREACH_MESSAGES = [
    "Hi {name}, I saw your post — we have a strong team of MERN/Laravel developers at Tafsol Technologies. We work on fixed-cost projects with clear timelines. Happy to share our portfolio and discuss your requirement!",
    "Hi {name}, noticed you're looking for a developer. At Tafsol, we have experienced MERN & Laravel devs available for immediate start. Would love to understand your project and share how we can help!",
    "Hi {name}, saw your requirement! We're Tafsol Technologies — a dev team specializing in MERN stack & Laravel. We've delivered 50+ projects for clients globally. Can we jump on a quick call to discuss?",
    "Hi {name}, we can help! Tafsol has dedicated MERN/Laravel developers ready to start. We offer transparent pricing, NDA, and regular updates. Would you like to see some relevant work we've done?",
]

# ─── SCRAPER ──────────────────────────────────────────────────────────────────

def find_dev_leads():
    leads = []
    seen = set()
    print(f"\nSearching for developer requirement posts on LinkedIn...\n")

    with DDGS() as ddgs:
        for query in NEED_QUERIES:
            print(f"  Searching: {query[:70]}...")
            try:
                results = ddgs.text(query, region="us-en", max_results=8, timelimit="w")
                for r in results:
                    url   = r.get("href", "")
                    title = r.get("title", "")
                    body  = r.get("body", "")

                    if "linkedin.com" not in url or url in seen:
                        continue

                    seen.add(url)

                    # Extract name
                    name = title.split(" - ")[0].strip() if " - " in title else title.split("|")[0].strip()
                    first_name = name.split()[0] if name else "there"

                    # Detect tech stack mentioned
                    body_lower = body.lower()
                    tech = []
                    if "mern" in body_lower: tech.append("MERN")
                    if "laravel" in body_lower or "php" in body_lower: tech.append("Laravel/PHP")
                    if "react" in body_lower: tech.append("React")
                    if "node" in body_lower: tech.append("Node.js")
                    if "full stack" in body_lower or "fullstack" in body_lower: tech.append("Full Stack")
                    if "react native" in body_lower: tech.append("React Native")
                    if not tech: tech.append("Developer")

                    outreach = random.choice(OUTREACH_MESSAGES).format(name=first_name)

                    leads.append({
                        "Name":             name,
                        "Tech Stack":       ", ".join(tech),
                        "Post URL":         url,
                        "Post Snippet":     body[:250],
                        "Outreach Message": outreach,
                        "Status":           "Not Contacted",
                        "DM Sent":          "No",
                        "Reply":            "No",
                        "Follow Up Date":   "",
                        "Notes":            "",
                        "Found At":         datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

                time.sleep(random.uniform(2, 3.5))

            except Exception as e:
                print(f"  Error: {e}")

    return leads


def save_to_excel(leads):
    if not leads:
        print("\nNo leads found.")
        return

    df = pd.DataFrame(leads)
    df = df.sort_values("Tech Stack")

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dev Leads")
        ws = writer.sheets["Dev Leads"]
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
        ws.freeze_panes = "A2"

    print(f"\nSaved {len(df)} leads to {OUTPUT_FILE}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL — LinkedIn Developer Requirement Leads")
    print("  Finding people who NEED developers right now")
    print("=" * 60)

    leads = find_dev_leads()
    save_to_excel(leads)

    if leads:
        print(f"\nTop leads found:")
        print("-" * 60)
        for l in leads[:5]:
            print(f"{l['Name']} | {l['Tech Stack']}")
            print(f"  {l['Post URL'][:70]}")
        print(f"\nOpen {OUTPUT_FILE} — copy outreach message and DM them on LinkedIn.")


if __name__ == "__main__":
    main()
