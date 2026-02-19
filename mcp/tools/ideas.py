"""Ideas tools — core CRUD operations for the ideas table."""


def add_idea(supabase, title: str, content: str, category: str, tags: list[str] = [], metadata: dict = {}) -> dict:
    """Capture a new idea into the second brain."""
    return supabase.table("ideas").insert({
        "title": title, "content": content, "category": category,
        "tags": tags, "metadata": metadata
    }).execute().data[0]


def search_ideas(supabase, query: str, category: str = None, tags: list[str] = []) -> list:
    """Full-text search across ideas with optional category and tag filters."""
    q = supabase.table("ideas").select("*")
    if category:
        q = q.eq("category", category)
    if tags:
        q = q.overlaps("tags", tags)
    if query:
        q = q.text_search("content", query)
    return q.execute().data


def get_idea(supabase, idea_id: str) -> dict:
    """Retrieve a specific idea by ID."""
    return supabase.table("ideas").select("*").eq("id", idea_id).execute().data[0]


def update_idea(supabase, idea_id: str, fields: dict) -> dict:
    """Update any fields on an existing idea."""
    return supabase.table("ideas").update(fields).eq("id", idea_id).execute().data[0]


def list_by_category(supabase, category: str, limit: int = 20) -> list:
    """Browse recent ideas in a specific category."""
    return supabase.table("ideas").select("*").eq("category", category).order("created_at", desc=True).limit(limit).execute().data


def archive_idea(supabase, idea_id: str) -> dict:
    """Archive an idea (soft delete)."""
    return supabase.table("ideas").update({"is_archived": True}).eq("id", idea_id).execute().data[0]
