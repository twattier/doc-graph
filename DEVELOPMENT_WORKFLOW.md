# Development Workflow - User Story Branching Strategy

## Overview
This document outlines the development workflow for implementing user stories with proper branching, validation, and merge processes.

**IMPORTANT**: This application runs entirely in Docker containers. All development, testing, and building must be done within the Docker environment - no local npm or Python commands.

## Branching Strategy

### Branch Naming Convention
- **Feature branches**: `story/{story-id}-{short-description}`
- **Example**: `story/1.2-user-authentication`
- **Hotfix branches**: `hotfix/{issue-id}-{short-description}`
- **Release branches**: `release/{version}`

### Workflow Process

#### 1. Story Development Start
```bash
# Create new branch for user story
git checkout master
git pull origin master
git checkout -b story/{story-id}-{short-description}

# Example:
git checkout -b story/1.2-user-authentication
```

#### 2. Development Phase
- Implement story requirements following acceptance criteria
- Make frequent, atomic commits with descriptive messages
- Run tests in Docker containers before committing
- Follow coding standards and architecture guidelines
- All development and testing done within Docker environment

#### 3. Story Validation Checklist
Before considering a story complete, ensure:

**Technical Validation:**
- [ ] All acceptance criteria implemented
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Type checking passes (TypeScript/mypy)
- [ ] Linting passes without errors
- [ ] No security vulnerabilities introduced
- [ ] Performance requirements met

**Code Quality:**
- [ ] Code follows project coding standards
- [ ] Proper error handling implemented
- [ ] Documentation updated if needed
- [ ] No hard-coded values or secrets
- [ ] Proper logging added where appropriate

**Story Completeness:**
- [ ] All tasks/subtasks completed
- [ ] Dev notes updated with implementation details
- [ ] Any architectural decisions documented
- [ ] Breaking changes noted if applicable

#### 4. Pre-Merge Process
```bash
# Ensure branch is up to date with master
git checkout master
git pull origin master
git checkout story/{story-id}-{short-description}
git rebase master

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run full test suite in containers
docker-compose -f docker-compose.dev.yml exec web npm test
docker-compose -f docker-compose.dev.yml exec api pytest tests/

# Run linting and type checking in containers
docker-compose -f docker-compose.dev.yml exec web npm run lint
docker-compose -f docker-compose.dev.yml exec web npm run type-check
docker-compose -f docker-compose.dev.yml exec api python -m mypy src/

# Build and verify no errors
docker-compose -f docker-compose.dev.yml exec web npm run build

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

#### 5. Merge to Master
```bash
# Switch to master and merge
git checkout master
git merge story/{story-id}-{short-description}

# Push to remote
git push origin master

# Clean up feature branch
git branch -d story/{story-id}-{short-description}
git push origin --delete story/{story-id}-{short-description}
```

## Story Status Tracking

### Story States
- **Backlog**: Story defined but not started
- **In Progress**: Development actively underway
- **Code Review**: Development complete, awaiting review
- **Testing**: Undergoing QA validation
- **Done**: Merged to master, validation complete

### Documentation Requirements
Each story must maintain:
1. **Status updates** in story file
2. **Dev notes** with implementation details
3. **Change log** with version history
4. **QA results** when validation complete

## Quality Gates

### Gate 1: Development Complete
- All acceptance criteria implemented
- Docker container tests passing
- Code follows standards
- Ready for code review

### Gate 2: Review Complete
- Code review approved
- Integration tests passing
- Security review passed
- Ready for QA validation

### Gate 3: Story Done
- QA validation complete
- All tests passing in CI/CD
- Documentation updated
- Ready for production deployment

## Docker-First Development

### Prerequisites
- Docker and Docker Compose installed
- No local Node.js or Python required
- All development happens inside containers

### Container Architecture
- **web**: Frontend React application with Vite
- **api**: Backend FastAPI application
- **postgres**: PostgreSQL database with pgvector
- **neo4j**: Neo4j graph database
- **redis**: Redis cache

## Commands Reference

### Development Commands
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests in containers
docker-compose -f docker-compose.dev.yml exec web npm test
docker-compose -f docker-compose.dev.yml exec api pytest tests/

# Build applications in containers
docker-compose -f docker-compose.dev.yml exec web npm run build

# Lint and format in containers
docker-compose -f docker-compose.dev.yml exec web npm run lint
docker-compose -f docker-compose.dev.yml exec api black src/
docker-compose -f docker-compose.dev.yml exec api flake8 src/

# Access container shells for development
docker-compose -f docker-compose.dev.yml exec web bash
docker-compose -f docker-compose.dev.yml exec api bash

# View logs
docker-compose -f docker-compose.dev.yml logs -f web
docker-compose -f docker-compose.dev.yml logs -f api

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

### Git Commands
```bash
# Create story branch
git checkout -b story/{id}-{description}

# Commit with conventional format
git commit -m "feat(story-{id}): implement {feature}"

# Rebase before merge
git rebase master

# Merge to master
git checkout master && git merge story/{id}-{description}
```

## CI/CD Integration

### Automated Checks
All branches automatically run:
- Unit and integration tests
- Code linting and formatting checks
- Security vulnerability scanning
- Type checking
- Build verification

### Merge Requirements
To merge to master:
- All CI/CD checks must pass
- Code review approval required
- Story validation checklist complete
- No merge conflicts

## Emergency Procedures

### Hotfix Process
For critical production issues:
```bash
# Create hotfix branch from master
git checkout master
git checkout -b hotfix/{issue-id}-{description}

# Implement fix and test
# ... development work ...

# Merge directly to master after validation
git checkout master
git merge hotfix/{issue-id}-{description}
git push origin master

# Clean up
git branch -d hotfix/{issue-id}-{description}
```

### Rollback Process
If issues found after merge:
```bash
# Revert the merge commit
git revert -m 1 {merge-commit-hash}
git push origin master

# Create new story branch to fix issues
git checkout -b story/{id}-{description}-fix
```

This workflow ensures:
- **Quality**: Comprehensive validation before merge
- **Traceability**: Clear story progression tracking
- **Safety**: Protected master branch with validation gates
- **Consistency**: Standardized process for all development