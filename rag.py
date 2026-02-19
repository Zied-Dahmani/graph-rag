"""
Convert graph facts into textual context for LLM consumption.
"""

from typing import List, Dict, Any


def format_single_fact(fact: Dict[str, Any]) -> str:
    """
    Convert a single relationship fact into a natural language sentence.
    """
    source = fact["source_name"]
    target = fact["target_name"]
    relation = fact["relation"]
    attrs = fact.get("attributes", {})

    # Format based on relationship type
    templates = {
        "founded": f"{source} founded {target}",
        "co_founded": f"{source} co-founded {target}",
        "leads": f"{source} leads {target}",
        "works_at": f"{source} works at {target}",
        "invested_in": f"{source} invested in {target}",
        "acquired": f"{source} acquired {target}",
        "partners_with": f"{source} partners with {target}",
        "supplies": f"{source} supplies to {target}",
    }

    sentence = templates.get(relation, f"{source} {relation} {target}")

    # Add attribute details
    attr_parts = []
    if "year" in attrs:
        attr_parts.append(f"in {attrs['year']}")
    if "amount" in attrs:
        attr_parts.append(f"({attrs['amount']})")
    if "role" in attrs and relation == "leads":
        attr_parts.append(f"as {attrs['role']}")
    if "product" in attrs:
        attr_parts.append(f"({attrs['product']})")

    if attr_parts:
        sentence += " " + " ".join(attr_parts)

    return sentence


def build_context(facts: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> str:
    """
    Build a textual context from graph facts for LLM consumption.
    """
    if not facts:
        return "No relevant information found in the knowledge graph."

    # Group facts by subject
    context_parts = []

    # Add header about what entities were found
    if entities:
        entity_names = [e["name"] for e in entities]
        context_parts.append(f"Information about: {', '.join(entity_names)}")
        context_parts.append("")

    # Convert facts to sentences
    context_parts.append("Known facts:")
    for fact in facts:
        sentence = format_single_fact(fact)
        context_parts.append(f"- {sentence}")

    return "\n".join(context_parts)


def format_traversal_summary(traversal_data: Dict[str, Any]) -> str:
    """
    Format traversal information for display to the user.
    """
    parts = []
    parts.append(f"Started from: {traversal_data.get('start_node', 'unknown')}")
    parts.append(f"Visited nodes: {', '.join(traversal_data.get('visited_nodes', []))}")
    parts.append(f"Facts discovered: {len(traversal_data.get('facts', []))}")
    return "\n".join(parts)
