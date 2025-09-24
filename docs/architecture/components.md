# Components

## GitHub Integration Service
**Responsibility:** Handles repository import, OAuth authentication, and file synchronization with GitHub API

**Key Interfaces:**
- POST /projects - Import repository from GitHub URL
- GET /projects/{id}/sync - Refresh repository content
- GitHub OAuth callback handling

**Dependencies:** AWS Cognito (authentication), S3 (file storage), SQS (async processing queue)

**Technology Stack:** Python FastAPI, GitHub API v4 (GraphQL), boto3 for AWS services, asyncio for concurrent file processing

## Template Detection Service
**Responsibility:** Analyzes imported documents to classify template types and extract metadata patterns

**Key Interfaces:**
- POST /template-detection/analyze - Process documents for template classification
- GET /template-detection/rules - Retrieve template matching rules
- PUT /template-detection/mappings - Update project-specific template mappings

**Dependencies:** PostgreSQL (document storage), Redis (caching), Machine Learning models for pattern recognition

**Technology Stack:** Python FastAPI, scikit-learn for classification, spaCy for NLP processing, custom pattern matching engines

## Visualization Generation Service
**Responsibility:** Creates Mermaid diagrams from template-classified documents and relationships

**Key Interfaces:**
- POST /visualizations/generate - Create new visualization from project data
- GET /visualizations/{id}/export - Export visualization in various formats
- PUT /visualizations/{id}/config - Update visualization styling and layout

**Dependencies:** Neo4j (relationship queries), Redis (diagram caching), Mermaid.js (diagram generation)

**Technology Stack:** Python FastAPI, Neo4j driver, Puppeteer for diagram rendering, custom Mermaid template engines

## Search & Relationship Service
**Responsibility:** Provides template-aware search and cross-template relationship detection

**Key Interfaces:**
- GET /projects/{id}/search - Template-aware document search
- POST /relationships/detect - Analyze cross-template connections
- GET /relationships/{id} - Retrieve relationship details with metadata

**Dependencies:** PostgreSQL with pgvector (similarity search), Neo4j (relationship storage), Template Detection Service

**Technology Stack:** Python FastAPI, pgvector for embedding search, sentence-transformers for document embeddings, custom relationship analysis algorithms

## Project Configuration Service
**Responsibility:** Manages project settings, template mappings, and user preferences

**Key Interfaces:**
- GET/PUT /projects/{id}/config - Project configuration management
- POST /projects/{id}/template-mappings - Update template detection rules
- GET /users/{id}/preferences - User-specific configuration settings

**Dependencies:** PostgreSQL (configuration storage), AWS Cognito (user management), Redis (session caching)

**Technology Stack:** Python FastAPI, SQLAlchemy ORM, Pydantic for configuration validation, custom template mapping logic

## Component Diagrams

```mermaid
C4Container
    title DocGraph Container Diagram

    Person(user, "Project Manager", "Assesses project readiness through documentation visualization")

    Container_Boundary(frontend, "Frontend Application") {
        Container(webapp, "React Web App", "TypeScript, React, shadcn/ui", "Template-aware visualization interface")
    }

    Container_Boundary(backend, "Backend Services") {
        Container(gateway, "API Gateway", "AWS API Gateway", "Request routing and authentication")
        Container(github, "GitHub Service", "Python FastAPI", "Repository import and sync")
        Container(template, "Template Service", "Python FastAPI", "Document classification and analysis")
        Container(visual, "Visualization Service", "Python FastAPI", "Mermaid diagram generation")
        Container(search, "Search Service", "Python FastAPI", "Template-aware search and relationships")
        Container(config, "Config Service", "Python FastAPI", "Project and user configuration")
    }

    Container_Boundary(data, "Data Layer") {
        ContainerDb(postgres, "PostgreSQL", "Documents and metadata with pgvector for embeddings")
        ContainerDb(neo4j, "Neo4j", "Graph relationships and cross-template connections")
        ContainerDb(redis, "Redis", "Caching and session storage")
        Container(s3, "S3 Storage", "File storage for imported documents")
    }

    System_Ext(github_api, "GitHub API", "Repository access and authentication")

    Rel(user, webapp, "Explores project documentation")
    Rel(webapp, gateway, "API requests")
    Rel(gateway, github, "Import projects")
    Rel(gateway, template, "Classify documents")
    Rel(gateway, visual, "Generate diagrams")
    Rel(gateway, search, "Search and relationships")
    Rel(gateway, config, "Manage settings")

    Rel(github, github_api, "Fetch repositories")
    Rel(github, s3, "Store files")
    Rel(template, postgres, "Store classifications")
    Rel(visual, neo4j, "Query relationships")
    Rel(search, postgres, "Vector search")
    Rel(search, neo4j, "Graph queries")

    UpdateRelStyle(github, postgres, $offsetY="-40")
    UpdateRelStyle(template, redis, $offsetX="-90")
    UpdateRelStyle(visual, redis, $offsetX="-70")
```
