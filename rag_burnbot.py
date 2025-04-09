import os
from dotenv import load_dotenv
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_document(path):
    doc = Document(path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())
            print(paragraph.text.strip())
    return text

DOC_PATH = "./data/data.docx"

data = extract_text_from_document(DOC_PATH)
