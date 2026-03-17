# agents/resume_tailor.py
import anthropic
from loguru import logger
from pathlib import Path
from core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are an expert resume writer specializing in ML/AI engineering roles.
You rewrite resumes to be ATS-optimized and perfectly tailored to specific job descriptions.
Keep all facts truthful — only reframe and reorder, never fabricate experience."""

def tailor(resume_text: str, job: dict, jd_analysis: dict) -> str:
    required  = ", ".join(jd_analysis.get("required_skills", []))
    keywords  = ", ".join(jd_analysis.get("ats_keywords", []))
    stack     = ", ".join(jd_analysis.get("tech_stack", []))
    seniority = jd_analysis.get("seniority", "mid")

    prompt = f"""
Rewrite this resume to be perfectly tailored for the job below.

=== TARGET JOB ===
Title: {job['title']}
Company: {job['company']}
Seniority: {seniority}
Required skills: {required}
ATS keywords to include: {keywords}
Tech stack: {stack}

=== ORIGINAL RESUME ===
{resume_text[:3000]}

=== INSTRUCTIONS ===
1. Reorder bullet points to lead with most relevant experience
2. Naturally weave in these ATS keywords: {keywords}
3. Quantify achievements where possible (add realistic metrics if missing)
4. Tailor the summary/objective to match this specific role
5. Mirror the exact job title language from the posting
6. Keep everything factually accurate — reframe, never fabricate
7. Format as clean plain text with clear sections

Return the complete tailored resume as plain text.
"""
    try:
        resp = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 1500,
            messages   = [{"role": "user", "content": prompt}],
            system     = SYSTEM,
        )
        result = resp.content[0].text.strip()
        logger.info(f"Resume tailored for: {job['title']} @ {job['company']}")
        return result
    except Exception as e:
        logger.error(f"Resume tailor failed for {job['title']}: {e}")
        return ""