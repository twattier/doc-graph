#!/bin/bash

# DocGraph Git Repository Import System Test Runner
# Story 1.2 - Magnet Repository Test Suite
#
# This script runs all tests inside Docker containers for consistent environment
# and proper database/service integration. The API container will be automatically
# started if not already running.

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to print section headers
print_header() {
    echo
    print_color $BLUE "============================================="
    print_color $BLUE "$1"
    print_color $BLUE "============================================="
    echo
}

# Function to run tests with error handling inside Docker container
run_tests() {
    local test_command=$1
    local test_name=$2

    print_color $YELLOW "Running: $test_name"
    echo "Docker Command: docker-compose exec $API_SERVICE_NAME $test_command"
    echo

    # Ensure API container is running
    if ! check_api_container; then
        print_color $YELLOW "API container is not running. Starting it now..."
        if ! docker-compose up -d "$API_SERVICE_NAME"; then
            print_color $RED "Failed to start API container"
            return 1
        fi

        # Wait for container to be ready
        print_color $YELLOW "Waiting for API container to be ready..."
        sleep 10
    fi

    # Run tests inside the container
    if docker-compose exec -T "$API_SERVICE_NAME" bash -c "cd /app && $test_command"; then
        print_color $GREEN "✓ $test_name completed successfully"
    else
        print_color $RED "✗ $test_name failed"
        return 1
    fi
    echo
}

# Default test suite selection
SUITE="all"
COVERAGE=false
VERBOSE=false
REAL_GIT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--suite)
            SUITE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -r|--real-git)
            REAL_GIT=true
            shift
            ;;
        -h|--help)
            echo "DocGraph Git Repository Import System Test Runner (Docker Mode)"
            echo ""
            echo "This script runs tests inside the Docker API container for the magnet repository import system."
            echo "The API container will be automatically started if not already running."
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -s, --suite SUITE     Test suite to run (all, unit, integration, e2e, performance, real-git)"
            echo "  -c, --coverage        Run tests with coverage reporting"
            echo "  -v, --verbose         Run tests in verbose mode"
            echo "  -r, --real-git        Include real Git operations (requires internet)"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Requirements:"
            echo "  - Docker and docker-compose must be installed and running"
            echo "  - Must be run from the project root directory"
            echo "  - API service must be defined in docker-compose.yml"
            echo ""
            echo "Test Suites:"
            echo "  all          Run all tests (excluding real-git unless specified)"
            echo "  unit         Run unit tests only"
            echo "  integration  Run integration tests only"
            echo "  e2e          Run end-to-end tests only"
            echo "  performance  Run performance tests only"
            echo "  real-git     Run real Git operations tests only"
            echo "  fast         Run fast tests only (unit + integration, no slow tests)"
            echo "  ci           Run CI-suitable tests (all except real-git and slow)"
            echo ""
            echo "Examples:"
            echo "  $0                           # Run all tests in Docker (excluding real-git)"
            echo "  $0 -s unit                   # Run unit tests only inside API container"
            echo "  $0 -s integration -c         # Run integration tests with coverage reporting"
            echo "  $0 -r -v                     # Run all tests including real-git with verbose output"
            echo "  $0 -s ci -c                  # Run CI tests with coverage (suitable for pipelines)"
            echo "  $0 -s fast                   # Run fast tests only (unit + integration, no slow tests)"
            echo ""
            echo "Note: All tests run inside the Docker API container for consistent environment."
            echo "Database services (PostgreSQL, Neo4j, Redis) are automatically available."
            exit 0
            ;;
        *)
            print_color $RED "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

# Add coverage options
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html:htmlcov"
fi

# Add verbose option
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD --tb=short"
fi

print_header "DocGraph Git Repository Import System - Magnet Repository Tests"

print_color $BLUE "Test Configuration:"
print_color $YELLOW "  Suite: $SUITE"
print_color $YELLOW "  Coverage: $COVERAGE"
print_color $YELLOW "  Verbose: $VERBOSE"
print_color $YELLOW "  Real Git: $REAL_GIT"
print_color $YELLOW "  Docker Mode: Enabled (tests run inside API container)"
print_color $YELLOW "  Docker Compose File: $DOCKER_COMPOSE_FILE"
print_color $YELLOW "  API Service: $API_SERVICE_NAME"
echo

# Check Docker environment
print_color $BLUE "Checking Docker environment..."
if ! docker info &> /dev/null; then
    print_color $RED "Error: Docker daemon is not running"
    exit 1
fi

print_color $GREEN "✓ Docker is available and running"

# Check if compose file exists
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    print_color $RED "Error: Docker Compose file '$DOCKER_COMPOSE_FILE' not found in $(pwd)"
    exit 1
fi

print_color $GREEN "✓ Docker Compose file found"
echo

