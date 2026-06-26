import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CONFIG ───────────────────────────────────────────────────────────────────

PROFILE_QUERIES = [
    # Highest buying intent — decision makers actively looking
    'site:linkedin.com/in "looking for software development company" USA',
    'site:linkedin.com/in "looking for development agency" USA',
    'site:linkedin.com/in "looking for offshore developers" USA',
    'site:linkedin.com/in "dedicated development team" founder OR CEO USA',
    'site:linkedin.com/in "staff augmentation" "IT" founder OR "operations" USA',
    'site:linkedin.com/in "digital transformation" "partner" CEO OR founder USA',
    # Startup / MVP
    'site:linkedin.com/in "startup" "looking for CTO" OR "technical cofounder" USA',
    'site:linkedin.com/in "MVP development" founder OR CEO California OR Texas OR "New York"',
    'site:linkedin.com/in "SaaS founder" "need developers" OR "build product" USA',
    'site:linkedin.com/in "startup founder" "launch" "app" OR "software" USA 2024 OR 2025',
    # AI & Automation demand
    'site:linkedin.com/in "AI automation" "business" CEO OR founder USA',
    'site:linkedin.com/in "ChatGPT integration" OR "OpenAI integration" CEO OR founder USA',
    'site:linkedin.com/in "workflow automation" "need" OR "looking" founder USA',
    # Real Estate
    'site:linkedin.com/in "real estate" "CEO" OR "Founder" OR "Owner" USA',
    'site:linkedin.com/in "real estate agency" "founder" Florida OR Texas OR California',
    'site:linkedin.com/in "property management" "CEO" OR "owner" United States',
    'site:linkedin.com/in "commercial real estate" "CEO" OR "managing director" USA',
    # Healthcare
    'site:linkedin.com/in "healthcare" "founder" OR "CEO" "software" OR "app" USA',
    'site:linkedin.com/in "dental" OR "medical practice" "owner" "software" OR "app" USA',
    # Legal / Finance
    'site:linkedin.com/in "law firm" "founder" OR "managing partner" "software" USA',
    'site:linkedin.com/in "fintech" "founder" OR "CEO" "development" USA',
    # E-commerce / Retail
    'site:linkedin.com/in "ecommerce" "founder" OR "CEO" "Shopify" OR "WooCommerce" USA',
    'site:linkedin.com/in "online store" "owner" "scaling" OR "automation" United States',
    # Construction / Logistics / Manufacturing
    'site:linkedin.com/in "construction" "CEO" OR "founder" "ERP" OR "software" USA',
    'site:linkedin.com/in "logistics" "founder" OR "CEO" "automation" OR "software" USA',
    # Marketing Agencies (white-label potential)
    'site:linkedin.com/in "marketing agency" "founder" "white label" OR "development" USA',
    'site:linkedin.com/in "digital agency" "CEO" "outsource" OR "development team" USA',
]

POST_QUERIES = [
    # Highest buying intent posts
    'site:linkedin.com "looking for software development company"',
    'site:linkedin.com "looking for development agency"',
    'site:linkedin.com "need a development partner"',
    'site:linkedin.com "looking for offshore developers"',
    'site:linkedin.com "dedicated development team"',
    'site:linkedin.com "staff augmentation" "looking" OR "need"',
    'site:linkedin.com "software outsourcing" "partner"',
    'site:linkedin.com "CTO as a Service" OR "fractional CTO"',
    # Startup signals
    'site:linkedin.com "build MVP" "looking" OR "need developer"',
    'site:linkedin.com "startup" "looking for technical cofounder"',
    'site:linkedin.com "launch SaaS" "need developers" OR "looking"',
    # AI & Automation
    'site:linkedin.com "ChatGPT integration" "business" "looking" OR "need"',
    'site:linkedin.com "AI automation" "need developer" OR "looking for"',
    'site:linkedin.com "OpenAI integration" "need" OR "looking" 2025',
    # Hiring signals (companies that might outsource)
    'site:linkedin.com "hiring MERN developer" OR "hiring React developer" USA',
    'site:linkedin.com "hiring full stack developer" "remote" OR "contract" USA',
    'site:linkedin.com "hiring Flutter developer" OR "hiring React Native developer"',
    'site:linkedin.com "urgent hiring developer" OR "immediate hiring developer"',
    # Industry + software need
    'site:linkedin.com "healthcare" "need app" OR "need software" OR "build platform"',
    'site:linkedin.com "real estate" "need website" OR "need app" OR "chatbot"',
    'site:linkedin.com "e-commerce" "custom development" OR "need developer"',
    'site:linkedin.com "logistics" "automation" "looking for" developer OR company',
    'site:linkedin.com "CRM development" OR "ERP development" "looking" OR "need"',
]

