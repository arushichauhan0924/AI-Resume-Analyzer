import re
import spacy

# English model ek baar load hota hai (parser aur ner humein nahi chahiye, isse fast chalta hai)
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

EMAIL_PATTERN = r"[\w\.-]+@[\w\.-]+\.\w+"
URL_PATTERN = r"https?://\S+|www\.\S+|(?:linkedin|github)\.com/\S+"
PHONE_PATTERN = r"\+?\d[\d\s\-()]{8,}\d"


def clean_text(text: str) -> str:
    """Halka cleaning: lowercase, email/phone/links hatao. c++, c#, node.js safe rehte hain."""
    text = text.lower()
    text = re.sub(EMAIL_PATTERN, " ", text)
    text = re.sub(URL_PATTERN, " ", text)
    text = re.sub(PHONE_PATTERN, " ", text)
    text = re.sub(r"[^a-z0-9+#.\-/\s]", " ", text)  # sirf kaam ke characters rakho
    text = re.sub(r"\s+", " ", text)                 # extra spaces ek kar do
    return text.strip()


def lemmatize_text(text: str) -> str:
    """Zyada cleaning: stopwords hatao aur words ko root form me badlo (matching ke liye)."""
    doc = nlp(clean_text(text))
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) > 1
    ]
    return " ".join(tokens)