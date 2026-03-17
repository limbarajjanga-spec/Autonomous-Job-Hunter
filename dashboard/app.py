# dashboard/app.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import sqlite3
import streamlit as st
from db.database import get_conn, DB_PATH

st.set_page_config(
    page_title = "Job Hunter Dashboard",
    page_icon  = "🎯",
    layout     = "wide"
)

# ── helpers ────────────────────────────────────────────────

def load_jobs(status_filter="all"):
    conn = get_conn()
    if status_filter == "all":
        rows = conn.execute("""
            SELECT id, title, company, url, source, location,
                   salary, match_score, jd_analysis,
                   tailored_resume, cover_letter, interview_qa,
                   status, created_at
            FROM processed_jobs
            ORDER BY match_score DESC
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, title, company, url, source, location,
                   salary, match_score, jd_analysis,
                   tailored_resume, cover_letter, interview_qa,
                   status, created_at
            FROM processed_jobs
            WHERE status = ?
            ORDER BY match_score DESC
        """, (status_filter,)).fetchall()
    conn.close()

    cols = ["id","title","company","url","source","location",
            "salary","match_score","jd_analysis","tailored_resume",
            "cover_letter","interview_qa","status","created_at"]
    return [dict(zip(cols, row)) for row in rows]

def update_status(job_id: str, new_status: str):
    conn = get_conn()
    conn.execute(
        "UPDATE processed_jobs SET status=? WHERE id=?",
        (new_status, job_id)
    )
    conn.commit()
    conn.close()

def count_by_status():
    conn = get_conn()
    rows = conn.execute("""
        SELECT status, COUNT(*) FROM processed_jobs GROUP BY status
    """).fetchall()
    conn.close()
    return dict(rows)

# ── sidebar ────────────────────────────────────────────────

st.sidebar.title("Job Hunter")
st.sidebar.markdown("---")

status_options = ["all", "new", "applied", "interview", "rejected", "saved"]
selected_status = st.sidebar.selectbox("Filter by status", status_options)

st.sidebar.markdown("---")
if st.sidebar.button("Run pipeline now"):
    with st.spinner("Scraping + processing jobs..."):
        from scrapers.runner import run_all_scrapers
        from core.pipeline   import process_jobs
        from delivery.sender import deliver_all
        jobs    = run_all_scrapers()
        results = process_jobs(jobs[:5])
        deliver_all()
    st.sidebar.success(f"Done — {len(results)} new jobs")

st.sidebar.markdown("---")
counts = count_by_status()
st.sidebar.markdown("**Job counts**")
for s in status_options[1:]:
    n = counts.get(s, 0)
    st.sidebar.markdown(f"`{s}` — {n}")

# ── main header ────────────────────────────────────────────

st.title("Your job hunt dashboard")

jobs = load_jobs(selected_status)

if not jobs:
    st.info("No jobs found. Run the pipeline first or change the filter.")
    st.stop()

# ── metrics row ────────────────────────────────────────────

total    = sum(counts.values())
applied  = counts.get("applied", 0)
saved    = counts.get("saved", 0)
new      = counts.get("new", 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total jobs",   total)
c2.metric("New today",    new)
c3.metric("Saved",        saved)
c4.metric("Applied",      applied)

st.markdown("---")

# ── job cards ─────────────────────────────────────────────

for job in jobs:
    score    = int(job["match_score"] * 100)
    jd       = json.loads(job["jd_analysis"] or "{}")
    stack    = jd.get("tech_stack", [])
    missing  = jd.get("missing_from_resume", [])
    seniority= jd.get("seniority", "")
    salary   = jd.get("salary_range", "") or job.get("salary", "")

    # score color
    score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔵"

    with st.expander(
        f"{score_color} {score}%  |  {job['title']}  @  {job['company']}  —  {job['source']}"
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### {job['title']}")
            st.markdown(f"**{job['company']}** · {job['location']} · {job['source']}")
            if salary:
                st.markdown(f"💰 {salary}")

            # tags
            if stack:
                st.markdown(" ".join([f"`{t}`" for t in stack[:8]]))
            if missing:
                st.markdown(
                    "⚠️ Missing: " +
                    " ".join([f"`{m}`" for m in missing[:4]])
                )

        with col2:
            st.markdown(f"**Match score:** {score}%")
            st.markdown(f"**Seniority:** {seniority.title() if seniority else 'N/A'}")
            st.markdown(f"**Status:** `{job['status']}`")
            st.link_button("Apply now", job["url"])

            new_status = st.selectbox(
                "Update status",
                ["new", "saved", "applied", "interview", "rejected"],
                index=["new","saved","applied","interview","rejected"].index(
                    job["status"] if job["status"] in
                    ["new","saved","applied","interview","rejected"] else "new"
                ),
                key=f"status_{job['id']}"
            )
            if st.button("Save status", key=f"btn_{job['id']}"):
                update_status(job["id"], new_status)
                st.success("Updated!")
                st.rerun()

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs([
            "JD Analysis", "Tailored Resume", "Cover Letter", "Interview Q&A"
        ])

        with tab1:
            if jd:
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown("**Required skills**")
                    for s in jd.get("required_skills", []):
                        st.markdown(f"- {s}")
                    st.markdown("**Responsibilities**")
                    for r in jd.get("responsibilities", [])[:4]:
                        st.markdown(f"- {r}")
                with r2:
                    st.markdown("**Why you're a fit**")
                    for m in jd.get("match_reasons", []):
                        st.markdown(f"- {m}")
                    st.markdown("**ATS keywords**")
                    st.markdown(", ".join(jd.get("ats_keywords", [])))
            else:
                st.info("No JD analysis available.")

        with tab2:
            if job["tailored_resume"]:
                st.markdown("**Tailored resume for this role:**")
                st.text_area(
                    "Copy and use this resume",
                    job["tailored_resume"],
                    height=400,
                    key=f"resume_{job['id']}"
                )
            else:
                st.info("No tailored resume available.")

        with tab3:
            if job["cover_letter"]:
                st.markdown("**Cover letter for this role:**")
                st.text_area(
                    "Copy and use this cover letter",
                    job["cover_letter"],
                    height=300,
                    key=f"cover_{job['id']}"
                )
            else:
                st.info("No cover letter available.")

        with tab4:
            qa_list = json.loads(job["interview_qa"] or "[]")
            if qa_list:
                for i, qa in enumerate(qa_list):
                    st.markdown(f"**Q{i+1}: {qa.get('question','')}**")
                    st.markdown(f"*Type: {qa.get('type','')}*")
                    st.markdown(qa.get("answer", ""))
                    tip = qa.get("tip", "")
                    if tip:
                        st.info(f"Tip: {tip}")
                    st.markdown("---")
            else:
                st.info("No interview Q&A available.")