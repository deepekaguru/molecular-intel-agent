# 🧬 Molecular Intel — Multi-Agent Clinical Treatment Recommendation System

A production-grade multi-agent AI system that recommends oncology treatments based on patient genomic profiles. Built with security-first design, human-in-the-loop controls, and a self-improving knowledge graph.

> **Wipro Forward Deployed Engineer Pre-screening Assignment**  
> Deepeka Gurunathan | April 2026

---

## 🎯 Problem Statement

Given a cancer patient's genomic mutation profile, recommend the most effective treatments by combining knowledge graph traversal, clinical literature retrieval, and ML-based ranking — with full security guardrails and oncologist approval before any decision is logged.

---

## 🏗️ Architecture — 5-Agent Sequential Pipeline

```
Clinical Notes → [Agent 1] → [Agent 2] → [Agent 3] → [Agent 4] → [Agent 5] → Ranked Treatments
                 Extractor   KG Query     RAG          XGBoost     Rationale
                 (GPT-4o)    (Neo4j)      (ChromaDB)   (ML Rank)   (GPT-4o)
```

| Agent | Role | Technology |
|-------|------|------------|
| Agent 1 — Feature Extractor | Extracts genomic features from clinical notes | GPT-4o-mini |
| Agent 2 — Knowledge Graph | Queries gene→drug relationships | Neo4j Aura (Cypher) |
| Agent 3 — RAG Retriever | Retrieves supporting clinical literature | ChromaDB + embeddings |
| Agent 4 — ML Ranker | Scores and ranks treatments | XGBoost |
| Agent 5 — Rationale Generator | Generates clinical reasoning narrative | GPT-4o-mini |

**Communication pattern:** Shared state dictionary passed sequentially through agents  
**Orchestration:** Custom Python pipeline (no framework overhead)

---

## 🔒 Security & Guardrails

### 3-Layer Security Architecture

**Layer 1 — Input Validation**
- Patient ID format validation
- Age range validation  
- Prompt injection detection in clinical notes
- Automatic halt on suspicious patterns

**Layer 2 — Human-in-the-Loop Consent Gate**
- Explicit user consent required before pipeline execution
- Session-state persisted checkbox + confirmation button
- No consent = no pipeline, no exceptions

**Layer 3 — LLM Guardrails + Action Control**
- `ActionController` authorizes every LLM call
- `LLMGuardrails` enforces role constraints and output filtering
- `DataSecurityHandler` masks PII before data reaches external APIs
- All security events logged via `secure_log()`

### Key Security Design Decisions
- Only **Agent 5** calls an LLM — minimizes attack surface, cost, and hallucination risk
- **XGBoost** used for ranking (not LLM) — deterministic, auditable, explainable
- Oncologist must **approve treatments** before anything is written to the knowledge graph

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Agents | Python 3.10, custom orchestration |
| LLM | GPT-4o-mini (OpenAI API) |
| Knowledge Graph | Neo4j Aura |
| Vector Store | ChromaDB |
| ML Ranking | XGBoost |
| Security Layer | Custom guardrails (4 modules) |
| UI | Streamlit |
| Deployment | Google Cloud Platform (VM) |

---

## 📁 Project Structure

```
molecular-intel-agent/
├── agents/
│   ├── agent1_extractor.py      # Genomic feature extraction (GPT-4o-mini)
│   ├── agent2_graph.py          # Neo4j knowledge graph query
│   ├── agent3_rag.py            # ChromaDB literature retrieval
│   ├── agent4_ranker.py         # XGBoost treatment ranking
│   └── agent5_rationale.py      # Clinical rationale generation (GPT-4o-mini)
├── security/
│   ├── input_validator.py       # Input validation + prompt injection detection
│   ├── llm_guardrails.py        # LLM role constraints + output filtering
│   ├── data_security.py         # PII masking + secure logging
│   └── action_control.py        # Action authorization controller
├── dashboard/
│   └── app.py                   # Streamlit UI
├── models/
│   └── xgboost_ranker.pkl       # Trained XGBoost model
├── utils/
│   └── security_guardrails.py   # Shared guardrail utilities
├── load_graph.py                # Neo4j graph seeding script
└── README.md
```

---

## 🚀 Running the System

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_password
```

### Seed the Knowledge Graph
```bash
python load_graph.py
```

### Launch the Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🔄 How It Works — End to End

1. **Clinician** enters patient ID, age, cancer type, and gene mutations in the sidebar
2. **Consent gate** requires explicit acknowledgment before any AI runs
3. **Agent 1** extracts structured genomic features from clinical notes
4. **Agent 2** queries Neo4j for gene→drug matches with historical response rates
5. **Agent 3** retrieves supporting literature from ChromaDB vector store
6. **Agent 4** ranks treatments using XGBoost ML model
7. **Agent 5** generates a clinical rationale narrative using GPT-4o-mini
8. **Oncologist** reviews recommendations, selects a treatment, adds notes
9. **Approved treatment** is written back to Neo4j — system learns from real decisions

---


## 📊 Neo4j Knowledge Graph Schema

```cypher
(Gene)-[:HAS_MUTATION]->(Mutation)-[:TARGETED_BY]->(Drug)-[:HAS_OUTCOME]->(Outcome)
(Patient)-[:RECEIVED_TREATMENT]->(Drug)
```

The graph self-improves — every oncologist approval adds a `RECEIVED_TREATMENT` edge, enriching future recommendations for similar patient profiles.

---
