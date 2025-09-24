# Epic 1: Foundation & Template Discovery Engine

**Epic Goal:** Establish the foundational infrastructure and core template detection capabilities that enable DocGraph to successfully import, parse, and classify the Magnet project's dual BMAD-METHOD and Claude Code structure, demonstrating the fundamental value proposition of template-aware documentation discovery.

## Story 1.1: Project Infrastructure Setup
As a **developer**,
I want **a fully configured development environment with project scaffolding**,
so that **I can begin building DocGraph features with proper tooling, testing, and deployment pipelines in place**.

### Acceptance Criteria
1. Monorepo structure established with frontend (React + shadcn/ui) and backend (Python FastAPI) separation
2. Docker containerization configured for both development and production environments
3. CI/CD pipeline configured with automated testing and deployment workflows
4. Database services (pgvector + Neo4j) containerized and integrated
5. Basic health check endpoints operational with monitoring capabilities
6. TypeScript and Python type checking integrated into development workflow
7. Testing frameworks configured (Jest/Vitest for frontend, pytest for backend)

## Story 1.2: GitHub Repository Import System
As a **project decision maker**,
I want **to import the Magnet project repository through a simple URL input**,
so that **I can access all project documentation for template-aware analysis**.

### Acceptance Criteria
1. Web interface accepts GitHub repository URLs with validation
2. OAuth authentication system integrated for GitHub API access
3. Repository content downloaded and stored locally with proper error handling
4. File structure preserved maintaining original directory relationships
5. Import progress indicators show real-time status to users
6. Successful import of `./projects/magnet` repository structure verified
7. Rate limiting and caching implemented for GitHub API interactions

## Story 1.3: BMAD-METHOD Template Detection
As a **system**,
I want **to automatically detect BMAD-METHOD documentation patterns**,
so that **I can classify Magnet project's `/docs` directory content appropriately**.

### Acceptance Criteria
1. Template detection engine identifies standard BMAD-METHOD files (INITIAL.md, brief.md, prd.md, architecture.md, front-end-spec.md)
2. Workflow progression sequence detected and mapped (brainstorming→PRD→architecture→UX)
3. Document metadata extracted including creation dates, version information, and content structure
4. Cross-document references identified and cataloged for relationship mapping
5. Magnet project `/docs` directory successfully classified with 95% accuracy
6. Template confidence scores calculated and reported for each detected document
7. Unrecognized files appropriately categorized as generic documentation

## Story 1.4: Claude Code Template Detection
As a **system**,
I want **to automatically detect Claude Code configuration patterns**,
So that **I can classify Magnet project's `.bmad-core` directory structure appropriately**.

### Acceptance Criteria
1. Agent hierarchy detection from `.bmad-core/agents/` directory with role identification
2. Task relationship mapping from `.bmad-core/tasks/` with dependency analysis
3. Template structure analysis from `.bmad-core/templates/` with usage pattern detection
4. Workflow configuration parsing from `.bmad-core/workflows/` directory
5. Agent-team relationship mapping from `.bmad-core/agent-teams/` configurations
6. Magnet project `.bmad-core` structure successfully parsed with complete relationship mapping
7. Configuration validation ensuring detected patterns match Claude Code specifications

## Story 1.5: Template Mapping Configuration Interface
As a **project decision maker**,
I want **to review and adjust template detection results**,
so that **I can ensure DocGraph correctly interprets my project's documentation structure**.

### Acceptance Criteria
1. Template detection results displayed in clear, reviewable interface
2. Override capabilities provided for incorrect template classifications
3. Custom template mapping rules can be defined and saved per project
4. Validation system prevents conflicting or invalid template assignments
5. Configuration changes immediately reflected in template processing
6. Magnet project template mappings successfully reviewed and confirmed accurate
7. Template mapping decisions exported and importable for reuse across similar projects
