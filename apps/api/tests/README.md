# DocGraph Git Repository Import System Tests

This directory contains comprehensive tests for the DocGraph Git Repository Import System (Story 1.2) using the real GitHub repository: https://github.com/twattier/magnet

## Test Structure

### Test Categories

1. **Integration Tests** (`integration/test_magnet_repository_import.py`)
   - Complete repository import workflow testing
   - URL validation for magnet repository
   - Repository analysis and metadata extraction
   - File counting and structure preservation
   - Progress tracking during import

2. **End-to-End Tests** (`e2e/test_magnet_user_journey.py`)
   - Complete user journey from login to file browsing
   - Repository import initiation and progress tracking
   - Repository listing and details retrieval
   - File browsing and directory navigation
   - Authentication and authorization flows

3. **Repository Structure Tests** (`unit/test_magnet_repository_structure.py`)
   - Magnet-specific repository structure validation
   - JavaScript file detection and analysis
   - Package.json parsing and metadata extraction
   - Documentation file detection
   - Build configuration file recognition

4. **Error Handling Tests** (`unit/test_magnet_error_handling.py`)
   - Network timeout simulation
   - Repository not found scenarios
   - Authentication failures
   - Rate limiting behavior
   - Storage space exhaustion
   - Database connection failures

5. **Performance Tests** (`performance/test_magnet_performance_and_rate_limiting.py`)
   - Rate limiting enforcement and behavior
   - Concurrent import performance
   - Large repository handling
   - Memory usage during operations
   - Database query performance

6. **Real Git Operations** (`real_git/test_magnet_real_git_operations.py`)
   - Actual Git operations against the real magnet repository
   - Real network operations (requires internet connectivity)
   - Validation against live repository data

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, mocked dependencies)
- `@pytest.mark.integration` - Integration tests (multiple components)
- `@pytest.mark.e2e` - End-to-end tests (full user workflows)
- `@pytest.mark.performance` - Performance and load tests
- `@pytest.mark.real_git` - Real Git operations (requires internet)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.magnet` - Tests specific to magnet repository

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests by Category
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# End-to-end tests
pytest -m e2e

# Performance tests
pytest -m performance

# Real Git operations (requires internet)
pytest -m real_git
```

### Run Tests by Directory
```bash
# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Unit tests
pytest tests/unit/

# Performance tests
pytest tests/performance/

# Real Git operations
pytest tests/real_git/
```

### Run Specific Test Files
```bash
# Magnet repository import tests
pytest tests/integration/test_magnet_repository_import.py

# User journey tests
pytest tests/e2e/test_magnet_user_journey.py

# Repository structure tests
pytest tests/unit/test_magnet_repository_structure.py

# Error handling tests
pytest tests/unit/test_magnet_error_handling.py

# Performance tests
pytest tests/performance/test_magnet_performance_and_rate_limiting.py

# Real Git operations
pytest tests/real_git/test_magnet_real_git_operations.py
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Fast Tests Only (excluding slow tests)
```bash
pytest -m "not slow"
```

### Run Tests Excluding Real Git Operations
```bash
pytest -m "not real_git"
```

## Test Requirements

### Standard Tests (Mocked)
- No internet connectivity required
- All Git operations are mocked
- Fast execution
- Safe for CI/CD pipelines

### Real Git Tests
- Internet connectivity required
- Access to GitHub (github.com)
- Slower execution
- Should be run separately for validation

## Test Data

The tests use the real magnet repository (https://github.com/twattier/magnet) which provides:
- JavaScript/Node.js project structure
- Package.json configuration
- Source code in src/ directory
- Test files in test/ directory
- Documentation files (README.md, docs/)
- Build configuration (webpack.config.js, .eslintrc.js)

## Expected Test Coverage

The test suite validates:

### Repository Import Workflow
- [x] URL validation for GitHub repositories
- [x] Complete import process from URL to completion
- [x] Background task processing
- [x] Progress tracking and status updates
- [x] Repository metadata extraction

### Repository Analysis
- [x] File structure preservation
- [x] File counting accuracy
- [x] Size calculation correctness
- [x] Branch and commit hash extraction
- [x] Description extraction from README

### User Experience
- [x] User authentication and authorization
- [x] Repository listing and pagination
- [x] Repository details retrieval
- [x] File browsing and navigation
- [x] Repository synchronization

### Error Handling
- [x] Network timeouts and connectivity issues
- [x] Invalid repository URLs
- [x] Authentication failures
- [x] Rate limiting enforcement
- [x] Storage space management
- [x] Concurrent access control

### Performance
- [x] Rate limiting behavior (10 imports per minute)
- [x] Concurrent import handling
- [x] Large repository processing
- [x] Memory usage optimization
- [x] Database query efficiency

## Test Fixtures

### Common Fixtures
- `git_service` - GitService instance
- `repository_service` - RepositoryService instance
- `mock_user` - Test user data
- `mock_magnet_repo_info` - Expected magnet repository data
- `temp_storage_path` - Temporary directory for file operations

### Mock Data
- Realistic magnet repository structure
- Package.json with correct metadata
- JavaScript source files
- Test files with proper naming
- Documentation files

## CI/CD Integration

### Fast Test Suite (CI Pipeline)
```bash
# Run all tests except real Git operations
pytest -m "not real_git and not slow" --cov=src
```

### Full Test Suite (Nightly Build)
```bash
# Run all tests including real Git operations
pytest --cov=src --cov-report=html
```

### Performance Validation
```bash
# Run performance tests only
pytest -m performance --tb=short
```

## Test Maintenance

### Adding New Tests
1. Follow the existing test structure and naming conventions
2. Use appropriate pytest markers
3. Mock external dependencies for unit tests
4. Include both positive and negative test cases
5. Add performance considerations for slow operations

### Updating Tests
1. Update tests when API changes occur
2. Maintain backward compatibility where possible
3. Update expected data when magnet repository structure changes
4. Review and update performance benchmarks periodically

### Test Data Updates
If the magnet repository structure changes significantly:
1. Update mock data in test fixtures
2. Update expected file counts and sizes
3. Update expected metadata and descriptions
4. Validate real Git tests still pass