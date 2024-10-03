import PyPDF2
from docx import Document
import os

def read_pdf(file):
    """Funzione per leggere il contenuto di un file PDF."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    """Funzione per leggere il contenuto di un file DOCX."""
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def handle_uploaded_file(uploaded_file):
    """Gestisce il caricamento di file e ritorna il contenuto in formato testo."""
    if uploaded_file.type == "application/pdf":
        return read_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        # Salva il file caricato temporaneamente
        with open("temp_uploaded_file.docx", "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
        # Leggi il contenuto del file DOCX
        aru_content = read_docx("temp_uploaded_file.docx")
        # Rimuovi il file temporaneo
        os.remove("temp_uploaded_file.docx")
        return aru_content
    else:  # Tratta il file come un semplice testo
        return uploaded_file.read().decode('utf-8', errors='ignore')
