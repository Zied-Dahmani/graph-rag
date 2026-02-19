# Graph RAG Demo with LangGraph

A CLI app that answers questions using a knowledge graph and LangGraph workflow orchestration.

## How it works

Unlike document-based RAG that searches text chunks, Graph RAG traverses explicit relationships in a knowledge graph:

```
Question → Entity Detection → Node Retrieval → Graph Traversal → Context Building → LLM Answer
```

Each step is a node in the LangGraph workflow, with state flowing between them.

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your-api-key"
```

## Usage

```bash
python3 main.py
```

Example output:

```
🔍 STEP 1: Entity Detection
   Question: What companies did Elon Musk found?
   Detected 1 entities:
   - Elon Musk (person)

📊 STEP 2: Node Retrieval
   Found: Elon Musk (ID: p1)

🔗 STEP 3: Graph Traversal
   Traversing from: Elon Musk
   - Visited 4 nodes
   - Found 5 relationships
     → Elon Musk --[founded]--> Tesla
     → Elon Musk --[founded]--> SpaceX
     → Elon Musk --[founded]--> Neuralink

📝 STEP 4: Context Building
   Unique facts collected: 5

🤖 STEP 5: Answer Generation (Groq LLM)
   ✅ LLM response generated successfully

📌 FINAL ANSWER:
Tesla (2003), SpaceX (2002), and Neuralink (2016).
```

## Project Structure

| File | Description |
|------|-------------|
| `main.py` | CLI interface |
| `graph.py` | LangGraph workflow definition |
| `kg.py` | Knowledge graph creation + traversal (networkx) |
| `query.py` | Entity detection logic |
| `rag.py` | Convert graph facts to context |
| `data.py` | Sample dataset |

## Sample Data

- **People**: Elon Musk, Sam Altman, Satya Nadella, Jensen Huang, Demis Hassabis
- **Companies**: Tesla, SpaceX, OpenAI, Microsoft, NVIDIA, DeepMind, Google, Neuralink
- **Relationships**: founded, leads, invested_in, acquired, partners_with, supplies
