# AI Resume Analyzer & Job Matcher

Upload a resume PDF, paste a job description, and get skill match, TF-IDF score,
Transformer score, combined score with charts, and AI analysis (missing skills,
suggestions, job roles, 4-week roadmap).

Tech: Streamlit, pdfplumber, spaCy, scikit-learn, sentence-transformers, Gemini API, Plotly

Run: pip install -r requirements.txt, add GEMINI_API_KEY in .env, then streamlit run app.py