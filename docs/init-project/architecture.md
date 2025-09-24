# DocGraph Fullstack Architecture Document

## Introduction

This document outlines the complete fullstack architecture for DocGraph, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### Starter Template or Existing Project

**N/A - Greenfield project** with specialized requirements for template-aware documentation processing and Mermaid visualization that don't align with standard fullstack starters. Custom architecture required to handle complex template detection, cross-template relationship mapping, and performance-optimized diagram generation.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-09-24 | 1.0 | Initial fullstack architecture document | Architect Winston |

## High Level Architecture

### Technical Summary

DocGraph implements a microservices architecture within a monorepo structure, featuring a React + shadcn/ui frontend with Python FastAPI backend services deployed on cloud infrastructure. The system specializes in template-aware document processing with dedicated services for GitHub integration, template detection, Mermaid visualization generation, and cross-template relationship analysis. Key integration points include a unified TypeScript type system, RESTful APIs with OpenAPI specifications, and hybrid database architecture using pgvector for document embeddings and Neo4j for graph relationships. This architecture achieves the PRD's performance goals through intelligent caching, progressive rendering, and specialized template processing pipelines optimized for BMAD-METHOD and Claude Code documentation structures.

### Platform and Infrastructure Choice

**Platform:** AWS Cloud Platform
**Key Services:** Lambda Functions (serverless compute), API Gateway (routing), S3 (file storage), CloudFront (CDN), RDS PostgreSQL with pgvector (document embeddings), Neo4j AuraDB (graph relationships), Cognito (authentication)
**Deployment Host and Regions:** Primary: us-east-1, Secondary: eu-west-1 for global CDN distribution

**Rationale:** AWS provides comprehensive serverless ecosystem with excellent GitHub integration capabilities, mature ML/AI services for template detection enhancement, and proven scalability for document processing workloads. Neo4j AuraDB cloud service eliminates infrastructure complexity while providing specialized graph database capabilities essential for cross-template relationship mapping.

### Repository Structure

**Structure:** Monorepo with clear frontend/backend separation
**Monorepo Tool:** Nx with integrated build caching and dependency graph management
**Package Organization:** Apps (web, api) + Packages (shared types, UI components, template engines, database clients) + Infrastructure (AWS CDK definitions)

### High Level Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface"
        U[User Browser] --> CF[CloudFront CDN]
        CF --> S3W[S3 Web Assets]
    end

    subgraph "API Layer"
        CF --> AGW[API Gateway]
        AGW --> LB[Load Balancer]
    end

    subgraph "Microservices"
        LB --> TDS[Template Detection Service]
        LB --> VGS[Visualization Generation Service]
        LB --> GIS[GitHub Integration Service]
        LB --> SRS[Search & Relationship Service]
        LB --> PCS[Project Configuration Service]
    end

    subgraph "Data Layer"
        TDS --> PG[(PostgreSQL + pgvector)]
        VGS --> PG
        SRS --> NEO[(Neo4j Graph DB)]
        GIS --> S3F[S3 File Storage]
        PCS --> PG
    end

    subgraph "External"
        GIS --> GH[GitHub API]
        VGS --> MJ[Mermaid.js Engine]
    end

    subgraph "Authentication"
        AGW --> COG[AWS Cognito]
    end