OUTPUT_PROFILES = "linkedin_profiles.xlsx"
OUTPUT_POSTS    = "linkedin_posts.xlsx"

# ─── CONNECTION MESSAGES ──────────────────────────────────────────────────────
# Framework 2 (Master Authority) + Framework 4 (Clarity) + Framework 1 (Genius Understanding)

CONNECTION_MESSAGES = [
    "Hi {name}, after working with 100+ US agencies on their digital presence, I've found that most lose 60-70% of website visitors due to 3 fixable gaps. I'd love to share what's working for top performers in your market — happy to connect!",

    "Hi {name}, noticed your work at {company} — impressive. One thing I've reverse-engineered from the top 1% of US real estate agencies: they capture leads automatically at 2am, 11pm, weekends. Most competitors don't. I build this exact system. Let's connect!",

    "Hi {name}, quick insight from 100+ agency audits: the gap isn't traffic, it's what happens after the click. 70% of searchers arrive outside business hours. An AI chatbot on your site captures every one of them. I'd love to show you how {company} can do this. Connect?",

    "Hi {name}, here's a formula that works for agencies like {company}: Fast Site + AI Chatbot + One Clear CTA = 2-3x booked appointments. No extra ad spend. I build this for US businesses. Would love to connect and share a quick idea specific to your market.",

    "Hi {name}, most founders I speak with feel overwhelmed by AI tools — completely fair. But the agencies winning right now aren't more tech-savvy, they just have the right partner. That's what Tafsol does. Your work at {company} looks solid — let's connect!",

    "Hi {name}, one agency we worked with went from 3 to 19 qualified leads/month in 8 weeks. The secret? We fixed their website's conversion rate BEFORE touching their ad budget. I think {company} has the same opportunity. Worth a connect?",

    "Hi {name}, does {company}'s website capture leads when your team is offline? For most agencies, the answer is no — and that's where 60% of opportunities are lost. I specialize in AI chatbots and high-converting sites that work 24/7. Let's connect!",

    "Hi {name}, I've analyzed hundreds of US agency websites. The ones that consistently outperform share 3 things: speed under 3s, a free tool that captures emails, and an AI chatbot for instant response. Happy to share a quick audit for {company} if you connect!",
]

# ─── COMMENT TEMPLATES ────────────────────────────────────────────────────────
# Framework 3 (Fix Mental Blocks) + Framework 5 (PhD Breakdown) + Framework 1 (Genius Analogies)

