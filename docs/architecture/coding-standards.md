# Coding Standards

## Critical Fullstack Rules

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

## Naming Conventions
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
