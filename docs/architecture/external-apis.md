# External APIs

## GitHub API
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

## AWS Cognito
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
