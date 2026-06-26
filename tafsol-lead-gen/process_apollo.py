import pandas as pd
import sys
import io
import random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

df = pd.read_csv(r'C:\Users\Imran Qayyum\Downloads\apollo-contacts-export.csv')


def clean_phone(row):
    for col in ['Corporate Phone', 'Work Direct Phone', 'Mobile Phone', 'Home Phone']:
        val = row.get(col, '')
        if val and str(val).strip() not in ['', 'nan']:
            return str(val).replace("'", '').strip()
    return ''


# ─── EMAIL VARIANTS ───────────────────────────────────────────────────────────
# Framework 2 (Master Authority) + Framework 4 (Clarity/Metaphor) + Framework 1 (Genius)

def generate_email_A(row):
    """Variant A: Insight-first — lead with a specific observation (highest open rate)"""
    name    = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    website = str(row.get('Website', '')).strip()
    tech    = str(row.get('Technologies', '')).lower()

    has_chatbot = any(x in tech for x in [
        'intercom', 'drift', 'tidio', 'hubspot', 'livechat',
        'tawk', 'crisp', 'zendesk', 'freshchat'
    ])

    chatbot_line = (
        "Your website doesn't appear to have a live chat or AI chatbot — which means you're likely missing 60-70% of after-hours visitors who won't fill a form but would engage in a conversation."
        if not has_chatbot else
        "You're already using live chat — smart move. The next level is a real estate-specific AI chatbot that qualifies leads automatically and books appointments without manual follow-up."
    )

    site_line = f"your website ({website})" if website and website != 'nan' else "your website"

    return f"""Subject: {name}, one gap I noticed on {site_line}

Hi {name},

I spent a few minutes reviewing {site_line} — you're clearly doing solid work in real estate.

One thing stood out: {chatbot_line}

Here's what the data shows: 70% of property searches happen after 9pm. If no one's there to capture them, those leads go to whoever has a chatbot — usually a larger competitor.

We've fixed this exact issue for several US real estate agencies. One client went from 3 to 19 qualified leads/month in 8 weeks without increasing their ad spend.

I'd love to offer {company} a free 15-minute website audit — not a pitch, just honest feedback on what's costing you leads right now.

Would a quick call this week work?

Best,
Imran Qayyum
Tafsol Technologies | AI-Powered Web & Chatbot Solutions
branding.tafsol@gmail.com | www.tafsol.com"""


def generate_email_B(row):
    """Variant B: Story-first — use an analogy/metaphor (Framework 4: Clarity)"""
    name    = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    website = str(row.get('Website', '')).strip()

    site_line = f"({website})" if website and website != 'nan' else ""

    return f"""Subject: {name} — the late-night receptionist problem

Hi {name},

Here's a quick analogy that explains something I see constantly with real estate agencies:

Imagine your office had no receptionist after 6pm. A motivated buyer walks in at 9pm — nobody there. They leave. That deal is gone.

That's exactly what most real estate websites do.

{company}'s website {site_line} is your 24/7 digital office. But if it has no chatbot — no way to capture visitors after hours — 60-70% of your traffic is walking out the door without leaving their name.

At Tafsol, we build AI chatbots specifically for real estate agencies. They ask qualifying questions, capture contact details, and book appointments — while you sleep.

Three agencies we worked with this year collectively added 47 qualified leads/month that they were previously losing to after-hours silence.

Free 15-minute audit for {company} — I'll show you exactly what you're currently missing and what it would take to fix it. No obligation.

Worth a quick call?

Best,
Imran Qayyum
Tafsol Technologies
branding.tafsol@gmail.com | www.tafsol.com"""