```

### Architectural Patterns

- **Microservices Architecture:** Specialized services for template detection, visualization, and data processing - *Rationale:* Clear separation of concerns enables independent scaling and optimization of complex template processing logic
- **Event-Driven Processing:** Asynchronous document processing with SQS queues - *Rationale:* Handles large repository imports without blocking user interface, enables progressive loading
- **CQRS Pattern:** Separate read/write models for document querying vs. processing - *Rationale:* Optimizes performance for complex graph queries while maintaining simple write operations
- **Template Strategy Pattern:** Pluggable template detection engines for BMAD-METHOD, Claude Code, and future frameworks - *Rationale:* Enables extensibility without core system modification
- **Graph-First Data Modeling:** Neo4j for relationships, PostgreSQL for documents - *Rationale:* Matches the natural structure of cross-template documentation relationships
- **Progressive Enhancement:** Client-side rendering with server-side fallbacks - *Rationale:* Ensures performance for complex visualizations while maintaining accessibility

## Tech Stack

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.3+ | Type-safe frontend development | Essential for complex data modeling and API integration |
| Frontend Framework | React | 18.2+ | Component-based UI development | Mature ecosystem with excellent performance for complex visualizations |
| UI Component Library | shadcn/ui | Latest | Consistent design system | Accessibility-first components with Tailwind integration |
| State Management | Zustand | 4.4+ | Lightweight state management | Simple API ideal for template-aware context management |
| Backend Language | Python | 3.11+ | AI/ML processing and web APIs | Excellent libraries for document processing and template pattern matching |
| Backend Framework | FastAPI | 0.104+ | High-performance async API development | Automatic OpenAPI generation and excellent TypeScript integration |
| API Style | REST with OpenAPI | 3.0 | Standardized API documentation | Clear contract between frontend and backend with code generation |
| Database | PostgreSQL + pgvector | 15+ | Document storage with vector search | Combines relational data integrity with AI-powered document similarity |
| Graph Database | Neo4j | 5.15+ | Relationship and graph data | Specialized for complex cross-template relationship queries |
| Cache | Redis | 7.2+ | Performance caching and sessions | Essential for template detection caching and real-time features |
| File Storage | AWS S3 | Latest | Document and asset storage | Scalable storage with CloudFront integration for global distribution |
| Authentication | AWS Cognito | Latest | User management and OAuth | GitHub OAuth integration with minimal implementation complexity |
| Frontend Testing | Vitest + Testing Library | Latest | Component and unit testing | Fast execution with excellent React component testing support |
| Backend Testing | pytest + FastAPI TestClient | Latest | API and service testing | Comprehensive async testing support for FastAPI applications |
| E2E Testing | Playwright | Latest | Cross-browser integration testing | Excellent support for complex visualization testing and interactions |
| Build Tool | Vite | 5.0+ | Fast frontend builds and HMR | Superior performance for large TypeScript codebases with complex dependencies |
| Bundler | Vite (Rollup) | Latest | Production optimized bundles | Tree shaking and code splitting optimized for visualization libraries |
| IaC Tool | AWS CDK | 2.100+ | Infrastructure as code | Type-safe infrastructure definitions with excellent AWS service integration |
| CI/CD | GitHub Actions | Latest | Automated testing and deployment | Native GitHub integration with repository-based workflows |
| Monitoring | AWS CloudWatch + DataDog | Latest | Application performance monitoring | Comprehensive logging and metrics with custom dashboard support |
| Logging | Winston + CloudWatch Logs | Latest | Structured application logging | Centralized logging with queryable structured data for debugging |
| CSS Framework | Tailwind CSS | 3.3+ | Utility-first styling | Rapid development with consistent design system integration |
| Visualization Engine | Mermaid.js | 10.6+ | Diagram generation and rendering | GitHub-compatible diagrams with extensive customization options |

## Data Models

### Project
**Purpose:** Represents a GitHub repository imported for template-aware analysis and visualization

**Key Attributes:**
- id: string (UUID) - Unique project identifier
- name: string - Human-readable project name
- githubUrl: string - Source repository URL
- importDate: Date - When project was imported
- templateMappings: TemplateMapping[] - Template detection configuration
- status: ProjectStatus - Processing status (importing, processing, ready, error)
- metadata: ProjectMetadata - Repository statistics and configuration

#### TypeScript Interface
```typescript
interface Project {
  id: string;
  name: string;
  githubUrl: string;
  importDate: Date;
  templateMappings: TemplateMapping[];
  status: 'importing' | 'processing' | 'ready' | 'error';
  metadata: {
    fileCount: number;
    lastCommit: Date;
    primaryBranch: string;
    detectionConfidence: number;
  };
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships
- Has many Documents
- Has many TemplateZones
- Belongs to User

### Document
**Purpose:** Individual file within a project with template classification and extracted metadata

**Key Attributes:**
- id: string (UUID) - Unique document identifier
- projectId: string - Parent project reference
- filePath: string - Relative path within repository
- content: string - Document content
- templateType: TemplateType - Detected template classification
- extractedMetadata: DocumentMetadata - Template-specific metadata
- embeddingVector: number[] - pgvector embedding for similarity search
- processingStatus: ProcessingStatus - Current processing state

#### TypeScript Interface
```typescript
interface Document {
  id: string;
  projectId: string;
  filePath: string;
  content: string;
  templateType: 'bmad-method' | 'claude-code' | 'generic';
  extractedMetadata: Record<string, any>;
  embeddingVector?: number[];
  processingStatus: 'pending' | 'processed' | 'failed';
  detectionConfidence: number;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships
- Belongs to Project
- Has many CrossTemplateRelationships (source and target)
- Part of TemplateZone

### TemplateZone
**Purpose:** Logical grouping of documents within a project that share the same template type

**Key Attributes:**
- id: string (UUID) - Unique zone identifier
- projectId: string - Parent project reference
- templateType: TemplateType - Template classification for this zone
- rootPath: string - Base directory path for this template zone
- visualizationConfig: VisualizationConfig - Zone-specific visualization settings
- completenessScore: number - Assessment of template completeness

#### TypeScript Interface
```typescript
interface TemplateZone {
  id: string;
  projectId: string;
  templateType: 'bmad-method' | 'claude-code' | 'generic';
  rootPath: string;
  visualizationConfig: {
    preferredLayout: 'tree' | 'pipeline' | 'graph';
    colorScheme: string;
    nodeStyles: Record<string, any>;
  };
  completenessScore: number;
  documentCount: number;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships
- Belongs to Project
- Contains many Documents
- Has many Visualizations

### CrossTemplateRelationship
**Purpose:** Represents connections and dependencies between documents from different template zones

**Key Attributes:**
- id: string (UUID) - Unique relationship identifier
- sourceDocumentId: string - Source document reference
- targetDocumentId: string - Target document reference
- relationshipType: RelationshipType - Type of connection
- strength: number - Relationship strength score (0-1)
- metadata: RelationshipMetadata - Additional relationship context
- detectedBy: string - Detection method used

#### TypeScript Interface
```typescript
interface CrossTemplateRelationship {
  id: string;
  sourceDocumentId: string;
  targetDocumentId: string;
  relationshipType: 'reference' | 'dependency' | 'implementation' | 'workflow';
  strength: number;
  metadata: {
    detectionMethod: string;
    confidence: number;
    contextualInfo?: Record<string, any>;
  };
  detectedBy: 'automatic' | 'manual' | 'ai-enhanced';
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships
- Links two Documents
- Part of relationship analysis for Visualizations

### Visualization
**Purpose:** Generated Mermaid diagram representing template-specific or cross-template relationships

**Key Attributes:**
- id: string (UUID) - Unique visualization identifier
- projectId: string - Parent project reference
- templateZoneId: string - Associated template zone (if applicable)
- visualizationType: VisualizationType - Type of diagram generated
- mermaidCode: string - Generated Mermaid diagram syntax
- generationMetadata: GenerationMetadata - Creation details and performance metrics
- cacheStatus: CacheStatus - Cache state for performance optimization

#### TypeScript Interface
```typescript
interface Visualization {
  id: string;
  projectId: string;
  templateZoneId?: string;
  visualizationType: 'tree' | 'pipeline' | 'graph' | 'cross-template';
  mermaidCode: string;
  generationMetadata: {
    generatedAt: Date;
    generationTimeMs: number;
    nodeCount: number;
    relationshipCount: number;
    cacheHit: boolean;
  };
  cacheStatus: 'fresh' | 'stale' | 'expired';
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Relationships
- Belongs to Project
- May belong to TemplateZone
- Generated from Documents and CrossTemplateRelationships

## API Specification

### REST API Specification

```yaml
openapi: 3.0.0
info:
  title: DocGraph API
  version: 1.0.0
  description: Template-aware documentation exploration and visualization API
servers:
  - url: https://api.docgraph.dev
    description: Production API server
paths:
  /projects:
    get:
      summary: List user projects
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [importing, processing, ready, error]
      responses:
        '200':
          description: List of projects
          content:
            application/json:
              schema:
                type: object
                properties:
                  projects:
                    type: array
                    items:
                      $ref: '#/components/schemas/Project'
    post:
      summary: Import new project from GitHub
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                githubUrl:
                  type: string
                  format: uri
                name:
                  type: string
                templateMappings:
                  type: array
                  items:
                    $ref: '#/components/schemas/TemplateMapping'
      responses:
        '201':
          description: Project import started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Project'

  /projects/{projectId}/template-zones:
    get:
      summary: Get template zones for project
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Template zones with document counts
          content:
            application/json:
              schema:
                type: object
                properties:
                  templateZones:
                    type: array
                    items:
                      $ref: '#/components/schemas/TemplateZone'

  /projects/{projectId}/visualizations:
    get:
      summary: Get available visualizations for project
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: templateZoneId
          in: query
          schema:
            type: string
            format: uuid
        - name: visualizationType
          in: query
          schema:
            type: string
            enum: [tree, pipeline, graph, cross-template]
      responses:
        '200':
          description: Available visualizations
          content:
            application/json:
              schema:
                type: object
                properties:
                  visualizations:
                    type: array
                    items:
                      $ref: '#/components/schemas/Visualization'
    post:
      summary: Generate new visualization
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                visualizationType:
                  type: string
                  enum: [tree, pipeline, graph, cross-template]
                templateZoneId:
                  type: string
                  format: uuid
                config:
                  type: object
      responses:
        '201':
          description: Visualization generated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Visualization'

  /projects/{projectId}/search:
    get:
      summary: Search project documents with template-aware filtering
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: query
          in: query
          required: true
          schema:
            type: string
        - name: templateType
          in: query
          schema:
            type: string
            enum: [bmad-method, claude-code, generic]
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Search results with template context
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        document:
                          $ref: '#/components/schemas/Document'
                        relevanceScore:
                          type: number
                        matchContext:
                          type: string

  /visualizations/{visualizationId}/export:
    get:
      summary: Export visualization as Mermaid code or image
      parameters:
        - name: visualizationId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: format
          in: query
          schema:
            type: string
            enum: [mermaid, svg, png]
            default: mermaid
      responses:
        '200':
          description: Exported visualization
          content:
            text/plain:
              schema:
                type: string
            image/svg+xml:
              schema:
                type: string
            image/png:
              schema:
                type: string
                format: binary

components:
  schemas:
    Project:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        githubUrl:
          type: string
          format: uri
        status:
          type: string
          enum: [importing, processing, ready, error]
        templateMappings:
          type: array
          items:
            $ref: '#/components/schemas/TemplateMapping'
        metadata:
          type: object
          properties:
            fileCount:
              type: integer
            lastCommit:
              type: string
              format: date-time
            detectionConfidence:
              type: number
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    TemplateMapping:
      type: object
      properties:
        pathPattern:
          type: string
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        confidence:
          type: number
        override:
          type: boolean

    Document:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        filePath:
          type: string
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        extractedMetadata:
          type: object
        detectionConfidence:
          type: number
        processingStatus:
          type: string
          enum: [pending, processed, failed]

    TemplateZone:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        rootPath:
          type: string
        completenessScore:
          type: number
        documentCount:
          type: integer
        visualizationConfig:
          type: object

    Visualization:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        visualizationType:
          type: string
          enum: [tree, pipeline, graph, cross-template]
        mermaidCode:
          type: string
        generationMetadata:
          type: object
          properties:
            generatedAt:
              type: string
              format: date-time
            generationTimeMs:
              type: integer
            nodeCount:
              type: integer
            relationshipCount:
              type: integer
            cacheHit:
              type: boolean

  securitySchemes:
    CognitoAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - CognitoAuth: []
```

## Components

### GitHub Integration Service
**Responsibility:** Handles repository import, OAuth authentication, and file synchronization with GitHub API

**Key Interfaces:**
- POST /projects - Import repository from GitHub URL
- GET /projects/{id}/sync - Refresh repository content
- GitHub OAuth callback handling

**Dependencies:** AWS Cognito (authentication), S3 (file storage), SQS (async processing queue)

**Technology Stack:** Python FastAPI, GitHub API v4 (GraphQL), boto3 for AWS services, asyncio for concurrent file processing

### Template Detection Service
**Responsibility:** Analyzes imported documents to classify template types and extract metadata patterns

**Key Interfaces:**
- POST /template-detection/analyze - Process documents for template classification
- GET /template-detection/rules - Retrieve template matching rules
- PUT /template-detection/mappings - Update project-specific template mappings

**Dependencies:** PostgreSQL (document storage), Redis (caching), Machine Learning models for pattern recognition

**Technology Stack:** Python FastAPI, scikit-learn for classification, spaCy for NLP processing, custom pattern matching engines

### Visualization Generation Service
**Responsibility:** Creates Mermaid diagrams from template-classified documents and relationships

**Key Interfaces:**
- POST /visualizations/generate - Create new visualization from project data
- GET /visualizations/{id}/export - Export visualization in various formats
- PUT /visualizations/{id}/config - Update visualization styling and layout

**Dependencies:** Neo4j (relationship queries), Redis (diagram caching), Mermaid.js (diagram generation)

**Technology Stack:** Python FastAPI, Neo4j driver, Puppeteer for diagram rendering, custom Mermaid template engines

### Search & Relationship Service
**Responsibility:** Provides template-aware search and cross-template relationship detection

**Key Interfaces:**
- GET /projects/{id}/search - Template-aware document search
- POST /relationships/detect - Analyze cross-template connections
- GET /relationships/{id} - Retrieve relationship details with metadata

**Dependencies:** PostgreSQL with pgvector (similarity search), Neo4j (relationship storage), Template Detection Service

**Technology Stack:** Python FastAPI, pgvector for embedding search, sentence-transformers for document embeddings, custom relationship analysis algorithms

### Project Configuration Service
**Responsibility:** Manages project settings, template mappings, and user preferences

**Key Interfaces:**
- GET/PUT /projects/{id}/config - Project configuration management
- POST /projects/{id}/template-mappings - Update template detection rules
- GET /users/{id}/preferences - User-specific configuration settings

**Dependencies:** PostgreSQL (configuration storage), AWS Cognito (user management), Redis (session caching)

**Technology Stack:** Python FastAPI, SQLAlchemy ORM, Pydantic for configuration validation, custom template mapping logic

### Component Diagrams

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

## External APIs

### GitHub API
- **Purpose:** Repository import, file access, and OAuth authentication for DocGraph users
- **Documentation:** https://docs.github.com/en/rest
- **Base URL(s):** https://api.github.com (REST), https://api.github.com/graphql (GraphQL)
- **Authentication:** OAuth 2.0 with GitHub App installation for enhanced rate limits
- **Rate Limits:** 5,000 requests/hour (authenticated), 1,000 requests/hour (GraphQL)

**Key Endpoints Used:**
- `GET /repos/{owner}/{repo}` - Repository metadata and statistics
- `GET /repos/{owner}/{repo}/contents/{path}` - File content retrieval
- `GET /repos/{owner}/{repo}/git/trees/{sha}` - Directory tree structure
- `POST /graphql` - Bulk queries for repository structure and file content

**Integration Notes:** Implements intelligent caching to minimize API calls, uses GraphQL for bulk operations, handles rate limiting with exponential backoff and queue management.

### AWS Cognito
- **Purpose:** User authentication, OAuth integration, and session management
- **Documentation:** https://docs.aws.amazon.com/cognito/
- **Base URL(s):** https://cognito-idp.{region}.amazonaws.com
- **Authentication:** AWS IAM roles with service-to-service authentication
- **Rate Limits:** 10,000 requests/second per user pool

**Key Endpoints Used:**
- `POST /InitiateAuth` - User login and token generation
- `POST /RespondToAuthChallenge` - Multi-factor authentication handling
- `POST /GetUser` - User profile information retrieval
- `POST /RefreshToken` - Token refresh for session management

**Integration Notes:** Integrated with GitHub OAuth for seamless developer experience, supports custom attributes for project preferences and template configurations.

## Core Workflows

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant G as GitHub Service
    participant T as Template Service
    participant V as Visualization Service
    participant DB as Database
    participant GH as GitHub API

