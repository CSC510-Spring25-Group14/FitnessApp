# Import necessary packages
import os
import re
import faiss
import numpy as np
from dotenv import load_dotenv
from docx import Document
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Loading the API key for the google gemini model
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

bot_state = 0

DOC_PATH = "./data/data.docx"

# Configuring the LLM model and embedding function
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def cleaned_text(text):
    text = re.sub(r"\s+", " ", text)  
    return text.strip()

# Extracting the relevant text from the document for retrieval
def extract_text_from_document(path):
    doc = Document(path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())
    return text

def chunk_text(text, chunk_size=500, chunk_overlap=50):
    text_blob = "\n".join(text)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text_blob)

def build_faiss_index(chunks):
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, chunks

# Function to retrieve the most relevant text from the document
def retrieve_context(query, k=3):
    query_vector = embedding_model.encode([query])
    _, indices = index.search(np.array(query_vector), k)
    arr = []
    for i in indices[0]:
        arr.append(chunk_store[i])
    return arr

# Function to generate a response using the LLM model
def gemini_response(context, query):
    context = "\n".join(context)
    prompt = f"You are a fitness assistant and your task is to answer user query in polite and concise manner.Generate a human response for all the queries.\n\nUse the following context to answer the query asked by the user.\n\nContext: {context}\n\nQuery: {query}\n\nStick to the context and generate response accordingly.If you don't know the answer, convey that you don't know the answer."
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        return re.sub(r"\*+", "", answer)
    except Exception as e:
        return f"Gemini API error: {e}"

def bot_response(query):
    global bot_state
    query = query.lower().strip()
    if query in ["0", "menu", "start", "reset", "restart"]:
        bot_state = 0
        return (
            f"Hello there! I am BurnBot, and I am here to help you achieve your fitness goals.\n\n"
            + "Select an option below.\n\n"
            + "0. View the menu again.\n"
            + "1. Tell me the food item, and I'll fetch its calorie count for you!\n"
            + "2. Ask a fitness-related question from the document!\n"
        )
    
    context = retrieve_context(query)
    answer = gemini_response(context, query)
    return answer

def initialize_rag():
    paragraphs = extract_text_from_document(DOC_PATH)
    chunks = chunk_text(paragraphs)
    index, chunk_store = build_faiss_index(chunks)
    return chunks, index
        
if __name__=="__main__":
    chunk_store, index = initialize_rag()