<div align="center">

# 🧠 Production RAG App

**From Basic PDF Q&A to Enterprise-Grade Conversational AI**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-green)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)](https://www.trychroma.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)

[Overview](#overview) • [Architecture](#architecture) • [Features](#features) • [Quick Start](#quick-start) • [Roadmap](#roadmap) • [Contributing](#contributing)

</div>

---

## 📋 Overview

Production RAG App is an enterprise-ready conversational retrieval-augmented generation (RAG) system that goes far beyond typical demo implementations. Built for real-world production workloads, it addresses the critical failure points that cause most RAG applications to collapse under production pressure.

> **The hard truth:** Most RAG demos fail the moment they face hallucinations, prompt injection, PII leakage, context drift, or multi-turn conversations. This project solves these problems incrementally with production-grade architecture decisions.

### Why This Project Exists

| Problem | Typical Demo | This Solution |
|---------|-------------|---------------|
| Hallucinations | Uncontrolled generation | Structured outputs + confidence scoring |
| Prompt Injection | No protection | Multi-layer guardrails & pattern detection |
| PII Leakage | Raw data exposure | Regex-based redaction across all pipelines |
| Retrieval Quality | Single vector search | Hybrid (Dense + Sparse) + MMR + Cross-Encoder Reranking |
| Conversational Memory | Stateless | History-aware query rewriting |
| Observability | Blind debugging | Full LangSmith tracing & cost tracking |
| API Reliability | No fallback | Retry + exponential backoff + graceful degradation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Upload     │  │    Chat      │  │   Streaming  │  │  Cost Tracking  │ │
│  │    PDFs      │  │   Interface  │  │   Responses  │  │   Dashboard     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRE-PROCESSING & SECURITY                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ PII Redaction│──▶│  Guardrails  │──▶│   Conversational  │──▶│  History-Aware │ │
│  │ (PAN/Phone/  │  │(Injection/   │  │     Memory        │  │Query Rewriting │ │
│  │   Email)     │  │  Sanitization│  │                   │  │                │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RETRIEVAL PIPELINE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Hybrid     │  │     MMR      │  │ Cross-Encoder │  │  Context        │ │
│  │  Retrieval   │──▶│  Retrieval   │──▶│   Reranking   │──▶│  Assembly       │ │
│  │(Vector+BM25) │  │  (Diversity) │  │  (Precision)  │  │                 │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GENERATION & OUTPUT                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │     LLM      │  │  Structured  │  │   Streaming  │  │   LangSmith     │ │
│  │  Generation  │──▶│   Output     │──▶│   Response   │──▶│    Tracing      │ │
│  │ (DeepSeek)   │  │   Parsing    │  │              │  │  & Monitoring   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🔒 Security & Compliance
- **PII Redaction** — Automatic detection and masking of PAN numbers, phone numbers, and email addresses during ingestion and query processing
- **Guardrails** — Multi-layer prompt injection detection with suspicious pattern validation and context sanitization
- **Input Sanitization** — Pre-processing pipeline to neutralize adversarial inputs before retrieval or generation

### 🧠 Advanced Retrieval
- **Hybrid Retrieval** — Combines dense semantic search (embeddings) with sparse lexical search (BM25) for optimal keyword precision and semantic recall
- **MMR (Max Marginal Relevance)** — Ensures diversity in retrieved chunks, eliminating redundant information and improving context coverage
- **Cross-Encoder Reranking** — Re-evaluates query-chunk pairs jointly (not independently) for significantly improved precision and contextual grounding
- **Query Rewriting** — Automatically reformulates ambiguous or conversational queries into retrieval-friendly, semantically rich queries

### 💬 Conversational Intelligence
- **History-Aware Retrieval** — Transforms follow-up queries (e.g., *"Tell me more"*) into fully contextualized searches (e.g., *"Tell me more about Zoho's business model"*)
- **Conversational Memory** — Maintains topic context across multi-turn interactions with sliding window management
- **Streaming Responses** — Real-time token streaming for improved perceived latency and user experience

### 📊 Observability & Reliability
- **LangSmith Integration** — Full execution tracing, retrieval inspection, prompt visibility, and latency tracking
- **Retry & Fallback** — Exponential backoff with graceful failure recovery and comprehensive observability logs
- **Cost Tracking** — Token usage monitoring and cost attribution per query
- **Structured Outputs** — Pydantic-enforced JSON responses ensuring consistent, parseable output schemas

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [DeepSeek API Key](https://platform.deepseek.com/) (or compatible OpenAI-compatible endpoint)
- [LangSmith API Key](https://smith.langchain.com/) (for observability)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/production-rag-app.git
cd production-rag-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# LLM Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Observability
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=production-rag-app
LANGCHAIN_TRACING_V2=true

# Vector Store
CHROMA_PERSIST_DIR=./chroma_db

# Optional: Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Running the Application

```bash
# Launch the Streamlit interface
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Usage Example

```python
from rag_system import ProductionRAG

# Initialize the system
rag = ProductionRAG(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    llm_model="deepseek-chat",
    enable_guardrails=True,
    enable_observability=True
)

# Ingest a document
rag.ingest_document("path/to/document.pdf")

# Query with full pipeline
response = rag.chat("What are the key differentiators of Zoho's business model?")

print(response.answer)
print(f"Sources: {response.sources}")
print(f"Confidence: {response.confidence}")
```

---

## 📁 Project Structure

```
production-rag-app/
├── app.py                          # Streamlit UI entry point
├── config/
│   ├── settings.py                 # Configuration management
│   └── prompts.py                  # System prompts & templates
├── core/
│   ├── __init__.py
│   ├── document_processor.py       # PDF ingestion & chunking
│   ├── retriever.py                # Hybrid + MMR retrieval logic
│   ├── reranker.py                 # Cross-encoder reranking
│   ├── generator.py                # LLM generation with structured outputs
│   ├── memory.py                   # Conversational memory management
│   ├── guardrails.py              # Security & input validation
│   └── observability.py           # LangSmith tracing & cost tracking
├── models/
│   └── schemas.py                  # Pydantic output models
├── utils/
│   ├── pii_redaction.py           # PII detection & masking
│   ├── query_rewriter.py          # Query reformulation
│   └── retry_handler.py           # Retry & fallback mechanisms
├── tests/
│   ├── test_retrieval.py
│   ├── test_guardrails.py
│   └── test_memory.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧪 Evaluation & Benchmarking

The system is designed for continuous evaluation. Planned metrics include:

| Metric | Description | Status |
|--------|-------------|--------|
| Precision@K | Relevance of top-K retrieved chunks | 🔜 Planned |
| Recall@K | Coverage of relevant information | 🔜 Planned |
| RAGAS | Automated RAG evaluation framework | 🔜 Planned |
| Latency P95 | 95th percentile response time | ✅ Active |
| Cost per Query | Token cost attribution | ✅ Active |
| Injection Detection Rate | Guardrails effectiveness | 🔜 Planned |

---

## 🗺️ Roadmap

### Current (v1.0)
- [x] Hybrid Retrieval (Vector + BM25)
- [x] Cross-Encoder Reranking
- [x] Conversational Memory & History-Aware Retrieval
- [x] PII Redaction & Guardrails
- [x] Structured Outputs & Streaming
- [x] LangSmith Observability
- [x] Retry & Fallback Mechanisms

### Next (v1.1)
- [ ] Topic-Aware Memory (contamination detection)
- [ ] Retrieval Evaluation Metrics (Precision@K, Recall@K)
- [ ] RAGAS Integration for automated evaluation
- [ ] Multi-Query Retrieval for improved recall

### Future (v2.0)
- [ ] Entity-Aware Retrieval Filtering
- [ ] Caching Layer (Redis/Semantic Cache)
- [ ] Async Retrieval Pipelines
- [ ] Production Deployment Architecture (Docker/K8s)
- [ ] A/B Testing Framework for retrieval strategies

---

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linting
ruff check .
black .
```

### Areas for Contribution
- 🐛 Bug fixes and edge case handling
- 📊 Evaluation framework implementation
- 🌍 Multi-language support for PII detection
- ⚡ Performance optimizations
- 📚 Documentation improvements

---

## 📝 Key Learnings & Insights

> **RAG is Mostly a Retrieval Problem**
> Better prompts alone cannot fix bad chunks, poor ranking, or noisy retrieval. Retrieval quality matters more than model size in many production scenarios.

> **Reranking is Extremely Powerful**
> Cross-encoder reranking improved retrieval quality more than many other optimizations combined. The joint encoding of query + chunk is a game-changer.

> **Memory Systems Are Hard**
> Conversational AI introduces topic drift and memory contamination. A sliding window helps, but topic-aware memory is the next frontier.

> **Prompt Engineering Becomes System Engineering**
> At advanced stages, prompts are no longer "just prompts" — they become core architectural components for routing, rewriting, and grounding.

> **Observability Changes Everything**
> Without LangSmith, many retrieval and memory bugs would remain invisible. Tracing transformed debugging from art to science.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the orchestration framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) for embedding & reranking models
- [Streamlit](https://github.com/streamlit/streamlit) for the UI framework

---

<div align="center">

**Built with ❤️ by AI Engineers, for AI Engineers.**

[⭐ Star this repo](https://github.com/yourusername/production-rag-app) • [🐛 Report Bug](../../issues) • [💡 Request Feature](../../issues)

</div>
