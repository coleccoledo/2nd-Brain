"""
Cole's Second Brain — MCP Server

Every tool description is the sole source of context for Claude on mobile.
Descriptions must be thorough enough that Claude can operate without CLAUDE.md.
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from supabase import create_client

load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

CATEGORIES = [
    "groceries",
    "religious_study",
    "finance_journal",
    "product_ideas",
    "health_wellness",
    "cf_care",
    "cooking_recipes",
    "business_learning",
]

CATEGORY_LIST = ", ".join(CATEGORIES)

mcp = FastMCP(
    "Second Brain",
    instructions=(
        "You are Cole's second brain — a personal knowledge capture system. "
        "Cole is often on his phone, so keep responses SHORT and conversational. "
        "When he mentions something interesting, proactively ask if he wants to capture it. "
        "For cf_care entries always ask for a type (treatment, insurance, medication, or appointment) and store it in metadata. "
        "For religious_study or finance_journal, ask if it connects to past notes. "
        "Always confirm writes succeeded. Never lose data."
    ),
)


# ---------------------------------------------------------------------------
# System / orientation
# ---------------------------------------------------------------------------


@mcp.tool()
def get_system_info() -> dict:
    """Return the full schema of Cole's second brain: available categories,
    how ideas/tags/relationships/insights work, and behavioral guidelines.

    CALL THIS FIRST in any new conversation to orient yourself before doing anything else.
    """
    return {
        "categories": {
            "groceries": "Shopping lists, meal-prep ingredients, household supplies",
            "religious_study": "Bible study notes, sermon reflections, theology questions — always ask if it connects to past notes",
            "finance_journal": "Budget thoughts, investment ideas, financial goals — always ask if it connects to past notes",
            "product_ideas": "App concepts, SaaS ideas, side-project plans",
            "health_wellness": "Exercise, nutrition, mental-health reflections",
            "cf_care": "Cystic fibrosis care — ALWAYS include metadata.type as one of: treatment, insurance, medication, appointment",
            "cooking_recipes": "Recipes, cooking techniques, meal plans",
            "business_learning": "Books, courses, frameworks, career insights",
        },
        "tables": {
            "ideas": "Core notes. Fields: id, title, content, category, tags[], metadata{}, created_at, is_archived",
            "topics": "Tag registry for autocomplete. Fields: id, name, description, category",
            "idea_relationships": "Links between ideas. Fields: id, source_id, target_id, relationship_type, note",
            "insights": "AI-generated patterns. Fields: id, title, summary, related_idea_ids[], tags[], category, action_item, is_actioned",
        },
        "guidelines": [
            "Keep responses SHORT — Cole is usually on mobile",
            "Confirm every write with a brief summary of what was saved",
            "For cf_care: always store metadata.type (treatment/insurance/medication/appointment)",
            "For religious_study and finance_journal: ask if it connects to existing notes",
            "When Cole asks 'what have I been thinking about X': search across ALL categories",
            "Use tags liberally — they power cross-category discovery",
        ],
    }


# ---------------------------------------------------------------------------
# Ideas — CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_idea(
    title: str,
    content: str,
    category: str,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Capture a new idea into Cole's second brain.

    category MUST be one of: groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning

    tags: free-form list of keywords for cross-category discovery (e.g. ["prayer", "healing", "insurance"]).
    metadata: optional JSON object. For cf_care, MUST include {"type": "treatment|insurance|medication|appointment"}.

    Returns the saved idea with its generated UUID.
    """
    return (
        supabase.table("ideas")
        .insert(
            {
                "title": title,
                "content": content,
                "category": category,
                "tags": tags or [],
                "metadata": metadata or {},
            }
        )
        .execute()
        .data[0]
    )


@mcp.tool()
def search_ideas(
    query: str = "",
    category: str | None = None,
    tags: list[str] | None = None,
) -> list:
    """Full-text search across all ideas. Use this when Cole asks 'what have I noted about X'.

    query: free-text search (searches title + content).
    category: optional filter — one of: groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning
    tags: optional — return ideas that have ANY of these tags.

    Returns a list of matching ideas (most recent first, max 25).
    """
    q = supabase.table("ideas").select("*").eq("is_archived", False)
    if category:
        q = q.eq("category", category)
    if tags:
        q = q.overlaps("tags", tags)
    if query:
        q = q.text_search("content", query)
    return q.order("created_at", desc=True).limit(25).execute().data


@mcp.tool()
def get_idea(idea_id: str) -> dict:
    """Retrieve a single idea by its UUID. Use when you need full detail on a specific note."""
    return supabase.table("ideas").select("*").eq("id", idea_id).execute().data[0]


@mcp.tool()
def update_idea(idea_id: str, fields: dict) -> dict:
    """Update fields on an existing idea. Pass only the fields to change.

    Updatable fields: title, content, category (must be one of: groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning), tags, metadata.
    """
    return supabase.table("ideas").update(fields).eq("id", idea_id).execute().data[0]


