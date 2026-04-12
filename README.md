# 🏛️ AI-Driven Research Engine for Commercial Courts

An intelligent, **100% local** legal research assistant that helps lawyers, judges, and legal professionals quickly search and analyze commercial court cases — powered entirely by [Ollama](https://ollama.com) with no external API calls.

| Component | Technology |
|-----------|-----------|
| **LLM** | `phi3-legal` (custom fine-tuned via Modelfile) |
| **Embeddings** | `mxbai-embed-large` (retrieval-specialised) |
| **Vector Store** | FAISS with MMR retrieval |
| **UI** | Gradio (dark glassmorphism theme) |

> **Privacy First** — All inference runs on your machine. No data leaves your system. No API keys required for core functionality.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed
- **[Ollama](https://ollama.com)** installed and running
- ~4 GB free disk space (for models)

### 1. Clone & Install

```bash
git clone https://github.com/psychic-coder/ai_resarch_pbl.git
cd ai_resarch_pbl
pip install -r requirements.txt
```

### 2. Set Up Ollama Models

Pull the embedding model and base LLM:

```bash
ollama pull mxbai-embed-large
ollama pull phi3:mini
```

Create the custom legal persona model from the included `Modelfile`:

```bash
ollama create phi3-legal -f Modelfile
```

### 3. Populate Data

Place your legal PDF files in the `data/` folder. You can also generate starter documents:

```bash
python generate_pdfs.py           # Commercial Courts Act & Arbitration Act
python generate_evidence_act.py   # Indian Evidence Act summary
python generate_legal_book.py     # Legal Maxims & Interpretation guide
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Navigate to: **http://localhost:7861**

The system will automatically:
1. Connect to Ollama
2. Load/build the FAISS vector store from PDFs in `data/`
3. Initialize the phi3-legal LLM
4. Launch the Gradio web interface

---

## 📁 Project Structure

### Core Application

| File | Purpose |
|------|---------|
| [`app.py`](app.py) | **Main Application.** Initializes the RAG pipeline using LangChain — loads PDFs, chunks text with `RecursiveCharacterTextSplitter`, generates embeddings via `mxbai-embed-large`, stores them in FAISS, connects to `phi3-legal` (Ollama) for answering queries, and launches the Gradio web interface. |
| [`Modelfile`](Modelfile) | **Custom LLM Persona.** Defines the `phi3-legal` model — a fine-tuned phi3:mini with a strict legal research assistant persona, low temperature (0.05), and a structured output format (ISSUES → APPLICABLE LAW → ANALYSIS → CONCLUSION). |
| [`.env`](.env) | **Configuration.** Stores environment variables: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`, and optional Google Drive settings. |
| [`requirements.txt`](requirements.txt) | **Dependencies.** All Python libraries required (LangChain, FAISS, Gradio, Ollama bindings, etc.). |

### Data Management Tools

| File | Purpose |
|------|---------|
| [`generate_pdfs.py`](generate_pdfs.py) | Generates PDFs containing the full text of the **Commercial Courts Act, 2015** and the **Arbitration & Conciliation Act, 1996**. |
| [`generate_evidence_act.py`](generate_evidence_act.py) | Generates a PDF summary of the **Indian Evidence Act, 1872** focused on sections relevant to commercial disputes. |
| [`generate_legal_book.py`](generate_legal_book.py) | Generates a synthetic legal reference book on **Statutory Interpretation & Legal Maxims** for commercial courts. |
| [`scrape_legal_data.py`](scrape_legal_data.py) | Web scraper to fetch official legal PDFs (Acts, Rules, Reports) from government websites with file-size validation. |
| [`drive_sync.py`](drive_sync.py) | Google Drive integration — downloads all PDFs from a shared Drive folder to the local `data/` directory via OAuth. |
| [`credentials.json`](credentials.json) | Google OAuth credentials for `drive_sync.py`. (Download from Google Cloud Console.) |

### Evaluation & Prototyping

| File | Purpose |
|------|---------|
| [`App.ipynb`](App.ipynb) | Jupyter notebook for initial RAG pipeline experiments and data exploration. |
| [`Model_Evaluation.ipynb`](Model_Evaluation.ipynb) | Model performance evaluation — compares embedding models (MiniLM vs InLegalBERT), chunking strategies, and measures accuracy/latency. |
| [`generate_notebook.py`](generate_notebook.py) | Script that generates the `Model_Evaluation.ipynb` notebook programmatically. |

### Deployment

| File | Purpose |
|------|---------|
| [`Dockerfile`](Dockerfile) | Container image definition (Python 3.11-slim, port 7861). |
| [`docker-compose.yml`](docker-compose.yml) | Docker Compose config with volume mounts for `data/`, `vector_store/`, and `.env`. |

### Directories

| Directory | Contents |
|-----------|----------|
| `data/` | **Document Repository.** Place all legal PDF files here. The app scans this folder on startup to build the knowledge base. |
| `vector_store/` | **Search Index.** Auto-generated FAISS vector embeddings. Delete this folder to force a complete re-indexing. |
| `legal_docs/` | **Download Staging.** Temporary folder used by `scrape_legal_data.py` for downloaded files. |

---

## ✨ Features

- **🔒 100% Local & Private** — Runs entirely on your machine via Ollama. No data leaves your system.
- **⚖️ Custom Legal Persona** — The `phi3-legal` model is tuned with a strict legal research assistant persona that structures every response as ISSUES → LAW → ANALYSIS → CONCLUSION.
- **📄 Smart PDF Ingestion** — Automatically reads, chunks (600 chars / 150 overlap), and indexes legal documents using FAISS.
- **🔍 MMR Retrieval** — Uses Maximal Marginal Relevance to fetch diverse, relevant context chunks (top 4 from 10 candidates).
- **🎨 Premium Dark UI** — Glassmorphism-themed Gradio interface with Inter typography, smooth gradients, and micro-animations.
- **📎 Source Citations** — Every answer includes the source PDF filename and page number.
- **☁️ Google Drive Sync** — Keep your document library in the cloud and sync it to the engine.
- **🐳 Docker Ready** — Deploy with a single `docker-compose up`.

---

## 💬 Example Queries

Try asking:

- *"What are the core factual disputes between the parties in this case?"*
- *"Identify the primary legal statutes and case precedents relied upon by the court."*
- *"What is the court's final ruling and the reasoning behind it?"*
- *"Summarize the key arguments made by both parties."*
- *"Explain the concept of delay and laches in filing petitions."*
- *"What does the Commercial Courts Act say about pre-institution mediation?"*

---

## 📈 Adding More Documents

### Option 1: Manual Upload

1. Add your PDF files to the `data/` folder
2. Delete the `vector_store/` folder (to rebuild the index)
3. Restart the application (`python app.py`)

### Option 2: Google Drive Sync

1. **Setup:** Download `credentials.json` from Google Cloud Console
2. **Configure:** Add `GOOGLE_DRIVE_FOLDER_ID` to `.env`
3. **Sync:** Run `python drive_sync.py`
4. **Run:** Start `python app.py`

---

## 🔧 Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `phi3-legal` | LLM model name |
| `OLLAMA_EMBED_MODEL` | `mxbai-embed-large` | Embedding model name |
| `GOOGLE_DRIVE_FOLDER_ID` | — | Google Drive folder for sync (optional) |

### Adjust Chunking

Edit `app.py` to change the text splitting strategy:

```python
CHUNK_SIZE    = 600   # Characters per chunk (smaller = more precise retrieval)
CHUNK_OVERLAP = 150   # Overlap between chunks
```

### Change the LLM Model

Edit the `Modelfile` to use a different base model, then rebuild:

```bash
# Edit Modelfile: change "FROM phi3:mini" to your preferred model
ollama create phi3-legal -f Modelfile
```

Or change `OLLAMA_MODEL` in `.env` to any Ollama-compatible model:

```env
OLLAMA_MODEL=llama3:8b
OLLAMA_EMBED_MODEL=mxbai-embed-large
```

### The Modelfile (Custom Legal Persona)

The `Modelfile` bakes a strict legal persona into the LLM:

```
FROM phi3:mini

PARAMETER temperature 0.05      # Near-deterministic for factual accuracy
PARAMETER num_predict 512       # Long enough for complete legal opinions
PARAMETER num_ctx 2048          # Full context window for legal chunks

SYSTEM """
You are a Legal Research Assistant for the Commercial Courts of India.
- ONLY use facts from the provided CONTEXT
- NEVER hallucinate legal facts
- Structure: ISSUES → APPLICABLE LAW → ANALYSIS → CONCLUSION
"""
```

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# The app will be available at http://localhost:7861
```

> **Note:** Ollama must be running on the host machine (or accessible at the configured `OLLAMA_BASE_URL`).

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | [Ollama](https://ollama.com) + phi3:mini | Local inference with custom legal persona |
| **Embeddings** | mxbai-embed-large | Retrieval-specialised sentence embeddings |
| **Framework** | [LangChain](https://langchain.com) | RAG pipeline orchestration (LCEL chains) |
| **Vector Store** | [FAISS](https://github.com/facebookresearch/faiss) | High-performance similarity search with MMR |
| **UI** | [Gradio](https://gradio.app) | Web interface with custom dark theme |
| **Containerisation** | Docker + Docker Compose | Reproducible deployment |

---

## 👤 Author

**Shreyas Kumar Singh** — 2427030027

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
