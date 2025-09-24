# Database Schema

## PostgreSQL Schema (Documents & Metadata)

```sql
-- Enable pgvector extension for embedding search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Access Control Model:
-- Projects can be shared among multiple users with different roles:
-- - owner: Full control, can delete project, manage users
-- - editor: Can modify project content, view all data
-- - viewer: Read-only access to project and visualizations
-- Future enhancement: Granular permissions in the permissions JSONB field

-- Users table (basic email-based authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table (removed user_id as projects can have multiple users)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    github_url TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'importing',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT projects_status_check CHECK (status IN ('importing', 'processing', 'ready', 'error'))
);

CREATE INDEX projects_status_idx ON projects(status);
CREATE INDEX projects_github_url_idx ON projects USING HASH(github_url);
CREATE INDEX projects_created_by_idx ON projects(created_by);

-- Project users association table (many-to-many relationship)
CREATE TABLE project_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    permissions JSONB NOT NULL DEFAULT '{"read": true, "write": false, "admin": false}',
    added_by UUID REFERENCES users(id),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT project_users_unique UNIQUE(project_id, user_id),
    CONSTRAINT project_users_role_check CHECK (role IN ('owner', 'editor', 'viewer'))
);

CREATE INDEX project_users_project_id_idx ON project_users(project_id);
CREATE INDEX project_users_user_id_idx ON project_users(user_id);
CREATE INDEX project_users_role_idx ON project_users(role);

-- Project documentation types table
CREATE TABLE project_docs_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    doc_type VARCHAR(50) NOT NULL,
    root_path TEXT NOT NULL,
    visualization_config JSONB NOT NULL DEFAULT '{}',
    completeness_score DECIMAL(3,2) DEFAULT 0.0,
    document_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT project_docs_type_check CHECK (doc_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT project_docs_completeness_check CHECK (completeness_score >= 0.0 AND completeness_score <= 1.0)
);

CREATE INDEX project_docs_type_project_id_idx ON project_docs_type(project_id);
CREATE INDEX project_docs_type_doc_type_idx ON project_docs_type(doc_type);

-- Documents table with pgvector embeddings
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    project_docs_type_id UUID REFERENCES project_docs_type(id) ON DELETE SET NULL,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    extracted_metadata JSONB NOT NULL DEFAULT '{}',
    embedding_vector vector(768), -- OpenAI ada-002 embedding size
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    detection_confidence DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT documents_doc_type_check CHECK (doc_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT documents_status_check CHECK (processing_status IN ('pending', 'processed', 'failed')),
    CONSTRAINT documents_confidence_check CHECK (detection_confidence >= 0.0 AND detection_confidence <= 1.0),
    CONSTRAINT documents_project_path_unique UNIQUE (project_id, file_path)
);

CREATE INDEX documents_project_id_idx ON documents(project_id);
CREATE INDEX documents_doc_type_idx ON documents(doc_type);
CREATE INDEX documents_processing_status_idx ON documents(processing_status);
CREATE INDEX documents_embedding_vector_idx ON documents USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Visualizations table
CREATE TABLE visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    project_docs_type_id UUID REFERENCES project_docs_type(id) ON DELETE SET NULL,
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

-- Documentation type mappings table for project-specific overrides
CREATE TABLE doc_type_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    path_pattern TEXT NOT NULL,
    doc_type VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL DEFAULT 1.0,
    is_override BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT doc_type_mappings_check CHECK (doc_type IN ('bmad-method', 'claude-code', 'generic')),
    CONSTRAINT doc_type_mappings_confidence_check CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX doc_type_mappings_project_id_idx ON doc_type_mappings(project_id);

-- Update triggers for updated_at fields
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_docs_type_updated_at BEFORE UPDATE ON project_docs_type FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_visualizations_updated_at BEFORE UPDATE ON visualizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Neo4j Schema (Relationships & Graph Data)

```cypher
// Create constraints for performance and data integrity
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT project_docs_type_id IF NOT EXISTS FOR (pdt:ProjectDocsType) REQUIRE pdt.id IS UNIQUE;

// Create indexes for common queries
CREATE INDEX project_github_url IF NOT EXISTS FOR (p:Project) ON (p.github_url);
CREATE INDEX document_doc_type IF NOT EXISTS FOR (d:Document) ON (d.doc_type);
CREATE INDEX document_file_path IF NOT EXISTS FOR (d:Document) ON (d.file_path);

// Node creation patterns for projects
MERGE (p:Project {
    id: $project_id,
    name: $project_name,
    github_url: $github_url,
    created_at: datetime()
});

// Project documentation type nodes with hierarchy
MERGE (p:Project {id: $project_id})
MERGE (pdt:ProjectDocsType {
    id: $docs_type_id,
    project_id: $project_id,
    doc_type: $doc_type,
    root_path: $root_path
})
MERGE (p)-[:CONTAINS_DOCS_TYPE]->(pdt);

// Document nodes with documentation type classification
MERGE (pdt:ProjectDocsType {id: $docs_type_id})
MERGE (d:Document {
    id: $document_id,
    project_id: $project_id,
    file_path: $file_path,
    doc_type: $doc_type,
    detection_confidence: $confidence
})
MERGE (pdt)-[:CONTAINS_DOCUMENT]->(d);

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
