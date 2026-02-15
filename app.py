"""
AI-Driven Research Engine for Commercial Courts
================================================

A Gradio-based application that uses LangChain, FAISS, and OpenRouter
to provide intelligent Q&A over legal PDF documents.

Features:
- Loads all PDFs from the 'data/' folder
- Creates vector embeddings using HuggingFace sentence-transformers
- Uses FAISS for efficient similarity search
- Connects to OpenRouter API for LLM inference (Claude Opus 4.5)
- Provides a beautiful Gradio chat interface
"""

import os
import glob
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import gradio as gr

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = Path("data")
VECTOR_STORE_DIR = Path("vector_store")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "anthropic/claude-opus-4.5"  # Claude Opus 4.5


def load_pdfs_from_directory(directory: Path) -> list:
    """Load all PDF documents from the specified directory."""
    documents = []
    pdf_files = list(directory.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {directory}")
        return documents
    
    print(f"📂 Found {len(pdf_files)} PDF file(s) in {directory}")
    
    for pdf_path in pdf_files:
        try:
            print(f"  📄 Loading: {pdf_path.name}")
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            documents.extend(docs)
            print(f"     ✓ Loaded {len(docs)} pages")
        except Exception as e:
            print(f"  ❌ Error loading {pdf_path.name}: {e}")
    
    return documents


def create_vector_store(documents: list, embeddings) -> FAISS:
    """Create or load FAISS vector store from documents."""
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"📊 Split into {len(chunks)} chunks")
    
    # Create vector store
    print("🔄 Creating vector embeddings (this may take a moment)...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save vector store for future use
    VECTOR_STORE_DIR.mkdir(exist_ok=True)
    vector_store.save_local(str(VECTOR_STORE_DIR))
    print(f"💾 Vector store saved to {VECTOR_STORE_DIR}")
    
    return vector_store


def initialize_system():
    """Initialize the complete RAG system."""
    print("\n" + "="*60)
    print("🏛️  AI Research Engine for Commercial Courts")
    print("="*60 + "\n")
    
    # Check for API key
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        raise ValueError(
            "❌ OpenRouter API key not found!\n"
            "Please add your API key to the .env file:\n"
            "OPENROUTER_API_KEY=your_actual_key_here\n"
            "Get a free key at: https://openrouter.ai/keys"
        )
    
    # Initialize embeddings
    print("🧠 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Load or create vector store
    if VECTOR_STORE_DIR.exists() and (VECTOR_STORE_DIR / "index.faiss").exists():
        print("📥 Loading existing vector store...")
        vector_store = FAISS.load_local(
            str(VECTOR_STORE_DIR), 
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✓ Vector store loaded successfully")
    else:
        # Load PDFs and create new vector store
        DATA_DIR.mkdir(exist_ok=True)
        documents = load_pdfs_from_directory(DATA_DIR)
        
        if not documents:
            raise ValueError(
                f"❌ No documents found!\n"
                f"Please add PDF files to the '{DATA_DIR}' folder."
            )
        
        vector_store = create_vector_store(documents, embeddings)
    
    # Initialize LLM with OpenRouter
    print(f"🤖 Connecting to OpenRouter (model: {MODEL_NAME})...")
    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.3,
        max_tokens=1024,
    )
    
    # Create retrieval chain
    # Create retrieval chain
    prompt_template = """You are an expert Legal Research Assistant and Judge's Clerk for the Commercial Courts of India.
Your task is to provide comprehensive legal analysis and specific decision-making guidance based on the provided context (Case Laws, Statutes, Books).

If the user asks for a decision or legal opinion:
1. ACT AS A JUDGE: Weigh the arguments based *only* on the provided context.
2. CITE SPECIFIC SECTIONS/CASES: Refer to specific sections of the Commercial Courts Act, Arbitration Act, or case precedents found in the context.
3. STRUCTURE YOUR ANSWER:
   - **Issues**: What are the legal questions?
   - **Rule of Law**: What acts/sections apply? (Cite from context)
   - **Analysis**: Apply the rules to the facts.
   - **Conclusion/Opinion**: What should be the likely decision?

If the answer is not in the context, state: "I cannot find specific information in the available legal documents to answer this."

Context:
{context}

Question: {question}

Legal Opinion:"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("\n✅ System initialized successfully!\n")
    return qa_chain


def query_system(qa_chain, question: str) -> str:
    """Query the system and return answer with sources."""
    try:
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        
        # Extract source information
        sources = []
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            sources.append(f"📄 {Path(source).name} (Page {page + 1})")
        
        sources_text = "\n".join(set(sources)) if sources else "No sources found"
        
        full_response = f"{answer}\n\n---\n**📚 Sources:**\n{sources_text}"
        return full_response
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Global variable for the QA chain
qa_chain = None


def chat_response(message, history):
    """Handle chat response for Gradio."""
    global qa_chain
    if qa_chain is None:
        return "System not initialized. Please restart the application."
    return query_system(qa_chain, message)


def main():
    """Main entry point."""
    global qa_chain
    
    try:
        # Initialize the system
        qa_chain = initialize_system()
        
        # Create simple Gradio interface
        print("🚀 Launching Gradio interface...")
        print("   Open your browser at the URL shown below")
        print("   Press Ctrl+C to stop the server\n")
        
        demo = gr.ChatInterface(
            fn=chat_response,
            title="🏛️ AI Research Engine for Commercial Courts",
            description="""Ask questions about commercial court cases and legal documents.
            
**Example questions:**
- What was the case of Manoj Kumar Pandey about?
- What does the Constitution say about right to appointment?
- Explain the concept of delay and laches in filing petitions

💡 **Tip:** Add more PDFs to the `data/` folder and restart to expand the knowledge base.""",
            examples=[
                "What was the case of Manoj Kumar Pandey about?",
                "What is the concept of delay and laches?",
                "What did the Supreme Court say about waiting list candidates?",
            ],
            # theme=gr.themes.Soft(),  <-- Removed
        )
        
        demo.launch(
            server_name="0.0.0.0",
            server_port=7861,
            share=True,
        )
        
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