    Note over U,GH: Project Import & Template Detection Workflow

    U->>W: Import GitHub repository
    W->>G: POST /projects {githubUrl}
    G->>GH: Authenticate & validate repo
    GH-->>G: Repository metadata
    G->>DB: Store project record
    G->>G: Queue file import job

    Note over G,DB: Async File Processing
    loop For each file in repository
        G->>GH: Fetch file content
        GH-->>G: File data
        G->>DB: Store document
        G->>T: Queue template detection
    end

    T->>DB: Load documents
    T->>T: Analyze template patterns
    T->>DB: Update template classifications
    T->>V: Queue visualization generation

    V->>DB: Query classified documents
    V->>V: Generate Mermaid diagrams
    V->>DB: Store visualizations
    V-->>W: Notify completion

    W-->>U: Project ready notification

    Note over U,V: Template-Aware Exploration Workflow

    U->>W: Explore project visualizations
    W->>V: GET /projects/{id}/visualizations
    V->>DB: Query cached diagrams
    DB-->>V: Visualization data
    V-->>W: Mermaid diagrams
    W->>W: Render interactive visualization

    U->>W: Switch template zones
    W->>V: Request different template view
    V->>DB: Query template-specific data
    V->>V: Generate zone-specific diagram
    V-->>W: Updated visualization

    U->>W: Export to GitHub
    W->>V: POST /visualizations/{id}/export
    V->>V: Generate export format
    V-->>W: Mermaid code
    W-->>U: Download/copy export
```

## Database Schema

### PostgreSQL Schema (Documents & Metadata)

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

### Neo4j Schema (Relationships & Graph Data)

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

## Frontend Architecture

### Component Architecture

#### Component Organization
```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui base components
│   ├── visualization/   # Template-aware visualization components
│   │   ├── MermaidViewer.tsx
│   │   ├── TemplateZoneIndicator.tsx
│   │   └── CrossTemplateLink.tsx
│   ├── navigation/      # Navigation and routing components
│   └── forms/           # Form components with validation
├── pages/               # Next.js pages or React Router routes
│   ├── dashboard/       # Project dashboard
│   ├── project/         # Project exploration views
│   └── import/          # Repository import flow
├── hooks/               # Custom React hooks
│   ├── useProject.ts    # Project data management
│   ├── useVisualization.ts # Visualization state
│   └── useTemplateDetection.ts
├── services/            # API client and external integrations
│   ├── api.ts           # Base API client configuration
│   ├── projects.ts      # Project-related API calls
│   └── visualizations.ts
├── stores/              # Zustand state management
│   ├── projectStore.ts  # Project state
│   ├── visualizationStore.ts
│   └── uiStore.ts       # UI state and preferences
├── types/               # TypeScript type definitions
│   ├── api.ts           # API response types
│   ├── project.ts       # Project domain types
│   └── visualization.ts
└── utils/               # Utility functions
    ├── templateDetection.ts
    ├── mermaidHelpers.ts
    └── formatters.ts
```

#### Component Template
```typescript
import React from 'react';
import { cn } from '@/lib/utils';

interface VisualizationViewerProps {
  projectId: string;
  templateZoneId?: string;
  visualizationType: 'tree' | 'pipeline' | 'graph' | 'cross-template';
  className?: string;
  onExport?: (format: 'mermaid' | 'svg' | 'png') => void;
}

export const VisualizationViewer: React.FC<VisualizationViewerProps> = ({
  projectId,
  templateZoneId,
  visualizationType,
  className,
  onExport
}) => {
  // Component implementation following shadcn/ui patterns
  return (
    <div className={cn('flex flex-col space-y-4', className)}>
      {/* Template-aware visualization component */}
    </div>
  );
};
```

### State Management Architecture

#### State Structure
```typescript
// Project Store
interface ProjectState {
  currentProject: Project | null;
  projects: Project[];
  templateZones: TemplateZone[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentProject: (project: Project) => void;
  loadProject: (projectId: string) => Promise<void>;
  importProject: (githubUrl: string, name: string) => Promise<Project>;
  updateTemplateMapping: (projectId: string, mappings: TemplateMapping[]) => Promise<void>;
}

// Visualization Store
interface VisualizationState {
  visualizations: Map<string, Visualization>;
  currentVisualization: Visualization | null;
  generationProgress: number;
  isGenerating: boolean;

