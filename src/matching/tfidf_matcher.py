from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing.text_cleaner import lemmatize_text


def tfidf_score(resume_text: str, jd_text: str) -> dict:
    """Resume aur JD ka TF-IDF + cosine similarity score nikalta hai."""
    resume_clean = lemmatize_text(resume_text)
    jd_clean = lemmatize_text(jd_text)

    if not resume_clean or not jd_clean:
        return {"score": 0.0, "common_words": []}

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([resume_clean, jd_clean])

    score = cosine_similarity(vectors[0], vectors[1])[0][0]

    # Dono me common top words (jinka weight dono me zyada ho)
    words = vectorizer.get_feature_names_out()
    resume_vec = vectors[0].toarray()[0]
    jd_vec = vectors[1].toarray()[0]
    common = [
        (words[i], resume_vec[i] * jd_vec[i])
        for i in range(len(words))
        if resume_vec[i] > 0 and jd_vec[i] > 0
    ]
    common.sort(key=lambda x: x[1], reverse=True)

    return {
        "score": round(float(score), 4),
        "common_words": [w for w, _ in common[:10]],
    }