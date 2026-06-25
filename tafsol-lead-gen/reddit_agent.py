import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Subreddits to monitor
SEARCH_QUERIES = [
    "site:reddit.com realestate website not getting leads help",
    "site:reddit.com realestate branding website redesign help",
    "site:reddit.com realestate digital marketing strategy 2024 OR 2025",
    "site:reddit.com PropertyManagement website design leads generation",
    "site:reddit.com RealEstateAgents chatbot AI website clients",
    "site:reddit.com realestateinvesting marketing online presence improve",
    "site:reddit.com smallbusiness real estate website struggling conversions",
    "site:reddit.com realestate SEO website traffic leads",
    "site:reddit.com realestate social media marketing not working",
    "site:reddit.com entrepreneur real estate agency website tips",
]

OUTPUT_FILE = "reddit_leads.xlsx"

# ─── COMMENT TEMPLATES ────────────────────────────────────────────────────────
# Generic, helpful — not spammy. Mention Tafsol only subtly.

COMMENT_TEMPLATES = [
    """Great question! A few things that actually move the needle for real estate lead gen:

1. **AI chatbot on your website** — 70% of real estate searches happen after 9pm. If no one answers, that lead is gone. A chatbot captures them 24/7.
2. **"Get a Free Home Valuation" CTA above the fold** — this converts 3-4x better than a generic contact form.
3. **Mobile speed** — if your site loads in 4+ seconds on mobile, you're losing the majority of your traffic right there.

We've helped several US real estate agencies fix exactly these issues. Happy to share more if useful.""",

    """This is super common for real estate agencies. The websites that consistently convert have:

- A clear value prop on the homepage (not just "Buy & Sell Homes" — something specific to your market)
- An AI chatbot or live chat for after-hours inquiries (biggest ROI we've seen)
- Social proof above the fold — sold listings, client reviews, local market stats

The good news: a quick audit usually surfaces 3-4 quick wins that don't need a full redesign. What does your homepage look like right now?""",

    """From working with real estate agencies across the US — the gap is almost always conversion, not traffic.

Quick wins that work:
- Free home valuation tool (captures emails + phone numbers)
- AI chatbot for instant response (we use this for clients — huge difference)
- Click-to-call button that's visible on mobile
- Testimonials from local clients with photos

What platform is your website on? That usually determines how fast these can be implemented.""",

    """Real talk — most real estate websites are built to look good, not to convert. The agencies killing it right now have:

- **Speed**: Under 2.5s load time on mobile
- **Chatbot**: Captures leads when you're unavailable (which is most of the time)
- **Trust signals**: Reviews, certifications, local market expertise upfront
- **One clear CTA**: Not 5 options — just one thing you want visitors to do

What's your biggest challenge right now — traffic or converting the traffic you already have?""",
]


# ─── REDDIT AGENT — DDG Search (no credentials needed) ────────────────────────

def find_opportunities():
    opportunities = []
    seen = set()
    print(f"\nSearching Reddit via DuckDuckGo (no login needed)...\n")

    with DDGS() as ddgs:
        for query in SEARCH_QUERIES:
            print(f"  Searching: {query[:60]}...")
            try:
                results = ddgs.text(query, region="us-en", max_results=10)
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if "reddit.com" in url and url not in seen:
                        seen.add(url)
                        subreddit = url.split("/r/")[1].split("/")[0] if "/r/" in url else "reddit"
                        opportunities.append({
                            "subreddit":         subreddit,
                            "title":             title,
                            "url":               url,
                            "snippet":           body[:200],
                            "suggested_comment": random.choice(COMMENT_TEMPLATES),
                            "status":            "Pending",
                            "commented":         "No",
                            "notes":             "",
                            "found_at":          datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                print(f"  Error: {e}")

    return opportunities


def save_opportunities(opportunities):
    df = pd.DataFrame(opportunities)
    df = df.sort_values("subreddit", ascending=True)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reddit Opportunities")
        ws = writer.sheets["Reddit Opportunities"]
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
        ws.freeze_panes = "A2"

    print(f"\nSaved {len(df)} opportunities to {OUTPUT_FILE}")
    return df


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL REDDIT AGENT")
    print("  No login required — using public Reddit API")
    print("=" * 60)

    opps = find_opportunities()

    if not opps:
        print("\nNo relevant posts found.")
        return

    df = save_opportunities(opps)

    print(f"\nTop 5 opportunities:")
    print("-" * 60)
    for _, row in df.head(5).iterrows():
        print(f"r/{row['subreddit']} | {row['title'][:55]}")
        print(f"  {row['url']}")

    print(f"\nOpen {OUTPUT_FILE} — review posts + suggested comments, then post manually.")


if __name__ == "__main__":
    main()