  // Actions
  generateVisualization: (config: VisualizationConfig) => Promise<Visualization>;
  exportVisualization: (id: string, format: ExportFormat) => Promise<string>;
  cacheVisualization: (visualization: Visualization) => void;
}

// UI Store for interface state
interface UIState {
  activeTemplateZone: string | null;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  breadcrumbHistory: BreadcrumbItem[];

  // Actions
  setActiveTemplateZone: (zoneId: string | null) => void;
  addBreadcrumb: (item: BreadcrumbItem) => void;
  toggleSidebar: () => void;
}
```

#### State Management Patterns
- **Optimistic Updates**: UI updates immediately, rollback on API failure
- **Selective Reactivity**: Component subscriptions to specific state slices
- **Persist Configuration**: User preferences and project settings in localStorage
- **Error Boundaries**: Graceful error handling with state recovery
- **Loading States**: Granular loading indicators for different operations

### Routing Architecture

#### Route Organization
```
/                           # Landing page
/dashboard                  # User project dashboard
/projects/import            # Repository import flow
/projects/:id               # Project overview
/projects/:id/explore       # Multi-template exploration
/projects/:id/zones/:zoneId # Template zone specific view
/projects/:id/search        # Template-aware search interface
/projects/:id/config        # Project configuration
/visualizations/:id         # Individual visualization view
/visualizations/:id/export  # Export interface
/settings                   # User preferences
```

#### Protected Route Pattern
```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = []
}) => {
  const { user, isAuthenticated, hasPermissions } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredPermissions.length > 0 && !hasPermissions(requiredPermissions)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

### Frontend Services Layer

#### API Client Setup
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuth } from '@/hooks/useAuth';

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth token
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }

  // Additional HTTP methods...
}

export const apiClient = new ApiClient();
```

#### Service Example
```typescript
import { apiClient } from './api';
import { Project, TemplateZone, Visualization } from '@/types';

export class ProjectService {
  static async getProjects(): Promise<Project[]> {
    return apiClient.get<{ projects: Project[] }>('/projects')
      .then(response => response.projects);
  }

  static async importProject(githubUrl: string, name: string): Promise<Project> {
    return apiClient.post<Project>('/projects', { githubUrl, name });
  }

  static async getTemplateZones(projectId: string): Promise<TemplateZone[]> {
    return apiClient.get<{ templateZones: TemplateZone[] }>(`/projects/${projectId}/template-zones`)
      .then(response => response.templateZones);
  }

  static async generateVisualization(projectId: string, config: VisualizationConfig): Promise<Visualization> {
    return apiClient.post<Visualization>(`/projects/${projectId}/visualizations`, config);
  }

  static async searchDocuments(projectId: string, query: string, filters: SearchFilters): Promise<SearchResult[]> {
    const params = new URLSearchParams({ query, ...filters });
    return apiClient.get<{ results: SearchResult[] }>(`/projects/${projectId}/search?${params}`)
      .then(response => response.results);
  }
}
```

## Backend Architecture

### Service Architecture

#### Function Organization (Serverless)
```
src/
├── handlers/              # Lambda function handlers
│   ├── projects/          # Project management handlers
│   │   ├── import.ts      # POST /projects
│   │   ├── list.ts        # GET /projects
│   │   └── detail.ts      # GET /projects/{id}
│   ├── templates/         # Template detection handlers
│   │   ├── detect.ts      # POST /template-detection/analyze
│   │   └── mappings.ts    # PUT /template-detection/mappings
│   ├── visualizations/    # Visualization generation handlers
│   │   ├── generate.ts    # POST /visualizations/generate
│   │   └── export.ts      # GET /visualizations/{id}/export
│   └── search/            # Search and relationship handlers
│       ├── search.ts      # GET /projects/{id}/search
│       └── relationships.ts # POST /relationships/detect
├── services/              # Business logic services
│   ├── ProjectService.ts  # Project management logic
│   ├── TemplateService.ts # Template detection and classification
│   ├── VisualizationService.ts # Mermaid generation logic
│   └── SearchService.ts   # Search and relationship analysis
├── models/                # Data access layer
│   ├── Project.ts         # Project data model
│   ├── Document.ts        # Document data model
│   └── Visualization.ts   # Visualization data model
├── utils/                 # Shared utilities
│   ├── github.ts          # GitHub API integration
│   ├── mermaid.ts         # Mermaid generation utilities
│   └── embeddings.ts      # Vector embedding utilities
└── types/                 # Shared TypeScript types
    ├── api.ts             # API request/response types
    └── domain.ts          # Domain object types
```

#### Function Template
```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { ProjectService } from '../services/ProjectService';
import { validateRequestBody, createResponse, handleError } from '../utils/api';
import { ImportProjectRequest } from '../types/api';

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    // Extract user context from JWT token
    const userId = event.requestContext.authorizer?.claims?.sub;
    if (!userId) {
      return createResponse(401, { error: 'Unauthorized' });
    }

    // Validate request body
    const body = validateRequestBody<ImportProjectRequest>(event.body);

    // Execute business logic
    const project = await ProjectService.importProject(userId, body);

    return createResponse(201, { project });
  } catch (error) {
    return handleError(error);
  }
};
```

### Database Architecture

#### Schema Design
(See Database Schema section above for complete SQL definitions)

#### Data Access Layer
```typescript
import { Pool } from 'pg';
import { Project, Document, TemplateZone } from '../types/domain';

