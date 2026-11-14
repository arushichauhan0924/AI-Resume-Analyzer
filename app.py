import streamlit as st

from src.extraction.pdf_reader import get_page_count, extract_text
from src.parsing.resume_parser import parse_resume
from src.skills.skill_extractor import extract_skills
from src.matching.skill_matcher import compare_skills
from src.matching.tfidf_matcher import tfidf_score
from src.matching.embedding_matcher import embedding_score
from src.matching.score_utils import score_label
from src.matching.score_combiner import combine_scores
from src.llm.client import analyze_resume
from src.utils.charts import score_gauge, scores_bar

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")


@st.cache_data(show_spinner=False)
def run_pipeline(text: str, jd_text: str) -> dict:
    parsed = parse_resume(text)
    jd_skills = extract_skills(jd_text)["skills"]
    skills = compare_skills(parsed["skills"]["skills"], jd_skills)
    tfidf = tfidf_score(text, jd_text)
    emb = embedding_score(text, jd_text)
    final = combine_scores(tfidf["score"], emb, skills["match_percent"])
    return {"parsed": parsed, "jd_skills": jd_skills, "skills": skills,
            "tfidf": tfidf, "emb": emb, "final": final}


# ---------- Sidebar ----------
with st.sidebar:
    st.title("📄 Resume Analyzer")
    st.caption("Upload resume, paste JD, get your match.")
    uploaded_file = st.file_uploader("1. Resume (PDF)", type=["pdf"])
    jd_text = st.text_area("2. Job description", height=250, placeholder="Paste JD here...")
    st.divider()
    st.caption("Built with Streamlit, spaCy, scikit-learn, Sentence-Transformers, Gemini")

# ---------- Main ----------
st.title("AI Resume Analyzer & Job Matcher")

if uploaded_file is None or not jd_text.strip():
    st.info("👈 Sidebar me resume PDF upload karo aur job description paste karo.")
    st.stop()

text = extract_text(uploaded_file)
if not text:
    st.warning("Is PDF se text nahi nikla (scanned image ho sakti hai).")
    st.stop()

with st.spinner("Analyzing... (pehli baar model load hone me time lagta hai)"):
    r = run_pipeline(text, jd_text)

parsed, skills, final = r["parsed"], r["skills"], r["final"]
tfidf_value, emb_value = r["tfidf"]["score"], r["emb"]

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Skills", "👤 Resume Details", "🤖 AI Analysis"])

# ----- Overview -----
with tab1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Overall", f"{final['final']}%", final["verdict"], delta_color="off")
    m2.metric("Skill Match", f"{skills['match_percent']}%")
    m3.metric("TF-IDF", f"{tfidf_value * 100:.1f}%", score_label(tfidf_value), delta_color="off")
    m4.metric("Transformer", f"{emb_value * 100:.1f}%",
              score_label(emb_value, high=0.55, medium=0.35), delta_color="off")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(score_gauge(final["final"]), use_container_width=True)
    with c2:
        st.plotly_chart(
            scores_bar(
                ["Skill", "TF-IDF", "Transformer", "Final"],
                [skills["match_percent"], round(tfidf_value * 100, 1),
                 round(emb_value * 100, 1), final["final"]],
            ),
            use_container_width=True,
        )
    st.caption(f"Top common words: {', '.join(r['tfidf']['common_words']) or 'None'}")

# ----- Skills -----
with tab2:
    a, b, c = st.columns(3)
    with a:
        st.subheader("✅ Matched")
        st.write(" ".join(f":green-badge[{s}]" for s in skills["matched"]) or "None")
    with b:
        st.subheader("❌ Missing")
        st.write(" ".join(f":red-badge[{s}]" for s in skills["missing"]) or "None")
    with c:
        st.subheader("➕ Extra")
        st.write(" ".join(f":blue-badge[{s}]" for s in skills["extra"]) or "None")

    st.subheader("All skills in your resume")
    for cat, items in parsed["skills"]["by_category"].items():
        st.write(f"**{cat}:** {', '.join(items)}")

# ----- Resume details -----
with tab3:
    contact, edu, exp = parsed["contact"], parsed["education"], parsed["experience"]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contact")
        st.write(f"**Name:** {contact['name']}")
        st.write(f"**Email:** {contact['email']}")
        st.write(f"**Phone:** {contact['phone']}")
        st.write(f"**LinkedIn:** {contact['linkedin']}")
        st.write(f"**GitHub:** {contact['github']}")
    with col2:
        st.subheader("Education")
        st.write(f"**Degrees:** {', '.join(edu['degrees']) or 'Not found'}")
        st.write(f"**Years:** {', '.join(edu['years']) or 'Not found'}")
        st.write(f"**CGPA:** {', '.join(edu['cgpa']) or 'Not found'}")
        st.subheader("Experience")
        if exp["ranges"]:
            st.write(f"**Total:** ~{exp['total_years']} years")
        else:
            st.write("Fresher / no dates found")

    with st.expander("Detected sections"):
        for name, content in parsed["sections"].items():
            st.markdown(f"**{name.upper()}**")
            st.text(content)

# ----- AI analysis -----
with tab4:
    if st.button("🤖 Get AI Analysis", type="primary"):
        try:
            with st.spinner("AI analysis ho raha hai..."):
                st.session_state["ai"] = analyze_resume(
                    text, jd_text, skills["matched"], skills["missing"], final["final"]
                )
        except Exception as e:
            st.error(f"AI analysis fail hua: {e}")

    ai = st.session_state.get("ai")
    if ai:
        st.info(ai["summary"])
        left, right = st.columns(2)
        with left:
            st.subheader("Missing Skills")
            for s in ai["missing_skills"]:
                st.markdown(f"**{s['skill']}**: {s['why_it_matters']}")
                st.caption(f"Kaise seekhein: {s['how_to_learn']}")
            st.subheader("Resume Suggestions")
            for tip in ai["resume_suggestions"]:
                st.write(f"- {tip}")
        with right:
            st.subheader("Recommended Job Roles")
            for j in ai["job_roles"]:
                st.markdown(f"**{j['role']}**: {j['why_fit']}")
            st.subheader("4-Week Roadmap")
            for w in ai["roadmap"]:
                with st.expander(f"{w['week']}: {w['focus']}"):
                    for t in w["tasks"]:
                        st.write(f"- {t}")