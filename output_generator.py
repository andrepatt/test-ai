from io import BytesIO
from docx import Document
import markdown2
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

def create_docx_from_markdown(markdown_text):
    """Crea un file DOCX a partire da un testo markdown."""
    doc = Document()
    html = markdown2.markdown(markdown_text)
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
        if element.name == 'h1':
            doc.add_heading(element.text, level=1)
        elif element.name == 'h2':
            doc.add_heading(element.text, level=2)
        elif element.name == 'h3':
            doc.add_heading(element.text, level=3)
        elif element.name == 'p':
            doc.add_paragraph(element.text)
        elif element.name == 'ul':
            for li in element.find_all('li'):
                doc.add_paragraph(li.text, style='List Bullet')
        elif element.name == 'ol':
            for li in element.find_all('li'):
                doc.add_paragraph(li.text, style='List Number')
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_pdf_from_markdown(markdown_text):
    """Crea un file PDF a partire da un testo markdown."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    # Converti markdown in HTML, quindi in PDF con ReportLab
    html = markdown2.markdown(markdown_text)
    soup = BeautifulSoup(html, 'html.parser')
    styles = getSampleStyleSheet()

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
        if element.name == 'h1':
            story.append(Paragraph(f"<b>{element.text}</b>", styles['Heading1']))
        elif element.name == 'h2':
            story.append(Paragraph(f"<b>{element.text}</b>", styles['Heading2']))
        elif element.name == 'h3':
            story.append(Paragraph(f"<b>{element.text}</b>", styles['Heading3']))
        elif element.name == 'p':
            story.append(Paragraph(element.text, styles['BodyText']))
        elif element.name == 'ul':
            for li in element.find_all('li'):
                story.append(Paragraph(f"- {li.text}", styles['BodyText']))
        elif element.name == 'ol':
            for idx, li in enumerate(element.find_all('li'), start=1):
                story.append(Paragraph(f"{idx}. {li.text}", styles['BodyText']))

    doc.build(story)
    buffer.seek(0)
    return buffer
