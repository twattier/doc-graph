-- DocGraph Database Initialization Script
-- This script sets up the initial database schema for development

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create basic tables for document storage and vector embeddings
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding ON document_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Insert sample data for development
INSERT INTO documents (title, content, file_path, file_type) VALUES
('Sample Document', 'This is a sample document for testing the DocGraph system.', '/sample/doc.txt', 'text')
ON CONFLICT DO NOTHING;