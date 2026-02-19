"""Topics tools — manage the topics/tags registry."""


def add_topic(supabase, name: str, description: str = "", category: str = None) -> dict:
    """Add a new topic to the registry."""
    data = {"name": name}
    if description:
        data["description"] = description
    if category:
        data["category"] = category
    return supabase.table("topics").insert(data).execute().data[0]


def list_topics(supabase, category: str = None) -> list:
    """List all topics, optionally filtered by category."""
    q = supabase.table("topics").select("*")
    if category:
        q = q.eq("category", category)
    return q.order("name").execute().data


def search_topics(supabase, query: str) -> list:
    """Search topics by name (for autocomplete)."""
    return supabase.table("topics").select("*").ilike("name", f"%{query}%").execute().data
