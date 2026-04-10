"""
AI Research Engine - Commercial Courts
100% local via Ollama. No API keys.
  Embeddings : mxbai-embed-large  (retrieval-specialised)
  LLM        : phi3:mini
"""

import os, shutil
from pathlib import Path

# Fix for macOS OpenMP library conflict (OMP: Error #15)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import gradio as gr

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR         = Path("data")
VECTOR_STORE_DIR = Path("vector_store")
CHUNK_SIZE       = 600      # Smaller = more precise retrieval hits
CHUNK_OVERLAP    = 150
OLLAMA_BASE_URL  = os.getenv("OLLAMA_BASE_URL",    "http://localhost:11434")
MODEL_NAME       = os.getenv("OLLAMA_MODEL",       "phi3-legal")
EMBED_MODEL_NAME = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
# ─────────────────────────────────────────────────────────────────────────────


def load_pdfs(directory: Path) -> list:
    docs, files = [], list(directory.glob("*.pdf"))
    if not files:
        print(f"No PDFs in {directory}")
        return docs
    print(f"Found {len(files)} PDF(s)")
    for p in files:
        try:
            d = PyPDFLoader(str(p)).load()
            docs.extend(d)
            print(f"  {p.name}: {len(d)} pages")
        except Exception as e:
            print(f"  Error loading {p.name}: {e}")
    return docs


def build_vector_store(documents: list, embeddings) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    print(f"Building embeddings with {EMBED_MODEL_NAME}  (takes ~1-2 min)...")
    vs = FAISS.from_documents(chunks, embeddings)
    VECTOR_STORE_DIR.mkdir(exist_ok=True)
    vs.save_local(str(VECTOR_STORE_DIR))
    (VECTOR_STORE_DIR / ".ollama_embeddings").touch()
    print(f"Saved to {VECTOR_STORE_DIR}")
    return vs


def format_docs(docs) -> str:
    return "\n\n---\n\n".join(d.page_content for d in docs)


def initialize_system():
    print("\n" + "=" * 60)
    print("  AI Research Engine for Commercial Courts")
    print("=" * 60 + "\n")

    import urllib.request
    try:
        urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    except Exception:
        raise RuntimeError("Cannot reach Ollama. Open the Ollama app from Applications first.")

    # mxbai-embed-large: purpose-built for retrieval tasks
    print(f"Loading embedding model: {EMBED_MODEL_NAME}")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME, base_url=OLLAMA_BASE_URL)

    # Auto-rebuild if old HuggingFace store exists (no sentinel = stale)
    sentinel = VECTOR_STORE_DIR / ".ollama_embeddings"
    if (VECTOR_STORE_DIR / "index.faiss").exists() and sentinel.exists():
        print("Loading cached vector store...")
        vs = FAISS.load_local(
            str(VECTOR_STORE_DIR), embeddings, allow_dangerous_deserialization=True
        )
        print("Vector store ready")
    else:
        if VECTOR_STORE_DIR.exists():
            print("Removing stale vector store (old embeddings)...")
            shutil.rmtree(VECTOR_STORE_DIR)
        DATA_DIR.mkdir(exist_ok=True)
        docs = load_pdfs(DATA_DIR)
        if not docs:
            raise ValueError(f"No PDFs in '{DATA_DIR}'. Add PDF files and restart.")
        vs = build_vector_store(docs, embeddings)

    # phi3:mini: low temperature for factual legal reasoning
    print(f"Loading LLM: {MODEL_NAME}")
    llm = ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        num_predict=1024,
        num_ctx=4096,
    )

    # The strict legal persona and formatting (ISSUES/LAW/ANALYSIS/CONCLUSION)
    # are now permanently baked into the phi3-legal model itself via the Modelfile.
    prompt = PromptTemplate.from_template(
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Legal Opinion:"
    )

    # MMR retriever: diverse top-6 chunks from 20 candidates
    retriever = vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20},
    )

    # Modern LCEL chain (replaces deprecated RetrievalQA)
    chain = (
        {
            "context":  retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\nSystem initialized successfully!\n")
    return chain, retriever


# Globals
chain = None
retriever = None


def query_system(question: str) -> str:
    global chain, retriever
    try:
        answer = chain.invoke(question)

        # Fetch source docs for citation
        source_docs = retriever.invoke(question)
        sources = sorted({
            f"  {Path(d.metadata.get('source', 'Unknown')).name}  "
            f"(page {int(d.metadata.get('page', 0)) + 1})"
            for d in source_docs
        })
        src_text = "\n".join(sources) if sources else "  No sources found"
        return f"{answer}\n\n---\nSources:\n{src_text}"
    except Exception as e:
        return f"Error: {e}"


def chat_response(message, history):
    global chain
    if chain is None:
        return "System not initialized. Please restart."
    return query_system(message)


def main():
    global chain, retriever
    try:
        chain, retriever = initialize_system()

        print("Launching Gradio interface...")
        demo = gr.ChatInterface(
            fn=chat_response,
            title="AI Research Engine for Commercial Courts",
            description=(
                "Ask questions about commercial court cases and legal documents.\n\n"
                "Examples:\n"
                "- What are the core factual disputes between the parties in this case?\n"
                "- Identify the primary legal statutes and case precedents relied upon by the court.\n"
                "- What is the court's final ruling and the reasoning behind it?\n\n"
                "Tip: Add more PDFs to the data/ folder and restart to expand the knowledge base."
            ),
            examples=[
                "What are the core factual disputes between the parties in this case?",
                "Identify the primary legal statutes and case precedents relied upon by the court.",
                "What is the court's final ruling and the reasoning behind it?",
            ],
        )
        demo.launch(server_name="0.0.0.0", server_port=7861, share=True)
    except Exception as e:
        print(f"\nFailed to start: {e}")
        raise


if __name__ == "__main__":
    main()
