from scrapers.runner import run_all_scrapers

jobs = run_all_scrapers()

print(f"\n--- {len(jobs)} total unique jobs ---\n")
for j in jobs[:5]:
    source  = j['source'].ljust(16)
    title   = j['title'][:42].ljust(42)
    company = j['company']
    print(f"  {source} | {title} | {company}")