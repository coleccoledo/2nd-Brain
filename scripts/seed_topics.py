"""Seed the topics table with initial tags for each category."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

SEED_TOPICS = [
    # Groceries
    {"name": "weekly-list", "description": "Regular weekly shopping items", "category": "groceries"},
    {"name": "costco-run", "description": "Costco bulk shopping", "category": "groceries"},
    {"name": "meal-prep", "description": "Ingredients for meal prep", "category": "groceries"},

    # Religious Study
    {"name": "scripture-insight", "description": "Scriptural insights and study notes", "category": "religious_study"},
    {"name": "faith", "description": "Thoughts on faith and belief", "category": "religious_study"},
    {"name": "talk-notes", "description": "Notes from talks and sermons", "category": "religious_study"},
    {"name": "spiritual-journal", "description": "Personal spiritual reflections", "category": "religious_study"},

    # Finance Journal
    {"name": "equities", "description": "Stock and equity research", "category": "finance_journal"},
    {"name": "crypto", "description": "Cryptocurrency research and notes", "category": "finance_journal"},
    {"name": "macro", "description": "Macroeconomic observations", "category": "finance_journal"},
    {"name": "portfolio", "description": "Portfolio management notes", "category": "finance_journal"},
    {"name": "real-estate", "description": "Real estate investment ideas", "category": "finance_journal"},

    # Product Ideas
    {"name": "feature-request", "description": "New feature ideas", "category": "product_ideas"},
    {"name": "ux-improvement", "description": "User experience improvements", "category": "product_ideas"},
    {"name": "mvp", "description": "Minimum viable product concepts", "category": "product_ideas"},
    {"name": "bug-idea", "description": "Bug-inspired feature improvements", "category": "product_ideas"},

    # Health & Wellness
    {"name": "fitness", "description": "Exercise and fitness notes", "category": "health_wellness"},
    {"name": "nutrition", "description": "Diet and nutrition tracking", "category": "health_wellness"},
    {"name": "sleep", "description": "Sleep quality and habits", "category": "health_wellness"},
    {"name": "mental-health", "description": "Mental health and mindfulness", "category": "health_wellness"},

    # CF Care
    {"name": "treatment", "description": "CF treatment plans and updates", "category": "cf_care"},
    {"name": "insurance", "description": "Insurance claims and coverage", "category": "cf_care"},
    {"name": "medication", "description": "Medication tracking and changes", "category": "cf_care"},
    {"name": "appointment", "description": "Doctor appointments and follow-ups", "category": "cf_care"},
    {"name": "pulmonary", "description": "Pulmonary function and respiratory notes", "category": "cf_care"},

    # Cooking & Recipes
    {"name": "recipe", "description": "New recipes to try or save", "category": "cooking_recipes"},
    {"name": "technique", "description": "Cooking techniques and tips", "category": "cooking_recipes"},
    {"name": "ingredient-note", "description": "Notes on specific ingredients", "category": "cooking_recipes"},
    {"name": "meal-plan", "description": "Weekly meal planning", "category": "cooking_recipes"},

    # Business Topics & Learning
    {"name": "strategy", "description": "Business strategy notes", "category": "business_learning"},
    {"name": "book-notes", "description": "Notes from business books", "category": "business_learning"},
    {"name": "market-research", "description": "Market research findings", "category": "business_learning"},
    {"name": "leadership", "description": "Leadership and management insights", "category": "business_learning"},
    {"name": "startup", "description": "Startup and entrepreneurship ideas", "category": "business_learning"},
]


def main():
    print(f"Seeding {len(SEED_TOPICS)} topics...\n")

    created = 0
    skipped = 0
    for topic in SEED_TOPICS:
        try:
            sb.table("topics").insert(topic).execute()
            print(f"  + {topic['name']} ({topic['category']})")
            created += 1
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower() or "23505" in str(e):
                print(f"  ~ {topic['name']} (already exists, skipped)")
                skipped += 1
            else:
                print(f"  ! {topic['name']} ERROR: {e}")

    print(f"\nDone. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
