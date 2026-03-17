# agents/jd_analyzer.py
import json
import anthropic
from loguru import logger
from core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are an expert technical recruiter and job description analyst.
Extract structured information from job descriptions with precision.
Return ONLY valid JSON. No preamble, no markdown, no explanation."""

def analyze(job: dict) -> dict:
    prompt = f"""
Analyze this job posting and extract structured data.

Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description:
{job.get('description', '')[:3000]}

Return this exact JSON structure:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "ats_keywords": ["keyword1", "keyword2"],
  "responsibilities": ["resp1", "resp2"],
  "experience_years": "3-5 years",
  "education": "Bachelor's in CS or related",
  "salary_range": "$120k-$160k or empty string",
  "remote_type": "fully remote / hybrid / remote-friendly",
  "company_size": "startup / mid-size / enterprise",
  "company_culture": ["fast-paced", "data-driven"],
  "seniority": "junior / mid / senior / staff",
  "tech_stack": ["Python", "PyTorch"],
  "missing_from_resume": ["skill not in resume"],
  "match_reasons": ["why this is a good fit"]
}}
"""
    try:
        resp = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 1000,
            messages   = [{"role": "user", "content": prompt}],
            system     = SYSTEM,
        )
        raw  = resp.content[0].text.strip()
        # strip markdown fences if present
        raw  = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        logger.info(f"JD analyzed: {job['title']} @ {job['company']}")
        return data
    except Exception as e:
        logger.error(f"JD analyzer failed for {job['title']}: {e}")
        return {}