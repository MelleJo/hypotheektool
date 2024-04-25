import streamlit as st
from langchain import LangChain
from langchain.clients import OpenAIChatClient
from langchain.chains import GenerateDocumentChain
from langchain.memory import InMemoryDocumentStore
import pdfplumber
from docx import Document

# Initialize LangChain with the API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]
client = OpenAIChatClient(api_key=api_key, model="gpt-4-turbo")
lang_chain = LangChain(chat_client=client)

# Paths to your document templates
MOTIVATION_TEXTS_PATH = "path/to/motivation_texts.docx"
STANDARD_REPORT_PATH = "path/to/standard_report.pdf"

st.title('Hypotheekadviesrapport Generator')

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return " ".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return " ".join(paragraph.text for paragraph in doc.paragraphs)

def generate_document(context):
    return lang_chain.complete(prompt=context, max_tokens=512)

def save_document(text, filename="final_report.docx"):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    return filename

if st.button('Generate Report'):
    motivation_texts = extract_text_from_docx(MOTIVATION_TEXTS_PATH)
    standard_report = extract_text_from_pdf(STANDARD_REPORT_PATH)
    customer_info = st.text_area("Enter customer information:", key="customer_info")

    if customer_info:
        final_text = generate_document(f"{customer_info}\n{motivation_texts}\n{standard_report}")
        doc_filename = save_document(final_text)
        
        with open(doc_filename, "rb") as file:
            st.download_button("Download Report", file, file_name=doc_filename, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.text("Please enter the customer details and generate a customized mortgage advice report.")
