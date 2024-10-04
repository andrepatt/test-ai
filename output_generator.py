import io
from docx import Document
from markdown import markdown
from xhtml2pdf import pisa

def create_docx_from_markdown(markdown_text):
    html = markdown(markdown_text)
    doc = Document()
    doc.add_paragraph(html, style='Normal')
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_pdf_from_markdown(markdown_text):
    html = markdown(markdown_text)
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    buffer.seek(0)
    return buffer
