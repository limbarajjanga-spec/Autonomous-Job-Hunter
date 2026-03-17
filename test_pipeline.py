# test_pipeline.py
from scrapers.runner import run_all_scrapers
from core.pipeline   import process_jobs

# scrape + rank
jobs = run_all_scrapers()
print(f"\nScraped {len(jobs)} relevant jobs\n")

# only process top 2 to save API tokens during testing
top2 = jobs[:2]

results = process_jobs(top2)

for r in results:
    job = r["job"]
    jd  = r["jd_analysis"]
    print(f"\n{'='*60}")
    print(f"  {job['title']} @ {job['company']}")
    print(f"  Match: {job['match_score']*100:.0f}%")
    print(f"  Stack: {', '.join(jd.get('tech_stack', []))}")
    print(f"  Seniority: {jd.get('seniority', 'unknown')}")
    print(f"\n  COVER LETTER PREVIEW:")
    print(f"  {r['cover_letter'][:300]}...")
    print(f"\n  INTERVIEW Q1:")
    if r['interview_qa']:
        print(f"  Q: {r['interview_qa'][0]['question']}")
        print(f"  A: {r['interview_qa'][0]['answer'][:200]}...")