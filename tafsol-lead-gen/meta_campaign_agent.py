import sys
import io
import os
from dotenv import load_dotenv

load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CREDENTIALS ──────────────────────────────────────────────────────────────
ACCESS_TOKEN  = os.getenv("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")
PAGE_ID       = os.getenv("META_PAGE_ID", "")

# ─── CAMPAIGN SETTINGS ────────────────────────────────────────────────────────
CAMPAIGN_CONFIG = {
    "name":      "Tafsol - Real Estate Lead Gen",
    "objective": "LEAD_GENERATION",
    "status":    "PAUSED",
    "daily_budget": 1000,
}

AD_SET_CONFIG = {
    "name":              "Real Estate Owners - USA",
    "billing_event":     "IMPRESSIONS",
    "optimization_goal": "LEAD_GENERATION",
    "daily_budget":      1000,
    "targeting": {
        "geo_locations": {
            "countries": ["US"],
        },
        "age_min": 28,
        "age_max": 60,
        "interests": [
            {"id": "6003263633354", "name": "Real estate"},
            {"id": "6003386637820", "name": "Property management"},
        ],
        "flexible_spec": [
            {
                "behaviors": [
                    {"id": "6002714895372", "name": "Small business owners"},
                ]
            }
        ],
    },
    "start_time": "2026-07-01T00:00:00+0000",
}

# ─── AD CREATIVE VARIANTS ─────────────────────────────────────────────────────
# Framework 4 (Clarity/Mental Shortcut) + Framework 2 (Master Authority) + Framework 3 (Fix Mental Blocks)

AD_CREATIVES = [
    {
        "name":     "Tafsol Ad v1 - After Hours Problem",
        # Framework 3: Fix mental blocks — address the hidden root cause
        "headline": "70% of Real Estate Leads Come After 9pm. Who's Capturing Them?",
        "body":     "Most real estate agency websites are closed when buyers are searching. No chatbot = no lead. We build AI-powered websites that capture, qualify, and book appointments 24/7 — while you sleep. Free website audit for US agencies. No pitch.",
        "cta":      "LEARN_MORE",
        "link":     "https://tafsol.com",
    },
    {
        "name":     "Tafsol Ad v2 - Data Authority",
        # Framework 2: Master authority — specific numbers, reverse-engineered success
        "headline": "Real Estate Agency? You're Losing 60% of Leads (Here's the Fix)",
        "body":     "After auditing 100+ US real estate websites: the average agency converts just 1-2% of visitors. Top performers hit 5-8% — same traffic, 4x more leads. The difference? AI chatbot + free home valuation tool + clear CTA. We implement all 3 in under 2 weeks. Free audit.",
        "cta":      "GET_QUOTE",
        "link":     "https://tafsol.com",
    },
    {
        "name":     "Tafsol Ad v3 - Clarity Metaphor",
        # Framework 4: Clarity through analogy — mental shortcut
        "headline": "Your Real Estate Website Has No Receptionist After 6pm",
        "body":     "Think of your website as your 24/7 office. If no one greets visitors after hours, they leave — and go to a competitor who does. We add an AI receptionist (chatbot) that captures leads, answers questions, and books calls — even at 2am. One agency added 16 extra leads/month. Free 15-min audit.",
        "cta":      "LEARN_MORE",
        "link":     "https://tafsol.com",
    },
    {
        "name":     "Tafsol Ad v4 - Result Proof",
        # Framework 1: Genius understanding — multi-perspective, real-world proof
        "headline": "Real Estate Agency in the US? We Added 16 Leads/Month for One Client",
        "body":     "Without touching their ad budget. We fixed 3 things: AI chatbot for after-hours capture, free home valuation tool, and a clear mobile CTA. In 8 weeks: 3 leads/month → 19 leads/month. Now offering free website audits to 10 US real estate agencies this month.",
        "cta":      "SIGN_UP",
        "link":     "https://tafsol.com",
    },
]

# Active creative (change index 0-3 to test different variants)
ACTIVE_CREATIVE_INDEX = 0
AD_CREATIVE_CONFIG = AD_CREATIVES[ACTIVE_CREATIVE_INDEX]


# ─── META AGENT FUNCTIONS ─────────────────────────────────────────────────────

def check_credentials():
    missing = []
    if not ACCESS_TOKEN:  missing.append("META_ACCESS_TOKEN")
    if not AD_ACCOUNT_ID: missing.append("META_AD_ACCOUNT_ID")
    if not PAGE_ID:       missing.append("META_PAGE_ID")
    return missing


def create_campaign(api):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign

    account  = AdAccount(AD_ACCOUNT_ID)
    campaign = account.create_campaign(fields=[], params={
        Campaign.Field.name:                  CAMPAIGN_CONFIG["name"],
        Campaign.Field.objective:             CAMPAIGN_CONFIG["objective"],
        Campaign.Field.status:                CAMPAIGN_CONFIG["status"],
        Campaign.Field.special_ad_categories: [],
    })
    print(f"  Campaign created: {campaign['id']}")
    return campaign["id"]


