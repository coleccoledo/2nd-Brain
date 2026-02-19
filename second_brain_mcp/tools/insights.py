"""Insights tools — manage Claude-generated patterns and action items."""


def add_insight(supabase, title: str, summary: str, related_idea_ids: list[str] = [],
                tags: list[str] = [], category: str = None, action_item: str = "") -> dict:
    """Record a new insight."""
    data = {"title": title, "summary": summary, "related_idea_ids": related_idea_ids, "tags": tags}
    if category:
        data["category"] = category
    if action_item:
        data["action_item"] = action_item
    return supabase.table("insights").insert(data).execute().data[0]


def list_insights(supabase, category: str = None, unactioned_only: bool = False) -> list:
    """List insights, optionally filtered by category or action status."""
    q = supabase.table("insights").select("*")
    if category:
        q = q.eq("category", category)
    if unactioned_only:
        q = q.eq("is_actioned", False)
    return q.order("created_at", desc=True).execute().data


def mark_actioned(supabase, insight_id: str) -> dict:
    """Mark an insight's action item as completed."""
    return supabase.table("insights").update({"is_actioned": True}).eq("id", insight_id).execute().data[0]