export class ProjectRepository {
  private pool: Pool;

  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
    });
  }

  async createProject(userId: string, projectData: Partial<Project>): Promise<Project> {
    const query = `
      INSERT INTO projects (user_id, name, github_url, status, metadata)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;

    const values = [
      userId,
      projectData.name,
      projectData.githubUrl,
      'importing',
      JSON.stringify(projectData.metadata || {})
    ];

    const result = await this.pool.query(query, values);
    return this.mapProjectRow(result.rows[0]);
  }

  async findProjectsByUserId(userId: string): Promise<Project[]> {
    const query = `
      SELECT p.*, COUNT(d.id) as document_count
      FROM projects p
      LEFT JOIN documents d ON p.id = d.project_id
      WHERE p.user_id = $1
      GROUP BY p.id
      ORDER BY p.updated_at DESC
    `;

    const result = await this.pool.query(query, [userId]);
    return result.rows.map(this.mapProjectRow);
  }

  async searchDocuments(projectId: string, query: string, templateType?: string): Promise<Document[]> {
    const searchQuery = `
      SELECT d.*, ts_rank(to_tsvector('english', d.content), plainto_tsquery($2)) as rank
      FROM documents d
      WHERE d.project_id = $1
      AND to_tsvector('english', d.content) @@ plainto_tsquery($2)
      ${templateType ? 'AND d.template_type = $3' : ''}
      ORDER BY rank DESC
      LIMIT 20
    `;

    const values = templateType ? [projectId, query, templateType] : [projectId, query];
    const result = await this.pool.query(searchQuery, values);
    return result.rows.map(this.mapDocumentRow);
  }

  private mapProjectRow(row: any): Project {
    return {
      id: row.id,
      userId: row.user_id,
      name: row.name,
      githubUrl: row.github_url,
      status: row.status,
      metadata: row.metadata,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      documentCount: parseInt(row.document_count) || 0,
    };
  }

  private mapDocumentRow(row: any): Document {
    return {
      id: row.id,
      projectId: row.project_id,
      templateZoneId: row.template_zone_id,
      filePath: row.file_path,
      content: row.content,
      templateType: row.template_type,
      extractedMetadata: row.extracted_metadata,
      processingStatus: row.processing_status,
      detectionConfidence: parseFloat(row.detection_confidence),
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }
}
```

### Authentication and Authorization

#### Auth Flow
```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant C as AWS Cognito
    participant G as GitHub
    participant A as API Gateway
    participant L as Lambda Functions

    U->>W: Login request
    W->>C: Initiate GitHub OAuth
    C->>G: Redirect to GitHub OAuth
    G-->>C: Authorization code
    C-->>W: JWT tokens (access + refresh)
    W->>W: Store tokens securely

    Note over U,L: Authenticated API Request Flow

    U->>W: Make API request
    W->>A: Request with Authorization header
    A->>C: Validate JWT token
    C-->>A: Token validation result
    A->>L: Forward request with user context
    L->>L: Process business logic
    L-->>A: Response
    A-->>W: API response
    W-->>U: Updated UI
```

#### Middleware/Guards
```typescript
import { APIGatewayProxyEvent } from 'aws-lambda';
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';

interface AuthContext {
  userId: string;
  email: string;
  permissions: string[];
}

export class AuthMiddleware {
  private jwksClient: jwksClient.JwksClient;

  constructor() {
    this.jwksClient = jwksClient({
      jwksUri: `https://cognito-idp.${process.env.AWS_REGION}.amazonaws.com/${process.env.COGNITO_USER_POOL_ID}/.well-known/jwks.json`,
      cache: true,
      cacheMaxAge: 86400000, // 24 hours
    });
  }

  async validateToken(event: APIGatewayProxyEvent): Promise<AuthContext> {
    const token = this.extractToken(event);
    if (!token) {
      throw new Error('No authorization token provided');
    }

    try {
      const decodedToken = await this.verifyJWT(token);

      return {
        userId: decodedToken.sub,
        email: decodedToken.email,
        permissions: decodedToken['custom:permissions'] || [],
      };
    } catch (error) {
      throw new Error('Invalid or expired token');
    }
  }

  private extractToken(event: APIGatewayProxyEvent): string | null {
    const authHeader = event.headers?.Authorization || event.headers?.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return null;
    }
    return authHeader.substring(7);
  }

  private async verifyJWT(token: string): Promise<any> {
    const decodedHeader = jwt.decode(token, { complete: true });
    if (!decodedHeader || typeof decodedHeader === 'string') {
      throw new Error('Invalid token format');
    }

    const kid = decodedHeader.header.kid;
    const key = await this.jwksClient.getSigningKey(kid);
    const signingKey = key.getPublicKey();

    return jwt.verify(token, signingKey, {
      algorithms: ['RS256'],
      issuer: `https://cognito-idp.${process.env.AWS_REGION}.amazonaws.com/${process.env.COGNITO_USER_POOL_ID}`,
    });
  }
}

// Usage in Lambda handlers
export const requireAuth = (handler: Function) => {
  return async (event: APIGatewayProxyEvent, context: any) => {
    const authMiddleware = new AuthMiddleware();

    try {
      const authContext = await authMiddleware.validateToken(event);

      // Add auth context to event for use in handler
      (event as any).authContext = authContext;

      return handler(event, context);
    } catch (error) {
      return {
        statusCode: 401,
        body: JSON.stringify({ error: error.message }),
      };
    }
  };
};
```

## Unified Project Structure

```plaintext
docgraph/
├── .github/                        # CI/CD workflows and GitHub configuration
│   └── workflows/
│       ├── ci.yaml                 # Continuous integration pipeline
│       ├── deploy-staging.yaml     # Staging environment deployment
│       └── deploy-production.yaml  # Production deployment pipeline
├── apps/                           # Application packages
│   ├── web/                        # React frontend application
│   │   ├── src/
│   │   │   ├── components/         # Reusable UI components
│   │   │   │   ├── ui/             # shadcn/ui base components
│   │   │   │   ├── visualization/  # Template-aware visualization
│   │   │   │   ├── navigation/     # Navigation components
│   │   │   │   └── forms/          # Form components
│   │   │   ├── pages/              # Application pages/routes
│   │   │   │   ├── dashboard/      # Project dashboard
│   │   │   │   ├── project/        # Project exploration views
│   │   │   │   └── import/         # Repository import flow
│   │   │   ├── hooks/              # Custom React hooks
│   │   │   │   ├── useProject.ts   # Project data management
│   │   │   │   ├── useVisualization.ts
│   │   │   │   └── useAuth.ts      # Authentication hook
│   │   │   ├── services/           # API client services
│   │   │   │   ├── api.ts          # Base API configuration
│   │   │   │   ├── projects.ts     # Project API calls
│   │   │   │   └── visualizations.ts
│   │   │   ├── stores/             # Zustand state management
│   │   │   │   ├── projectStore.ts # Project state
│   │   │   │   ├── visualizationStore.ts
│   │   │   │   └── uiStore.ts      # UI preferences
│   │   │   ├── styles/             # Tailwind CSS styles
│   │   │   └── utils/              # Frontend utilities
│   │   ├── public/                 # Static assets
│   │   ├── tests/                  # Frontend tests (Vitest)
│   │   ├── next.config.js          # Next.js configuration
│   │   ├── tailwind.config.js      # Tailwind configuration
│   │   └── package.json
│   └── api/                        # Python FastAPI backend
│       ├── src/
│       │   ├── handlers/           # Lambda function handlers
│       │   │   ├── projects/       # Project management endpoints
│       │   │   ├── templates/      # Template detection endpoints
│       │   │   ├── visualizations/ # Visualization generation
│       │   │   └── search/         # Search and relationships
│       │   ├── services/           # Business logic services
│       │   │   ├── ProjectService.py
│       │   │   ├── TemplateService.py
│       │   │   ├── VisualizationService.py
│       │   │   └── SearchService.py
│       │   ├── models/             # Data access layer
│       │   │   ├── Project.py      # Project data model
│       │   │   ├── Document.py     # Document data model
│       │   │   └── database.py     # Database connections
│       │   ├── utils/              # Backend utilities
│       │   │   ├── github.py       # GitHub API integration
│       │   │   ├── mermaid.py      # Mermaid generation
│       │   │   └── embeddings.py   # Vector embeddings
│       │   └── types/              # Python type definitions
│       ├── tests/                  # Backend tests (pytest)
│       ├── requirements.txt        # Python dependencies
│       └── serverless.yml          # Serverless Framework config
├── packages/                       # Shared packages
│   ├── shared/                     # Shared TypeScript types and utilities
│   │   ├── src/
│   │   │   ├── types/              # Shared type definitions
│   │   │   │   ├── project.ts      # Project domain types
│   │   │   │   ├── visualization.ts # Visualization types
│   │   │   │   └── api.ts          # API contract types
│   │   │   ├── constants/          # Shared constants
│   │   │   │   ├── templateTypes.ts
│   │   │   │   └── apiEndpoints.ts
│   │   │   └── utils/              # Shared utility functions
│   │   │       ├── validation.ts   # Input validation
│   │   │       └── formatting.ts   # Data formatting
│   │   └── package.json
│   ├── ui/                         # Shared UI component library
│   │   ├── src/
│   │   │   ├── components/         # Reusable components
│   │   │   │   ├── TemplateZoneIndicator/
│   │   │   │   ├── MermaidViewer/
│   │   │   │   └── CrossTemplateLink/
│   │   │   └── styles/             # Component styles
│   │   └── package.json
│   └── config/                     # Shared configuration
│       ├── eslint/                 # ESLint configurations
│       │   ├── base.js
│       │   ├── react.js
│       │   └── node.js
│       ├── typescript/             # TypeScript configurations
│       │   ├── base.json
│       │   ├── react.json
│       │   └── node.json
│       └── jest/                   # Jest test configurations
├── infrastructure/                 # AWS CDK infrastructure definitions
│   ├── lib/
│   │   ├── database-stack.ts       # PostgreSQL and Neo4j setup
│   │   ├── api-stack.ts            # API Gateway and Lambda functions
│   │   ├── frontend-stack.ts       # CloudFront and S3 setup
│   │   └── monitoring-stack.ts     # CloudWatch and alerting
│   ├── bin/
│   │   └── docgraph.ts             # CDK app entry point
│   ├── cdk.json                    # CDK configuration
│   └── package.json
├── scripts/                        # Build and deployment scripts
│   ├── build.sh                    # Full project build
│   ├── deploy-staging.sh           # Staging deployment
│   ├── deploy-production.sh        # Production deployment
│   └── setup-dev.sh                # Development environment setup
├── docs/                           # Project documentation
│   ├── prd.md                      # Product Requirements Document
│   ├── front-end-spec.md           # UI/UX Specification
│   ├── architecture.md             # This document
│   └── api-documentation.md        # API reference
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── nx.json                         # Nx monorepo configuration
├── package.json                    # Root package.json with workspace config
├── README.md                       # Project overview and setup
└── tsconfig.json                   # Root TypeScript configuration
```

## Development Workflow

### Local Development Setup

#### Prerequisites
```bash
# Install Node.js 18+ and npm
node --version  # Should be 18+
npm --version

