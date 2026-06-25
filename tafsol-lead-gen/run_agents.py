import sys
import io
import subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENTS = {
    "1": ("Lead Gen (Google Search)",  "main.py"),
    "2": ("Apollo CSV Processor",      "process_apollo.py"),
    "3": ("Email Sender",              "send_emails.py"),
    "4": ("Reddit Agent",              "reddit_agent.py"),
    "5": ("Quora Agent",               "quora_agent.py"),
    "6": ("LinkedIn Agent",            "linkedin_agent.py"),
    "7": ("Meta Campaign Agent",       "meta_campaign_agent.py"),
}

def main():
    print("=" * 60)
    print("  TAFSOL AGENT RUNNER")
    print("=" * 60)
    print()
    for key, (name, _) in AGENTS.items():
        print(f"  [{key}] {name}")
    print("  [A] Run ALL agents")
    print("  [Q] Quit")
    print()

    choice = input("Konsa agent chalana hai? : ").strip().upper()

    if choice == "Q":
        print("Bye!")
        return

    if choice == "A":
        for key, (name, script) in AGENTS.items():
            print(f"\n>>> Running: {name}")
            print("-" * 40)
            subprocess.run([sys.executable, "-X", "utf8", script])
        return

    if choice in AGENTS:
        name, script = AGENTS[choice]
        print(f"\n>>> Running: {name}")
        print("-" * 40)
        subprocess.run([sys.executable, "-X", "utf8", script])
    else:
        print("Galat choice. Dobara try karo.")

if __name__ == "__main__":
    main()
