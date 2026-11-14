import pdfplumber


def get_page_count(file) -> int:
    """PDF ke kitne pages hain, ye wapas deta hai."""
    with pdfplumber.open(file) as pdf:
        return len(pdf.pages)

def extract_text(file) -> str:
    """PDF ke saare pages ka text ek string me wapas deta hai."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()