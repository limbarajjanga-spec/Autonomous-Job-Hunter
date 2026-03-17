# core/pipeline.py
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from loguru import logger
from core.ranker import RESUME_TEXT
from core.config import load_profile
from agents.jd_analyzer   import analyze
from agents.resume_tailor import tailor
from agents.cover_letter  import write
from agents.interview_prep import generate
from db.database import get_conn

class JobState(TypedDict):
    job:            dict
    jd_analysis:    dict
    tailored_resume: str
    cover_letter:   str
    interview_qa:   list
    match_score:    float
    skip:           bool

# ── nodes ──────────────────────────────────────────────────

def node_analyze(state: JobState) -> JobState:
    state["jd_analysis"] = analyze(state["job"])
    return state

def node_score_gate(state: JobState) -> str:
    """Only process jobs above threshold."""
    profile = load_profile()
    threshold = float(profile.get("min_match_score", 0.20))
    if state["job"].get("match_score", 0) < threshold:
        state["skip"] = True
        return "skip"
    return "process"

def node_tailor(state: JobState) -> JobState:
    state["tailored_resume"] = tailor(RESUME_TEXT, state["job"], state["jd_analysis"])
    return state

def node_cover_letter(state: JobState) -> JobState:
    state["cover_letter"] = write(RESUME_TEXT, state["job"], state["jd_analysis"])
    return state

def node_interview(state: JobState) -> JobState:
    state["interview_qa"] = generate(RESUME_TEXT, state["job"], state["jd_analysis"])
    return state

def node_save(state: JobState) -> JobState:
    job = state["job"]
    conn = get_conn()
    conn.execute("""
        INSERT OR REPLACE INTO processed_jobs
        (id, title, company, url, source, location, salary,
         match_score, jd_analysis, tailored_resume, cover_letter, interview_qa, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        job["id"], job["title"], job["company"], job["url"],
        job.get("source", ""),
        job.get("location", "Remote"),
        job.get("salary", ""),
        job.get("match_score", 0),
        json.dumps(state["jd_analysis"]),
        state["tailored_resume"],
        state["cover_letter"],
        json.dumps(state["interview_qa"]),
        "new"
    ))
    conn.commit()
    conn.close()
    logger.success(f"Saved: {job['title']} @ {job['company']}")
    return state

def node_skip(state: JobState) -> JobState:
    logger.debug(f"Skipped low-score job: {state['job']['title']}")
    return state

# ── build graph ─────────────────────────────────────────────

def build_pipeline():
    g = StateGraph(JobState)

    g.add_node("analyze",      node_analyze)
    g.add_node("tailor",       node_tailor)
    g.add_node("cover_letter", node_cover_letter)
    g.add_node("interview",    node_interview)
    g.add_node("save",         node_save)
    g.add_node("skip",         node_skip)

    g.set_entry_point("analyze")
    g.add_conditional_edges("analyze", node_score_gate, {
        "process": "tailor",
        "skip":    "skip",
    })
    g.add_edge("tailor",       "cover_letter")
    g.add_edge("cover_letter", "interview")
    g.add_edge("interview",    "save")
    g.add_edge("save",         END)
    g.add_edge("skip",         END)

    return g.compile()

def process_jobs(jobs: list[dict]) -> list[dict]:
    pipeline = build_pipeline()
    results  = []

    for job in jobs:
        logger.info(f"Processing: {job['title']} @ {job['company']}")
        final_state = pipeline.invoke({
            "job":             job,
            "jd_analysis":     {},
            "tailored_resume": "",
            "cover_letter":    "",
            "interview_qa":    [],
            "match_score":     job.get("match_score", 0),
            "skip":            False,
        })
        if not final_state.get("skip"):
            results.append(final_state)

    logger.success(f"Pipeline complete — {len(results)} jobs fully processed")
    return results