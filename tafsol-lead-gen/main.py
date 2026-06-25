import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
from config import (
    SEARCH_QUERIES, RESULTS_PER_QUERY, REQUEST_TIMEOUT,
    DELAY_BETWEEN_REQUESTS, CHATBOT_SIGNATURES, SLOW_SITE_THRESHOLD,
    EXCEL_OUTPUT_FILE, GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ─── STEP 1: Search ───────────────────────────────────────────────────────────

def search_google(query, num_results=10):
    """Search using DuckDuckGo API library (no blocking)."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(query, region="us-en", max_results=num_results)
            urls = [r["href"] for r in results if r.get("href", "").startswith("http")]
            return urls
    except Exception as e:
        print(f"  [Search Error] {query}: {e}")
        return []


# ─── STEP 2: Website Analysis ─────────────────────────────────────────────────

def analyze_website(url):
    """Visit a website and check for common issues."""
    issues = []
    score = 100
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")

    try:
        start = time.time()
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        load_time = round(time.time() - start, 2)
        html = response.text.lower()
        soup = BeautifulSoup(response.text, "html.parser")

        # SSL check
        has_ssl = url.startswith("https://")
        if not has_ssl:
            issues.append("No SSL certificate")
            score -= 20

        # Speed check
        if load_time > SLOW_SITE_THRESHOLD:
            issues.append(f"Slow website ({load_time}s load time)")
            score -= 15

        # Chatbot check
        has_chatbot = any(sig in html for sig in CHATBOT_SIGNATURES)
        if not has_chatbot:
            issues.append("No chatbot / live chat")
            score -= 15

        # Mobile-friendly check
        viewport = soup.find("meta", attrs={"name": "viewport"})
        is_mobile_friendly = bool(viewport)
        if not is_mobile_friendly:
            issues.append("Not mobile-friendly")
            score -= 20

        # Contact form check
        forms = soup.find_all("form")
        has_contact_form = any(
            "contact" in str(f).lower() or "email" in str(f).lower()
            for f in forms
        )
        if not has_contact_form:
            issues.append("No contact / lead capture form")
            score -= 10

        # Page title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "No title"

        # Phone number extraction
        phone = extract_phone(response.text)

        # Email extraction
        email = extract_email(response.text)

        return {
            "domain": domain,
            "url": url,
            "title": title,
            "phone": phone,
            "email": email,
            "ceo_linkedin": "",       # filled in next step
            "load_time_sec": load_time,
            "has_ssl": "Yes" if has_ssl else "No",
            "has_chatbot": "Yes" if has_chatbot else "No",
            "mobile_friendly": "Yes" if is_mobile_friendly else "No",
            "has_contact_form": "Yes" if has_contact_form else "No",
            "issues_found": " | ".join(issues) if issues else "No major issues",
            "website_score": max(score, 0),
            "pitch": generate_pitch(issues),
            "status": "OK",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except Exception as e:
        return {
            "domain": domain,
            "url": url,
            "title": "",
            "phone": "",
            "email": "",
            "ceo_linkedin": "",
            "load_time_sec": "",
            "has_ssl": "",
            "has_chatbot": "",
            "mobile_friendly": "",
            "has_contact_form": "",
            "issues_found": "Site unreachable",
            "website_score": 0,
            "pitch": "",
            "status": f"Error: {e}",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }


# ─── STEP 3: Phone, Email & LinkedIn Extraction ───────────────────────────────

def extract_phone(html):
    """Extract first US phone number found in page HTML."""
    pattern = r'(\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
    matches = re.findall(pattern, html)
    for match in matches:
        number = "".join(match).strip()
        digits = re.sub(r'\D', '', number)
        if len(digits) >= 10:
            return number
    return ""


def extract_email(html):
    """Extract first business email found in page HTML (skip generic/noreply)."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    skip = {"noreply", "no-reply", "support", "info@example", "email@"}
    matches = re.findall(pattern, html)
    for email in matches:
        if not any(s in email.lower() for s in skip):
            return email
    return ""


def find_ceo_linkedin(company_name):
    """Search DuckDuckGo for CEO/Founder LinkedIn profile of the company."""
    query = f'"{company_name}" CEO OR Founder site:linkedin.com/in'
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(query, region="us-en", max_results=5)
            for r in results:
                href = r.get("href", "")
                if "linkedin.com/in/" in href:
                    return href
    except Exception:
        pass
    return ""


# ─── STEP 4: Auto Pitch Generator ─────────────────────────────────────────────

def generate_pitch(issues):
    """Turn issues into pitch points for Tafsol."""
    pitch_map = {
        "No chatbot":          "Add AI chatbot to capture leads 24/7 — never miss a buyer/seller inquiry",
        "Slow website":        "Speed optimization — faster site = lower bounce rate = more leads",
        "No SSL":              "SSL installation — required for trust & Google ranking",
        "Not mobile-friendly": "Mobile-responsive redesign — 70%+ of US real estate searches are mobile",
        "No contact":          "Lead capture form + CRM integration to convert visitors into clients",
    }
    pitch_points = []
    for issue in issues:
        for keyword, pitch in pitch_map.items():
            if keyword.lower() in issue.lower():
                pitch_points.append(pitch)
                break

    return " | ".join(pitch_points) if pitch_points else "Full website audit & redesign recommended"


# ─── STEP 4: Save to Excel ────────────────────────────────────────────────────

def save_to_excel(leads):
    df = pd.DataFrame(leads)
    filename = EXCEL_OUTPUT_FILE.replace(".xlsx", f"_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tafsol Leads")
        ws = writer.sheets["Tafsol Leads"]
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 60)
    print(f"\n  Excel saved: {filename}  ({len(leads)} leads)")


