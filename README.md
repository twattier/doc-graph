# DocGraph

DocGraph is an AI-powered document insight engine that helps you extract knowledge from documents and discover connections between them.

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
- **Git** for repository operations

### Development Setup (Docker-Only)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd doc-graph
   ```

2. **Copy environment configuration**
   ```bash
   cp .env.example .env
   ```

3. **Start the full application stack**
   ```bash
   # Start all services (databases + applications)
   docker-compose up --build

   # Or run in background
   docker-compose up -d --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7475
   - Database services running on configured ports

## 🏗️ Architecture

DocGraph is built as a monorepo with the following structure:

```
doc-graph/
├── apps/
│   ├── web/                 # React frontend application
│   └── api/                 # FastAPI backend application
├── packages/
│   ├── shared/             # Shared TypeScript types
│   └── ui/                 # Shared UI component library
├── scripts/                # Database initialization scripts
└── data/                   # Local development data (gitignored)
```

### Technology Stack

**Frontend:**
- React 19 with TypeScript
- Vite for build tooling
- Tailwind CSS + shadcn/ui components
- Zustand for state management
- Vitest + React Testing Library for testing

**Backend:**
- FastAPI with Python 3.11+
- PostgreSQL with pgvector for document storage
- Neo4j for knowledge graph relationships
- Redis for caching and sessions
- pytest for testing

**Development:**
- Docker-first development environment
- Docker Compose for complete application stack
- GitHub Actions for CI/CD

## 📊 Database Services

The application uses three database services:

### PostgreSQL (Port 5433)
- **Purpose**: Primary document storage with vector embeddings
- **Access**: `postgresql://docgraph_user:secure_dev_password@localhost:5433/docgraph_dev`
- **Features**: pgvector extension for semantic search

### Neo4j (Port 7475/7688)
- **Purpose**: Knowledge graph for document relationships
- **Access**: http://localhost:7475 (browser), bolt://localhost:7688 (driver)
- **Credentials**: neo4j / secure_dev_neo4j_password

### Redis (Port 6380)
- **Purpose**: Caching and session management
- **Access**: localhost:6380
- **Password**: secure_dev_redis_password

## 🛠️ Development Commands (Docker-Based)

### Application Management
```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs [web|api|postgres|neo4j|redis]

# Restart specific service
docker-compose restart [web|api]

# Rebuild and restart service
docker-compose up --build [web|api]
```

### Development Workflow
```bash
# View real-time logs for debugging
docker-compose logs -f api
docker-compose logs -f web

# Execute commands inside containers
docker-compose exec api python -m pytest tests/
docker-compose exec web npm run test

# Access container shell for debugging
docker-compose exec api bash
docker-compose exec web sh
```

### Database Management
```bash
# Start database services
docker-compose -f docker-compose.dev.yml up -d

# Stop database services
docker-compose -f docker-compose.dev.yml down

# View database logs
docker-compose -f docker-compose.dev.yml logs [postgres|neo4j|redis]

# Reset all data (WARNING: This will delete all data)
docker-compose -f docker-compose.dev.yml down -v
rm -rf data/
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm run test

# Run frontend tests with watch mode
cd apps/web && npm test -- --watch

# Run backend tests with coverage
cd apps/api && pytest --cov=src --cov-report=html
```

### Test Structure

**Frontend Tests:**
- `apps/web/src/**/*.spec.tsx` - Component tests
- `apps/web/src/**/*.test.tsx` - Integration tests

**Backend Tests:**
- `apps/api/tests/unit/` - Unit tests
- `apps/api/tests/integration/` - Integration tests
- `apps/api/tests/fixtures/` - Test fixtures

## 🚀 Deployment

### Building for Production

```bash
# Build all projects
npm run build

# Build specific project
npm run build --workspace=apps/web
npm run build --workspace=apps/api
```

### Docker Production Build

```bash
# Build and run full stack
docker-compose up --build

# Build individual services
docker-compose build web
docker-compose build api
```

## 📝 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /health` - Health check
- `GET /api/documents` - List documents
- `POST /api/documents` - Create document
- `GET /api/documents/{id}` - Get specific document

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Key configuration options:

**Frontend (apps/web/.env.local):**
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Backend (.env):**
```env
DATABASE_URL=postgresql://docgraph_user:secure_dev_password@localhost:5433/docgraph_dev
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_dev_neo4j_password
REDIS_URL=redis://:secure_dev_redis_password@localhost:6380
JWT_SECRET=generate-secure-random-key-for-development
```

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5433  # PostgreSQL
lsof -i :7688  # Neo4j
lsof -i :6380  # Redis
```

**Database connection issues:**
```bash
# Check database health
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs postgres
```

**Python dependencies:**
```bash
# Reinstall backend dependencies
cd apps/api
pip install --upgrade pip
pip install -r requirements.txt
```

**Node.js dependencies:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules apps/*/node_modules packages/*/node_modules
npm install
```

### Performance Tips

1. **Use Docker BuildKit** for faster builds:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Database performance**: The databases persist data in `./data/` directory for faster restarts

3. **Hot reloading**: Both frontend and backend support hot reloading in development

## 🤝 Contributing

1. Follow the existing code style
2. Write tests for new features
3. Ensure all tests pass: `npm run test`
4. Update documentation as needed

### Code Style

- **TypeScript**: Use strict mode and proper typing
- **Python**: Follow PEP 8, use type hints
- **Components**: Use functional components with hooks
- **API**: Follow RESTful conventions

## 📄 License

This project is licensed under the MIT License.