def create_ad_set(api, campaign_id):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adset import AdSet

    account = AdAccount(AD_ACCOUNT_ID)
    ad_set  = account.create_ad_set(fields=[], params={
        AdSet.Field.name:              AD_SET_CONFIG["name"],
        AdSet.Field.campaign_id:       campaign_id,
        AdSet.Field.daily_budget:      AD_SET_CONFIG["daily_budget"],
        AdSet.Field.billing_event:     AD_SET_CONFIG["billing_event"],
        AdSet.Field.optimization_goal: AD_SET_CONFIG["optimization_goal"],
        AdSet.Field.targeting:         AD_SET_CONFIG["targeting"],
        AdSet.Field.status:            "PAUSED",
    })
    print(f"  Ad Set created: {ad_set['id']}")
    return ad_set["id"]


def upload_image(api, image_path):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adimage import AdImage

    account = AdAccount(AD_ACCOUNT_ID)
    image   = account.create_ad_image(params={AdImage.Field.filename: image_path})
    image.remote_read(fields=[AdImage.Field.hash])
    print(f"  Image uploaded: {image['hash']}")
    return image["hash"]


def create_ad_creative(api, image_hash):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adcreative import AdCreative

    account  = AdAccount(AD_ACCOUNT_ID)
    creative = account.create_ad_creative(params={
        AdCreative.Field.name: AD_CREATIVE_CONFIG["name"],
        AdCreative.Field.object_story_spec: {
            "page_id": PAGE_ID,
            "link_data": {
                "message":    AD_CREATIVE_CONFIG["body"],
                "link":       AD_CREATIVE_CONFIG["link"],
                "name":       AD_CREATIVE_CONFIG["headline"],
                "call_to_action": {
                    "type":  AD_CREATIVE_CONFIG["cta"],
                    "value": {"link": AD_CREATIVE_CONFIG["link"]},
                },
                "image_hash": image_hash,
            }
        }
    })
    print(f"  Creative created: {creative['id']}")
    return creative["id"]


def create_ad(api, ad_set_id, creative_id):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.ad import Ad

    account = AdAccount(AD_ACCOUNT_ID)
    ad      = account.create_ad(params={
        Ad.Field.name:     AD_CREATIVE_CONFIG["name"],
        Ad.Field.adset_id: ad_set_id,
        Ad.Field.creative: {"creative_id": creative_id},
        Ad.Field.status:   "PAUSED",
    })
    print(f"  Ad created: {ad['id']}")
    return ad["id"]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL META CAMPAIGN AGENT v2")
    print("=" * 60)

    # Show all creative variants
    print("\n  Available Ad Creatives:")
    for i, c in enumerate(AD_CREATIVES):
        marker = " ← ACTIVE" if i == ACTIVE_CREATIVE_INDEX else ""
        print(f"  [{i}] {c['name']}{marker}")
        print(f"      Headline: {c['headline'][:60]}...")
    print(f"\n  Active variant: [{ACTIVE_CREATIVE_INDEX}]")
    print("  (To change: edit ACTIVE_CREATIVE_INDEX at top of file)")

    # Check credentials
    missing = check_credentials()
    if missing:
        print("\nERROR: .env mein yeh fields missing hain:")
        for m in missing:
            print(f"  {m}=")
        print("\nSetup guide:")
        print("  1. developers.facebook.com → My Apps → Create App → Business")
        print("  2. Marketing API enable karo")
        print("  3. Tools → Graph API Explorer → Access Token generate karo")
        print("  4. Ad Account ID: Business Manager → Ad Accounts")
        print("  5. Page ID: Facebook Page → About → Page ID")
        print("\n  In values .env mein daal do, phir dobara chalao.")
        return

    image_path = input("\nBanner image ka path do (Enter = skip): ").strip()

    print("\n" + "=" * 60)
    print("  Campaign Preview:")
    print(f"  Name      : {CAMPAIGN_CONFIG['name']}")
    print(f"  Objective : {CAMPAIGN_CONFIG['objective']}")
    print(f"  Budget    : ${AD_SET_CONFIG['daily_budget']/100}/day")
    print(f"  Target    : USA, Age 28-60, Real Estate + Small Business Owners")
    print(f"  Headline  : {AD_CREATIVE_CONFIG['headline'][:60]}...")
    print(f"  Body      : {AD_CREATIVE_CONFIG['body'][:80]}...")
    print(f"  CTA       : {AD_CREATIVE_CONFIG['cta']}")
    print(f"  Status    : PAUSED")
    print("=" * 60)

    confirm = input("\nLaunch karna hai? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Campaign cancel kiya. Koi charge nahi hua.")
        return

    from facebook_business.api import FacebookAdsApi
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)
    api = FacebookAdsApi.get_default_api()

    print("\nCreating campaign...")
    try:
        campaign_id = create_campaign(api)
        ad_set_id   = create_ad_set(api, campaign_id)

        if image_path and os.path.exists(image_path):
            image_hash  = upload_image(api, image_path)
            creative_id = create_ad_creative(api, image_hash)
            ad_id       = create_ad(api, ad_set_id, creative_id)
        else:
            print("  No image provided — skipping creative creation")
            creative_id = None
            ad_id       = None

        print("\n" + "=" * 60)
        print("  Campaign created successfully!")
        print(f"  Campaign ID : {campaign_id}")
        print(f"  Ad Set ID   : {ad_set_id}")
        if creative_id:
            print(f"  Creative ID : {creative_id}")
            print(f"  Ad ID       : {ad_id}")
        print("\n  Status: PAUSED")
        print("  → business.facebook.com/adsmanager mein jao aur manually start karo")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        print("Access Token ya Ad Account ID check karo.")


if __name__ == "__main__":
    main()
