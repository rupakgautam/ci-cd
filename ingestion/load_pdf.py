from pypdf import PdfReader


def load_pdf(path):
    reader = PdfReader(path)
    pages = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"text": text, "page": page_num})

    return pages
