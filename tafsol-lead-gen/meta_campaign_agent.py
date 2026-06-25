import sys
import io
import os
from dotenv import load_dotenv

load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─── CREDENTIALS (from .env) ──────────────────────────────────────────────────
ACCESS_TOKEN  = os.getenv("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "")   # format: act_XXXXXXXXXX
PAGE_ID       = os.getenv("META_PAGE_ID", "")

# ─── CAMPAIGN SETTINGS ────────────────────────────────────────────────────────
CAMPAIGN_CONFIG = {
    "name":      "Tafsol - Real Estate Lead Gen",
    "objective": "LEAD_GENERATION",    # or CONVERSIONS, BRAND_AWARENESS
    "status":    "PAUSED",             # PAUSED = safe, won't spend until you manually start
    "daily_budget": 1000,              # in cents = $10/day
}

AD_SET_CONFIG = {
    "name":              "Real Estate Owners - USA",
    "billing_event":     "IMPRESSIONS",
    "optimization_goal": "LEAD_GENERATION",
    "daily_budget":      1000,         # cents = $10/day
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

AD_CREATIVE_CONFIG = {
    "name":    "Tafsol Real Estate Ad",
    "headline": "Real Estate Agency? Get 2-3x More Leads in 60 Days",
    "body":     "70% of real estate searches happen after 9pm — is your website capturing them? We build AI chatbots & high-converting websites for US real estate agencies. Free website audit — no pitch, just honest feedback.",
    "cta":      "LEARN_MORE",
    "link":     "https://tafsol.com",
}


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

    account = AdAccount(AD_ACCOUNT_ID)
    campaign = account.create_campaign(fields=[], params={
        Campaign.Field.name:                CAMPAIGN_CONFIG["name"],
        Campaign.Field.objective:           CAMPAIGN_CONFIG["objective"],
        Campaign.Field.status:              CAMPAIGN_CONFIG["status"],
        Campaign.Field.special_ad_categories: [],
    })
    print(f"  Campaign created: {campaign['id']}")
    return campaign["id"]


def create_ad_set(api, campaign_id):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adset import AdSet

    account = AdAccount(AD_ACCOUNT_ID)
    ad_set = account.create_ad_set(fields=[], params={
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
    image = account.create_ad_image(params={
        AdImage.Field.filename: image_path,
    })
    image.remote_read(fields=[AdImage.Field.hash])
    print(f"  Image uploaded: {image['hash']}")
    return image["hash"]


def create_ad_creative(api, image_hash):
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adcreative import AdCreative

    account = AdAccount(AD_ACCOUNT_ID)
    creative = account.create_ad_creative(params={
        AdCreative.Field.name:  AD_CREATIVE_CONFIG["name"],
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
    ad = account.create_ad(params={
        Ad.Field.name:        "Tafsol Real Estate Ad",
        Ad.Field.adset_id:    ad_set_id,
        Ad.Field.creative:    {"creative_id": creative_id},
        Ad.Field.status:      "PAUSED",
    })
    print(f"  Ad created: {ad['id']}")
    return ad["id"]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TAFSOL META CAMPAIGN AGENT")
    print("=" * 60)

    # Check credentials
    missing = check_credentials()
    if missing:
        print("\nERROR: .env mein yeh fields missing hain:")
        for m in missing:
            print(f"  {m}=")
        print("\nSetup guide:")
        print("  1. developers.facebook.com pe jao")
        print("  2. My Apps > Create App > Business")
        print("  3. Marketing API enable karo")
        print("  4. Access Token generate karo (Tools > Graph API Explorer)")
        print("  5. Ad Account ID: Business Manager > Ad Accounts")
        print("  6. Page ID: Facebook Page > About > Page ID")
        print("\nIn values .env mein daal do, phir dobara chalao.")
        return

    # Ask for banner image path
    print("\nBanner image ka path do (ya Enter dabao default content use karne ke liye):")
    image_path = input("  Image path: ").strip()

    # Confirm before launching
    print("\n" + "=" * 60)
    print("  Campaign Preview:")
    print(f"  Name      : {CAMPAIGN_CONFIG['name']}")
    print(f"  Objective : {CAMPAIGN_CONFIG['objective']}")
    print(f"  Budget    : ${AD_SET_CONFIG['daily_budget']/100}/day")
    print(f"  Target    : USA, Age 28-60, Real Estate Owners")
    print(f"  Headline  : {AD_CREATIVE_CONFIG['headline']}")
    print(f"  Status    : PAUSED (aap manually start karoge)")
    print("=" * 60)

    confirm = input("\nLaunch karna hai? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Campaign cancel kiya. Koi charge nahi hua.")
        return

    # Initialize Meta API
    from facebook_business.api import FacebookAdsApi
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)

    api = FacebookAdsApi.get_default_api()

    print("\nCreating campaign...")
    try:
        campaign_id  = create_campaign(api)
        ad_set_id    = create_ad_set(api, campaign_id)

        if image_path and os.path.exists(image_path):
            image_hash   = upload_image(api, image_path)
        else:
            print("  No image provided — using default Meta placeholder")
            image_hash = None

        if image_hash:
            creative_id = create_ad_creative(api, image_hash)
            ad_id       = create_ad(api, ad_set_id, creative_id)
        else:
            creative_id = None
            ad_id       = None

        print("\n" + "=" * 60)
        print("  Campaign created successfully!")
        print(f"  Campaign ID : {campaign_id}")
        print(f"  Ad Set ID   : {ad_set_id}")
        if creative_id:
            print(f"  Creative ID : {creative_id}")
            print(f"  Ad ID       : {ad_id}")
        print("\n  Status: PAUSED — Facebook Ads Manager mein jao aur manually start karo")
        print("  business.facebook.com/adsmanager")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        print("Access Token ya Ad Account ID check karo.")


if __name__ == "__main__":
    main()
