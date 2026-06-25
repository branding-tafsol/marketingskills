import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

df = pd.read_excel(r'C:\Users\Imran Qayyum\Downloads\tafsol_outreach_leads.xlsx')

for i, row in df.iterrows():
    print("=" * 70)
    print(f"LEAD {i+1}: {row['First Name']} {row['Last Name']}")
    print(f"Company : {row['Company']}")
    print(f"TO      : {row['Email']}  |  Status: {row['Email Status']}")
    print(f"Phone   : {row['Phone']}")
    print("-" * 70)
    print(row['Personalized Email'])
    print()
