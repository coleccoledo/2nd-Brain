"""Validation script: insert one test idea per category, test retrieval and linking."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

TEST_IDEAS = [
    {
        "title": "Weekly grocery run",
        "content": "Need eggs, milk, bread, and chicken thighs for the week.",
        "category": "groceries",
        "tags": ["weekly-list"],
        "metadata": {"checked": False, "store": "Costco"}
    },
    {
        "title": "Alma 32 — Faith as a seed",
        "content": "The analogy of faith as a seed that grows when nourished. Connects to patience and long-term growth.",
        "category": "religious_study",
        "tags": ["scripture-insight", "faith"],
        "metadata": {"scripture_ref": "Alma 32:21", "study_date": "2026-02-18"}
    },
    {
        "title": "AAPL earnings thesis",
        "content": "Apple services revenue continues to grow. Consider position sizing ahead of earnings.",
        "category": "finance_journal",
        "tags": ["equities", "portfolio"],
        "metadata": {"ticker": "AAPL", "asset_class": "equities", "status": "researching"}
    },
    {
        "title": "Dashboard dark mode toggle",
        "content": "Add a dark mode toggle to the Orion Dashboard settings page. Users have been requesting this.",
        "category": "product_ideas",
        "tags": ["feature-request", "ux-improvement"],
        "metadata": {"project": "Orion Dashboard", "target_user": "advisors", "feasibility": "medium"}
    },
    {
        "title": "Morning routine improvement",
        "content": "Try waking at 5:30 AM, cold shower, 20 min walk before breakfast. Track energy levels.",
        "category": "health_wellness",
        "tags": ["fitness", "sleep"],
        "metadata": {"body_system": "circadian", "goal": "consistent 5:30 AM wake"}
    },
    {
        "title": "Trikafta refill schedule",
        "content": "Next Trikafta refill due March 1. Need to confirm insurance pre-auth is still active.",
        "category": "cf_care",
        "tags": ["medication", "insurance"],
        "metadata": {"type": "medication", "provider": "CF clinic", "next_action": "call pharmacy March 1"}
    },
    {
        "title": "Smoked brisket recipe",
        "content": "225F for 12 hours, oak wood, salt and pepper rub. Wrap at 165F internal temp.",
        "category": "cooking_recipes",
        "tags": ["recipe", "technique"],
        "metadata": {"cuisine": "BBQ", "servings": 8, "cook_time_min": 720, "source": "personal"}
    },
    {
        "title": "Blue ocean strategy notes",
        "content": "Key insight: compete in uncontested market space rather than fighting over existing demand.",
        "category": "business_learning",
        "tags": ["strategy", "book-notes"],
        "metadata": {"type": "learning", "domain": "strategy", "source": "Blue Ocean Strategy book"}
    },
]


def main():
    print("=== Step 8: Validation ===\n")

    # 1. Insert one idea per category
    print("1. Inserting one test idea per category...\n")
    idea_ids = {}
    for idea in TEST_IDEAS:
        result = sb.table("ideas").insert(idea).execute()
        row = result.data[0]
        idea_ids[idea["category"]] = row["id"]
        print(f"   [{idea['category']}] {row['id']} — {idea['title']}")

    print(f"\n   Inserted {len(idea_ids)} ideas.\n")

    # 2. Retrieve by category
    print("2. Retrieving ideas by category...\n")
    for cat, iid in idea_ids.items():
        rows = sb.table("ideas").select("id, title").eq("category", cat).execute().data
        titles = [r["title"] for r in rows]
        print(f"   [{cat}] {len(rows)} idea(s): {titles}")

    # 3. Link two ideas and verify
    print("\n3. Testing idea linking...\n")
    src = idea_ids["finance_journal"]
    tgt = idea_ids["business_learning"]
    link = sb.table("idea_relationships").insert({
        "source_id": src,
        "target_id": tgt,
        "relationship_type": "informs",
        "note": "Investment thesis informed by blue ocean strategy thinking"
    }).execute().data[0]
    print(f"   Linked finance_journal -> business_learning (id: {link['id']})")

    # Verify forward lookup
    fwd = sb.table("idea_relationships").select("*, target:target_id(title)").eq("source_id", src).execute().data
    print(f"   Forward lookup from finance_journal: {len(fwd)} relationship(s)")
    for r in fwd:
        print(f"     -> {r['target']['title']} ({r['relationship_type']})")

    # Verify reverse lookup
    rev = sb.table("idea_relationships").select("*, source:source_id(title)").eq("target_id", tgt).execute().data
    print(f"   Reverse lookup from business_learning: {len(rev)} relationship(s)")
    for r in rev:
        print(f"     <- {r['source']['title']} ({r['relationship_type']})")

    # 4. Tag search across categories
    print("\n4. Cross-category tag search for 'strategy'...\n")
    results = sb.table("ideas").select("id, title, category, tags").overlaps("tags", ["strategy"]).execute().data
    for r in results:
        print(f"   [{r['category']}] {r['title']} — tags: {r['tags']}")

    print("\n=== VALIDATION COMPLETE ===")
    print(f"\nTest ideas left in database (not cleaned up — these are your starter data).")
    print("Idea IDs for reference:")
    for cat, iid in idea_ids.items():
        print(f"  {cat}: {iid}")


if __name__ == "__main__":
    main()
