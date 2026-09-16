import re
import pymupdf


def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)
    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


def extract_section(text, start_heading, end_headings):
    lines = text.split("\n")

    section_lines = []
    inside_section = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.upper() == start_heading.upper():
            inside_section = True
            continue

        if inside_section:
            if stripped_line.upper() in [
                heading.upper() for heading in end_headings
            ]:
                break

            section_lines.append(stripped_line)

    return " ".join(section_lines).strip()