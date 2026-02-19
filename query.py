"""
Entity detection logic for extracting entities from user questions.
"""

from typing import List, Dict, Any
import re


# Known entity names for simple matching
KNOWN_ENTITIES = [
    # People
    "elon musk", "elon", "musk",
    "sam altman", "sam", "altman",
    "satya nadella", "satya", "nadella",
    "jensen huang", "jensen", "huang",
    "demis hassabis", "demis", "hassabis",
    # Companies
    "tesla",
    "spacex",
    "openai",
    "microsoft",
    "nvidia",
    "deepmind",
    "google",
    "neuralink",
]

# Map short names to full names for better matching
NAME_ALIASES = {
    "elon": "elon musk",
    "musk": "elon musk",
    "sam": "sam altman",
    "altman": "sam altman",
    "satya": "satya nadella",
    "nadella": "satya nadella",
    "jensen": "jensen huang",
    "huang": "jensen huang",
    "demis": "demis hassabis",
    "hassabis": "demis hassabis",
}


def detect_entities(question: str) -> List[Dict[str, Any]]:
    """
    Detect entities mentioned in the user's question.
    Returns a list of detected entities with their types.
    """
    question_lower = question.lower()
    detected = []
    seen_names = set()

    # Sort by length (longest first) to match full names before partial
    sorted_entities = sorted(KNOWN_ENTITIES, key=len, reverse=True)

    for entity in sorted_entities:
        if entity in question_lower:
            # Resolve aliases to full names
            full_name = NAME_ALIASES.get(entity, entity)

            if full_name not in seen_names:
                seen_names.add(full_name)

                # Determine entity type
                entity_type = "person" if any(
                    name in full_name for name in ["musk", "altman", "nadella", "huang", "hassabis"]
                ) else "company"

                detected.append({
                    "name": full_name.title(),
                    "type": entity_type,
                    "matched_text": entity,
                })

    return detected


def extract_relationship_intent(question: str) -> List[str]:
    """
    Try to understand what kind of relationships the user is asking about.
    """
    question_lower = question.lower()
    intents = []

    relationship_keywords = {
        "founded": ["found", "start", "creat", "establish"],
        "leads": ["lead", "run", "ceo", "head", "manage"],
        "works_at": ["work", "employ"],
        "invested_in": ["invest", "fund", "money"],
        "acquired": ["acquir", "bought", "purchase"],
        "partners_with": ["partner", "collaborat", "work with"],
        "supplies": ["supply", "provide", "sell"],
    }

    for relation, keywords in relationship_keywords.items():
        if any(kw in question_lower for kw in keywords):
            intents.append(relation)

    return intents


def analyze_question(question: str) -> Dict[str, Any]:
    """
    Full analysis of the user's question.
    """
    return {
        "original_question": question,
        "detected_entities": detect_entities(question),
        "relationship_intents": extract_relationship_intent(question),
    }