@mcp.tool()
def list_by_category(category: str, limit: int = 20) -> list:
    """Browse recent ideas in a category. Good for 'show me my recent X'.

    category MUST be one of: groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning
    """
    return (
        supabase.table("ideas")
        .select("*")
        .eq("category", category)
        .eq("is_archived", False)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )


@mcp.tool()
def archive_idea(idea_id: str) -> dict:
    """Soft-delete an idea by marking it archived. It won't appear in searches."""
    return (
        supabase.table("ideas")
        .update({"is_archived": True})
        .eq("id", idea_id)
        .execute()
        .data[0]
    )


# ---------------------------------------------------------------------------
# Topics — tag registry
# ---------------------------------------------------------------------------


@mcp.tool()
def add_topic(name: str, description: str = "", category: str | None = None) -> dict:
    """Register a new topic/tag for autocomplete and discovery.

    category (optional): one of groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning
    """
    data = {"name": name}
    if description:
        data["description"] = description
    if category:
        data["category"] = category
    return supabase.table("topics").insert(data).execute().data[0]


@mcp.tool()
def list_topics(category: str | None = None) -> list:
    """List all registered topics, optionally filtered by category (groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning).
    Useful for suggesting tags when capturing new ideas.
    """
    q = supabase.table("topics").select("*")
    if category:
        q = q.eq("category", category)
    return q.order("name").execute().data


@mcp.tool()
def search_topics(query: str) -> list:
    """Search topics by partial name match. Use for tag autocomplete."""
    return (
        supabase.table("topics")
        .select("*")
        .ilike("name", f"%{query}%")
        .execute()
        .data
    )


# ---------------------------------------------------------------------------
# Relationships — cross-referencing
# ---------------------------------------------------------------------------


@mcp.tool()
def link_ideas(
    source_id: str,
    target_id: str,
    relationship_type: str = "related",
    note: str = "",
) -> dict:
    """Create a directional link between two ideas.

    relationship_type: free text, e.g. 'related', 'builds_on', 'contradicts', 'action_from'.
    note: optional explanation of the connection.
    """
    return (
        supabase.table("idea_relationships")
        .insert(
            {
                "source_id": source_id,
                "target_id": target_id,
                "relationship_type": relationship_type,
                "note": note,
            }
        )
        .execute()
        .data[0]
    )


@mcp.tool()
def get_related_ideas(idea_id: str) -> list:
    """Fetch all ideas linked to a given idea (both directions).

    Returns the relationship record with the linked idea embedded.
    """
    fwd = (
        supabase.table("idea_relationships")
        .select("*, target:target_id(*)")
        .eq("source_id", idea_id)
        .execute()
        .data
    )
    rev = (
        supabase.table("idea_relationships")
        .select("*, source:source_id(*)")
        .eq("target_id", idea_id)
        .execute()
        .data
    )
    return fwd + rev


@mcp.tool()
def remove_relationship(relationship_id: str) -> dict:
    """Remove a link between two ideas."""
    return (
        supabase.table("idea_relationships")
        .delete()
        .eq("id", relationship_id)
        .execute()
        .data
    )


# ---------------------------------------------------------------------------
# Insights — pattern analysis
# ---------------------------------------------------------------------------


@mcp.tool()
def add_insight(
    title: str,
    summary: str,
    related_idea_ids: list[str] | None = None,
    tags: list[str] | None = None,
    category: str | None = None,
    action_item: str = "",
) -> dict:
    """Record a Claude-generated insight — a pattern or actionable observation.

    Use this after analyzing multiple ideas to capture a meta-observation.
    category (optional): one of groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning
    action_item: a concrete next step Cole should consider.
    """
    data = {
        "title": title,
        "summary": summary,
        "related_idea_ids": related_idea_ids or [],
        "tags": tags or [],
    }
    if category:
        data["category"] = category
    if action_item:
        data["action_item"] = action_item
    return supabase.table("insights").insert(data).execute().data[0]


@mcp.tool()
def list_insights(category: str | None = None, unactioned_only: bool = False) -> list:
    """List past insights, optionally filtered.

    category: one of groceries, religious_study, finance_journal, product_ideas, health_wellness, cf_care, cooking_recipes, business_learning
    unactioned_only: if true, only show insights with pending action items.
    """
    q = supabase.table("insights").select("*")
    if category:
        q = q.eq("category", category)
    if unactioned_only:
        q = q.eq("is_actioned", False)
    return q.order("created_at", desc=True).execute().data


@mcp.tool()
def mark_actioned(insight_id: str) -> dict:
    """Mark an insight's action item as completed."""
    return (
        supabase.table("insights")
        .update({"is_actioned": True})
        .eq("id", insight_id)
        .execute()
        .data[0]
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
