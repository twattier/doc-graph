# Deployment Architecture

## Deployment Strategy

**Frontend Deployment:**
- **Platform:** Vercel with Next.js deployment optimization
- **Build Command:** `nx build web`
- **Output Directory:** `apps/web/.next`
- **CDN/Edge:** Vercel Edge Network with global caching

**Backend Deployment:**
- **Platform:** AWS Lambda with Serverless Framework
- **Build Command:** `nx build api && serverless package`
- **Deployment Method:** Infrastructure as Code with AWS CDK

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

## Environments
| Environment | Frontend URL | Backend URL | Purpose |
|-------------|-------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:3001 | Local development and testing |
| Staging | https://staging.docgraph.dev | https://api-staging.docgraph.dev | Pre-production testing and demos |
| Production | https://app.docgraph.dev | https://api.docgraph.dev | Live production environment |
