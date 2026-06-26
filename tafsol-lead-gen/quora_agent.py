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
    # Highest buying intent — looking for dev company / agency
    "site:quora.com best software development company USA",
    "site:quora.com how to find software development company",
    "site:quora.com how to hire dedicated developers",
    "site:quora.com best offshore software development company",
    "site:quora.com how to outsource software development",
    "site:quora.com staff augmentation software development",
    "site:quora.com how to find development partner startup",
    "site:quora.com how to find technical partner startup",
    # Startup / MVP
    "site:quora.com how to build MVP startup",
    "site:quora.com how to find CTO startup",
    "site:quora.com startup looking for developers where",
    "site:quora.com how to build SaaS application",
    "site:quora.com how to hire software team startup",
    # AI & Automation
    "site:quora.com ChatGPT integration business website",
    "site:quora.com AI automation for small business",
    "site:quora.com how to build AI chatbot for business",
    "site:quora.com OpenAI integration website how",
    "site:quora.com workflow automation software development",
    # Web & App Development
    "site:quora.com how to build custom CRM software",
    "site:quora.com how to build mobile app startup",
    "site:quora.com web application development company USA",
    "site:quora.com how to build marketplace website",
    "site:quora.com custom software development benefits",
    # Real estate
    "site:quora.com real estate website not getting leads",
    "site:quora.com chatbot for real estate website",
    "site:quora.com real estate digital marketing strategy",
    # Industry specific
    "site:quora.com healthcare software development",
    "site:quora.com legal software development law firm",
    "site:quora.com e-commerce custom development",
    "site:quora.com how to get clients web development agency",
    # Cold outreach / Agency growth
    "site:quora.com cold email outreach for agency clients",
    "site:quora.com how to get clients software development company",
]

OUTPUT_FILE = "quora_opportunities.xlsx"

# ─── ANSWER TEMPLATES ─────────────────────────────────────────────────────────
# Framework 1 (Genius Understanding) + Framework 5 (PhD Breakdown) + Framework 4 (Clarity)

