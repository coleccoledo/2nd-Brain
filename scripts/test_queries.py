"""Test script to verify Supabase connection and basic CRUD operations."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def main():
    print("=== Second Brain — Connection & CRUD Test ===\n")

    # 1. Connect
    print("1. Connecting to Supabase...")
    sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print(f"   Connected to {SUPABASE_URL}\n")

    # 2. Insert a test idea
    print("2. Inserting test idea...")
    result = sb.table("ideas").insert({
        "title": "Test Idea",
        "content": "This is a test idea to verify CRUD operations.",
        "category": "business_learning",
        "tags": ["test", "setup"],
        "metadata": {"type": "learning", "domain": "testing"}
    }).execute()
    idea = result.data[0]
    idea_id = idea["id"]
    print(f"   Created idea: {idea_id}\n")

    # 3. Read it back
    print("3. Reading idea back...")
    fetched = sb.table("ideas").select("*").eq("id", idea_id).execute().data[0]
    assert fetched["title"] == "Test Idea", "Title mismatch!"
    assert fetched["category"] == "business_learning", "Category mismatch!"
    print(f"   Read OK: '{fetched['title']}' in {fetched['category']}\n")

    # 4. Update it
    print("4. Updating idea...")
    updated = sb.table("ideas").update({"title": "Test Idea (Updated)"}).eq("id", idea_id).execute().data[0]
    assert updated["title"] == "Test Idea (Updated)", "Update failed!"
    print(f"   Updated title: '{updated['title']}'\n")

    # 5. Search (full-text)
    print("5. Full-text search for 'verify'...")
    results = sb.table("ideas").select("*").text_search("content", "verify").execute().data
    found = any(r["id"] == idea_id for r in results)
    print(f"   Found test idea in search results: {found}\n")

    # 6. Test topics table
    print("6. Inserting test topic...")
    topic = sb.table("topics").insert({
        "name": "_test_topic",
        "description": "Temporary test topic",
        "category": "business_learning"
    }).execute().data[0]
    topic_id = topic["id"]
    print(f"   Created topic: {topic_id}\n")

    # 7. Cleanup
    print("7. Cleaning up test data...")
    sb.table("topics").delete().eq("id", topic_id).execute()
    sb.table("ideas").delete().eq("id", idea_id).execute()
    print("   Cleaned up.\n")

    print("=== ALL TESTS PASSED ===")


if __name__ == "__main__":
    main()
