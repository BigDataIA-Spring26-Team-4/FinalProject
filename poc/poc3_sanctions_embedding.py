"""
POC 3: Sanctions Embedding + Semantic Search
==============================================
Downloads real OFAC sanctions data from OpenSanctions, extracts maritime
entities, embeds them with OpenAI, and demonstrates semantic search.

Prerequisites:
    1. Add to .env: OPENAI_API_KEY=your_key_here

Usage:
    poetry run python poc/poc3_sanctions_embedding.py
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENSANCTIONS_URL = "https://data.opensanctions.org/datasets/latest/us_ofac_cons/entities.ftm.json"

# Maritime-related schema types and keywords
MARITIME_KEYWORDS = ["vessel", "ship", "maritime", "shipping", "tanker", "cargo", "fleet", "port", "marine"]
VESSEL_SCHEMA = "Vessel"


def download_ofac_data() -> list[dict]:
    """Download OFAC consolidated sanctions from OpenSanctions."""
    import httpx

    print(f"  📥 Downloading from OpenSanctions OFAC dataset...")
    print(f"     URL: {OPENSANCTIONS_URL}")

    response = httpx.get(OPENSANCTIONS_URL, timeout=60, follow_redirects=True)
    response.raise_for_status()

    # Each line is a JSON entity
    entities = []
    for line in response.text.strip().split("\n"):
        try:
            entity = json.loads(line)
            entities.append(entity)
        except json.JSONDecodeError:
            continue

    print(f"  ✅ Downloaded {len(entities)} total OFAC entities")
    return entities


def extract_maritime_entities(entities: list[dict]) -> list[dict]:
    """Filter for maritime-related entities (vessels, shipping companies)."""
    maritime = []

    for entity in entities:
        schema = entity.get("schema", "")
        props = entity.get("properties", {})

        # Direct vessel entities
        if schema == VESSEL_SCHEMA:
            maritime.append({
                "id": entity.get("id", ""),
                "type": "vessel",
                "name": " | ".join(props.get("name", ["Unknown"])),
                "imo": " | ".join(props.get("imoNumber", [])),
                "mmsi": " | ".join(props.get("mmsi", [])),
                "flag": " | ".join(props.get("flag", [])),
                "tonnage": " | ".join(props.get("tonnage", [])),
                "description": _build_description(entity),
            })
            continue

        # Companies/organizations with maritime keywords in name or description
        name_str = " ".join(props.get("name", [])).lower()
        notes_str = " ".join(props.get("notes", [])).lower()
        combined = f"{name_str} {notes_str}"

        if any(kw in combined for kw in MARITIME_KEYWORDS):
            maritime.append({
                "id": entity.get("id", ""),
                "type": schema.lower(),
                "name": " | ".join(props.get("name", ["Unknown"])),
                "country": " | ".join(props.get("country", [])),
                "program": " | ".join(props.get("program", [])),
                "description": _build_description(entity),
            })

    return maritime


def _build_description(entity: dict) -> str:
    """Build a text description from entity properties for embedding."""
    props = entity.get("properties", {})
    parts = []

    name = " | ".join(props.get("name", []))
    if name:
        parts.append(f"Name: {name}")

    schema = entity.get("schema", "")
    parts.append(f"Type: {schema}")

    for field in ["imoNumber", "mmsi", "flag", "tonnage", "country", "program", "notes", "summary"]:
        values = props.get(field, [])
        if values:
            parts.append(f"{field}: {' | '.join(str(v) for v in values)}")

    return ". ".join(parts)


def embed_texts(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """Embed a batch of texts using OpenAI API."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Batch in groups of 100
    all_embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        response = client.embeddings.create(model=model, input=batch)
        for item in response.data:
            all_embeddings.append(item.embedding)

    return all_embeddings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import numpy as np

    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


def semantic_search(query: str, documents: list[dict], embeddings: list[list[float]], k: int = 5) -> list[dict]:
    """Search documents by embedding similarity."""
    query_embedding = embed_texts([query])[0]

    scores = []
    for i, doc_embedding in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, doc_embedding)
        scores.append((i, sim))

    scores.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, sim in scores[:k]:
        doc = documents[idx].copy()
        doc["similarity"] = round(sim, 4)
        results.append(doc)

    return results


def main():
    print(f"🚢 Maritime AI Sentinel — POC 3: Sanctions Embedding + Search")
    print(f"{'=' * 60}")

    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set in .env")
        sys.exit(1)

    # ── Step 1: Download OFAC data ──
    print(f"\n── Step 1: Download OFAC Sanctions Data ──")
    entities = download_ofac_data()

    # ── Step 2: Extract maritime entities ──
    print(f"\n── Step 2: Extract Maritime Entities ──")
    maritime = extract_maritime_entities(entities)
    print(f"  🚢 Found {len(maritime)} maritime-related entities")

    vessels = [e for e in maritime if e["type"] == "vessel"]
    others = [e for e in maritime if e["type"] != "vessel"]
    print(f"     Vessels:              {len(vessels)}")
    print(f"     Companies/Other:      {len(others)}")

    if not maritime:
        print("  ⚠️ No maritime entities found. Check OFAC dataset format.")
        sys.exit(1)

    # Show sample entities
    print(f"\n  Sample vessels:")
    for v in vessels[:5]:
        print(f"    {v['name'][:60]:<60s} IMO:{v.get('imo', 'N/A'):<12s} Flag:{v.get('flag', 'N/A')}")

    print(f"\n  Sample maritime companies:")
    for c in others[:5]:
        print(f"    {c['name'][:60]:<60s} Type:{c['type']}")

    # ── Step 3: Generate embeddings ──
    print(f"\n── Step 3: Generate OpenAI Embeddings ──")
    descriptions = [e["description"] for e in maritime]
    print(f"  📊 Embedding {len(descriptions)} documents with text-embedding-3-small...")

    embeddings = embed_texts(descriptions)
    print(f"  ✅ Generated {len(embeddings)} embeddings (dim={len(embeddings[0])})")

    # Estimate cost
    total_chars = sum(len(d) for d in descriptions)
    est_tokens = total_chars // 4  # rough estimate
    est_cost = est_tokens * 0.02 / 1_000_000
    print(f"  💰 Estimated cost: ~{est_tokens:,} tokens = ~${est_cost:.4f}")

    # ── Step 4: Semantic search demo ──
    print(f"\n── Step 4: Semantic Search Demo ──")

    test_queries = [
        "Iranian oil tanker sanctions",
        "North Korean shipping vessel",
        "Russian maritime company",
        "vessel flag Panama sanctions",
        "Syria cargo ship",
    ]

    for query in test_queries:
        print(f"\n  🔍 Query: \"{query}\"")
        results = semantic_search(query, maritime, embeddings, k=3)
        for i, r in enumerate(results):
            name = r["name"][:50]
            sim = r["similarity"]
            etype = r["type"]
            print(f"     [{i + 1}] {name:<50s} type:{etype:<10s} similarity:{sim:.4f}")

    # ── Step 5: Save results ──
    output_path = "poc/ofac_maritime_entities.json"
    with open(output_path, "w") as f:
        json.dump(maritime, f, indent=2)
    print(f"\n💾 Saved {len(maritime)} maritime entities to {output_path}")

    print(f"\n{'=' * 60}")
    print(f"✅ POC 3 complete — real OFAC data + OpenAI embeddings + semantic search")
    print(f"   This proves: sanctions data ingestion, embedding pipeline, RAG retrieval")
    print(f"   Next: Store in ChromaDB (Docker) with metadata filters for production")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
