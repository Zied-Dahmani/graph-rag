"""
Knowledge Graph creation and traversal using networkx.
"""

import networkx as nx
from typing import List, Dict, Any, Tuple
from data import PEOPLE, COMPANIES, RELATIONSHIPS


def create_knowledge_graph() -> nx.MultiDiGraph:
    """
    Create a knowledge graph from the sample data.
    Uses MultiDiGraph to allow multiple edges between nodes.
    """
    G = nx.MultiDiGraph()

    # Add people nodes
    for person in PEOPLE:
        G.add_node(person["id"], **person)

    # Add company nodes
    for company in COMPANIES:
        G.add_node(company["id"], **company)

    # Add relationships as edges
    for source, target, rel_type, attrs in RELATIONSHIPS:
        G.add_edge(source, target, relation=rel_type, **attrs)

    return G


def get_node_by_name(G: nx.MultiDiGraph, name: str) -> List[Tuple[str, Dict]]:
    """
    Find nodes by name (case-insensitive partial match).
    Returns list of (node_id, node_data) tuples.
    """
    matches = []
    name_lower = name.lower()

    for node_id, data in G.nodes(data=True):
        node_name = data.get("name", "").lower()
        if name_lower in node_name or node_name in name_lower:
            matches.append((node_id, data))

    return matches


def get_node_relationships(G: nx.MultiDiGraph, node_id: str) -> List[Dict[str, Any]]:
    """
    Get all relationships for a given node (both outgoing and incoming).
    """
    relationships = []

    # Outgoing edges
    for _, target, data in G.out_edges(node_id, data=True):
        target_data = G.nodes[target]
        relationships.append({
            "direction": "outgoing",
            "source": node_id,
            "source_name": G.nodes[node_id].get("name"),
            "target": target,
            "target_name": target_data.get("name"),
            "relation": data.get("relation"),
            "attributes": {k: v for k, v in data.items() if k != "relation"}
        })

    # Incoming edges
    for source, _, data in G.in_edges(node_id, data=True):
        source_data = G.nodes[source]
        relationships.append({
            "direction": "incoming",
            "source": source,
            "source_name": source_data.get("name"),
            "target": node_id,
            "target_name": G.nodes[node_id].get("name"),
            "relation": data.get("relation"),
            "attributes": {k: v for k, v in data.items() if k != "relation"}
        })

    return relationships


def traverse_from_node(G: nx.MultiDiGraph, node_id: str, depth: int = 1) -> Dict[str, Any]:
    """
    Traverse the graph from a starting node up to a certain depth.
    Returns the subgraph data with all discovered facts.
    """
    visited = set()
    facts = []
    to_visit = [(node_id, 0)]

    while to_visit:
        current_id, current_depth = to_visit.pop(0)

        if current_id in visited or current_depth > depth:
            continue

        visited.add(current_id)

        # Get relationships for current node
        rels = get_node_relationships(G, current_id)
        facts.extend(rels)

        # Add neighbors to visit queue
        if current_depth < depth:
            for neighbor in list(G.successors(current_id)) + list(G.predecessors(current_id)):
                if neighbor not in visited:
                    to_visit.append((neighbor, current_depth + 1))

    # Remove duplicate facts
    unique_facts = []
    seen = set()
    for fact in facts:
        key = (fact["source"], fact["target"], fact["relation"])
        if key not in seen:
            seen.add(key)
            unique_facts.append(fact)

    return {
        "start_node": node_id,
        "visited_nodes": list(visited),
        "facts": unique_facts
    }


def get_graph_stats(G: nx.MultiDiGraph) -> Dict[str, int]:
    """Get basic statistics about the knowledge graph."""
    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "people": len([n for n, d in G.nodes(data=True) if d.get("type") == "person"]),
        "companies": len([n for n, d in G.nodes(data=True) if d.get("type") == "company"]),
    }
