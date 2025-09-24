# Security and Performance

## Security Requirements

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

## Performance Optimization

**Frontend Performance:**
- Bundle Size Target: <500KB initial bundle, code splitting by route, dynamic imports for heavy components
- Loading Strategy: Progressive enhancement, skeleton screens, lazy loading for visualizations, service worker caching
- Caching Strategy: Static asset caching (1 year), API response caching (5 minutes), visualization caching with invalidation

**Backend Performance:**
- Response Time Target: <200ms for simple queries, <2000ms for visualization generation, <5000ms for Mermaid export
- Database Optimization: Connection pooling, query optimization with EXPLAIN ANALYZE, index optimization for common queries
- Caching Strategy: Redis caching for template detection (1 hour), visualization caching (24 hours), GitHub API response caching (15 minutes)