# Install Python 3.11+ and pip
python3 --version  # Should be 3.11+
pip3 --version

# Install Docker for local services
docker --version
docker-compose --version

# Install AWS CLI for deployment
aws --version

# Install Nx CLI for monorepo management
npm install -g nx
```

#### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd docgraph

# Install all dependencies (uses nx to manage monorepo)
npm install

# Copy environment template
cp .env.example .env.local

# Start local development services (PostgreSQL, Neo4j, Redis)
docker-compose up -d

# Run database migrations
npm run db:migrate

# Install Python dependencies for API
cd apps/api
pip install -r requirements.txt
cd ../..

# Build shared packages
nx build shared
nx build ui
```

#### Development Commands
```bash
# Start all services in development mode
nx run-many --target=dev --all

# Start frontend only
nx dev web

# Start backend only
nx dev api

# Run tests
nx run-many --target=test --all

# Run specific app tests
nx test web
nx test api

# Lint all projects
nx run-many --target=lint --all

# Build for production
nx run-many --target=build --all
```

### Environment Configuration

#### Required Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_BASE_URL=http://localhost:3001
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
NEXT_PUBLIC_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx

# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/docgraph_dev
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=development
REDIS_URL=redis://localhost:6379
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Shared
NODE_ENV=development
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
S3_BUCKET_NAME=docgraph-dev-storage
```

## Deployment Architecture

### Deployment Strategy

**Frontend Deployment:**
- **Platform:** Vercel with Next.js deployment optimization
- **Build Command:** `nx build web`
- **Output Directory:** `apps/web/.next`
- **CDN/Edge:** Vercel Edge Network with global caching

**Backend Deployment:**
- **Platform:** AWS Lambda with Serverless Framework
- **Build Command:** `nx build api && serverless package`
- **Deployment Method:** Infrastructure as Code with AWS CDK

### CI/CD Pipeline
```yaml
name: DocGraph CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      neo4j:
        image: neo4j:5.15
        env:
          NEO4J_AUTH: neo4j/test_password
        options: >-
          --health-cmd "cypher-shell 'RETURN 1'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build shared packages
        run: |
          nx build shared
          nx build ui

      - name: Lint all projects
        run: nx run-many --target=lint --all

      - name: Test frontend
        run: nx test web --coverage

      - name: Test backend
        run: |
          cd apps/api
          pip install -r requirements.txt
          pytest --cov=src tests/

      - name: Build applications
        run: nx run-many --target=build --all

  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    needs: test
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy infrastructure
        run: |
          cd infrastructure
          npm install
          npx cdk deploy --all --require-approval never

      - name: Deploy backend
        run: |
          cd apps/api
          npm install -g serverless
          serverless deploy --stage staging

      - name: Deploy frontend
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--env NODE_ENV=staging'

  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        run: |
          # Production deployment steps
          echo "Deploying to production..."
          # Add production deployment logic
```

### Environments
| Environment | Frontend URL | Backend URL | Purpose |
|-------------|-------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:3001 | Local development and testing |
| Staging | https://staging.docgraph.dev | https://api-staging.docgraph.dev | Pre-production testing and demos |
| Production | https://app.docgraph.dev | https://api.docgraph.dev | Live production environment |

## Security and Performance

### Security Requirements

**Frontend Security:**
- CSP Headers: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;`
- XSS Prevention: Content sanitization for user inputs, React's built-in XSS protection, secure innerHTML alternatives
- Secure Storage: JWT tokens in httpOnly cookies, sensitive data encryption, no localStorage for authentication tokens

**Backend Security:**
- Input Validation: Pydantic models for request validation, SQL injection prevention with parameterized queries, file upload restrictions
- Rate Limiting: API Gateway throttling (1000 req/min per user), Lambda concurrency limits, Redis-based rate limiting for expensive operations
- CORS Policy: Restricted origins based on environment, credentials support for authenticated requests, preflight request handling

**Authentication Security:**
- Token Storage: JWT access tokens (15min expiry), refresh tokens (7 days), automatic token rotation
- Session Management: AWS Cognito session management, secure logout with token revocation, concurrent session limits
- Password Policy: GitHub OAuth only (no custom passwords), MFA support through GitHub, secure account linking

### Performance Optimization

**Frontend Performance:**
- Bundle Size Target: <500KB initial bundle, code splitting by route, dynamic imports for heavy components
- Loading Strategy: Progressive enhancement, skeleton screens, lazy loading for visualizations, service worker caching
- Caching Strategy: Static asset caching (1 year), API response caching (5 minutes), visualization caching with invalidation

**Backend Performance:**
- Response Time Target: <200ms for simple queries, <2000ms for visualization generation, <5000ms for Mermaid export
- Database Optimization: Connection pooling, query optimization with EXPLAIN ANALYZE, index optimization for common queries
- Caching Strategy: Redis caching for template detection (1 hour), visualization caching (24 hours), GitHub API response caching (15 minutes)

## Testing Strategy

### Testing Pyramid
```
        E2E Tests (10%)
       /              \
      Integration Tests (30%)
     /                    \
  Frontend Unit (30%)   Backend Unit (30%)
```

### Test Organization

#### Frontend Tests
```
apps/web/tests/
├── components/           # Component unit tests
│   ├── ui/              # shadcn/ui component tests
│   ├── visualization/   # Visualization component tests
│   └── navigation/      # Navigation component tests
├── hooks/               # Custom hook tests
│   ├── useProject.test.ts
│   ├── useVisualization.test.ts
│   └── useAuth.test.ts
├── services/            # API service tests
│   ├── projects.test.ts
│   └── visualizations.test.ts
├── stores/              # State management tests
│   ├── projectStore.test.ts
│   └── visualizationStore.test.ts
├── utils/               # Utility function tests
└── __mocks__/           # Test mocks and fixtures
```

#### Backend Tests
```
apps/api/tests/
├── unit/                # Unit tests
│   ├── services/        # Service layer tests
│   ├── models/          # Data model tests
│   └── utils/           # Utility tests
├── integration/         # Integration tests
│   ├── handlers/        # Lambda handler tests
│   ├── database/        # Database integration tests
│   └── github/          # GitHub API integration tests
├── fixtures/            # Test data fixtures
│   ├── projects.json
│   ├── documents.json
│   └── visualizations.json
└── conftest.py          # pytest configuration
```

#### E2E Tests
```
e2e/
├── specs/               # Test specifications
│   ├── project-import.spec.ts
│   ├── visualization-generation.spec.ts
│   └── cross-template-navigation.spec.ts
├── fixtures/            # Test data
├── page-objects/        # Page object models
└── playwright.config.ts
```

### Test Examples

#### Frontend Component Test
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { VisualizationViewer } from '@/components/visualization/VisualizationViewer';
import { useVisualization } from '@/hooks/useVisualization';

// Mock the hook
vi.mock('@/hooks/useVisualization');
const mockUseVisualization = vi.mocked(useVisualization);

