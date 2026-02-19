"""
LangGraph workflow definition for the Graph RAG pipeline.
Orchestrates: entity detection → node retrieval → traversal → context building → answer generation
"""

import os
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator

from kg import create_knowledge_graph, get_node_by_name, traverse_from_node, get_graph_stats
from query import analyze_question
from rag import build_context, format_single_fact

# LLM Integration with Groq
LLM_CLIENT = None

def init_llm():
    """Initialize the Groq LLM client."""
    global LLM_CLIENT

    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            LLM_CLIENT = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
            )
            return True
        except ImportError:
            print("Warning: langchain-groq not installed. Run: pip install langchain-groq")
    else:
        print("Warning: GROQ_API_KEY not set. LLM features disabled.")

    return False

# Initialize LLM on module load
LLM_AVAILABLE = init_llm()


# Define the state schema for our workflow
class GraphRAGState(TypedDict):
    """State that flows through the Graph RAG pipeline."""
    question: str
    detected_entities: List[Dict[str, Any]]
    matched_nodes: List[Dict[str, Any]]
    traversal_results: List[Dict[str, Any]]
    context: str
    answer: str
    debug_logs: Annotated[List[str], operator.add]


# Create the knowledge graph once (shared across invocations)
KG = create_knowledge_graph()


def detect_entities_node(state: GraphRAGState) -> Dict[str, Any]:
    """
    Node 1: Detect entities in the user's question.
    """
    question = state["question"]
    analysis = analyze_question(question)
    entities = analysis["detected_entities"]

    logs = [
        "\n🔍 STEP 1: Entity Detection",
        f"   Question: {question}",
        f"   Detected {len(entities)} entities:",
    ]
    for e in entities:
        logs.append(f"   - {e['name']} ({e['type']})")

    if not entities:
        logs.append("   ⚠️  No entities detected")

    return {
        "detected_entities": entities,
        "debug_logs": logs,
    }


def retrieve_nodes_node(state: GraphRAGState) -> Dict[str, Any]:
    """
    Node 2: Retrieve matching nodes from the knowledge graph.
    """
    entities = state["detected_entities"]
    matched_nodes = []

    logs = ["\n📊 STEP 2: Node Retrieval"]

    for entity in entities:
        matches = get_node_by_name(KG, entity["name"])
        for node_id, node_data in matches:
            matched_nodes.append({
                "node_id": node_id,
                "data": node_data,
                "matched_entity": entity["name"],
            })
            logs.append(f"   Found: {node_data.get('name')} (ID: {node_id})")

    if not matched_nodes:
        logs.append("   ⚠️  No matching nodes found in graph")
    else:
        logs.append(f"   Total nodes matched: {len(matched_nodes)}")

    return {
        "matched_nodes": matched_nodes,
        "debug_logs": logs,
    }


def traverse_relationships_node(state: GraphRAGState) -> Dict[str, Any]:
    """
    Node 3: Traverse relationships to gather connected facts.
    """
    matched_nodes = state["matched_nodes"]
    all_traversals = []

    logs = ["\n🔗 STEP 3: Graph Traversal"]

    for node in matched_nodes:
        node_id = node["node_id"]
        traversal = traverse_from_node(KG, node_id, depth=1)
        all_traversals.append(traversal)

        logs.append(f"   Traversing from: {node['data'].get('name')}")
        logs.append(f"   - Visited {len(traversal['visited_nodes'])} nodes")
        logs.append(f"   - Found {len(traversal['facts'])} relationships")

        # Show the connections followed
        for fact in traversal["facts"][:5]:  # Limit display
            logs.append(f"     → {fact['source_name']} --[{fact['relation']}]--> {fact['target_name']}")

    return {
        "traversal_results": all_traversals,
        "debug_logs": logs,
    }


def build_context_node(state: GraphRAGState) -> Dict[str, Any]:
    """
    Node 4: Convert graph data into textual context.
    """
    traversals = state["traversal_results"]
    entities = state["detected_entities"]

    # Collect all unique facts
    all_facts = []
    seen = set()
    for traversal in traversals:
        for fact in traversal.get("facts", []):
            key = (fact["source"], fact["target"], fact["relation"])
            if key not in seen:
                seen.add(key)
                all_facts.append(fact)

    context = build_context(all_facts, entities)

    logs = [
        "\n📝 STEP 4: Context Building",
        f"   Unique facts collected: {len(all_facts)}",
        "   Context preview:",
    ]
    for line in context.split("\n")[:8]:
        logs.append(f"   | {line}")

    return {
        "context": context,
        "debug_logs": logs,
    }


def generate_answer_node(state: GraphRAGState) -> Dict[str, Any]:
    """
    Node 5: Generate the final answer using Groq LLM.
    """
    context = state["context"]
    question = state["question"]

    logs = ["\n🤖 STEP 5: Answer Generation (Groq LLM)"]

    if "No relevant information" in context:
        answer = "I couldn't find any relevant information in the knowledge graph to answer your question."
        logs.append("   No context available, skipping LLM")
    elif LLM_CLIENT is None:
        answer = f"""[LLM not available - showing raw context]

{context}

Set GROQ_API_KEY environment variable to enable LLM responses."""
        logs.append("   ⚠️  LLM not available (missing API key or package)")
    else:
        # Build the prompt for the LLM
        prompt = f"""You are a helpful assistant answering questions based on a knowledge graph.
Use ONLY the provided context to answer. Be concise and direct.
If the context doesn't contain enough information, say so.

Context from knowledge graph:
{context}

Question: {question}

Answer:"""

        try:
            response = LLM_CLIENT.invoke(prompt)
            answer = response.content
            logs.append("   ✅ LLM response generated successfully")
        except Exception as e:
            answer = f"Error generating response: {e}\n\nRaw context:\n{context}"
            logs.append(f"   ❌ LLM error: {e}")

    return {
        "answer": answer,
        "debug_logs": logs,
    }


def create_graph_rag_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for Graph RAG.
    """
    # Initialize the workflow with our state schema
    workflow = StateGraph(GraphRAGState)

    # Add nodes to the workflow
    workflow.add_node("detect_entities", detect_entities_node)
    workflow.add_node("retrieve_nodes", retrieve_nodes_node)
    workflow.add_node("traverse_relationships", traverse_relationships_node)
    workflow.add_node("build_context", build_context_node)
    workflow.add_node("generate_answer", generate_answer_node)

    # Define the edges (flow between nodes)
    workflow.set_entry_point("detect_entities")
    workflow.add_edge("detect_entities", "retrieve_nodes")
    workflow.add_edge("retrieve_nodes", "traverse_relationships")
    workflow.add_edge("traverse_relationships", "build_context")
    workflow.add_edge("build_context", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow


def run_graph_rag(question: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Run the Graph RAG workflow on a question.
    """
    workflow = create_graph_rag_workflow()
    app = workflow.compile()

    # Initial state
    initial_state = {
        "question": question,
        "detected_entities": [],
        "matched_nodes": [],
        "traversal_results": [],
        "context": "",
        "answer": "",
        "debug_logs": [],
    }

    # Run the workflow
    final_state = app.invoke(initial_state)

    # Print debug logs if verbose
    if verbose:
        print("\n" + "="*60)
        print("GRAPH RAG PIPELINE EXECUTION")
        print("="*60)
        for log in final_state["debug_logs"]:
            print(log)
        print("\n" + "="*60)

    return final_state
