# Development Workflow

## Local Development Setup

### Prerequisites
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

### Initial Setup
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

### Development Commands
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

## Environment Configuration

### Required Environment Variables
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
