-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Categories enum
CREATE TYPE category_type AS ENUM (
  'groceries',
  'religious_study',
  'finance_journal',
  'product_ideas',
  'health_wellness',
  'cf_care',
  'cooking_recipes',
  'business_learning'
);

-- Core ideas table
CREATE TABLE ideas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category category_type NOT NULL,
  tags TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  is_archived BOOLEAN DEFAULT FALSE
);

-- Topics/tags registry for autocomplete and querying
CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  category category_type,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Relationships between ideas (for cross-referencing)
CREATE TABLE idea_relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES ideas(id) ON DELETE CASCADE,
  target_id UUID REFERENCES ideas(id) ON DELETE CASCADE,
  relationship_type TEXT DEFAULT 'related',
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_id, target_id)
);

-- Insight log: Claude-generated patterns and action items
CREATE TABLE insights (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  related_idea_ids UUID[] DEFAULT '{}',
  tags TEXT[] DEFAULT '{}',
  category category_type,
  action_item TEXT,
  is_actioned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ideas_updated_at
BEFORE UPDATE ON ideas
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Indexes for performance
CREATE INDEX idx_ideas_category ON ideas(category);
CREATE INDEX idx_ideas_tags ON ideas USING GIN(tags);
CREATE INDEX idx_ideas_created_at ON ideas(created_at DESC);
CREATE INDEX idx_ideas_metadata ON ideas USING GIN(metadata);
CREATE INDEX idx_ideas_fts ON ideas USING GIN(to_tsvector('english', title || ' ' || content));
