import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# Search 1: Find real estate people to connect with
PROFILE_QUERIES = [
    'site:linkedin.com/in "real estate" "CEO" OR "Founder" OR "Owner" USA',
    'site:linkedin.com/in "real estate agency" "founder" Florida OR Texas OR California',
    'site:linkedin.com/in "property management" "CEO" OR "owner" United States',
    'site:linkedin.com/in "real estate broker" "founder" New York OR Miami OR Chicago',
    'site:linkedin.com/in "boutique real estate" "CEO" OR "founder"',
    'site:linkedin.com/in "luxury real estate" "owner" OR "founder" USA',
    'site:linkedin.com/in "commercial real estate" "CEO" OR "managing director" USA',
    'site:linkedin.com/in "real estate investment" "founder" OR "principal" United States',
]

POST_QUERIES = [
    'site:linkedin.com "real estate website" "not getting leads" OR "struggling"',
    'site:linkedin.com "real estate" "website redesign" OR "need branding"',
    'site:linkedin.com "real estate agency" "digital marketing" help',
    'site:linkedin.com "property management" "website" "chatbot" OR "leads"',
    'site:linkedin.com "real estate" "online presence" improve',
    'site:linkedin.com "real estate" "AI" OR "chatbot" website 2024 OR 2025',
    'site:linkedin.com "real estate marketing" "what works" OR "tips"',
]

OUTPUT_PROFILES = "linkedin_profiles.xlsx"
OUTPUT_POSTS    = "linkedin_posts.xlsx"

# ─── MESSAGE TEMPLATES ────────────────────────────────────────────────────────

CONNECTION_MESSAGES = [
    "Hi {name}, I came across your profile and was impressed by your work at {company}. I help US real estate agencies capture more leads with AI chatbots and high-converting websites — we've helped similar firms 2-3x their inbound leads. Would love to connect!",
    "Hi {name}, love what you're building at {company}! I specialize in AI-powered web solutions for real estate founders — helping turn website visitors into booked appointments. Let's connect — I have one quick idea that might be useful.",
    "Hi {name}, noticed your work in real estate at {company}. We build AI chatbots and lead-gen websites specifically for US real estate agencies. Most of our clients see results in 60 days. Would be great to connect!",
    "Hi {name}, your work at {company} caught my attention. I help real estate agencies like yours stop losing after-hours leads with 24/7 AI chatbots. Happy to share what's worked — let's connect!",
]

COMMENT_TEMPLATES = [
    "Great point! One thing that's made a big difference for real estate agencies — an AI chatbot on the website. 70% of real estate searches happen after 9pm. If no one's available, you're losing those leads. Happy to share what's worked for agencies we've partnered with.",
    "This resonates! Website speed + mobile optimization are often the #1 untapped opportunity for real estate lead gen. We've seen 3x more conversions just from fixing load time and adding a click-to-call button on mobile. What does your current website setup look like?",
    "Totally agree. Real estate agencies that invest in website conversion (not just ad spend) consistently outperform. A free home valuation tool above the fold is one of the highest-converting lead magnets we've seen — simple to add, huge ROI.",
    "Interesting take. From working with US real estate agencies — the biggest gap isn't traffic, it's what happens after the click. A clear value prop, social proof (sold listings, reviews), and a chatbot for instant response can dramatically change your numbers.",
]

# ─── AGENT FUNCTIONS ──────────────────────────────────────────────────────────

def find_profiles():
    print("\n[1/2] Searching for LinkedIn profiles to connect with...\n")
    results = []
    seen = set()

    with DDGS() as ddgs:
        for query in PROFILE_QUERIES:
            print(f"  {query[:65]}...")
            try:
                hits = ddgs.text(query, region="us-en", max_results=8)
                for r in hits:
                    url   = r.get("href", "")
                    title = r.get("title", "")
                    body  = r.get("body", "")
                    if "linkedin.com/in/" in url and url not in seen:
                        seen.add(url)
                        # Extract name from title (usually "Name - Title - Company")
                        name    = title.split(" - ")[0].strip() if " - " in title else title
                        company = title.split(" - ")[2].strip() if title.count(" - ") >= 2 else ""
                        conn_msg = random.choice(CONNECTION_MESSAGES).format(
                            name=name.split()[0] if name else "there",
                            company=company if company else "your company"
                        )
                        results.append({
                            "name":               name,
                            "company":            company,
                            "profile_url":        url,
                            "snippet":            body[:150],
                            "connection_message": conn_msg,
                            "connected":          "No",
                            "replied":            "No",
                            "follow_up_date":     "",
                            "notes":              "",
                            "found_at":           datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                print(f"  Error: {e}")

    return results


def find_posts():
    print("\n[2/2] Searching for LinkedIn posts to comment on...\n")
    results = []
    seen = set()

    with DDGS() as ddgs:
        for query in POST_QUERIES:
            print(f"  {query[:65]}...")
            try:
                hits = ddgs.text(query, region="us-en", max_results=8)
                for r in hits:
                    url   = r.get("href", "")
                    title = r.get("title", "")
                    body  = r.get("body", "")
                    if "linkedin.com" in url and url not in seen:
                        seen.add(url)
                        results.append({
                            "title":             title,
                            "url":               url,
                            "snippet":           body[:200],
                            "suggested_comment": random.choice(COMMENT_TEMPLATES),
                            "commented":         "No",
                            "comment_date":      "",
                            "notes":             "",
                            "found_at":          datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                print(f"  Error: {e}")

    return results


def save_to_excel(data, filename, sheet_name):
    if not data:
        print(f"  No data to save for {sheet_name}")
        return
    df = pd.DataFrame(data)
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
        ws.freeze_panes = "A2"
    print(f"  Saved {len(df)} records to {filename}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL LINKEDIN AGENT")
    print("  No login required — finding profiles & posts via search")
    print("=" * 60)

    # Find profiles to connect with
    profiles = find_profiles()
    save_to_excel(profiles, OUTPUT_PROFILES, "Profiles to Connect")

    # Find posts to comment on
    posts = find_posts()
    save_to_excel(posts, OUTPUT_POSTS, "Posts to Comment")

    print("\n" + "=" * 60)
    print(f"  Done!")
    print(f"  Profiles found : {len(profiles)}  ->  {OUTPUT_PROFILES}")
    print(f"  Posts found    : {len(posts)}  ->  {OUTPUT_POSTS}")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. linkedin_profiles.xlsx kholo — profile open karo, connection message copy karo, send karo")
    print("  2. linkedin_posts.xlsx kholo — post open karo, comment copy karo, post karo")
    print("  LinkedIn automation = account ban, isliye manual hi safe hai.")


if __name__ == "__main__":
    main()
