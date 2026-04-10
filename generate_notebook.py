import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# \U0001f4ca Model Performance Evaluation\n",
    "\n",
    "This notebook evaluates the accuracy, precision, and performance of the RAG system using different algorithms (embedding models, chunking strategies, and LLMs)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "!pip install -q ragas datasets pandas matplotlib seaborn tqdm"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import time\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from tqdm import tqdm\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "from langchain_community.document_loaders import PyPDFLoader\n",
    "from langchain_text_splitters import RecursiveCharacterTextSplitter\n",
    "from langchain_community.vectorstores import FAISS\n",
    "from langchain_huggingface import HuggingFaceEmbeddings\n",
    "from langchain_ollama import OllamaLLM\n",
    "from langchain.chains import create_retrieval_chain\n",
    "from langchain.chains.combine_documents import create_stuff_documents_chain\n",
    "from langchain.prompts import ChatPromptTemplate\n",
    "\n",
    "# Evaluation Import (if ragas is available)\n",
    "try:\n",
    "    from ragas import evaluate\n",
    "    from ragas.metrics import faithfulness, answer_relevance, context_precision, context_recall\n",
    "    HAS_RAGAS = True\n",
    "except ImportError:\n",
    "    HAS_RAGAS = False\n",
    "    print(\"Ragas not installed or import error. Metrics will be calculated differently.\")\n",
    "\n",
    "load_dotenv()\n",
    "OPENROUTER_API_KEY = os.getenv(\"OPENROUTER_API_KEY\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. Load Data\n",
    "loader = PyPDFLoader(\"data/Case-Test.pdf\")\n",
    "docs = loader.load()\n",
    "\n",
    "# 2. Define Evaluation Set (Questions & Ground Truth)\n",
    "eval_set = [\n",
    "    {\n",
    "        \"question\": \"Who were the petitioners in Civil Misc. Writ Petition No. 40736 of 2002?\",\n",
    "        \"ground_truth\": \"The petitioners were Manoj Kumar Pandey and others.\",\n",
    "        \"context\": \"Civil Misc. Writ Petition No. 40736 of 2002 ... Manoj Kumar Pandey & others ...Petitioners\"\n",
    "    },\n",
    "    {\n",
    "        \"question\": \"What was the date of the judgment in Manoj Kumar Pandey V. State of U.P.?\",\n",
    "        \"ground_truth\": \"The judgment was dated 27.02.2006.\",\n",
    "        \"context\": \"DATED: ALLAHABAD 27.02.2006\"\n",
    "    },\n",
    "    {\n",
    "        \"question\": \"What was the result date of the competitive examination for the Post of A.P.O.?\",\n",
    "        \"ground_truth\": \"The result was declared on 20.3.99.\",\n",
    "        \"context\": \"held for the Post of A.P.O. result declared on 20.3.99\"\n",
    "    },\n",
    "    {\n",
    "        \"question\": \"Explain the concept of 'delay and laches' as mentioned in the case.\",\n",
    "        \"ground_truth\": \"The court rejected the petition because it was filed in September 2002, much after the expiry of the select list, citing delay and laches. A petition cannot be considered if the petitioner was dormant and waited for someone else's case to be decided.\",\n",
    "        \"context\": \"the Hon\u2019ble Supreme Court rejected the contention that a petition should be considered ignoring the delay and laches on the ground that he filed the petition just after coming to know of the relief granted by the Court in a similar case\"\n",
    "    },\n",
    "    {\n",
    "        \"question\": \"What was the specific relief granted in the case of Sheo Shyam & Ors. Vs. State of U.P. & Ors.?\",\n",
    "        \"ground_truth\": \"The Supreme Court directed that the 11 appellants should be considered for appointment if found suitable and eligible, reckoning the life of the waiting list from the last date of recommendation.\",\n",
    "        \"context\": \"The Supreme Court however granted relief to them by directing that they shall be considered by the Commission and the State Government, and would be appointed if otherwise found suitable and eligible.\"\n",
    "    }\n",
    "]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def setup_rag_chain(chunk_size, chunk_overlap, embedding_model_name, llm_model_name=\"llama3.2:1b\"):\n",
    "    # Split\n",
    "    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)\n",
    "    chunks = text_splitter.split_documents(docs)\n",
    "    \n",
    "    # Embeddings\n",
    "    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)\n",
    "    \n",
    "    # Vector store\n",
    "    vectorstore = FAISS.from_documents(chunks, embeddings)\n",
    "    retriever = vectorstore.as_retriever(search_kwargs={\"k\": 3})\n",
    "    \n",
    "    # LLM\n",
    "    llm = OllamaLLM(model=llm_model_name)\n",
    "    \n",
    "    # Simple Prompt\n",
    "    prompt = ChatPromptTemplate.from_template(\"\"\"Answer the question based only on the provided context:\n",
    "    Context: {context}\n",
    "    Question: {input}\n",
    "    Answer:\"\"\")\n",
    "    \n",
    "    # Chain\n",
    "    document_chain = create_stuff_documents_chain(llm, prompt)\n",
    "    retrieval_chain = create_retrieval_chain(retriever, document_chain)\n",
    "    \n",
    "    return retrieval_chain\n",
    "\n",
    "# Define Algorithms to Test\n",
    "algorithms = [\n",
    "    {\n",
    "        \"name\": \"Baseline (MiniLM, 1000/200)\",\n",
    "        \"chunk_size\": 1000,\n",
    "        \"chunk_overlap\": 200,\n",
    "        \"embedding_model\": \"sentence-transformers/all-MiniLM-L6-v2\"\n",
    "    },\n",
    "    {\n",
    "        \"name\": \"Legal Specifc (InLegalBERT, 500/50)\",\n",
    "        \"chunk_size\": 500,\n",
    "        \"chunk_overlap\": 50,\n",
    "        \"embedding_model\": \"law-ai/InLegalBERT\"\n",
    "    }\n",
    "]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "results = []\n",
    "\n",
    "for algo in algorithms:\n",
    "    print(f\"Evaluating: {algo['name']}\")\n",
    "    chain = setup_rag_chain(algo['chunk_size'], algo['chunk_overlap'], algo['embedding_model'])\n",
    "    \n",
    "    algo_results = []\n",
    "    start_total = time.time()\n",
    "    \n",
    "    for item in tqdm(eval_set):\n",
    "        start_q = time.time()\n",
    "        response = chain.invoke({\"input\": item['question']})\n",
    "        latency = time.time() - start_q\n",
    "        \n",
    "        # Collect data\n",
    "        algo_results.append({\n",
    "            \"question\": item['question'],\n",
    "            \"answer\": response['answer'],\n",
    "            \"contexts\": [doc.page_content for doc in response['context']],\n",
    "            \"ground_truth\": item['ground_truth'],\n",
    "            \"latency\": latency\n",
    "        })\n",
    "    \n",
    "    avg_latency = (time.time() - start_total) / len(eval_set)\n",
    "    results.append({\n",
    "        \"algorithm\": algo['name'],\n",
    "        \"data\": algo_results,\n",
    "        \"avg_latency\": avg_latency\n",
    "    })"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import difflib\n",
    "\n",
    "def calculate_similarity(ground_truth, answer):\n",
    "    # Simple lexical similarity as a fallback proxy for accuracy\n",
    "    return difflib.SequenceMatcher(None, ground_truth.lower(), answer.lower()).ratio()\n",
    "\n",
    "summary_stats = []\n",
    "\n",
    "for res in results:\n",
    "    accuracies = [calculate_similarity(d['ground_truth'], d['answer']) for d in res['data']]\n",
    "    summary_stats.append({\n",
    "        \"Algorithm\": res['algorithm'],\n",
    "        \"Avg Lexical Similarity\": np.mean(accuracies),\n",
    "        \"Avg Latency (s)\": res['avg_latency']\n",
    "    })\n",
    "\n",
    "df_summary = pd.DataFrame(summary_stats)\n",
    "df_summary"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(12, 6))\n",
    "\n",
    "plt.subplot(1, 2, 1)\n",
    "sns.barplot(x=\"Algorithm\", y=\"Avg Lexical Similarity\", data=df_summary)\n",
    "plt.title(\"Accuracy Proxy (Lexical Similarity)\")\n",
    "plt.ylim(0, 1)\n",
    "plt.xticks(rotation=45)\n",
    "\n",
    "plt.subplot(1, 2, 2)\n",
    "sns.barplot(x=\"Algorithm\", y=\"Avg Latency (s)\", data=df_summary)\n",
    "plt.title(\"Performance (Latency)\")\n",
    "plt.xticks(rotation=45)\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

os.makedirs('/Users/rohitganguly/Desktop/ai_resarch_pbl', exist_ok=True)
notebook_path = '/Users/rohitganguly/Desktop/ai_resarch_pbl/Model_Evaluation.ipynb'

with open(notebook_path, 'w') as f:
    json.dump(notebook_content, f, indent=1)

print(f"Created notebook at {notebook_path}")
