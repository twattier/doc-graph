# Database Schema

## PostgreSQL Schema (Documents & Metadata)

```sql
-- Enable pgvector extension for embedding search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (managed by Cognito, referenced only)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cognito_sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    github_url TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'importing',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT projects_status_check CHECK (status IN ('importing', 'processing', 'ready', 'error'))
);

CREATE INDEX projects_user_id_idx ON projects(user_id);
CREATE INDEX projects_status_idx ON projects(status);
CREATE INDEX projects_github_url_idx ON projects USING HASH(github_url);

-- Template zones table
CREATE TABLE template_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    template_type VARCHAR(50) NOT NULL,
    root_path TEXT NOT NULL,
    visualization_config JSONB NOT NULL DEFAULT '{}',
    completeness_score DECIMAL(3,2) DEFAULT 0.0,
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT template_zones_type_check CHECK (template_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT template_zones_completeness_check CHECK (completeness_score >= 0.0 AND completeness_score <= 1.0)
);

CREATE INDEX template_zones_project_id_idx ON template_zones(project_id);
CREATE INDEX template_zones_type_idx ON template_zones(template_type);

-- Documents table with pgvector embeddings
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    template_zone_id UUID REFERENCES template_zones(id) ON DELETE SET NULL,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    extracted_metadata JSONB NOT NULL DEFAULT '{}',
    embedding_vector vector(768), -- OpenAI ada-002 embedding size
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    detection_confidence DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT documents_template_type_check CHECK (template_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT documents_status_check CHECK (processing_status IN ('pending', 'processed', 'failed')),
    CONSTRAINT documents_confidence_check CHECK (detection_confidence >= 0.0 AND detection_confidence <= 1.0),
    CONSTRAINT documents_project_path_unique UNIQUE (project_id, file_path)
);

CREATE INDEX documents_project_id_idx ON documents(project_id);
CREATE INDEX documents_template_type_idx ON documents(template_type);
CREATE INDEX documents_processing_status_idx ON documents(processing_status);
CREATE INDEX documents_embedding_vector_idx ON documents USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Visualizations table
CREATE TABLE visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    template_zone_id UUID REFERENCES template_zones(id) ON DELETE SET NULL,
    visualization_type VARCHAR(50) NOT NULL,
    mermaid_code TEXT NOT NULL,
    generation_metadata JSONB NOT NULL DEFAULT '{}',
    cache_status VARCHAR(20) NOT NULL DEFAULT 'fresh',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT visualizations_type_check CHECK (visualization_type IN ('tree', 'pipeline', 'graph', 'cross-template')),
    CONSTRAINT visualizations_cache_check CHECK (cache_status IN ('fresh', 'stale', 'expired'))
);

CREATE INDEX visualizations_project_id_idx ON visualizations(project_id);
CREATE INDEX visualizations_expires_at_idx ON visualizations(expires_at);
CREATE INDEX visualizations_cache_status_idx ON visualizations(cache_status);

-- Template mappings table for project-specific overrides
CREATE TABLE template_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    path_pattern TEXT NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL DEFAULT 1.0,
    is_override BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT template_mappings_type_check CHECK (template_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT template_mappings_confidence_check CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX template_mappings_project_id_idx ON template_mappings(project_id);

-- Update triggers for updated_at fields
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_template_zones_updated_at BEFORE UPDATE ON template_zones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_visualizations_updated_at BEFORE UPDATE ON visualizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Neo4j Schema (Relationships & Graph Data)

```cypher
// Create constraints for performance and data integrity
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT template_zone_id IF NOT EXISTS FOR (tz:TemplateZone) REQUIRE tz.id IS UNIQUE;

// Create indexes for common queries
CREATE INDEX project_github_url IF NOT EXISTS FOR (p:Project) ON (p.github_url);
CREATE INDEX document_template_type IF NOT EXISTS FOR (d:Document) ON (d.template_type);
CREATE INDEX document_file_path IF NOT EXISTS FOR (d:Document) ON (d.file_path);

// Node creation patterns for projects
MERGE (p:Project {
    id: $project_id,
    name: $project_name,
    github_url: $github_url,
    created_at: datetime()
});

// Template zone nodes with hierarchy
MERGE (p:Project {id: $project_id})
MERGE (tz:TemplateZone {
    id: $zone_id,
    project_id: $project_id,
    template_type: $template_type,
    root_path: $root_path
})
MERGE (p)-[:CONTAINS_ZONE]->(tz);

// Document nodes with template classification
MERGE (tz:TemplateZone {id: $zone_id})
MERGE (d:Document {
    id: $document_id,
    project_id: $project_id,
    file_path: $file_path,
    template_type: $template_type,
    detection_confidence: $confidence
})
MERGE (tz)-[:CONTAINS_DOCUMENT]->(d);

// Cross-template relationship patterns
MATCH (source:Document {id: $source_id})
MATCH (target:Document {id: $target_id})
MERGE (source)-[r:RELATES_TO {
    relationship_type: $rel_type,
    strength: $strength,
    detected_by: $detection_method,
    created_at: datetime()
}]->(target);

// Template-specific relationship types
// BMAD-METHOD workflow relationships
MERGE (source)-[:WORKFLOW_PRECEDES {stage: $stage}]->(target);
MERGE (doc)-[:IMPLEMENTS_REQUIREMENT {requirement_id: $req_id}]->(spec);

// Claude Code agent-task relationships
MERGE (agent)-[:EXECUTES_TASK {priority: $priority}]->(task);
MERGE (task)-[:DEPENDS_ON {dependency_type: $dep_type}]->(dependency);

// Cross-template implementation relationships
MERGE (bmad_doc)-[:IMPLEMENTED_BY {confidence: $confidence}]->(claude_config);
MERGE (requirement)-[:TRACED_TO {traceability_level: $level}]->(implementation);

// Query patterns for visualization generation
// Tree structure query for Claude Code
MATCH (tz:TemplateZone {template_type: 'claude-code'})-[:CONTAINS_DOCUMENT]->(d:Document)
OPTIONAL MATCH (d)-[r:EXECUTES_TASK|DEPENDS_ON]->(related:Document)
RETURN d, r, related
ORDER BY d.file_path;

// Pipeline structure query for BMAD-METHOD
MATCH (tz:TemplateZone {template_type: 'bmad-method'})-[:CONTAINS_DOCUMENT]->(d:Document)
OPTIONAL MATCH (d)-[r:WORKFLOW_PRECEDES]->(next:Document)
RETURN d, r, next
ORDER BY r.stage;

// Cross-template relationship discovery
MATCH (source:Document)-[r:RELATES_TO]->(target:Document)
WHERE source.template_type <> target.template_type
RETURN source, r, target, r.strength
ORDER BY r.strength DESC;
```
