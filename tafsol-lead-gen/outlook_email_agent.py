import os
import sys
import io
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CREDENTIALS ──────────────────────────────────────────────────────────────
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
TENANT_ID = os.getenv("AZURE_TENANT_ID", "common")
SCOPES    = ["Mail.Read", "Mail.Send", "offline_access"]

TOKEN_FILE = "outlook_token.json"

# ─── AUTOMATED SENDERS TO SKIP ────────────────────────────────────────────────
AUTO_DOMAINS = [
    "noreply", "no-reply", "donotreply", "notifications", "newsletter",
    "apollo.io", "linkedin.com", "facebook", "instagram", "google.com",
    "microsoft.com", "github.com", "canva.com", "heygen.com", "zoho",
    "reddit", "anthropic.com", "trustpilot", "dribbble", "navtalk",
    "lessie.org", "reallygoodemails", "notion.so",
]

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_token():
    import msal

    cache = msal.SerializableTokenCache()
    if Path(TOKEN_FILE).exists():
        cache.deserialize(Path(TOKEN_FILE).read_text())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache,
    )

    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        print("\n" + "=" * 60)
        print("  OUTLOOK LOGIN")
        print("=" * 60)
        print(f"\n  Browser mein jao : {flow['verification_uri']}")
        print(f"  Yeh code enter karo : {flow['user_code']}")
        print(f"\n  Login ka wait kar raha hoon...")
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        Path(TOKEN_FILE).write_text(cache.serialize())
        return result["access_token"]

    print(f"\nERROR: {result.get('error_description', 'Login failed')}")
    return None


# ─── GRAPH API HELPERS ────────────────────────────────────────────────────────

def graph_get(token, url, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, params=params, timeout=15)
    return r.json()


def is_automated(sender_email):
    s = sender_email.lower()
    return any(kw in s for kw in AUTO_DOMAINS)


def already_replied(token, conversation_id, my_email):
    data = graph_get(
        token,
        "https://graph.microsoft.com/v1.0/me/messages",
        params={
            "$filter": f"conversationId eq '{conversation_id}' and from/emailAddress/address eq '{my_email}'",
            "$select": "id",
            "$top": 1,
        },
    )
    return len(data.get("value", [])) > 0


def get_full_body(token, message_id):
    data = graph_get(
        token,
        f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
        params={"$select": "body,subject,from,receivedDateTime,bodyPreview"},
    )
    return data.get("body", {}).get("content", data.get("bodyPreview", ""))


# ─── REPLY GENERATOR ──────────────────────────────────────────────────────────

def generate_reply(email, body_text=""):
    sender      = email["from"]["emailAddress"]
    sender_name = sender.get("name", "")
    first_name  = sender_name.split()[0] if sender_name else "there"
    subject     = email.get("subject", "")
    preview     = (body_text or email.get("bodyPreview", ""))[:300]

    return f"""Subject: Re: {subject}

Hi {first_name},

Thank you for your email. I wanted to follow up and make sure this didn't get missed.

[Yahan aap apna specific reply likhein — email ka context:
"{preview[:150]}..."]

Looking forward to hearing from you.

Best regards,
Imran Qayyum
Tafsol Technologies
miq@tafsol.com
+92-XXX-XXXXXXX"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL OUTLOOK EMAIL AGENT")
    print("  Emails jo reply ki wait kar rahi hain")
    print("=" * 60)

    if not CLIENT_ID:
        print("\nERROR: .env mein AZURE_CLIENT_ID missing hai")
        print("\nAzure setup (2 minute ka kaam):")
        print("  1. portal.azure.com → App registrations → New registration")
        print("  2. Name: Tafsol Outlook Agent")
        print("  3. Account types: Personal + Work/school accounts")
        print("  4. Register → 'Application (client) ID' copy karo")
        print("  5. API permissions → Microsoft Graph → Delegated:")
        print("     Mail.Read  +  Mail.Send  +  offline_access")
        print("  6. .env mein daalo: AZURE_CLIENT_ID=paste-here")
        return

    token = get_token()
    if not token:
        return

    # My email
    me       = graph_get(token, "https://graph.microsoft.com/v1.0/me")
    my_email = me.get("mail") or me.get("userPrincipalName", "")
    print(f"\nConnected: {my_email}")

    # Inbox
    print("\nInbox parh raha hoon...")
    data = graph_get(
        token,
        "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages",
        params={
            "$top": 50,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,receivedDateTime,conversationId,bodyPreview,isRead",
        },
    )
    emails = data.get("value", [])
    print(f"{len(emails)} emails mili")

    # Filter
    needs_reply = []
    print("\nCheck kar raha hoon kaunsi reply chahiye...\n")

    for email in emails:
        sender_info  = email.get("from", {}).get("emailAddress", {})
        sender_email = sender_info.get("address", "")

        if is_automated(sender_email):
            continue
        if my_email.lower() in sender_email.lower():
            continue

        replied = already_replied(token, email["conversationId"], my_email)
        if not replied:
            needs_reply.append(email)

        time.sleep(0.15)

    # Results
    if not needs_reply:
        print("Koi email nahi mili jo reply ki muntazir ho.")
        return

    print("=" * 60)
    print(f"  {len(needs_reply)} email(s) need reply")
    print("=" * 60)

    for i, email in enumerate(needs_reply, 1):
        sender = email["from"]["emailAddress"]
        print(f"\n[{i}] From    : {sender.get('name', '')} <{sender.get('address', '')}>")
        print(f"    Subject : {email['subject']}")
        print(f"    Date    : {email['receivedDateTime'][:10]}")
        print(f"    Preview : {email['bodyPreview'][:120]}...")
        print(f"\n    ── Suggested Reply ─────────────────────────────")
        reply = generate_reply(email)
        for line in reply.split("\n"):
            print(f"    {line}")
        print()

    print("=" * 60)
    print(f"  Done. {len(needs_reply)} replies ready.")
    print("  .env mein AZURE_CLIENT_ID daalo phir run karo.")
    print("=" * 60)


if __name__ == "__main__":
    main()
