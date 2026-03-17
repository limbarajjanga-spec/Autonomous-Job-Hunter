# agents/interview_prep.py
import json
import anthropic
from loguru import logger
from core.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are a senior ML/AI engineering interviewer and career coach.
Generate realistic interview questions and model STAR-format answers.
Return ONLY valid JSON. No preamble, no markdown fences."""

def generate(resume_text: str, job: dict, jd_analysis: dict) -> list[dict]:
    stack    = ", ".join(jd_analysis.get("tech_stack", []))
    required = ", ".join(jd_analysis.get("required_skills", []))
    seniority = jd_analysis.get("seniority", "mid")

    prompt = f"""
Generate interview preparation for this ML/AI engineering role.

Job: {job['title']} at {job['company']}
Seniority: {seniority}
Tech stack: {stack}
Required skills: {required}

Candidate background:
{resume_text[:1500]}

Generate 6 interview questions with model answers in this exact JSON format:
[
  {{
    "type": "technical / behavioral / system-design",
    "question": "Question text here",
    "answer": "Detailed STAR-format or technical answer tailored to this candidate",
    "tip": "One-line interview tip for this question"
  }}
]

Include:
- 2 technical questions specific to their stack
- 2 behavioral questions using candidate's actual experience
- 1 system design question relevant to the role
- 1 culture/motivation question specific to this company
"""
    try:
        resp = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 2000,
            messages   = [{"role": "user", "content": prompt}],
            system     = SYSTEM,
        )
        raw  = resp.content[0].text.strip()
        raw  = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        logger.info(f"Interview prep generated for: {job['title']} @ {job['company']}")
        return data
    except Exception as e:
        logger.error(f"Interview prep failed for {job['title']}: {e}")
        return []