# Function to check if API container is running
check_api_container() {
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$API_SERVICE_NAME" | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Run tests based on selected suite
case $SUITE in
    "unit")
        print_header "Running Unit Tests"
        run_tests "$PYTEST_CMD -m unit" "Unit Tests"
        ;;

    "integration")
        print_header "Running Integration Tests"
        run_tests "$PYTEST_CMD -m integration" "Integration Tests"
        ;;

    "e2e")
        print_header "Running End-to-End Tests"
        run_tests "$PYTEST_CMD -m e2e" "End-to-End Tests"
        ;;

    "performance")
        print_header "Running Performance Tests"
        run_tests "$PYTEST_CMD -m performance" "Performance Tests"
        ;;

    "real-git")
        print_header "Running Real Git Operations Tests"
        print_color $YELLOW "Warning: These tests require internet connectivity and will access GitHub"
        print_color $YELLOW "Press Ctrl+C within 5 seconds to cancel..."
        sleep 5
        run_tests "$PYTEST_CMD -m real_git" "Real Git Operations Tests"
        ;;

    "fast")
        print_header "Running Fast Tests"
        run_tests "$PYTEST_CMD -m \"unit or integration\" -m \"not slow\"" "Fast Tests (Unit + Integration, no slow tests)"
        ;;

    "ci")
        print_header "Running CI Tests"
        run_tests "$PYTEST_CMD -m \"not real_git and not slow\"" "CI Tests (All except real-git and slow)"
        ;;

    "all")
        print_header "Running All Tests"

        # Unit tests
        run_tests "$PYTEST_CMD -m unit" "Unit Tests"

        # Integration tests
        run_tests "$PYTEST_CMD -m integration" "Integration Tests"

        # End-to-end tests
        run_tests "$PYTEST_CMD -m e2e" "End-to-End Tests"

        # Performance tests
        run_tests "$PYTEST_CMD -m performance" "Performance Tests"

        # Real Git tests (only if explicitly requested)
        if [ "$REAL_GIT" = true ]; then
            print_color $YELLOW "Warning: About to run real Git operations tests"
            print_color $YELLOW "These tests require internet connectivity and will access GitHub"
            print_color $YELLOW "Press Ctrl+C within 5 seconds to cancel..."
            sleep 5
            run_tests "$PYTEST_CMD -m real_git" "Real Git Operations Tests"
        else
            print_color $BLUE "Skipping Real Git Operations Tests (use -r to include them)"
        fi
        ;;

    *)
        print_color $RED "Error: Unknown test suite '$SUITE'"
        print_color $YELLOW "Available suites: all, unit, integration, e2e, performance, real-git, fast, ci"
        exit 1
        ;;
esac

print_header "Test Execution Complete"

if [ "$COVERAGE" = true ]; then
    print_color $GREEN "Coverage report generated in htmlcov/ directory"
    if command -v open &> /dev/null; then
        print_color $BLUE "Opening coverage report..."
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        print_color $BLUE "Opening coverage report..."
        xdg-open htmlcov/index.html
    else
        print_color $YELLOW "Open htmlcov/index.html in your browser to view coverage report"
    fi
fi

print_color $GREEN "All requested tests completed successfully!"
print_color $BLUE "For more detailed output, use the -v (verbose) option"

# Summary of test files created
print_header "Test Suite Summary"
print_color $BLUE "DocGraph Git Repository Import System - Comprehensive Test Suite (Docker Mode):"
print_color $YELLOW "  • Integration Tests: apps/api/tests/integration/test_magnet_repository_import.py"
print_color $YELLOW "  • End-to-End Tests: apps/api/tests/e2e/test_magnet_user_journey.py"
print_color $YELLOW "  • Structure Tests: apps/api/tests/unit/test_magnet_repository_structure.py"
print_color $YELLOW "  • Error Handling: apps/api/tests/unit/test_magnet_error_handling.py"
print_color $YELLOW "  • Performance Tests: apps/api/tests/performance/test_magnet_performance_and_rate_limiting.py"
print_color $YELLOW "  • Real Git Tests: apps/api/tests/real_git/test_magnet_real_git_operations.py"
print_color $YELLOW "  • Documentation: apps/api/tests/README.md"
print_color $YELLOW "  • Docker Test Runner: apps/api/tests/run_tests.sh"
echo
print_color $GREEN "Test Target: BMad Method framework - https://github.com/twattier/magnet"
print_color $GREEN "Docker Integration: Tests run in isolated API container with full service stack"
print_color $GREEN "Test Coverage: Complete repository import workflow validation for real BMad framework"
echo
print_color $BLUE "Docker Services Available During Tests:"
print_color $YELLOW "  • PostgreSQL (Repository metadata storage)"
print_color $YELLOW "  • Neo4j (Graph database for relationships)"
print_color $YELLOW "  • Redis (Caching and rate limiting)"
print_color $YELLOW "  • FastAPI (Repository import API)"