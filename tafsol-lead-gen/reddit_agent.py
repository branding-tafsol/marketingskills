import pandas as pd
import time
import random
import sys
import io
from datetime import datetime
from ddgs import DDGS

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── SEARCH QUERIES ───────────────────────────────────────────────────────────

SEARCH_QUERIES = [
    # Highest buying intent — looking for dev company / agency
    "site:reddit.com \"looking for software development company\"",
    "site:reddit.com \"looking for development agency\"",
    "site:reddit.com \"recommend software development company\"",
    "site:reddit.com \"recommend web developer\" OR \"recommend app developer\"",
    "site:reddit.com \"software outsourcing\" recommend",
    "site:reddit.com \"offshore developers\" recommend OR experience",
    "site:reddit.com \"dedicated development team\" looking OR need",
    "site:reddit.com \"staff augmentation\" software experience",
    "site:reddit.com \"looking for development partner\" OR \"need development partner\"",
    # Startup / MVP signals
    "site:reddit.com startup \"looking for developers\" OR \"need developers\"",
    "site:reddit.com \"build MVP\" \"need developer\" OR \"hire developer\"",
    "site:reddit.com \"startup\" \"technical cofounder\" OR \"CTO\" looking",
    "site:reddit.com \"SaaS\" \"need developer\" OR \"build SaaS\" help",
    "site:reddit.com \"launch app\" \"need developer\" OR \"who can build\"",
    "site:reddit.com \"prototype\" \"need developer\" OR \"who builds\"",
    # AI & Automation demand
    "site:reddit.com \"ChatGPT integration\" business \"need developer\" OR \"who can\"",
    "site:reddit.com \"AI automation\" business \"looking for\" developer OR company",
    "site:reddit.com \"OpenAI integration\" \"need help\" OR \"hire developer\"",
    "site:reddit.com \"workflow automation\" \"need developer\" OR \"software company\"",
    "site:reddit.com \"AI agent\" \"build\" \"looking for\" developer OR company",
    # Problem-based — need software
    "site:reddit.com \"need a developer\" OR \"need software team\"",
    "site:reddit.com \"who can build my app\" OR \"who can develop\"",
    "site:reddit.com \"where to hire developers\" OR \"how to hire developers\"",
    "site:reddit.com \"need CRM\" OR \"need ERP\" \"developer\" OR \"company\"",
    "site:reddit.com \"custom software\" \"looking\" OR \"need\" OR \"recommendation\"",
    # Industry specific
    "site:reddit.com healthcare \"need app\" OR \"need software\" developer",
    "site:reddit.com realestate \"need website\" OR \"need app\" OR \"need developer\"",
    "site:reddit.com ecommerce \"custom development\" OR \"need developer\" help",
    "site:reddit.com legaltech OR lawfirm \"software\" \"looking\" OR \"need\"",
    "site:reddit.com fintech \"need developers\" OR \"looking for dev team\"",
    "site:reddit.com construction \"ERP\" OR \"software\" \"need\" OR \"recommend\"",
    "site:reddit.com logistics \"automation\" \"need developer\" OR \"software company\"",
    # General pain points
    "site:reddit.com smallbusiness \"website not converting\" OR \"no leads from website\"",
    "site:reddit.com Entrepreneur \"website\" \"leads\" \"struggling\" OR \"not working\"",
    "site:reddit.com startups \"need technical partner\" OR \"looking for tech team\"",
]

OUTPUT_FILE = "reddit_leads.xlsx"

# ─── COMMENT TEMPLATES ────────────────────────────────────────────────────────
# Framework 3 (Fix Mental Blocks — cognitive scientist approach)
# Framework 5 (PhD-Level Breakdown — first principles, theories)
# Framework 1 (Genius Understanding — advanced analogies)

