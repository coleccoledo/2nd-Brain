from fastmcp import FastMCP
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
mcp = FastMCP("second-brain")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

@mcp.tool()
def add_idea(title: str, content: str, category: str, tags: list[str] = [], metadata: dict = {}) -> dict:
    """Capture a new idea into the second brain."""
    return supabase.table("ideas").insert({
        "title": title, "content": content, "category": category,
        "tags": tags, "metadata": metadata
    }).execute().data[0]

@mcp.tool()
def search_ideas(query: str, category: str = None, tags: list[str] = []) -> list:
    """Full-text search across ideas with optional category and tag filters."""
    q = supabase.table("ideas").select("*")
    if category:
        q = q.eq("category", category)
    if tags:
        q = q.overlaps("tags", tags)
    if query:
        q = q.text_search("content", query)
    return q.execute().data

@mcp.tool()
def get_idea(idea_id: str) -> dict:
    """Retrieve a specific idea by ID."""
    return supabase.table("ideas").select("*").eq("id", idea_id).execute().data[0]

@mcp.tool()
def update_idea(idea_id: str, fields: dict) -> dict:
    """Update any fields on an existing idea."""
    return supabase.table("ideas").update(fields).eq("id", idea_id).execute().data[0]

@mcp.tool()
def get_related_ideas(idea_id: str) -> list:
    """Fetch all ideas linked to a given idea."""
    fwd = supabase.table("idea_relationships").select("*, target:target_id(*)").eq("source_id", idea_id).execute().data
    rev = supabase.table("idea_relationships").select("*, source:source_id(*)").eq("target_id", idea_id).execute().data
    return fwd + rev

@mcp.tool()
def link_ideas(source_id: str, target_id: str, relationship_type: str = "related", note: str = "") -> dict:
    """Create a relationship between two ideas."""
    return supabase.table("idea_relationships").insert({
        "source_id": source_id, "target_id": target_id,
        "relationship_type": relationship_type, "note": note
    }).execute().data[0]

@mcp.tool()
def list_by_category(category: str, limit: int = 20) -> list:
    """Browse recent ideas in a specific category."""
    return supabase.table("ideas").select("*").eq("category", category).order("created_at", desc=True).limit(limit).execute().data

@mcp.tool()
def archive_idea(idea_id: str) -> dict:
    """Archive an idea (soft delete)."""
    return supabase.table("ideas").update({"is_archived": True}).eq("id", idea_id).execute().data[0]

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
    else:
        mcp.run()