# ─── STEP 5: Save to Google Sheets (optional) ────────────────────────────────

def save_to_google_sheets(leads):
    if not GOOGLE_SHEET_ID:
        print("\n  Google Sheets skipped (GOOGLE_SHEET_ID not set in .env)")
        return

    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        df = pd.DataFrame(leads)
        values = [df.columns.tolist()] + df.values.tolist()
        body = {"values": values}

        sheet.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()

        print(f"  Google Sheets updated: {GOOGLE_SHEET_ID}")

    except FileNotFoundError:
        print(f"\n  Google Sheets skipped: credentials file '{GOOGLE_CREDENTIALS_FILE}' not found.")
    except Exception as e:
        print(f"\n  Google Sheets error: {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 60)
    print("  TAFSOL LEAD GEN - USA Real Estate Website Audit")
    print("=" * 60)

    all_urls = []

    # Collect URLs from all search queries
    for query in SEARCH_QUERIES:
        print(f"\n[Search] {query}")
        urls = search_google(query, RESULTS_PER_QUERY)
        print(f"  Found {len(urls)} URLs")
        all_urls.extend(urls)
        time.sleep(random.uniform(2, 4))  # Delay to avoid Google ban

    # Remove duplicates
    all_urls = list(dict.fromkeys(all_urls))
    print(f"\nTotal unique sites to analyze: {len(all_urls)}")

    # Analyze each website
    leads = []
    for i, url in enumerate(all_urls, 1):
        print(f"\n[{i}/{len(all_urls)}] Analyzing: {url}")
        result = analyze_website(url)

        # Find CEO LinkedIn
        print(f"  Searching CEO LinkedIn for: {result['domain']}")
        linkedin = find_ceo_linkedin(result["domain"].replace(".com", "").replace(".co", ""))
        result["ceo_linkedin"] = linkedin
        if linkedin:
            print(f"  LinkedIn found: {linkedin}")
        else:
            print(f"  LinkedIn: not found")

        leads.append(result)
        print(f"  Score: {result['website_score']}/100 | Phone: {result['phone'] or 'N/A'} | Email: {result['email'] or 'N/A'}")
        time.sleep(DELAY_BETWEEN_REQUESTS)

    if not leads:
        print("\nNo leads found. Try changing search queries in config.py")
        return

    # Sort by score (lowest score = most issues = best pitch opportunity)
    leads.sort(key=lambda x: x.get("website_score", 100))

    # Export
    print("\n" + "=" * 60)
    print("  Saving results...")
    save_to_excel(leads)
    save_to_google_sheets(leads)

    print("\nDone! Check tafsol_leads.xlsx")
    print("=" * 60)


if __name__ == "__main__":
    main()
