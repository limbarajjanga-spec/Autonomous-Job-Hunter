# agents/cover_letter.py
import anthropic
from loguru import logger
from core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are an expert cover letter writer for ML/AI engineering roles.
You write compelling, specific, non-generic cover letters that get interviews.
Never use clichés like 'I am writing to express my interest' or 'I am a hard worker'."""

def write(resume_text: str, job: dict, jd_analysis: dict) -> str:
    culture  = ", ".join(jd_analysis.get("company_culture", []))
    reasons  = ", ".join(jd_analysis.get("match_reasons", []))
    required = ", ".join(jd_analysis.get("required_skills", [])[:5])

    prompt = f"""
Write a tailored cover letter for this ML/AI engineering job application.

=== JOB ===
Title: {job['title']}
Company: {job['company']}
Culture signals: {culture}
Key requirements: {required}
Why I'm a fit: {reasons}

=== MY BACKGROUND (from resume) ===
{resume_text[:2000]}

=== COVER LETTER RULES ===
1. Open with a specific hook — reference the company's product/mission
2. Paragraph 2: match my top 2-3 experiences to their exact requirements
3. Paragraph 3: show I understand their technical challenges
4. Close with a confident call to action
5. Tone: confident, specific, technical but human
6. Length: exactly 3-4 paragraphs, under 350 words
7. No generic phrases, no fluff

Return only the cover letter text. No subject line, no date.
"""
    try:
        resp = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 800,
            messages   = [{"role": "user", "content": prompt}],
            system     = SYSTEM,
        )
        result = resp.content[0].text.strip()
        logger.info(f"Cover letter written for: {job['title']} @ {job['company']}")
        return result
    except Exception as e:
        logger.error(f"Cover letter failed for {job['title']}: {e}")
        return ""