COMMENT_TEMPLATES = [
    """The real reason most websites don't generate leads isn't what most people assume.

It's not traffic. It's not design. It's 3 psychological barriers stopping visitors from submitting their info:

1. **"Who are you?"** — No social proof visible in the first scroll
2. **"Will I be spammed?"** — A form feels like a commitment
3. **"Is this worth my time?"** — No clear value exchange

Fix these three, and conversion rates typically jump 2-4x with zero change in traffic.

An AI chatbot solves #2 and #3 automatically — it feels like conversation, not interrogation.""",

    """Here's the framework I use when auditing websites (tested across 100+ agencies):

**The Lead Conversion Stack:**
Layer 1 — Speed (under 3s on mobile — Google confirmed 53% of visits are abandoned after this)
Layer 2 — Trust (client results, testimonials, team photos — within first scroll)
Layer 3 — Capture (AI chatbot or free tool — not just a contact form)
Layer 4 — Nurture (automated email sequence for every new lead)

Most agencies have Layer 1 and maybe Layer 2. Layers 3 and 4 are where the money actually is.

What layer is your setup currently at?""",

    """Think of your website like a physical office.

If your office had no receptionist after hours, no visible sign outside, and required visitors to fill a 5-field paper form before speaking to anyone — you'd lose most walk-ins.

That's exactly what most websites do online.

The fix:
— AI chatbot = 24/7 receptionist
— Clear CTA above the fold = visible sign
— Free tool (valuation, audit, quiz) = value before commitment

Visitors need a reason to raise their hand. Give it to them immediately.""",

    """Here's the mental shortcut I share with every agency I work with:

**The ATC Framework** — Ask, Trust, Convert

— **Ask first**: Open with a question, not a pitch ("Are you buying or selling?")
— **Trust second**: Show 3 results + 2 client reviews before anything else
— **Convert third**: One CTA that matches where the visitor is in their journey

Most sites do it backwards — they pitch first, ask second. That's why 70% of visitors leave.

Flip the order. Watch the numbers change.""",

    """What the data actually shows about B2B and service business websites in 2025:

- 70% of prospects check your website before responding to ANY outreach (LinkedIn, email, cold call)
- 82% of people prefer chatting before calling
- Sites with live chat see 82% more conversions on average

The pattern: your marketing brings people to the door, but your website is either opening it or closing it — silently.

Most businesses spend 90% of their budget on traffic and 10% on conversion. The highest ROI move is flipping that ratio.""",

    """This is the single most overlooked growth lever for service businesses:

**Conversion Rate Optimization before ad spend.**

Here's the math:
- 1,000 visitors × 2% conversion = 20 leads
- 1,000 visitors × 5% conversion = 50 leads
Same traffic. 2.5x the leads. Zero additional ad spend.

Getting from 2% to 5% is very achievable with: faster load time, a chatbot for after-hours capture, one strong CTA, and social proof above the fold.

Ads amplify what's already working. Fix the foundation first.""",

    """The agencies growing fastest right now aren't spending more on ads.

They're converting more of the traffic they already have.

3 highest-ROI changes (based on 100+ audits):
1. **AI chatbot** — captures leads at 2am, 11pm, Sundays (that's 60%+ of web traffic hours)
2. **Free value tool** — home valuation, audit, calculator — 5-10x better than a contact form
3. **Mobile speed** — 70% of searches are mobile; 4s+ load time = most visitors gone

All three can be implemented for under $500 one-time. One extra client pays for that 20x over.""",

    """The #1 thing that changed lead volume for every agency I've worked with?

Not more ads. Not a rebrand. Not more content.

**A free tool on the homepage that offers value before asking for anything.**

Why it works psychologically:
- It gives first (trust) before asking for contact details
- It captures highly qualified leads (only serious buyers/sellers engage)
- It creates a natural follow-up reason ("Here's the report you requested...")

A home valuation widget, website audit tool, or ROI calculator converts 5-10x better than a generic "Contact Us" form. If you're not offering one, you're leaving leads on the table every day.""",
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
    print("  TAFSOL LINKEDIN AGENT v2")
    print("  Master-level outreach — No login required")
    print("=" * 60)

    profiles = find_profiles()
    save_to_excel(profiles, OUTPUT_PROFILES, "Profiles to Connect")

    posts = find_posts()
    save_to_excel(posts, OUTPUT_POSTS, "Posts to Comment")

    print("\n" + "=" * 60)
    print(f"  Done!")
    print(f"  Profiles : {len(profiles)}  →  {OUTPUT_PROFILES}")
    print(f"  Posts    : {len(posts)}  →  {OUTPUT_POSTS}")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. linkedin_profiles.xlsx → connection message copy karo, send karo")
    print("  2. linkedin_posts.xlsx   → comment copy karo, post karo")
    print("  LinkedIn automation = account ban — manual posting safe hai.")


if __name__ == "__main__":
    main()
