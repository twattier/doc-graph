# DocGraph

## GOAL
Create a solution named "DocGraph" as a project documentation exploration and visualization platform enhanced by generative AI and GraphRAG capabilities

## FEATURES

### For project managers, product managers, product owners, and architects

- Project management
    - Create and manage projects with metadata and configuration
    - Configure documentation sources (file upload, zip upload, or GitHub public repository link)
    - Apply multiple templates to different directories/file patterns within a project
    - Map file structure to appropriate templates (e.g., docs/ → BMAD Method, .bmad-core/ → Claude Code)
    - Synchronize documentation: initial sync at creation, then on-demand refresh

- Generic project visualization
    - Default view similar to GitHub file explorer
    - Hierarchical file structure navigation
    - Markdown content rendering with syntax highlighting
    - File search and filtering capabilities
    - Cross-document link navigation

- Template-specific visualization
    - Multiple templates can be applied to different parts of the same project
    - BMAD Method template: Applied to docs/ folder for conception specifications (prd.md, architecture.md, etc.)
    - Claude Code template: Applied to .bmad-core/ folder for agents/subagents, tasks, and templates
    - Custom template mapping based on file patterns and directory structure
    - Combined visualization showing relationships across different template zones
    - Graph-based entity and relationship visualization spanning multiple templates
    - Interactive exploration of project components and their cross-template connections

- Chatbot and RAG system
    - Intelligent chatbot for querying project documentation
    - Context-aware responses with source references
    - GraphRAG optimization based on project type
    - Advanced search with semantic understanding

### For solution admin

- System administration
    - User and project management dashboard
    - Usage monitoring and analytics
    - Template management and configuration
    - System health and performance metrics

### For external solutions

- MCP (Model Context Protocol) service
    - External API for documentation querying
    - Integration capabilities for other development tools
    - Standardized access to project knowledge

## TECHNICAL STACK

- Frontend: shadcn/ui with React
- Backend: Python FastAPI
- Agentic framework: pydantic
- Database: pgvector and/or neo4j for graph storage
- GraphRAG framework: Zep Graphiti
- File processing: Markdown parsing, GitHub API integration
- Visualization: D3.js or Cytoscape.js for graph rendering

## PROJECT TYPES & TEMPLATES

### Multi-Template Architecture
- Projects can have multiple templates applied simultaneously
- Template mapping based on directory structure and file patterns
- Cross-template relationship detection and visualization
- Unified knowledge graph spanning multiple template zones

### Template Mapping Examples
```
project-root/
├── docs/           → BMAD Method Template
│   ├── prd.md
│   ├── architecture.md
│   └── front-end-spec.md
├── .bmad-core/     → Claude Code Template
│   ├── agents/
│   ├── tasks/
│   └── templates/
├── src/            → Generic Template
│   └── components/
└── README.md       → Generic Template
```

### Generic Template (Default)
- Applied to unmapped directories and files
- Standard file explorer view
- Basic markdown rendering
- Simple search functionality

### BMAD Method Template
- Applied to docs/ directory and specification files
- Workflow visualization with agent sequences
- Document relationship mapping (PRD → Architecture → Frontend Spec)
- Progress tracking through development phases
- Artifact dependency visualization

### Claude Code Template
- Applied to .bmad-core/ directory structure
- Agent and subagent hierarchy
- Task execution flow visualization
- Template usage and relationships
- Command structure mapping

## CORE ENTITIES

### Project
- Name, description, and metadata
- Source configuration (upload, GitHub repo)
- Multiple template assignments with directory/file pattern mapping
- Template priority and conflict resolution rules
- Synchronization status and history

### Document
- File path and content
- Multiple template classifications based on location/pattern
- Cross-template relationships and references
- Metadata extraction based on applicable templates
- Version history

### Template
- Type definition and rules
- Directory/file pattern matching criteria
- Entity mapping for GraphRAG
- Visualization configuration
- Processing logic for specific document types
- Cross-template relationship definitions

## USER WORKFLOWS

### Project Creation
1. Create project with basic information
2. Configure documentation source (upload files/zip or GitHub repo)
3. Define template mappings for different directories/file patterns
4. Initial documentation processing and analysis with multi-template support
5. Generate unified knowledge graph spanning all template zones

### Documentation Exploration
1. Navigate project with combined visualization showing all templates
2. Switch between template-specific views and unified view
3. Search and filter documents across all template zones
4. Follow cross-references and relationships within and across templates
5. Query documentation via chatbot with cross-template awareness

### Project Maintenance
1. On-demand synchronization with source
2. Template mapping updates and re-processing
3. Cross-template relationship refresh and optimization
4. Template conflict resolution and priority management