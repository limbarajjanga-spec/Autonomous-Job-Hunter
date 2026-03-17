# delivery/digest.py
import json
from db.database import get_conn
from datetime import datetime

def build_html_digest(jobs: list[dict]) -> str:
    date_str = datetime.now().strftime("%A, %d %b %Y")
    count    = len(jobs)

    cards = ""
    for job in jobs:
        score      = int(job.get("match_score", 0) * 100)
        jd         = json.loads(job.get("jd_analysis", "{}"))
        stack      = ", ".join(jd.get("tech_stack", [])[:5])
        missing    = ", ".join(jd.get("missing_from_resume", [])[:3])
        seniority  = jd.get("seniority", "")
        salary     = jd.get("salary_range", "") or job.get("salary", "")
        cover_prev = job.get("cover_letter", "")[:300] + "..."

        score_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#6b7280"

        cards += f"""
        <div style="border:1px solid #e5e7eb;border-radius:12px;padding:20px;margin-bottom:20px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div>
              <h2 style="margin:0;font-size:16px;color:#111827;">{job['title']}</h2>
              <p style="margin:4px 0 0;font-size:13px;color:#6b7280;">
                {job['company']} &nbsp;·&nbsp; {job.get('location','Remote')} &nbsp;·&nbsp; {job.get('source','')}
              </p>
            </div>
            <span style="background:{score_color};color:white;padding:4px 12px;
                         border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap;">
              {score}% match
            </span>
          </div>

          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            {"".join(f'<span style="background:#eff6ff;color:#1d4ed8;padding:2px 10px;border-radius:4px;font-size:12px;">{t}</span>' for t in jd.get("tech_stack",[])[:6])}
            {"".join(f'<span style="background:#fefce8;color:#92400e;padding:2px 10px;border-radius:4px;font-size:12px;">missing: {m}</span>' for m in jd.get("missing_from_resume",[])[:2])}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;">
            <div style="background:#f9fafb;padding:8px 12px;border-radius:8px;font-size:12px;">
              <div style="color:#6b7280;">Seniority</div>
              <div style="font-weight:600;color:#111827;">{seniority.title()}</div>
            </div>
            <div style="background:#f9fafb;padding:8px 12px;border-radius:8px;font-size:12px;">
              <div style="color:#6b7280;">Salary</div>
              <div style="font-weight:600;color:#111827;">{salary or 'Not listed'}</div>
            </div>
            <div style="background:#f9fafb;padding:8px 12px;border-radius:8px;font-size:12px;">
              <div style="color:#6b7280;">Remote type</div>
              <div style="font-weight:600;color:#111827;">{jd.get('remote_type','Remote').title()}</div>
            </div>
          </div>

          <div style="background:#f0fdf4;border-left:3px solid #22c55e;padding:12px;
                      border-radius:0 8px 8px 0;margin-bottom:14px;font-size:13px;color:#166534;">
            <strong>Cover letter preview:</strong><br>{cover_prev}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
            <a href="{job['url']}" style="text-align:center;padding:8px;background:#111827;color:white;
               border-radius:8px;text-decoration:none;font-size:13px;">Apply now</a>
            <span style="text-align:center;padding:8px;border:1px solid #e5e7eb;
               border-radius:8px;font-size:13px;color:#374151;">Resume ready</span>
            <span style="text-align:center;padding:8px;border:1px solid #e5e7eb;
               border-radius:8px;font-size:13px;color:#374151;">Interview Q&A ready</span>
          </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                 max-width:680px;margin:0 auto;padding:24px;color:#111827;">

      <div style="border-bottom:2px solid #111827;padding-bottom:16px;margin-bottom:24px;">
        <h1 style="margin:0;font-size:22px;">Your job hunt digest</h1>
        <p style="margin:4px 0 0;color:#6b7280;font-size:14px;">
          {date_str} &nbsp;·&nbsp; {count} new matches today
        </p>
      </div>

      {cards}

      <p style="text-align:center;font-size:12px;color:#9ca3af;margin-top:32px;">
        Autonomous Job Hunter · running daily at 7 AM
      </p>
    </body>
    </html>
    """
    return html


def get_todays_jobs() -> list[dict]:
    """Fetch all new jobs processed today from the DB."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, title, company, url, source, match_score,
               jd_analysis, cover_letter, interview_qa, status
        FROM processed_jobs
        WHERE status = 'new'
        ORDER BY match_score DESC
    """).fetchall()
    conn.close()

    cols = ["id","title","company","url","source","match_score",
            "jd_analysis","cover_letter","interview_qa","status"]
    return [dict(zip(cols, row)) for row in rows]