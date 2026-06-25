import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

df = pd.read_csv(r'C:\Users\Imran Qayyum\Downloads\apollo-contacts-export.csv')


def clean_phone(row):
    for col in ['Corporate Phone', 'Work Direct Phone', 'Mobile Phone', 'Home Phone']:
        val = row.get(col, '')
        if val and str(val).strip() not in ['', 'nan']:
            return str(val).replace("'", '').strip()
    return ''


def generate_email(row):
    name = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    website = str(row.get('Website', '')).strip()
    tech = str(row.get('Technologies', '')).lower()

    has_chatbot = any(x in tech for x in [
        'intercom', 'drift', 'tidio', 'hubspot', 'livechat',
        'tawk', 'crisp', 'zendesk', 'freshchat'
    ])
    has_crm = any(x in tech for x in [
        'hubspot', 'salesforce', 'zoho', 'pipedrive', 'active campaign', 'infusionsoft'
    ])

    pitch_lines = []
    if not has_chatbot:
        pitch_lines.append("- AI chatbot to capture leads 24/7 (most real estate sites lose 60% of visitors who never fill a form)")
    if not has_crm:
        pitch_lines.append("- CRM + lead capture integration so every visitor becomes a trackable prospect")
    pitch_lines.append("- A sharp, branded digital presence that builds trust before the first call")

    pitch_str = "\n".join(pitch_lines)
    site_line = f"your website ({website})" if website and website != 'nan' else "your website"

    return f"""Subject: {name}, one idea that could bring {company} more leads this month

Hi {name},

I looked at {site_line} — you're clearly doing solid work in real estate.

I'll be direct: most real estate websites we review are losing 50–70% of their visitors because of a few fixable gaps. For {company}, here's what stood out:

{pitch_str}

We're Tafsol Technologies — we build AI-powered websites and chatbots specifically for real estate companies in the US. Our clients typically see a 2–3x increase in qualified leads within 60 days.

I'd love to offer {company} a free 15-minute website audit — no pitch, just honest feedback on what's costing you leads right now.

Are you open to a quick call this week?

Best regards,
Imran Qayyum
Tafsol Technologies | AI-Powered Web Solutions
branding.tafsol@gmail.com | www.tafsol.com"""


def generate_linkedin(row):
    name = str(row['First Name']).strip()
    company = str(row['Company Name']).strip()
    return (
        f"Hi {name}, I noticed {company} and was impressed by your work in real estate. "
        f"I help US real estate agencies capture more leads through AI chatbots and high-converting websites — "
        f"we've helped similar firms 2-3x their inbound leads. "
        f"Would love to connect and share one insight that might be useful for {company}."
    )


leads = []
for _, row in df.iterrows():
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
        'Personalized Email': generate_email(row),
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
