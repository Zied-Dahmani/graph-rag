"""
Sample dataset: people, companies, and relationships.
"""

# People with their attributes
PEOPLE = [
    {"id": "p1", "name": "Elon Musk", "type": "person", "role": "CEO"},
    {"id": "p2", "name": "Sam Altman", "type": "person", "role": "CEO"},
    {"id": "p3", "name": "Satya Nadella", "type": "person", "role": "CEO"},
    {"id": "p4", "name": "Jensen Huang", "type": "person", "role": "CEO"},
    {"id": "p5", "name": "Demis Hassabis", "type": "person", "role": "CEO"},
]

# Companies with their attributes
COMPANIES = [
    {"id": "c1", "name": "Tesla", "type": "company", "industry": "automotive"},
    {"id": "c2", "name": "SpaceX", "type": "company", "industry": "aerospace"},
    {"id": "c3", "name": "OpenAI", "type": "company", "industry": "AI"},
    {"id": "c4", "name": "Microsoft", "type": "company", "industry": "technology"},
    {"id": "c5", "name": "NVIDIA", "type": "company", "industry": "semiconductors"},
    {"id": "c6", "name": "DeepMind", "type": "company", "industry": "AI"},
    {"id": "c7", "name": "Google", "type": "company", "industry": "technology"},
    {"id": "c8", "name": "Neuralink", "type": "company", "industry": "neurotechnology"},
]

# Relationships between entities
# Format: (source_id, target_id, relationship_type, attributes)
RELATIONSHIPS = [
    # Elon Musk's connections
    ("p1", "c1", "founded", {"year": 2003}),
    ("p1", "c2", "founded", {"year": 2002}),
    ("p1", "c8", "founded", {"year": 2016}),
    ("p1", "c1", "leads", {"role": "CEO"}),
    ("p1", "c2", "leads", {"role": "CEO"}),

    # Sam Altman's connections
    ("p2", "c3", "leads", {"role": "CEO"}),
    ("p2", "c3", "co_founded", {"year": 2015}),

    # Satya Nadella's connections
    ("p3", "c4", "leads", {"role": "CEO"}),

    # Jensen Huang's connections
    ("p4", "c5", "founded", {"year": 1993}),
    ("p4", "c5", "leads", {"role": "CEO"}),

    # Demis Hassabis's connections
    ("p5", "c6", "founded", {"year": 2010}),
    ("p5", "c6", "leads", {"role": "CEO"}),

    # Company relationships
    ("c4", "c3", "invested_in", {"amount": "$13B", "year": 2023}),
    ("c4", "c3", "partners_with", {"type": "strategic"}),
    ("c7", "c6", "acquired", {"year": 2014}),
    ("c5", "c3", "supplies", {"product": "GPUs"}),
    ("c5", "c4", "partners_with", {"type": "hardware"}),
]