COMMENT_TEMPLATES = [
    # Framework 3: Root cause analysis like a cognitive scientist
    """The root cause here is almost never what people think it is.

Most businesses assume low leads = not enough traffic. So they spend more on ads.

But here's what the data actually shows: the average small business website converts at 1-2%. The top performers convert at 5-8%. Same traffic. 3-4x more leads.

The behavioural pattern behind low conversion:
1. Visitors arrive and don't immediately understand what you do for *them* (not what you do in general)
2. They feel no urgency or reason to act right now
3. The friction to contact is too high (forms feel like commitment)

The habit loop to fix it: Give value FIRST (free tool, audit, guide), then ask for contact. This one change typically 2-3x conversion rates.

What does your homepage above-the-fold currently say?""",

    # Framework 5: PhD-level breakdown from first principles
    """Let me break this down from first principles, because most advice online is surface-level.

**Why websites don't convert — the actual theory:**

In behavioural economics, there's a concept called "friction cost" — the psychological energy required to take an action. Every extra field in your form, every unclear CTA, every slow loading second adds friction.

There's also "loss aversion" (Kahneman, 1979) — people fear giving their email more than they value what they might get. Which means your offer must be specific and compelling enough to overcome that loss aversion.

**What works (reverse-engineered from high-converting sites):**
- One primary CTA that promises a specific outcome ("Get your free home valuation in 60 seconds")
- Chatbot instead of form (feels like conversation, not commitment)
- Social proof within first scroll (real results, not generic testimonials)
- Speed under 3s (53% of mobile users leave after 3 seconds — Google 2023)

The agencies applying all 4 consistently outperform by 3-5x in lead volume.""",

    # Framework 1: Genius-level analogy
    """Here's the best analogy I've found for this problem:

Imagine you open a store on a busy street. You spend $2,000/month on a giant billboard to drive people in. But inside, the store has dim lighting, no one greets customers, the products are hard to find, and the checkout requires a 10-step process.

Most businesses spend 90% of their budget on the billboard (ads, SEO, social) and 10% on the store experience (website conversion).

The businesses winning in 2025 have figured out that fixing the store experience is 5x cheaper and faster than buying more billboard space.

Your website IS the store. And most stores are leaking leads through the back door every hour.""",

    # Framework 4: Mental shortcut / framework
    """Here's the exact framework I use when auditing any service business website:

**The VCAT Audit:**
V — Value prop (Does the headline say what you do + who you help + what result they get — in one line?)
C — Credibility (Are there 3+ results/testimonials visible without scrolling?)
A — Action (Is there ONE clear next step? Not 5 options — just one.)
T — Time (Does the page load in under 3 seconds on mobile?)

Score yourself 0-4. Most businesses score 1-2.

Every point you add to this score roughly doubles your conversion rate.

What's your current score?""",

    """The most expensive mistake I see businesses make online:

Sending paid traffic to a website that isn't optimized to convert — then concluding "digital marketing doesn't work for us."

Here's what's actually happening: the marketing is working (people are clicking), but the website is failing (people aren't converting).

Before you spend another dollar on ads, run this quick check:
1. Load your website on mobile. Does it load in under 3 seconds?
2. Read your headline. Does it say exactly what problem you solve and for who?
3. Is there a way to engage that ISN'T a contact form? (Chat, free tool, quiz)
4. Is there real proof visible without scrolling? (Results, reviews, case studies)

If you answered "no" to any of these, that's where your leads are disappearing.""",

    # Framework 2: Master authority — 20-year expert reverse engineering
    """If I were starting a service business from scratch today knowing what I know after 100+ website audits, here's exactly what I'd do:

**Day 1-7**: Build the simplest possible website with: one headline that speaks to a specific pain, one CTA, 3 client results, and a chatbot.

**Week 2**: Add a free tool or lead magnet (valuation, audit, report) — this alone typically generates 3-5 leads/week with zero ad spend.

**Week 3-4**: Optimize for one keyword your ideal client actually searches. Write 2-3 articles answering their biggest questions. Google rewards specificity.

**Month 2+**: Only THEN consider paid ads — because now you have a website that actually converts and you know your cost per lead.

The businesses that skip steps 1-3 and jump straight to ads waste money, get burned, and conclude "digital marketing doesn't work." It works — but only when the foundation is right.""",

    """What's working for service businesses getting consistent leads online in 2025:

Not complicated. Not expensive. But few businesses actually do all of these:

1. **Niche down your messaging** — "We help [specific type of business] get [specific result] in [specific timeframe]" outperforms generic messaging by 4-6x

2. **Add a free resource** — not a PDF no one reads, but something interactive: a calculator, quiz, or instant-result tool. These convert 5-10x better than contact forms.

3. **24/7 availability** — 60% of web traffic happens outside business hours. If no one's there when a prospect lands, that lead is gone. AI chatbot solves this completely.

4. **Follow-up sequence** — 80% of sales happen after the 5th touchpoint. Most businesses give up after 1-2. An automated email sequence handles this for you.

Start with #1. Everything else builds on it.""",

    """Real talk from working with agencies, consultants, and service businesses across the US:

The difference between businesses with full pipelines and those struggling isn't budget. It isn't industry. It isn't even their offer (usually).

It's **systems**.

The businesses with full pipelines have:
- A website that captures leads 24/7 (not just during business hours)
- An automated follow-up sequence (not manual chasing)
- Clear positioning that attracts the right people (not everyone)
- Consistent content that builds trust before the first call

The businesses struggling are doing everything manually, one client at a time, with no system to capture or nurture new leads.

The gap closes when you build the system first. Happy to share specifically what that looks like for your type of business if useful.""",
]


# ─── REDDIT AGENT ─────────────────────────────────────────────────────────────

def find_opportunities():
    opportunities = []
    seen = set()
    print(f"\nSearching Reddit via DuckDuckGo...\n")

    with DDGS() as ddgs:
        for query in SEARCH_QUERIES:
            print(f"  Searching: {query[:65]}...")
            try:
                results = ddgs.text(query, region="us-en", max_results=10)
                for r in results:
                    url   = r.get("href", "")
                    title = r.get("title", "")
                    body  = r.get("body", "")
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
    print("  TAFSOL REDDIT AGENT v2")
    print("  PhD-level comments — No login required")
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
