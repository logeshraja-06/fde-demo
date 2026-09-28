# Enterprise AI Knowledge Assistant — Project Summary

**Forward Deployed Engineering (FDE) Customer Implementation Simulation**

---

## 30-Second Elevator Pitch

> *"The Enterprise AI Knowledge Assistant is a production-grade demonstration of how Forward Deployed Engineers take real customer problems—like employee confusion over company policies and fears of AI hallucinations—and engineer verifiable, grounded AI solutions. By wrapping semantic vector retrieval in a 3-layer deterministic safety perimeter, the system guarantees that answers are sourced strictly from approved company documentation, halts execution before calling the LLM when evidence is insufficient, intercepts prompt injections instantly, and provides full transparency through customer feedback loops and live pipeline observability."*

---

## 2-Minute Executive Summary

> *"Traditional enterprise AI pilots frequently fail because out-of-the-box large language models hallucinate policies, vulnerable interfaces leak system instructions, and employees do not trust unverified answers.
>
> *In this implementation for **Acme Corporation**, we simulated the full Forward Deployed Engineering lifecycle to deliver an internal policy knowledge assistant covering HR, Finance, and IT documentation.
>
> *Rather than treating AI as an unpredictable black box, we engineered an end-to-end **5-Stage Defense-in-Depth Pipeline**:
> 1. An **Input Guardrail** evaluates character boundaries and blocks prompt injections in under 1 millisecond.
> 2. A **RAG Retrieval Engine** powered by SentenceTransformers (`all-MiniLM-L6-v2`) and persistent ChromaDB vectors retrieves top matching policy chunks partitioned by departmental domain.
> 3. A **Grounding Guardrail** mathematically measures cosine similarity against a strict threshold (0.70). If evidence is lacking, the pipeline stops immediately—preventing hallucination and saving API costs.
> 4. A **Context-Restricted LLM** synthesizes answers solely from demarcated knowledge chunks.
> 5. An **Output Guardrail** validates verified citations and screens against internal data leakage.
>
> *Crucially, we incorporated the complete FDE customer engagement model: runtime customer configuration without code changes (`customer_config.json`), responsive role-based view simulation (Customer Demo Mode vs. Engineering Mode), an automated validation suite, and a visible customer feedback loop that drove the system through 5 iterative versions to final stakeholder acceptance."*

---

## Project Specification Overview

| Attribute | Details |
| :--- | :--- |
| **Project Name** | Enterprise AI Knowledge Assistant |
| **Fictional Customer** | Acme Corporation |
| **Operational Domains** | HR (Leave, Handbook, Remote Work), Finance (Expense, Travel), IT (Security, Password) |
| **Frontend Stack** | React (Vite) + Tailwind CSS + Vanilla CSS Tokens + Responsive Grid |
| **Backend Stack** | Python 3.11+ + FastAPI + Uvicorn + Pydantic v2 |
| **Embedding Engine** | `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dimensional dense vectors) |
| **Vector Store** | ChromaDB (Local persistent vector database with domain metadata filtering) |
| **Generative LLM** | Google Gemini 2.5 Flash / Gemini 1.5 Flash + Local Deterministic Grounded Fallback |
| **Safety Perimeter** | 3-Layer Guardrails: Input Defense → Grounding Evidence Verification → Output Validation |
| **Observability** | 5-Stage Visual Pipeline Tracing, Real-Time Audit Telemetry, Execution Duration Metrics |
| **FDE Workspace** | 7-Stage Lifecycle Tracker, Requirements Mapping, Feedback Loop, Iteration History, Sign-off |

---

## Architectural Breakdown

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
                 ┌─────────────────────┴─────────────────────┐
                 │                                           │
                 ▼                                           ▼
       [ KNOWLEDGE INGESTION ]                     [ QUERY EXECUTION ]
        PDF / TXT Document                           User Query
                 │                                           │
                 ▼                                           ▼
       Extraction & Cleaning                       [ Layer 1: Input Guardrail ]
                 │                                   (Empty / Length / Injection)
                 ▼                                           │ (Pass)
       Sliding-Window Chunking                               ▼
                 │                                 [ Layer 2: RAG Retrieval ]
                 ▼                                   (Embed query & search ChromaDB)
       SentenceTransformer Embed                             │
                 │                                           ▼
                 ▼                                 [ Layer 3: Grounding Guardrail ]
       ChromaDB Vector Store                         (Cosine Similarity Threshold 0.70)
        (Metadata: domain tag)                               │ (Sufficient Evidence)
                                                             ▼
                                                   [ Layer 4: Context-Restricted LLM ]
                                                     (Google Gemini / Local Synthesizer)
                                                             │
                                                             ▼
                                                   [ Layer 5: Output Guardrail ]
                                                     (Citation requirement & format check)
                                                             │
                                                             ▼
                                                   Answer + Provenance Sources
                                                             │
                                                             ▼
                                                   5-Stage Pipeline Telemetry Log
```

---

## The Core FDE Equation

$$\text{FDE} = \text{Customer Problem} + \text{Solution Design} + \text{Implementation} + \text{Testing} + \text{Feedback Loop} + \text{Rapid Iteration} + \text{Customer Acceptance}$$

RAG, ChromaDB, and Gemini are technical building blocks. FDE is the customer-aligned discipline of tailoring, validating, iterating, and handing off a trusted AI system to solve real business needs.

---

## Known Limitations & Production Roadmap

1. **Local Embedded Vector Store**: Prototype runs embedded ChromaDB on disk. Production scaling requires migration to managed vector databases (Pinecone, Qdrant, or Milvus) with multi-node replication.
2. **Regex-Based Input Guardrail**: Fast (<1ms) first-line perimeter defense; enterprise scale would complement this with dedicated semantic classifier models and ongoing red-teaming.
3. **Role-Based View Simulation**: Header view switcher is explicitly a client-side demo simulation for evaluation purposes. Production requires enterprise SSO (Okta, Azure AD, SAML).
4. **Document Access Control Lists (ACLs)**: In this version, all employees in the demo can query all uploaded policies. Multi-tier enterprise deployments would enforce departmental ACLs at the vector query level.

---

## Verification & Execution Commands

### Backend:
```powershell
cd "server"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend:
```powershell
cd "client"
npm run dev
```

### Automated Phase 8 Test Suite:
```powershell
cd "server"
.\venv\Scripts\python.exe test_phase8.py
```