def generate_answer(question_title):
    title = question_title.lower()

    if "chatbot" in title:
        return """Great question. Here's a PhD-level breakdown of why AI chatbots on service business websites are one of the highest-ROI investments in 2025:

**The core problem they solve:**
70% of website visitors arrive outside business hours. Traditional contact forms require commitment (name, email, phone, message) — which creates massive friction. Studies in behavioral economics show that friction cost is the #1 reason visitors don't convert, not lack of interest.

**Why chatbots solve this:**
1. **Conversation vs. commitment** — A chatbot feels like a chat, not a form. Psychologically, asking "Are you buying or selling?" gets a response; asking "Fill in your details" creates resistance.
2. **Instant response** — 78% of buyers choose the vendor that responds first (InsideSales). A chatbot responds in milliseconds, 24/7.
3. **Qualification at scale** — A well-built chatbot qualifies leads (budget, timeline, location) before your team ever gets involved, saving hours of back-and-forth.

**Best options in 2025:**
- Tidio (free tier, great for small agencies)
- Drift (enterprise-grade)
- Custom AI chatbot (best for branding and integration — what we build at Tafsol)

**What the best real estate chatbots do:**
They ask 3 qualifying questions → book a call directly into your calendar → send you a lead summary. No manual work. No missed after-hours leads.

The agencies I've seen implement this correctly typically see 40-60% more qualified leads within 60 days — from the same traffic."""

    elif "leads" in title or "clients" in title or "getting" in title:
        return """This is one of the most common questions from real estate and service business owners. Let me give you the framework that actually works — not the generic advice you'll find everywhere.

**First, understand the root cause:**
Most businesses assume "low leads = not enough traffic." So they spend more on ads. But the data tells a different story.

The average service business website converts at 1-2%. High performers convert at 5-8%. That's the SAME traffic producing 3-4x more leads. The problem is almost always conversion, not volume.

**The Lead Generation Stack (in order of priority):**

**Layer 1 — Foundation (fix first, always):**
- Website loads in under 3 seconds on mobile (53% of visitors leave after 3s — Google 2023)
- Homepage headline describes exactly what you do + for who + what result
- One primary CTA, not five options

**Layer 2 — Capture (what most businesses skip):**
- AI chatbot for after-hours engagement (60%+ of web traffic happens outside 9-5)
- Free value tool: home valuation, audit, ROI calculator — converts 5-10x better than contact forms
- Google My Business fully optimized — #1 free source of local leads

**Layer 3 — Nurture (where most leads are lost):**
- 80% of sales happen after the 5th follow-up (Salesforce research)
- Automated email sequence for every new lead — minimum 5 touchpoints over 2 weeks
- Personalized follow-up on day 1, day 3, day 7

**Layer 4 — Scale (only after 1-3 are working):**
- Google Ads targeting high-intent keywords ("real estate agent near me")
- Facebook Lead Gen ads (fast lead volume, lower quality)
- LinkedIn outreach for B2B/commercial real estate

The businesses I work with who implement Layers 1-3 first, then add Layer 4, consistently outperform those who jump straight to ads."""

    elif "branding" in title:
        return """Real estate branding is one of the most misunderstood topics in the industry. Let me break it down from first principles.

**Why branding matters more than most agents think:**

In psychology, there's a concept called the "halo effect" — we unconsciously assume that if something looks professional and polished, the person behind it is also professional and competent. Your brand is your halo.

Before a prospect ever speaks to you, they've already formed a judgment based on:
1. Your website (speed, design, content)
2. Your photos (professional vs. casual)
3. Your consistency across platforms
4. Your niche clarity (who specifically do you serve?)

**What strong real estate branding actually looks like:**

1. **Niche clarity** — "Luxury homes in South Miami for relocating executives" is infinitely more powerful than "I sell all types of properties everywhere." Niches command premium pricing and referrals.

2. **Visual consistency** — Same colors, fonts, and tone across website, social media, email signatures, and print. Inconsistency signals "this person is winging it."

3. **Professional photography** — Of YOU, not stock images. Real estate is a relationship business. People hire people they can see and trust.

4. **A signature process or methodology** — "Our 90-Day Home Sale System" is more compelling than "We list and sell homes." It implies expertise and reduces perceived risk.

**The ROI of strong branding:**
Clients close faster. They negotiate less on commission. They refer more. A single strong branding investment typically pays for itself within 1-2 transactions and compounds over time.

The mistake most agents make: spending $50K on ads and $500 on their brand. The math should be closer to reversed."""

    elif "website" in title or "design" in title or "conversion" in title:
        return """After auditing 100+ service business websites, here's what actually moves the needle — not the generic "make it look nice" advice.

**The 4 Elements of a High-Converting Website (proven framework):**

**1. Speed (Non-negotiable)**
- Under 3 seconds on mobile — period. Google confirmed 53% of mobile visits are abandoned after 3s.
- Use GTmetrix or Google PageSpeed Insights to check yours right now.
- Common culprits: unoptimized images, cheap hosting, too many plugins.

**2. Value Proposition (First 5 seconds)**
Your headline must answer: *What do you do + for who + what specific result?*
❌ "Welcome to [Company Name] Real Estate" — meaningless
✓ "We help first-time buyers in Austin find their perfect home in under 60 days" — specific, compelling, differentiating

**3. Lead Capture (Beyond the Contact Form)**
A contact form is the worst-converting lead capture tool on the internet. Replace or supplement it with:
- AI chatbot (conversational, low-friction, 24/7)
- Free home valuation tool (specific value, captures motivated sellers)
- Neighborhood report download (captures buyers early in research phase)

**4. Social Proof (Above the fold)**
Real estate is built on trust. Proof must be visible before the first scroll:
- 3 specific client results with names/locations (not just "Great agent!")
- Sold properties with prices and timelines
- Awards, certifications, years of experience

**What platforms work best:**
- WordPress + Elementor (most flexible, best SEO)
- Webflow (cleanest design, slightly harder to manage)
- Custom build (for agencies wanting full control and integration)

Implement all 4, and you'll consistently outperform competitors running expensive ads to mediocre websites."""

    elif "b2b" in title or "agency" in title or "web development" in title:
        return """Getting clients for a web development or digital agency is one of the most asked — and most poorly answered — questions online. Here's the framework that actually works, from first principles.

**The Fundamental Problem:**
Most agencies try to market to "everyone who needs a website." This is the fastest path to competing on price and losing.

The agencies with full pipelines and premium clients have done one thing differently: **they picked a niche and became the obvious expert in it.**

**The Expert Positioning Framework:**

Step 1 — Pick ONE industry (real estate, healthcare, restaurants, SaaS, e-commerce)
Step 2 — Pick ONE specific problem you solve (lead generation, conversion rate, booking systems)
Step 3 — Build ONE case study showing a specific result ("We helped [Client] go from 2 to 19 leads/month")
Step 4 — Create content around that problem (LinkedIn posts, Reddit answers, Quora answers — exactly like this)

**The outreach that works in 2025:**
- LinkedIn: connect with 10 niche prospects/day with a personalized message referencing a specific pain
- Cold email: 3-line emails work best — observation + insight + one question
- Quora/Reddit: answer niche questions with genuine expertise (builds trust at scale)
- Apollo.io: find verified emails of your ideal client profile at scale

**The #1 mistake agencies make:**
They build a beautiful portfolio website and wait for clients to come. No one is coming. Outbound, content, and referrals are how agencies fill their pipeline.

Pick your niche this week. Everything changes after that decision."""

    elif "cold email" in title or "outreach" in title:
        return """Cold email and outreach has a reputation for not working — usually because it's being done wrong. Here's the framework that actually gets replies.

**Why most cold emails fail (cognitive science perspective):**
The human brain filters out anything that triggers the "this is about you, not me" response. Most cold emails are: intro about the company, list of services, generic CTA. Every line is about the sender. The recipient's brain dismisses it in 2 seconds.

**The Cold Email Framework that works:**

Line 1 — Specific observation about THEM (not generic):
"I noticed [Company] is running Google Ads for [keyword] — your landing page doesn't have a CTA above the fold."

Line 2 — One specific insight (demonstrate expertise):
"Typically, adding a chatbot above the fold on pages like this increases conversion 2-3x."

Line 3 — Soft CTA (low commitment):
"Would it be useful if I sent you a quick 2-minute audit of the page?"

That's it. 3 lines. No company intro. No list of services. No "I hope this email finds you well."

**Subject lines that get opened:**
- "Quick question about [Company]'s website"
- "[Name], noticed something on your homepage"
- "Idea for [Company]'s lead generation"

**The follow-up sequence:**
Day 1: First email
Day 3: One-line follow-up ("Just bumping this up — did you get a chance to see it?")
Day 7: Value-add ("Here's a quick resource on [relevant topic]")
Day 14: Breakup email ("No worries if timing isn't right — happy to connect when it is.")

Response rates of 15-25% are achievable with this framework when targeting the right list."""

    else:
        return """Great question. Here's a comprehensive breakdown of what's actually driving digital lead generation results for service businesses in 2025.

**The Mental Model that changes everything:**

Most people think of lead generation as: Marketing → Leads → Sales.

The businesses consistently winning think of it as: Trust → Capture → Nurture → Convert.

The difference: trust is built BEFORE the lead is captured. And nurture happens after, automatically.

**What's actually working (evidence-based):**

1. **Niche positioning** — Specific beats general every time. "I help real estate agents in Miami get 10 leads/month from their website" outperforms "I do digital marketing for businesses" by 5-10x in both click-through and conversion.

2. **Website conversion optimization** — Fix the conversion rate first, then drive traffic. Going from 2% to 5% conversion is worth more than doubling your traffic and keeping 2%.

3. **AI chatbot** — 60% of web traffic happens outside business hours. A chatbot captures every single one of those visitors. The agencies using this see 40-60% more leads from the same traffic within 60 days.

4. **Free value tool** — A calculator, quiz, valuation tool, or instant audit converts 5-10x better than a contact form. It gives value before asking for anything — the psychological foundation of trust.

5. **Automated follow-up** — 80% of sales happen after the 5th touchpoint (Salesforce). Most businesses follow up once, maybe twice. An automated email sequence handles 5-7 touchpoints for every single lead, automatically.

**The order of operations:**
Fix website → Add chatbot + free tool → Build follow-up sequence → Then and only then, scale with paid ads.

Businesses that follow this order see a 3-5x improvement in lead volume at the same or lower cost per lead. Happy to go deeper on any of these if useful."""


# ─── QUORA AGENT ──────────────────────────────────────────────────────────────

def find_quora_questions():
    print("\nSearching for Quora questions...\n")
    results = []
    seen_urls = set()

    with DDGS() as ddgs:
        for query in QUORA_SEARCH_QUERIES:
            print(f"  Searching: {query[:65]}...")
            try:
                hits = ddgs.text(query, region="us-en", max_results=8)
                for r in hits:
                    url   = r.get("href", "")
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
    print("  TAFSOL QUORA AGENT v2")
    print("  Expert-level answers — Genius + PhD frameworks")
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
