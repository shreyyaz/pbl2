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
        num_predict=512,
        num_ctx=2048,
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
        search_kwargs={"k": 4, "fetch_k": 10},
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
        # Get source docs once (reuse for both context and citations)
        source_docs = retriever.invoke(question)
        context = format_docs(source_docs)

        # Run LLM with pre-fetched context
        answer = chain.invoke(question)

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

        # ── Dark Theme CSS ─────────────────────────────────────────
        custom_css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        ::-webkit-scrollbar { width: 0px !important; background: transparent !important; }
        * { scrollbar-width: none !important; }

        body, .gradio-container {
            font-family: 'Inter', sans-serif !important;
            background: linear-gradient(160deg, #0d0d12 0%, #121218 30%, #14141f 60%, #0f1119 100%) !important;
            color: #c8cad0 !important;
            overflow-x: hidden !important;
        }

        .title-banner h1 {
            text-align: center;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #a78bfa !important;
            margin-bottom: 0.5rem !important;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(167, 139, 250, 0.12) !important;
            border-radius: 16px !important;
            padding: 20px 24px !important;
            backdrop-filter: blur(12px) !important;
            margin: 10px auto 20px auto !important;
            max-width: 700px !important;
        }
        .glass-card p, .glass-card li {
            color: #8e90a0 !important;
            font-size: 0.88rem !important;
            line-height: 1.7 !important;
        }
        .glass-card code {
            background: rgba(167, 139, 250, 0.1) !important;
            color: #a78bfa !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
        .glass-card .tip { color: #7dd3fc !important; font-weight: 500; }

        .chatbot {
            background: rgba(12, 12, 18, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 16px !important;
            min-height: 420px !important;
        }

        .chatbot .user .message-bubble-border {
            background: linear-gradient(135deg, #6d5cae, #8b6fc0) !important;
            border: none !important;
            border-radius: 18px 18px 4px 18px !important;
        }
        .chatbot .user .message-bubble-border .message-content { color: #f0f0f5 !important; }

        .chatbot .bot .message-bubble-border {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 18px 18px 18px 4px !important;
        }
        .chatbot .bot .message-bubble-border .message-content { color: #b8bac5 !important; }

        .textbox textarea, .textbox input {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(167, 139, 250, 0.15) !important;
            border-radius: 14px !important;
            color: #d0d2da !important;
            font-family: 'Inter', sans-serif !important;
            padding: 14px 16px !important;
        }
        .textbox textarea:focus, .textbox input:focus {
            border-color: rgba(167, 139, 250, 0.45) !important;
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.08) !important;
            outline: none !important;
        }

        button.primary {
            background: linear-gradient(135deg, #7c5cbf, #6d5cae) !important;
            border: none !important;
            border-radius: 14px !important;
            color: #f0f0f5 !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(109, 92, 174, 0.2) !important;
        }
        button.primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(109, 92, 174, 0.35) !important;
        }

        button.secondary {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #7a7a90 !important;
            font-family: 'Inter', sans-serif !important;
        }

        .example-buttons button, .examples button {
            background: rgba(167, 139, 250, 0.04) !important;
            border: 1px solid rgba(167, 139, 250, 0.1) !important;
            border-radius: 12px !important;
            color: #8080a0 !important;
            font-size: 0.82rem !important;
            font-family: 'Inter', sans-serif !important;
            padding: 8px 16px !important;
        }

        .footer-text p {
            text-align: center;
            font-size: 0.7rem !important;
            color: #3a3a4a !important;
            margin-top: 20px !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        .block .label-wrap span {
            color: #6b6b80 !important;
            font-family: 'Inter', sans-serif !important;
        }

        footer { display: none !important; }

        """

        with gr.Blocks(css=custom_css, title="AI Legal Research Engine") as demo:
            gr.Markdown(
                "# ⚖️ AI Research Engine for Commercial Courts",
                elem_classes=["title-banner"]
            )

            gr.Markdown(
                """<div class="glass-card">
                <p>🔍 Ask questions about commercial court cases and legal documents loaded in the system.</p>
                <ul>
                    <li>What are the core factual disputes between the parties?</li>
                    <li>Identify the primary legal statutes and case precedents relied upon.</li>
                    <li>What is the court's final ruling and the reasoning behind it?</li>
                </ul>
                <p class="tip">💡 Tip: Add more PDFs to the <code>data/</code> folder and restart to expand the knowledge base.</p>
                </div>"""
            )

            gr.ChatInterface(
                fn=chat_response,
                examples=[
                    "What are the core factual disputes between the parties in this case?",
                    "Identify the primary legal statutes and case precedents relied upon by the court.",
                    "What is the court's final ruling and the reasoning behind it?",
                    "Summarize the key arguments made by both parties.",
                ],
            )

            gr.Markdown(
                "⚖️ AI LEGAL RESEARCH ENGINE · BUILT FOR COMMERCIAL COURTS OF INDIA\n\nSHREYAS KUMAR SINGH - 2427030027",
                elem_classes=["footer-text"]
            )

        demo.launch(server_name="0.0.0.0", server_port=7861, share=True)
    except Exception as e:
        print(f"\nFailed to start: {e}")
        raise


if __name__ == "__main__":
    main()
