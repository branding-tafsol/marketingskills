import sys
import io
import time
import random
import pandas as pd
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CONFIG ───────────────────────────────────────────────────────────────────

QUORA_SEARCH_QUERIES = [
    "site:quora.com real estate website not getting leads",
    "site:quora.com how to get more real estate clients online",
    "site:quora.com real estate agency website design tips",
    "site:quora.com real estate branding importance",
    "site:quora.com real estate digital marketing strategy",
    "site:quora.com chatbot for real estate website",
    "site:quora.com how to improve real estate website",
]

OUTPUT_FILE = "quora_opportunities.xlsx"

# ─── ANSWER TEMPLATES ─────────────────────────────────────────────────────────

def generate_answer(question_title):
    title = question_title.lower()

    if "chatbot" in title:
        return """Great question! A chatbot on a real estate website can be a game-changer. Here's why:

**Why it matters:**
- 70% of website visitors come outside business hours
- Most people won't fill a form — but they WILL chat
- A chatbot can qualify leads automatically (budget, timeline, area)

**Best options for real estate:**
1. Tidio (free tier available)
2. Drift (professional)
3. Custom AI chatbot (best for branding)

The agencies I've seen convert best are the ones with a chatbot that asks: "Are you buying or selling? What's your timeline?" — then books a call automatically.

If you want a branded solution built specifically for real estate, happy to point you in the right direction."""

    elif "leads" in title or "clients" in title or "getting" in title:
        return """This is one of the most common challenges for real estate agencies. Here's what actually works:

**Short-term (this month):**
- Add a free home valuation tool to your website (huge lead magnet)
- Make your phone number click-to-call on mobile
- Add a live chat — don't let visitors leave without engaging

**Medium-term (next 90 days):**
- Google My Business fully optimized (photos, reviews, posts)
- Neighborhood-specific landing pages ("Homes for Sale in [Area]")
- Email follow-up sequence for every inquiry

**What most agencies miss:**
The website itself is usually the problem — slow load time, no clear CTA, no trust signals. Before spending on ads, fix the conversion rate first.

Happy to elaborate on any of these."""

    elif "branding" in title:
        return """Real estate branding is more important than most agents realize. Here's the honest truth:

**Why branding matters in real estate:**
- Buyers and sellers choose agents they trust — trust is built visually before the first call
- A professional brand makes you look established even if you're new
- Consistent branding across website, social, and print = memorability

**What strong real estate branding looks like:**
1. A clear niche ("Luxury homes in Miami" vs "We sell everything everywhere")
2. Professional photography — of YOU, not stock images
3. A color palette and typography that feels premium
4. A website that loads fast and works perfectly on mobile

**Common mistake:**
Using a generic template website that looks identical to 500 other agencies. Differentiation is everything.

If you're serious about this, a custom brand identity investment pays for itself within 2-3 transactions."""

    elif "website" in title or "design" in title:
        return """After working with several real estate agencies on their websites, here are the highest-impact changes:

**Must-haves in 2025:**
- Mobile-first design (70%+ of searches are on phone)
- Under 3 second load time (Google penalizes slow sites)
- AI chatbot for after-hours lead capture
- Clear value proposition on the homepage — not just "Buy & Sell Homes"
- Social proof: reviews, sold properties, years of experience

**What actually converts:**
- A free tool (home valuation, neighborhood report)
- One strong CTA repeated throughout the page
- Real photos of your team (not stock photos)

**Platforms that work well:**
WordPress + Elementor, Webflow, or a custom build if you have the budget.

The agencies that invest in a proper website see 3-5x more inbound inquiries compared to template sites."""

    else:
        return """Great question! Digital marketing for real estate has changed significantly. Here's what's working right now:

**What's actually driving leads in 2025:**
1. **Google Search + SEO** — "homes for sale in [city]" searches convert very high
2. **Website conversion optimization** — most agencies have traffic but poor conversion
3. **AI chatbot** — captures leads 24/7 when you're not available
4. **Email nurture sequences** — most buyers take 3-6 months to decide

**The biggest mistake:**
Spending money on Meta/Google ads before fixing your website. If your site doesn't convert, ads just waste money.

**Quick wins:**
- Add a home valuation widget to your homepage
- Speed up your site (use GTmetrix to check)
- Make sure your Google My Business profile is 100% complete

Start with the website foundation — everything else builds on top of it."""


# ─── QUORA AGENT ──────────────────────────────────────────────────────────────

def find_quora_questions():
    print("\nSearching for Quora questions...\n")
    results = []
    seen_urls = set()

    with DDGS() as ddgs:
        for query in QUORA_SEARCH_QUERIES:
            print(f"  Searching: {query[:60]}...")
            try:
                hits = ddgs.text(query, region="us-en", max_results=8)
                for r in hits:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    if "quora.com" in url and url not in seen_urls:
                        seen_urls.add(url)
                        results.append({
                            "question":         title,
                            "url":              url,
                            "found_via":        query[:50],
                            "suggested_answer": generate_answer(title),
                            "status":           "Pending",
                            "posted":           "No",
                            "posted_date":      "",
                            "notes":            "",
                            "found_at":         datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                time.sleep(random.uniform(1.5, 3))
            except Exception as e:
                print(f"  Error: {e}")

    return results


def save_results(results):
    df = pd.DataFrame(results)
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Quora Opportunities")
        ws = writer.sheets["Quora Opportunities"]
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
        ws.freeze_panes = "A2"
    print(f"\nSaved {len(df)} Quora questions to {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("  TAFSOL QUORA AGENT")
    print("=" * 60)

    results = find_quora_questions()

    if not results:
        print("No Quora questions found. Try again later.")
        return

    save_results(results)

    print("\nTop opportunities:")
    print("-" * 60)
    for r in results[:5]:
        print(f"Q: {r['question'][:70]}")
        print(f"   {r['url']}")
        print()

    print("Open quora_opportunities.xlsx, review answers, then post manually.")
    print("Quora bans bots — manual posting is the safe way.")


if __name__ == "__main__":
    main()
