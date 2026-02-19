"""Relationships tools — manage idea cross-references."""


def link_ideas(supabase, source_id: str, target_id: str, relationship_type: str = "related", note: str = "") -> dict:
    """Create a relationship between two ideas."""
    return supabase.table("idea_relationships").insert({
        "source_id": source_id, "target_id": target_id,
        "relationship_type": relationship_type, "note": note
    }).execute().data[0]


def get_related_ideas(supabase, idea_id: str) -> list:
    """Fetch all ideas linked to a given idea."""
    fwd = supabase.table("idea_relationships").select("*, target:target_id(*)").eq("source_id", idea_id).execute().data
    rev = supabase.table("idea_relationships").select("*, source:source_id(*)").eq("target_id", idea_id).execute().data
    return fwd + rev


def remove_relationship(supabase, relationship_id: str) -> dict:
    """Remove a relationship between ideas."""
    return supabase.table("idea_relationships").delete().eq("id", relationship_id).execute().data