describe('VisualizationViewer', () => {
  const mockVisualization = {
    id: '123',
    mermaidCode: 'graph TD\nA-->B',
    visualizationType: 'tree' as const,
    generationMetadata: {
      generatedAt: new Date(),
      generationTimeMs: 1500,
      nodeCount: 10,
      relationshipCount: 5,
      cacheHit: false,
    },
  };

  beforeEach(() => {
    mockUseVisualization.mockReturnValue({
      visualization: mockVisualization,
      isLoading: false,
      error: null,
      generateVisualization: vi.fn(),
      exportVisualization: vi.fn(),
    });
  });

  it('renders visualization with Mermaid diagram', async () => {
    render(
      <VisualizationViewer
        projectId="project-123"
        visualizationType="tree"
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('img', { name: /mermaid diagram/i })).toBeInTheDocument();
    });

    expect(screen.getByText('10 nodes')).toBeInTheDocument();
    expect(screen.getByText('5 relationships')).toBeInTheDocument();
  });

  it('handles export functionality', async () => {
    const mockExport = vi.fn().mockResolvedValue('exported-content');
    mockUseVisualization.mockReturnValue({
      ...mockUseVisualization(),
      exportVisualization: mockExport,
    });

    render(
      <VisualizationViewer
        projectId="project-123"
        visualizationType="tree"
        onExport={vi.fn()}
      />
    );

    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    expect(mockExport).toHaveBeenCalledWith('123', 'mermaid');
  });
});
```

#### Backend API Test
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app
from src.services.ProjectService import ProjectService

client = TestClient(app)

class TestProjectEndpoints:
    @pytest.fixture
    def mock_auth_context(self):
        return {
            "userId": "user-123",
            "email": "test@example.com",
            "permissions": []
        }

    @patch.object(ProjectService, 'import_project')
    def test_import_project_success(self, mock_import, mock_auth_context):
        # Arrange
        mock_project = {
            "id": "project-123",
            "name": "Test Project",
            "github_url": "https://github.com/user/repo",
            "status": "importing"
        }
        mock_import.return_value = mock_project

        # Act
        response = client.post(
            "/projects",
            json={
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["project"]["name"] == "Test Project"
        assert data["project"]["status"] == "importing"
        mock_import.assert_called_once_with(
            "user-123",
            {
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            }
        )

    def test_import_project_unauthorized(self):
        # Act
        response = client.post(
            "/projects",
            json={
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            }
        )

        # Assert
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["error"]

    @patch.object(ProjectService, 'search_documents')
    def test_search_documents(self, mock_search, mock_auth_context):
        # Arrange
        mock_results = [
            {
                "document": {
                    "id": "doc-123",
                    "filePath": "docs/prd.md",
                    "templateType": "bmad-method"
                },
                "relevanceScore": 0.95,
                "matchContext": "...project requirements..."
            }
        ]
        mock_search.return_value = mock_results

        # Act
        response = client.get(
            "/projects/project-123/search?query=requirements&templateType=bmad-method",
            headers={"Authorization": "Bearer valid-token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["document"]["templateType"] == "bmad-method"
```

#### E2E Test
```typescript
import { test, expect } from '@playwright/test';

test.describe('Project Import and Visualization', () => {
  test('complete project import and visualization workflow', async ({ page }) => {
    // Navigate to application
    await page.goto('/dashboard');

    // Import new project
    await page.click('button:has-text("Import Project")');
    await page.fill('input[name="githubUrl"]', 'https://github.com/test/magnet');
    await page.fill('input[name="name"]', 'Magnet Test Project');
    await page.click('button:has-text("Import")');

    // Wait for import completion
    await page.waitForSelector('text=Project imported successfully', { timeout: 30000 });

    // Navigate to project
    await page.click('text=Magnet Test Project');

    // Wait for template detection
    await page.waitForSelector('text=Template detection complete', { timeout: 60000 });

    // Verify template zones are detected
    await expect(page.locator('[data-testid="template-zone-bmad-method"]')).toBeVisible();
    await expect(page.locator('[data-testid="template-zone-claude-code"]')).toBeVisible();

    // Generate tree visualization
    await page.click('[data-testid="visualization-type-tree"]');
    await page.waitForSelector('[data-testid="mermaid-diagram"]', { timeout: 10000 });

    // Verify visualization is generated
    const diagram = page.locator('[data-testid="mermaid-diagram"]');
    await expect(diagram).toBeVisible();

    // Test export functionality
    await page.click('button:has-text("Export")');
    await page.click('text=Mermaid Code');

    // Verify export dialog
    const exportDialog = page.locator('[data-testid="export-dialog"]');
    await expect(exportDialog).toBeVisible();

    const mermaidCode = page.locator('[data-testid="export-content"]');
    await expect(mermaidCode).toContainText('graph TD');

    // Test cross-template navigation
    await page.click('[data-testid="template-zone-claude-code"]');
    await page.waitForSelector('[data-testid="claude-code-visualization"]');

    // Verify context preservation
    await expect(page.locator('[data-testid="breadcrumb"]')).toContainText('Claude Code');
    await expect(page.locator('[data-testid="template-indicator"]')).toHaveClass(/claude-code/);
  });

  test('handles large repository import gracefully', async ({ page }) => {
    await page.goto('/dashboard');

    // Import large repository
    await page.click('button:has-text("Import Project")');
    await page.fill('input[name="githubUrl"]', 'https://github.com/large/repository');
    await page.fill('input[name="name"]', 'Large Repository');
    await page.click('button:has-text("Import")');

    // Verify progressive loading indicators
    await expect(page.locator('[data-testid="import-progress"]')).toBeVisible();

    // Wait for processing to complete (extended timeout for large repos)
    await page.waitForSelector('text=Project ready', { timeout: 120000 });

    // Verify performance meets requirements
    const startTime = Date.now();
    await page.click('[data-testid="generate-visualization"]');
    await page.waitForSelector('[data-testid="mermaid-diagram"]');
    const endTime = Date.now();

    // Visualization should generate within 2 seconds per requirements
    expect(endTime - startTime).toBeLessThan(2000);
  });
});
```

## Coding Standards

### Critical Fullstack Rules

- **Type Sharing:** Always define shared types in packages/shared and import from there - prevents type drift between frontend and backend
- **API Calls:** Never make direct HTTP calls in components - use the service layer for consistent error handling and caching
- **Environment Variables:** Access only through config objects, never process.env directly - ensures proper validation and type safety
- **Error Handling:** All API routes must use the standard error handler - maintains consistent error response format
- **State Updates:** Never mutate state directly - use proper state management patterns with immutable updates
- **Database Queries:** Always use the repository pattern - prevents SQL injection and provides testing abstraction
- **Authentication:** Never bypass auth middleware - all protected routes must validate JWT tokens
- **Caching:** Use Redis for all caching operations - ensures consistent cache invalidation and performance
- **File Uploads:** Validate file types and sizes - prevents security vulnerabilities and storage abuse
- **Logging:** Use structured logging with correlation IDs - enables effective debugging and monitoring

### Naming Conventions
| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Components | PascalCase | - | `VisualizationViewer.tsx` |
| Hooks | camelCase with 'use' | - | `useProjectData.ts` |
| API Routes | - | kebab-case | `/api/template-zones` |
| Database Tables | - | snake_case | `cross_template_relationships` |
| Service Methods | camelCase | snake_case | `generateVisualization` / `generate_visualization` |
| Environment Variables | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `GITHUB_API_KEY` |
| Constants | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |
| Interfaces | PascalCase with 'I' prefix | - | `IVisualizationConfig` |

## Error Handling Strategy

### Error Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Gateway
    participant L as Lambda
    participant S as Service
    participant D as Database

    C->>A: API Request
    A->>L: Forward Request
    L->>S: Business Logic Call
    S->>D: Database Query
    D-->>S: Database Error
    S->>S: Transform Error
    S-->>L: Service Error
    L->>L: Format Error Response
    L-->>A: Structured Error
    A-->>C: HTTP Error Response
    C->>C: Display User-Friendly Error
```

### Error Response Format
```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: Record<string, any>; // Additional error context
    timestamp: string;      // ISO 8601 timestamp
    requestId: string;      // Correlation ID for debugging
    path?: string;          // API endpoint that failed
    statusCode: number;     // HTTP status code
  };
}

