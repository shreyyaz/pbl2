import os
print("Importing gradio...")
import gradio as gr
print("Importing dotenv...")
from dotenv import load_dotenv
print("Importing langchain_community.document_loaders PyPDFLoader...")
from langchain_community.document_loaders import PyPDFLoader
print("Importing langchain_text_splitters RecursiveCharacterTextSplitter...")
from langchain_text_splitters import RecursiveCharacterTextSplitter
print("Importing langchain_community.vectorstores FAISS...")
from langchain_community.vectorstores import FAISS
print("Importing langchain_huggingface HuggingFaceEmbeddings...")
from langchain_huggingface import HuggingFaceEmbeddings
print("Importing langchain.chains RetrievalQA...")
from langchain.chains import RetrievalQA
print("Importing langchain_core.prompts PromptTemplate...")
from langchain_core.prompts import PromptTemplate
print("Importing langchain_openai ChatOpenAI...")
from langchain_openai import ChatOpenAI
print("Instantiating ChatOpenAI...")
try:
    llm = ChatOpenAI(
        model="anthropic/claude-opus-4.5",
        openai_api_key="sk-fake",
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,
        max_tokens=1024,
    )
    print("ChatOpenAI instantiated successfully")
except Exception as e:
    print(f"ChatOpenAI instantiation failed: {e}")
except TypeError as e:
    print(f"ChatOpenAI instantiation failed with TypeError: {e}")
print("All imports successful")
