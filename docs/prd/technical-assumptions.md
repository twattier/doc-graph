# Technical Assumptions

## Repository Structure: Monorepo
DocGraph will use a monorepo structure with clear frontend/backend separation, shared type definitions, and unified build processes for efficient development and deployment.

## Service Architecture
**Microservices approach within monorepo architecture** featuring:
- **Document Processing Service**: GitHub import, template detection, and content parsing
- **Template Management Service**: Template rule configuration and mapping logic
- **Visualization Service**: Mermaid diagram generation and rendering
- **Search Service**: Template-aware indexing and query processing
- **API Gateway**: Unified interface for frontend communication

## Testing Requirements
**Full testing pyramid approach** including:
- **Unit Testing**: Component-level testing for all services and frontend components
- **Integration Testing**: Template detection accuracy, GitHub API integration, Mermaid generation
- **End-to-End Testing**: Complete user workflows using Magnet project as validation target
- **Performance Testing**: Load testing for visualization rendering and diagram generation times
- **Template Validation Testing**: Accuracy testing across various BMAD-METHOD and Claude Code project structures

## Additional Technical Assumptions and Requests
- **GitHub API Rate Limiting**: Implementation of intelligent caching and request optimization to stay within API limits
- **Mermaid.js Integration**: Native integration for client-side diagram rendering with server-side generation capabilities
- **Template Rule Engine**: Configurable system for pattern matching and classification without requiring code changes
- **pgvector + Neo4j Hybrid**: Document embeddings in pgvector for search, graph relationships in Neo4j for visualization
- **OAuth Security**: GitHub authentication with minimal scope requirements (public repository read access only)
- **FastAPI Backend**: Python-based API with pydantic validation and agentic framework compatibility
- **React + shadcn/ui Frontend**: Modern component library with TypeScript for type safety
- **Container Orchestration**: Docker-based deployment with Kubernetes readiness for scaling
