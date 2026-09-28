# Enterprise AI Knowledge Assistant — Forward Deployed Engineering Demo

> **A production-grade Forward Deployed Engineering (FDE) customer implementation simulation for Acme Corporation.**  
> Delivering grounded internal policy answering across **HR**, **Finance**, and **IT** with a **5-stage Defense-in-Depth Guardrail Perimeter**, real-time pipeline observability, and automated customer acceptance testing.

---

> [!IMPORTANT]
> **FDE Core Principle**:
> RAG, embeddings, vector databases, LLMs, and guardrails are technical components used within the FDE solution. They are not themselves the definition of Forward Deployed Engineering.  
> **$\text{FDE} = \text{Customer Problem Understanding} + \text{Solution Design} + \text{Implementation} + \text{Testing} + \text{Feedback Loop} + \text{Iteration} + \text{Acceptance}$**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Customer Problem](#2-customer-problem)
3. [Forward Deployed Engineering (FDE) Context](#3-forward-deployed-engineering-fde-context)
4. [Key Requirements](#4-key-requirements)
5. [Architecture](#5-architecture)
6. [Technology Stack](#6-technology-stack)
7. [Document Processing Pipeline](#7-document-processing-pipeline)
8. [RAG Semantic Retrieval Engine](#8-rag-semantic-retrieval-engine)
9. [LLM Integration & Prompt Construction](#9-llm-integration--prompt-construction)
10. [AI Safety & Guardrail Perimeter](#10-ai-safety--guardrail-perimeter)
11. [Customer Workflow & FDE Workspace](#11-customer-workflow--fde-workspace)
12. [Testing & Validation Matrix](#12-testing--validation-matrix)
13. [Customer Configuration Management](#13-customer-configuration-management)
14. [Running Locally](#14-running-locally)
15. [Project Structure](#15-project-structure)
16. [Known Limitations](#16-known-limitations)
17. [Future Improvements](#17-future-improvements)

---

## 1. Project Overview

The **Enterprise AI Knowledge Assistant** simulates a real-world enterprise deployment led by a Forward Deployed Engineer (FDE). Built for a fictional customer, **Acme Corporation**, the system enables employees to query company policy documents and receive accurate, context-grounded answers with verified document citations, page numbers, and similarity metrics.

Rather than exposing an unconstrained foundation model, the system wraps retrieval and generation in a **3-Layer Deterministic Guardrail Perimeter** that:
* Blocks adversarial prompt injections and malformed inputs at Layer 1 in under 1ms.
* Evaluates semantic retrieval relevance mathematically at Layer 3; queries lacking sufficient evidence are refused immediately without invoking the generative LLM.
* Validates verified source citations at Layer 5 to eliminate hallucinations.
* Exposes a dual **Customer Demo Mode** (clean employee experience) and **Engineering Mode** (full pipeline observability).

---

## 2. Customer Problem

### The Customer: Acme Corporation
Acme Corporation is a mid-sized enterprise with employees working across distributed offices and remote locations. Employees frequently struggle to navigate fragmented documentation across three core departments:
1. **HR**: Leave entitlements, casual leave rules, attendance standards, probation, and hybrid work guidelines.
2. **Finance**: Business expense reimbursements, per diems, remote internet stipends, and itemized receipt submission windows.
3. **IT**: Password complexity requirements, 90-day expiration rules, multi-factor authentication (MFA), and data confidentiality.

### The Business Risks of Generic AI
Acme's leadership refused to adopt a generic AI chatbot due to four critical risks:
* **Hallucinations**: A standard LLM might invent non-existent company benefits (e.g., claiming employees receive 60 days of vacation or business-class flights).
* **Adversarial Injections**: Employees or external users might jailbreak the assistant to reveal internal system instructions or bypass security rules.
* **Lack of Attribution**: Employees need to know exactly which policy document and page number supports each answer.
* **Configuration Inflexibility**: The system must be customizable (organization name, grounding threshold, top-k chunks) without modifying underlying code.

---

## 3. Forward Deployed Engineering (FDE) Context

A **Forward Deployed Engineer (FDE)** works directly with customer executives and operational teams to transform real business requirements into functioning, verified AI systems.

```text
Customer Requirement
        ↓
Requirement Analysis
        ↓
Technical Configuration
        ↓
Implementation
        ↓
Testing
        ↓
Customer Feedback
        ↓
Iteration
        ↓
Customer Acceptance
```

* **RAG is not FDE**: Retrieval-Augmented Generation is simply a pattern for grounding models in text.
* **ChromaDB is not FDE**: A vector database is merely a data store.
* **Guardrails are not FDE**: Guardrails are defensive software checks.
* **FDE is the entire methodology**: Diagnosing the customer problem, selecting the appropriate technical building blocks, configuring them to customer constraints, validating edge cases, iterating on user feedback, and securing operational sign-off.

---

## 4. Key Requirements

| ID | Customer Requirement | Engineering Control | Verification Method |
| :--- | :--- | :--- | :--- |
| **R1** | Answer using approved company documents only. | RAG Vector Search + Demarcated Prompting | Query known policy topics; verify exact chunk citations. |
| **R2** | Never invent or hallucinate company policies. | Grounding Threshold Cutoff (`0.70`) | Query non-existent topics; verify LLM is not called. |
| **R3** | Refuse questions when evidence is unavailable. | Pre-generation Relevance Check | Returns *"Insufficient evidence in knowledge base"*. |
| **R4** | Block prompt injection and jailbreak attempts. | Layer 1 Input Guardrail Regex Engine | Attack payloads blocked in <1ms before vector search or LLM. |
| **R5** | Employees must see where answers came from. | `SourceList` & `RetrievedContext` UI Components | Displays document name, page, domain tag, and score. |
| **R6** | Engineering team must inspect pipeline telemetry. | 5-Stage Observable Pipeline & Audit Log | Step-by-step pipeline status, latency, and status codes. |
| **R7** | Configurable without editing source code. | `customer_config.json` + `/api/config` APIs | Runtime UI configuration panel updates thresholds. |

---

## 5. Architecture

### 5.1 Knowledge Ingestion Flow
```text
[ Raw PDF / TXT Document ]
            │
            ▼
    [ File Validation ] ──── (Type check, size limit <10MB, empty check)
            │
            ▼
    [ Text Extraction ] ──── (pypdf stream extraction / UTF-8 decoding)
            │
            ▼
    [ Text Cleaning ] ────── (Whitespace normalization, header/footer removal)
            │
            ▼
 [ Sliding-Window Chunking ] (500-char chunks, 100-char overlap, sentence boundaries)
            │
            ▼
 [ SentenceTransformer ] ── (384-dimensional dense vectors via all-MiniLM-L6-v2)
            │
            ▼
 [ ChromaDB Vector Store ] ─ (Stored with document_id, chunk_id, source, and domain)
```

### 5.2 User Query Execution Flow (5-Stage Defense-in-Depth)
```text
                              CUSTOMER / USER
                                     │
                                     ▼
                           React Web Application
                        (Customer Mode / Eng Mode)
                                     │
                                     ▼
                              FastAPI Backend
                                     │
                                     ▼
                    ┌───────────────────────────────────┐
                    │   LAYER 1: INPUT GUARDRAIL        │
                    │   • Empty / whitespace check      │
                    │   • Character limit (max 2000)    │
                    │   • Deterministic injection check │
                    └─────────────────┬─────────────────┘
                                      │ (Allowed)
                                      ▼
                    ┌───────────────────────────────────┐
                    │   LAYER 2: RAG RETRIEVAL          │
                    │   • Embed query (all-MiniLM-L6-v2)│
                    │   • Query ChromaDB (Top-K=3)      │
                    │   • Domain filter (HR/Finance/IT) │
                    └─────────────────┬─────────────────┘
                                      │ (Chunks retrieved)
                                      ▼
                    ┌───────────────────────────────────┐
                    │   LAYER 3: GROUNDING GUARDRAIL    │
                    │   • Cosine similarity evaluation  │
                    │   • Threshold cutoff (score ≥0.70)│
                    └─────────────────┬─────────────────┘
                                      │ (Sufficient evidence)
                                      ▼
                    ┌───────────────────────────────────┐
                    │   LAYER 4: CONTEXT-RESTRICTED LLM │
                    │   • Strict system instruction     │
                    │   • Demarcated SOURCE chunk blocks│
                    │   • Low temperature (0.1)         │
                    └─────────────────┬─────────────────┘
                                      │ (Generated text)
                                      ▼
                    ┌───────────────────────────────────┐
                    │   LAYER 5: OUTPUT GUARDRAIL       │
                    │   • Non-empty response check      │
                    │   • Citation requirement (≥1 src) │
                    │   • System prompt disclosure check│
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                         [ Grounded Answer Delivered ]
                         + Verified Source Provenance
                         + 5-Stage Telemetry Visualizer
```

---

## 6. Technology Stack

* **Frontend**: React 18, Vite 6, Tailwind CSS, Vanilla CSS Design Tokens, Lucide-style UI indicators.
* **Backend**: Python 3.11+, FastAPI, Uvicorn (ASGI), Pydantic v2.
* **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional dense vector space).
* **Vector Store**: ChromaDB (in-process persistent vector database with metadata filtering).
* **LLM**: Google Gemini 2.5 Flash / Gemini 1.5 Flash via `google-genai` SDK + Offline Deterministic Grounded Fallback.
* **Document Parsers**: `pypdf` for native PDF text streams, Python standard libraries for text files.
* **Testing**: Python `unittest`, custom automated validation harness (`test_phase8.py`).

---

## 7. Document Processing Pipeline

1. **Upload & Format Validation**:
   Accepts `.pdf` and `.txt` files up to 10 MB. Validates non-empty byte streams and valid PDF headers (`%PDF-`).
2. **Duplicate Replacement Policy**:
   Uploading a file with an existing filename replaces the previous version cleanly, removing stale vector embeddings from ChromaDB to prevent duplicate citations.
3. **Sliding-Window Chunking**:
   * Chunk size: 500 characters.
   * Chunk overlap: 100 characters.
   * Window boundary: Splits on sentence ends (`.`, `\n`) rather than breaking words in half.
4. **Domain Classification**:
   Documents are tagged with a departmental `domain` (`HR`, `Finance`, `IT`, `General`). The domain is stored in metadata and indexed directly in ChromaDB.

---

## 8. RAG Semantic Retrieval Engine

* **Dense Semantic Search**:
  User queries are vectorized in real-time using `all-MiniLM-L6-v2`. ChromaDB calculates cosine distances ($D$) converted into similarity scores:
  $$\text{Score} = 1.0 - \frac{D}{2.0}$$
* **Departmental Domain Partitioning**:
  Queries can target all documents or apply strict vector filtering:
  ```python
  where_filter = {"domain": domain} if domain and domain != "ALL" else None
  results = collection.query(query_texts=[query], n_results=top_k, where=where_filter)
  ```
* **Retrieval Playground**:
  An isolated developer console allowing engineers to test queries, adjust Top-K (1–8), tune similarity thresholds (0.20–0.70), inspect cosine scores, and verify raw retrieved chunks.

---

## 9. LLM Integration & Prompt Construction

* **Context Demarcation**:
  Retrieved chunks are formatted with strict XML-style demarcators:
  ```text
  --- SOURCE 1: leave-policy.txt [HR] (Page 1) ---
  Full-time employees receive 12 days of paid casual leave per calendar year.
  --- END SOURCE 1 ---
  ```
* **Strict Enterprise Instruction**:
  The LLM is commanded: *"Answer the user question using ONLY the facts contained in the provided sources above. If the sources do not contain sufficient evidence, refuse to answer."*
* **Deterministic Offline Fallback**:
  If running without an active Gemini API key, the system activates a local grounded synthesis fallback, enabling offline testing of the complete RAG and guardrail pipeline.

---

## 10. AI Safety & Guardrail Perimeter

### 10.1 Layer 1: Input Guardrail
* Rejects empty or whitespace-only queries.
* Enforces character ceiling (`MAX_INPUT_LENGTH=2000`).
* Inspects for prompt injection and instruction override patterns (e.g., *"ignore all previous instructions"*, *"system prompt"*, *"developer mode"*).

### 10.2 Layer 3: Grounding Guardrail
* Evaluates best retrieved chunk score against `grounding_threshold` (default `0.70`).
* **Halts execution before LLM invocation** when score is insufficient.
* Saves token cost and eliminates ungrounded hallucinations.

### 10.3 Layer 5: Output Guardrail
* Verifies non-empty generated text.
* Verifies that at least one verified source chunk accompanied the answer.
* Scans output text for accidental leakage of system instructions or demarcators.

---

## 11. Customer Workflow & FDE Workspace

The application provides a dedicated **FDE Workspace** representing the complete customer lifecycle:

```text
01 Requirements  ──►  02 Configuration  ──►  03 Knowledge Base
       ▲                                              │
       │                                              ▼
07 Acceptance    ◄──  06 Customer Feedback  ◄──  05 Testing
```

### 11.1 Requirement → Engineering Mapping (`RequirementMapping.jsx`)
Directly maps business risks to technical controls and verification methods for all 7 customer requirements.

### 11.2 Customer Feedback Loop & Iteration History
* **Feedback #1**: HR requested visible document citations → Implemented `SourceList` and `RetrievedContext` (Version 2).
* **Feedback #2**: Leadership demanded no answers outside policy → Implemented Grounding Threshold cutoff at 0.70 (Version 3).
* **Feedback #3**: IT administrators needed rejection visibility → Added 5-Stage Pipeline Status and telemetry log (Version 4).
* **Feedback #4**: Multi-department support → Added Domain Classification and Runtime Configuration (Version 5).

### 11.3 Role-Based View Simulation
* **Customer Demo Mode**: Clean employee view displaying answers, provenance badges, and a plain-English *"Why the system answered this way"* explanation card.
* **Engineering Mode**: Deep observability view showing raw chunk tensors, cosine scores, pipeline latency, and guardrail decision states.

---

## 12. Testing & Validation Matrix

Automated verification suite executable via `python test_phase8.py`:

| Test Scenario | Query | Expected Result | Verified |
| :--- | :--- | :--- | :---: |
| **Scenario A (HR)** | *"How many casual leaves do employees get?"* | Grounded answer citing `leave-policy.txt` (12 days) | **PASSED** |
| **Scenario B (Finance)** | *"How does expense reimbursement work?"* | Grounded answer citing `expense-policy.pdf` (30-day receipt) | **PASSED** |
| **Scenario C (IT)** | *"What are the password requirements?"* | Grounded answer citing `it-security-guidelines.txt` (12+ chars, 90 days) | **PASSED** |
| **Scenario D (Unknown)** | *"What is Acme's private jet policy?"* | Grounding Guardrail blocks at Layer 3; clean refusal | **PASSED** |
| **Scenario E (Injection)** | *"Ignore all previous instructions..."* | Input Guardrail blocks at Layer 1; RAG/LLM not called | **PASSED** |
| **Scenario F (Cross-Domain)**| Leave rules and internet expense limits | Multi-source synthesis citing both HR and Finance docs | **PASSED** |

---

## 13. Customer Configuration Management

Acme Corporation can modify assistant settings dynamically without editing code or restarting services via `GET /api/config` and `POST /api/config`:

```json
{
  "organization": "Acme Corporation",
  "assistant_name": "Acme Knowledge Assistant",
  "domains": ["HR", "Finance", "IT"],
  "max_input_length": 2000,
  "rag_top_k": 3,
  "grounding_threshold": 0.70,
  "allow_unknown_answers": true,
  "show_sources": true
}
```

---

## 14. Running Locally

### Prerequisites
* Python 3.11+
* Node.js 18+ and npm
* PowerShell (Windows) or Bash (macOS/Linux)

### 1. Configure Environment
```powershell
# Copy the example environment file
cp .env.example server/.env
```
*(Optional: Add your `GEMINI_API_KEY` to `server/.env`. If omitted, the system operates with its deterministic local grounded fallback).*

### 2. Start Backend (FastAPI)
```powershell
cd "server"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start Frontend (React + Vite)
```powershell
cd "client"
npm run dev
```

Open `http://localhost:5173` in your browser.

### 4. Run Automated Test Suite
```powershell
cd "server"
.\venv\Scripts\python.exe test_phase8.py
```

---

## 15. Project Structure

```text
enterprise-ai-assistant/
├── client/                               # React + Vite Frontend
│   ├── src/
│   │   ├── api/                          # Modular API clients
│   │   │   ├── api.js                    # Base HTTP client with error formatting
│   │   │   ├── chatApi.js                # Chat and pipeline execution API
│   │   │   ├── configApi.js              # Customer configuration API
│   │   │   ├── documentsApi.js           # Document ingestion & management API
│   │   │   └── ragApi.js                 # Vector search & RAG stats API
│   │   ├── components/
│   │   │   ├── Chat/                     # ChatView, SourceList, RetrievedContext
│   │   │   ├── Dashboard/                # Operational telemetry & system gauges
│   │   │   ├── Fde/                      # FdeWorkspaceView, RequirementMapping
│   │   │   ├── Guardrails/               # Guardrails Control Center & Live Tester
│   │   │   ├── KnowledgeBase/            # Document upload & chunk inspector
│   │   │   ├── Pipeline/                 # 5-Stage visual pipeline indicator
│   │   │   └── RetrievalPlayground/      # Semantic search isolation console
│   │   ├── hooks/                        # useBackendStatus health check hook
│   │   ├── App.jsx                       # Root view router & role mode state
│   │   └── index.css                     # Design tokens & responsive stylesheet
│   └── package.json
│
├── server/                               # FastAPI + Python Backend
│   ├── app/
│   │   ├── guardrails/                   # Input & Output guardrail evaluators
│   │   ├── routes/                       # FastAPI router endpoints (chat, rag, config)
│   │   ├── services/                     # Business logic (retrieval, processor, llm)
│   │   ├── vectorstore/                  # ChromaDB vector store integration
│   │   └── main.py                       # FastAPI application entrypoint & CORS
│   ├── data/
│   │   ├── customer_config.json          # Persistent customer configuration
│   │   ├── processed/                    # Extracted document chunk metadata
│   │   └── uploads/                      # Uploaded PDF and TXT files
│   ├── requirements.txt                  # Python dependencies
│   └── test_phase8.py                    # Automated customer validation suite
│
├── knowledge-base/                       # Fictional demo policy documents
│   ├── employee-handbook.txt             # Acme HR General Guidelines
│   ├── leave-policy.txt                  # Acme Annual & Casual Leave Policy
│   ├── remote-work-policy.txt            # Acme Hybrid & Remote Flexibility Policy
│   ├── expense-policy.pdf                # Acme Travel & Expense Guidelines
│   └── it-security-guidelines.txt        # Acme IT Security & Password Rules
│
├── .env.example                          # Environment configuration template
├── PROJECT_SUMMARY.md                    # Executive pitch & project summary
├── WEBINAR_DEMO_SCRIPT.md                # 5-10 minute presentation script
└── WEBINAR_QA.md                         # Technical & FDE interview Q&A guide
```

---

## 16. Known Limitations

1. **Demo Role Simulation**: The role switcher (`Customer Demo Mode` vs `Engineering Mode`) is a client-side simulation designed to demonstrate the user experience contrast without requiring full enterprise Single Sign-On (SSO).
2. **Regex Input Guardrail**: The keyword-based injection detection runs in <1ms and catches common instruction overrides. Production systems should combine this with dedicated semantic classification models.
3. **Local Vector Storage**: Embedded ChromaDB operates locally on disk. Multi-region enterprise scaling would require a managed vector database cluster.
4. **Digital PDF Text Only**: PDF extraction parses digital text streams via `pypdf`. Image-only scanned PDFs require an additional OCR pre-processing layer.

---

## 17. Future Improvements

* **Enterprise Authentication**: Okta / Azure Active Directory SAML/OIDC integration.
* **Document-Level Access Control (ACLs)**: Enforce role-based retrieval permissions so employees only access documents permitted by their clearance level.
* **Semantic Caching**: Redis-backed embedding cache to instantly serve repeated policy questions at zero token cost.
* **Managed Vector DB**: Migration to Pinecone, Qdrant, or Milvus with automated backup and cross-region replication.
* **Continuous Red-Teaming**: Automated evaluation harnesses simulating evolving prompt injection attacks.