def generate_email_C(row):
    """Variant C: Data-first — authority tone, specific numbers (Framework 2: Master Authority)"""
    name    = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    website = str(row.get('Website', '')).strip()
    tech    = str(row.get('Technologies', '')).lower()

    has_crm = any(x in tech for x in [
        'hubspot', 'salesforce', 'zoho', 'pipedrive', 'active campaign', 'infusionsoft'
    ])

    crm_line = (
        "Most agencies we work with also lack a CRM-integrated follow-up sequence — meaning even the leads they capture don't get the 5+ touchpoints needed to convert (Salesforce research shows 80% of sales happen after the 5th follow-up)."
        if not has_crm else
        "You're already using a CRM — great foundation. The missing piece is usually automated lead capture before prospects even reach your CRM."
    )

    site_line = f"your website ({website})" if website and website != 'nan' else "your website"

    return f"""Subject: {name}, 3 numbers about {company}'s website

Hi {name},

Three numbers worth knowing:

• 70% — the percentage of property searches that happen after 9pm (when most agency websites are unmanned)
• 53% — the percentage of mobile visitors who leave if a site loads in 4+ seconds (Google, 2023)
• 5x — how much more a free home valuation tool converts vs. a standard contact form

After auditing 100+ real estate websites, I've found that most agencies are losing leads at all three points — simultaneously.

{crm_line}

For {company}, fixing these three gaps typically means 2-3x more qualified leads from the same traffic — no additional ad spend.

We're Tafsol Technologies. We specialize in AI chatbots and high-converting websites for US real estate agencies.

I'd love to offer you a free audit of {site_line} — specific findings, no pitch. 15 minutes.

Open to a quick call this week?

Best,
Imran Qayyum
Tafsol Technologies | AI-Powered Web Solutions
branding.tafsol@gmail.com | www.tafsol.com"""


def generate_email(row):
    variant = random.choice(['A', 'B', 'C'])
    if variant == 'A':
        return generate_email_A(row), 'A - Insight-first'
    elif variant == 'B':
        return generate_email_B(row), 'B - Story/Metaphor'
    else:
        return generate_email_C(row), 'C - Data-authority'


# ─── LINKEDIN MESSAGE ─────────────────────────────────────────────────────────

LINKEDIN_VARIANTS = [
    "Hi {name}, I noticed {company} and was impressed by your work in real estate. After auditing 100+ US agency websites, I've found most lose 60-70% of after-hours leads — no chatbot means no capture at 2am. I help fix exactly this. Would love to connect and share one specific insight for {company}.",

    "Hi {name}, quick question — does {company}'s website capture leads when your team is offline? That's when 70% of property searches happen. I help real estate agencies fix this with AI chatbots and high-converting sites. Would love to connect and share what's working.",

    "Hi {name}, I reverse-engineered what the top US real estate agencies do differently online: they convert visitors to appointments 24/7, automatically. I build this exact system for agencies like {company}. Let's connect — I'll share the blueprint.",
]

def generate_linkedin(row):
    name    = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    return random.choice(LINKEDIN_VARIANTS).format(
        name=name.split()[0] if name else "there",
        company=company if company else "your company"
    )


# ─── BUILD OUTPUT ─────────────────────────────────────────────────────────────

leads = []
for _, row in df.iterrows():
    email_body, email_variant = generate_email(row)
    leads.append({
        'First Name':        row['First Name'],
        'Last Name':         row['Last Name'],
        'Title':             row['Title'],
        'Company':           row['Company Name'],
        'Email':             row['Email'],
        'Email Status':      row['Email Status'],
        'Phone':             clean_phone(row),
        'LinkedIn Profile':  row.get('Person Linkedin Url', ''),
        'Website':           row.get('Website', ''),
        'City':              row.get('City', ''),
        'State':             row.get('State', ''),
        'Country':           row.get('Country', ''),
        'Industry':          row.get('Industry', ''),
        'Employees':         row.get('# Employees', ''),
        'Email Variant':     email_variant,
        'Personalized Email': email_body,
        'LinkedIn Message':  generate_linkedin(row),
        'Outreach Status':   'Not Contacted',
        'Follow Up Date':    '',
        'Notes':             '',
    })

out = pd.DataFrame(leads)
filename = r'C:\Users\Imran Qayyum\Downloads\tafsol_outreach_leads.xlsx'

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    out.to_excel(writer, index=False, sheet_name='Tafsol Leads')
    ws = writer.sheets['Tafsol Leads']
    for col in ws.columns:
        max_len = max((len(str(c.value or '')) for c in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
    ws.freeze_panes = 'A2'

print(f"Done! {len(leads)} leads saved to:")
print(filename)
print(f"\nEmail variants distributed:")
for v in ['A - Insight-first', 'B - Story/Metaphor', 'C - Data-authority']:
    count = sum(1 for l in leads if l['Email Variant'] == v)
    print(f"  {v}: {count}")
