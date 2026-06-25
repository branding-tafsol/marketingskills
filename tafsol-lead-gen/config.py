from dotenv import load_dotenv
import os

load_dotenv()

# --- Search Settings ---
SEARCH_QUERIES = [
    "real estate agency website contact us New York",
    "property management company website contact Chicago Illinois",
    "realty group website Miami Florida contact us",
    "residential real estate broker website Los Angeles California",
    "home buyers sellers realtor website Dallas Texas contact",
    "luxury real estate agency website Seattle Washington contact",
    "commercial real estate company website Denver Colorado",
    "boutique real estate agency website Phoenix Arizona contact",
    "real estate investment company website Nashville Tennessee",
    "real estate brokerage website Charlotte North Carolina contact",
]
RESULTS_PER_QUERY = 10

# --- Website Analysis ---
REQUEST_TIMEOUT = 10       # seconds to wait for a site to respond
DELAY_BETWEEN_REQUESTS = 2 # seconds to wait between requests (avoid bans)

# Known chatbot scripts — if any of these appear in the page HTML, site has a chatbot
CHATBOT_SIGNATURES = [
    "intercom", "drift.com", "tidio", "hubspot",
    "livechat", "crisp.chat", "tawk.to", "zendesk",
    "freshchat", "olark", "smartsupp", "jivochat",
    "chatbot", "live-chat", "livechat",
]

# Slow if response takes longer than this many seconds
SLOW_SITE_THRESHOLD = 3.0

# --- Export Settings ---
EXCEL_OUTPUT_FILE = "tafsol_leads.xlsx"

# Google Sheets (optional — leave blank to skip)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
