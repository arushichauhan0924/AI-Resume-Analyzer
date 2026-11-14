import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELS = ["gemini-3.8-flash", "gemini-3.8-flash-lite"]  # pehla fail ho to doosra try hoga


def analyze_resume(resume_text: str, jd_text: str, matched: list, missing: list, score: float) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY .env me nahi mili")

    prompt = f"""You are a career coach. Analyze this resume against the job description.
Match score: {score}%. Matched skills: {matched}. Missing skills: {missing}.

RESUME:
{resume_text[:6000]}

JOB DESCRIPTION:
{jd_text[:4000]}

Return ONLY JSON in this exact shape:
{{
  "summary": "2-3 line overall feedback",
  "missing_skills": [{{"skill": "", "why_it_matters": "", "how_to_learn": ""}}],
  "resume_suggestions": ["specific improvement 1", "..."],
  "job_roles": [{{"role": "", "why_fit": ""}}],
  "roadmap": [{{"week": "Week 1", "focus": "", "tasks": ["", ""]}}]
}}
Give 3-5 suggestions, 3 job roles, and a 4-week roadmap."""

    client = genai.Client(api_key=api_key)
    last_error = None

    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                return json.loads(response.text)
            except Exception as e:
                last_error = e
                msg = str(e)
                if "404" in msg:
                    break  # ye model nahi mila, agle model pe jao
                if "503" in msg or "429" in msg:
                    time.sleep(3 * (attempt + 1))  # 3s, 6s, 9s ruk ke retry
                    continue
                raise  # koi aur error ho to seedha dikhao

    raise last_error