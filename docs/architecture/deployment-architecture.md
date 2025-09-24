# Deployment Architecture

## Deployment Strategy

**Local Docker Deployment:**
- **Platform:** Docker containers with docker-compose orchestration
- **Build Command:** `docker-compose build`
- **Deployment Method:** Local development environment with mapped volumes
- **Storage:** Docker volumes mapped to project directory structure for persistence

**Application Architecture:**
- **Frontend Container:** React application served via nginx
- **Backend Container:** FastAPI application
- **PostgreSQL Container:** PostgreSQL with pgvector extension for documents and embeddings
- **Neo4j Container:** Neo4j graph database for relationships and connections
- **Redis Container:** Redis for caching and session storage
- **Volume Mapping:** `/app/data` -> `./data` for persistent storage and repository files

## CI/CD Pipeline
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

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
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

      - name: Build Docker images
        run: docker-compose build

      - name: Test Docker deployment
        run: |
          docker-compose up -d
          sleep 30
          docker-compose exec web curl http://localhost:3000/health
          docker-compose down

  integration-test:
    if: github.ref == 'refs/heads/develop' || github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --exit-code-from test
```

## Environments
| Environment | Frontend URL | Backend URL | Purpose |
|-------------|-------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:8000 | Local Docker development |
| Test | http://localhost:3001 | http://localhost:8001 | Local Docker testing |