// Example error responses
const examples = {
  validation: {
    error: {
      code: 'VALIDATION_ERROR',
      message: 'Invalid request parameters',
      details: {
        field: 'githubUrl',
        constraint: 'Must be a valid GitHub repository URL'
      },
      timestamp: '2025-09-24T10:30:00.000Z',
      requestId: 'req-123456789',
      path: '/api/projects',
      statusCode: 400
    }
  },
  notFound: {
    error: {
      code: 'RESOURCE_NOT_FOUND',
      message: 'Project not found',
      details: {
        resourceType: 'project',
        resourceId: 'project-123'
      },
      timestamp: '2025-09-24T10:30:00.000Z',
      requestId: 'req-123456789',
      path: '/api/projects/project-123',
      statusCode: 404
    }
  },
  serverError: {
    error: {
      code: 'INTERNAL_SERVER_ERROR',
      message: 'An unexpected error occurred',
      timestamp: '2025-09-24T10:30:00.000Z',
      requestId: 'req-123456789',
      path: '/api/visualizations/generate',
      statusCode: 500
    }
  }
};
```

### Frontend Error Handling
```typescript
import { toast } from '@/components/ui/use-toast';
import { ApiError } from '@/types/api';

class ErrorHandler {
  static handleApiError(error: ApiError, context?: string) {
    const { code, message, details } = error.error;

    // Log error for debugging
    console.error(`API Error [${code}]:`, {
      message,
      details,
      context,
      requestId: error.error.requestId
    });

    // Show user-friendly error message
    switch (code) {
      case 'VALIDATION_ERROR':
        toast({
          title: 'Invalid Input',
          description: message,
          variant: 'destructive',
        });
        break;

      case 'RESOURCE_NOT_FOUND':
        toast({
          title: 'Not Found',
          description: 'The requested resource could not be found.',
          variant: 'destructive',
        });
        break;

      case 'RATE_LIMIT_EXCEEDED':
        toast({
          title: 'Rate Limit Exceeded',
          description: 'Please wait before making another request.',
          variant: 'destructive',
        });
        break;

      case 'INTERNAL_SERVER_ERROR':
      default:
        toast({
          title: 'Something went wrong',
          description: 'Please try again later or contact support.',
          variant: 'destructive',
        });

        // Report to error monitoring service
        this.reportError(error, context);
        break;
    }
  }

  static reportError(error: ApiError, context?: string) {
    // Send to monitoring service (DataDog, Sentry, etc.)
    if (typeof window !== 'undefined' && window.datadog) {
      window.datadog.addError(error, {
        context,
        requestId: error.error.requestId,
        userAgent: navigator.userAgent,
        url: window.location.href
      });
    }
  }

  static handleNetworkError(error: Error) {
    console.error('Network Error:', error);

    toast({
      title: 'Connection Error',
      description: 'Please check your internet connection and try again.',
      variant: 'destructive',
    });
  }
}

// Usage in API service
export class ApiService {
  async request<T>(config: RequestConfig): Promise<T> {
    try {
      const response = await this.httpClient.request(config);
      return response.data;
    } catch (error) {
      if (error.response) {
        // Server responded with error
        ErrorHandler.handleApiError(error.response.data, config.url);
      } else if (error.request) {
        // Network error
        ErrorHandler.handleNetworkError(error);
      } else {
        // Request setup error
        console.error('Request Error:', error.message);
      }
      throw error;
    }
  }
}
```

### Backend Error Handling
```python
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Custom exception classes
class DocGraphError(Exception):
    def __init__(self, code: str, message: str, details: Optional[Dict] = None, status_code: int = 500):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

class ValidationError(DocGraphError):
    def __init__(self, message: str, field: str, constraint: str):
        super().__init__(
            code='VALIDATION_ERROR',
            message=message,
            details={'field': field, 'constraint': constraint},
            status_code=400
        )

class ResourceNotFoundError(DocGraphError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code='RESOURCE_NOT_FOUND',
            message=f'{resource_type.title()} not found',
            details={'resourceType': resource_type, 'resourceId': resource_id},
            status_code=404
        )

class RateLimitError(DocGraphError):
    def __init__(self, limit: int, window: str):
        super().__init__(
            code='RATE_LIMIT_EXCEEDED',
            message=f'Rate limit of {limit} requests per {window} exceeded',
            details={'limit': limit, 'window': window},
            status_code=429
        )

# Error handler middleware
class ErrorHandler:
    @staticmethod
    def create_error_response(
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict] = None,
        path: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        error_data = {
            'error': {
                'code': code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'requestId': request_id or str(uuid.uuid4()),
                'statusCode': status_code
            }
        }

        if details:
            error_data['error']['details'] = details
        if path:
            error_data['error']['path'] = path

        # Log error for monitoring
        logging.error(f"API Error [{code}]: {message}", extra={
            'error_code': code,
            'status_code': status_code,
            'details': details,
            'request_id': error_data['error']['requestId'],
            'path': path
        })

        return JSONResponse(
            status_code=status_code,
            content=error_data
        )

    @staticmethod
    def handle_docgraph_error(error: DocGraphError, path: str, request_id: str) -> JSONResponse:
        return ErrorHandler.create_error_response(
            code=error.code,
            message=error.message,
            status_code=error.status_code,
            details=error.details,
            path=path,
            request_id=request_id
        )

    @staticmethod
    def handle_unexpected_error(error: Exception, path: str, request_id: str) -> JSONResponse:
        # Log full exception for debugging
        logging.exception(f"Unexpected error in {path}", extra={
            'request_id': request_id,
            'path': path,
            'error_type': type(error).__name__
        })

        return ErrorHandler.create_error_response(
            code='INTERNAL_SERVER_ERROR',
            message='An unexpected error occurred',
            status_code=500,
            path=path,
            request_id=request_id
        )

# Usage in Lambda handlers
def lambda_handler(event, context):
    request_id = str(uuid.uuid4())
    path = event.get('path', '')

    try:
        # Business logic here
        result = process_request(event)
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id
            }
        }

    except DocGraphError as e:
        return ErrorHandler.handle_docgraph_error(e, path, request_id).body

    except Exception as e:
        return ErrorHandler.handle_unexpected_error(e, path, request_id).body

# Usage in service classes
class ProjectService:
    def get_project(self, project_id: str, user_id: str) -> Project:
        project = self.repository.find_by_id(project_id)

        if not project:
            raise ResourceNotFoundError('project', project_id)

        if project.user_id != user_id:
            raise DocGraphError(
                code='FORBIDDEN',
                message='Access denied to this project',
                status_code=403
            )

        return project

    def import_project(self, user_id: str, github_url: str, name: str) -> Project:
        # Validate GitHub URL
        if not self._is_valid_github_url(github_url):
            raise ValidationError(
                message='Invalid GitHub repository URL',
                field='githubUrl',
                constraint='Must be a valid GitHub repository URL'
            )

        # Check rate limits
        if self._is_rate_limited(user_id):
            raise RateLimitError(limit=10, window='hour')

        # Process import
        return self._create_project(user_id, github_url, name)
```

## Monitoring and Observability

### Monitoring Stack
- **Frontend Monitoring:** Vercel Analytics + DataDog RUM for client-side performance and error tracking
- **Backend Monitoring:** AWS CloudWatch + DataDog APM for server-side performance and infrastructure metrics
- **Error Tracking:** DataDog Error Tracking with source map support for both frontend and backend
- **Performance Monitoring:** DataDog Synthetic Monitoring for end-to-end user journey validation

### Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP <2.5s, FID <100ms, CLS <0.1) for user experience optimization
- JavaScript errors and unhandled promise rejections for reliability tracking
- API response times from client perspective for performance monitoring
- User interactions and feature adoption rates for product insights

**Backend Metrics:**
- Request rate per endpoint and service for capacity planning
- Error rate by service and error type for reliability monitoring
- P50/P95/P99 response times for performance SLA compliance
- Database query performance and connection pool utilization for optimization
- GitHub API rate limit consumption and remaining quota for integration health
- Template detection accuracy and processing time for core feature monitoring
- Mermaid diagram generation time and cache hit rates for visualization performance

## Checklist Results Report

*This section will be populated after running the architect-checklist against this document to validate architectural completeness and design quality.*