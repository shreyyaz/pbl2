# 🏛️ AI-Driven Research Engine for Commercial Courts

An intelligent legal research assistant powered by **Claude Opus 4.5** that helps lawyers, judges, and legal professionals quickly search and analyze commercial court cases.

[![Explore the Demo](https://img.shields.io/badge/Explore%20the%20Demo%20-%E2%9C%94-green)](https://huggingface.co/spaces/hemanthkarthick03/Research-Agent-of-Commercial-Courts)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed
- **OpenRouter API Key** (free at [openrouter.ai/keys](https://openrouter.ai/keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/psychic-coder/ai_resarch_pbl.git
   cd ai_resarch_pbl
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   
   Edit the `.env` file and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Populate Data** (Optional but Recommended)
   Run the PDF generator to create initial legal documents (Commercial Courts Act & Arbitration Act):
   ```bash
   python generate_pdfs.py
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```

6. **Open in browser**
   
   Navigate to: **http://localhost:7861**

---

## 📁 Project Structure & File Guide

This project is organized into modular scripts for data ingestion, processing, and application serving.

### Core Application
| File | Purpose |
|------|---------|
| **`app.py`** | **The Main Application Logic.** <br> • Initializes the RAG (Retrieval-Augmented Generation) pipeline using LangChain. <br> • Loads PDFs from `data/` and chunks them using `RecursiveCharacterTextSplitter`. <br> • Generates embeddings via HuggingFace and stores them in FAISS. <br> • Connects to OpenRouter (Claude Opus 4.5) for answering queries. <br> • Launches the web interface using **Gradio**. |
| **`.env`** | **Configuration Secrets.** <br> Stores sensitive environment variables like `OPENROUTER_API_KEY` and `GOOGLE_DRIVE_FOLDER_ID`. **Never commit this file to public repositories.** |
| **`requirements.txt`** | **Dependency List.** <br> Lists all Python libraries required to run the project (e.g., `langchain`, `faiss-cpu`, `gradio`, `google-api-python-client`). |

### Data Management Tools
| File | Purpose |
|------|---------|
| **`drive_sync.py`** | **Google Drive Integration.** <br> Connects to a specified Google Drive folder (via OAuth) and downloads all PDF files to the local `data/` directory. Useful for teams to collaborate on a shared document repository. |
| **`credentials.json`** | **Google OAuth Credentials.** <br> Contains the Client ID and Client Secret required for `drive_sync.py` to authenticate with Google API. (You must download this from Google Cloud Console). |
| **`scrape_legal_data.py`** | **Web Scraper.** <br> A utility script designed to fetch official legal PDFs (Acts, Rules, Reports) from government websites. Includes file size validation to prevent corrupted downloads. |
| **`generate_pdfs.py`** | **Synthetic Data Generator.** <br> A fallback utility that generates valid PDF files containing the full text of key acts (Commercial Courts Act 2015, Arbitration Act 1996) locally. Use this when official download links are broken. |

### Directories
| Directory | Contents |
|-----------|----------|
| **`data/`** | **Document Repository.** <br> Place all your legal PDF files here. The application scans this folder on startup to build the knowledge base. |
| **`vector_store/`** | **Search Index.** <br> Automatically generated folder where FAISS stores the vector embeddings. Delete this folder to force a complete re-indexing of all documents in `data/`. |
| **`legal_docs/`** | **Download Staging.** <br> Temporary folder used by `scrape_legal_data.py` to save downloaded files before they are moved to `data/` or uploaded to Drive. |

### Research & Prototyping
| File | Purpose |
|------|---------|
| **`App.ipynb`** | **Jupyter Notebook.** <br> Used for initial experiments, data exploration, and testing the RAG pipeline logic piece-by-piece before deploying it in `app.py`. |

---

## ✨ Features

- **智能 PDF Analysis**: Automatically reads and understands complex legal documents.
- **Auto-Indexing**: Just drop a PDF in `data/`, restart, and it's searchable.
- **Context-Aware Answers**: Uses Claude Opus 4.5 to answer questions *specifically based on the provided documents*, citing page numbers.
- **Google Drive Sync**: Keep your document library in the cloud and sync it to the engine.
- **Robust Fallbacks**: Includes tools to generate legal texts if online sources fail.

---

## 💬 Example Queries

Try asking:
- "What was the case of Manoj Kumar Pandey about?"
- "What does the Constitution say about right to appointment?"
- "Explain the concept of delay and laches in filing petitions"
- "What did the Supreme Court say about waiting list candidates?"

---

## 📈 Adding More Documents

### Option 1: Manual Upload
1. Add your PDF files to the `data/` folder
2. Delete the `vector_store/` folder (to rebuild the index)
3. Restart the application

### Option 2: Google Drive Sync (Recommended)

1. **Setup**: Fill in `credentials.json` with your Google Cloud Client ID/Secret.
2. **Configure**: Add `GOOGLE_DRIVE_FOLDER_ID` to `.env`.
3. **Sync**: Run `python drive_sync.py` to download files.
4. **Run**: Start `python app.py`.

---

## 🔧 Configuration

### Change the LLM Model
Edit `app.py`:
```python
MODEL_NAME = "anthropic/claude-opus-4.5"
# Alternatives: "meta-llama/llama-3-70b-instruct", "google/gemini-pro"
```

### Adjust Chunking
For better context on long documents, tweak in `app.py`:
```python
CHUNK_SIZE = 1000      # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks
```

---

## 🛠️ Tech Stack

- **LangChain**: Architecture for RAG framework.
- **FAISS**: High-performance vector similarity search.
- **HuggingFace**: `all-MiniLM-L6-v2` for sentence embeddings.
- **OpenRouter**: Unified API for accessing top-tier LLMs.
- **Gradio**: Rapid UI development for ML apps.

---

## 📝 License

This project is open source and available under the MIT License.
