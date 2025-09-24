"""
Repository-specific tests for magnet repository structure validation - Story 1.2 Git Repository Import System

This test suite validates repository structure detection, file counting, metadata extraction,
and other magnet repository-specific functionality.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

from src.services.git_service import GitService, GitRepositoryInfo, GitOperationError


class TestMagnetRepositoryStructure:
    """Tests specific to magnet repository structure and characteristics."""

    MAGNET_REPO_URL = "https://github.com/twattier/magnet"

    @pytest.fixture
    def git_service(self):
        """Create GitService instance for testing."""
        return GitService()

    @pytest.fixture
    def magnet_repository_structure(self):
        """Create a realistic BMad framework structure based on the real magnet repository."""
        return {
            # BMad core configuration files
            ".bmad-core/core-config.yaml": """
markdownExploder: true
qa:
  qaLocation: "docs/qa"
prd:
  prdFile: "docs/prd.md"
  prdVersion: "v4"
  prdSharded: true
  prdShardedLocation: "docs/prd"
architecture:
  architectureFile: "docs/architecture.md"
  architectureVersion: "v4"
  architectureSharded: true
  architectureShardedLocation: "docs/architecture"
devLoadAlwaysFiles:
  - "docs/architecture/coding-standards.md"
  - "docs/architecture/tech-stack.md"
  - "docs/architecture/source-tree.md"
devDebugLog: ".ai/debug-log.md"
devStoryLocation: "docs/stories"
slashPrefix: "BMad"
            """,

            ".bmad-core/user-guide.md": """# BMad Method — User Guide

This guide will help you understand and effectively use the BMad Method for agile AI-driven planning and development.

## Overview

The BMad Method is an AI-driven development methodology that combines structured planning with intelligent execution to deliver high-quality software solutions.

## Core Components

- **Planning Phase**: Define stories, requirements, and technical specifications
- **Development Workflow**: AI-assisted development with quality gates
- **Documentation**: Living documentation that evolves with the codebase
- **Quality Assurance**: Automated testing and validation processes

## Getting Started

1. Configure your project with `.bmad-core/core-config.yaml`
2. Define your requirements in the `docs/` directory
3. Use Claude commands for development tasks
4. Maintain quality with automated gates

## Documentation Structure

See the various `.md` files in the documentation hierarchy for detailed guidance.
            """,

            ".bmad-core/install-manifest.yaml": """
name: magnet
version: 1.0.0
type: bmad-method
install_date: 2024-01-01T00:00:00Z
components:
  - core-config
  - user-guide
  - claude-commands
  - documentation-templates
requirements:
  - claude-code
  - markdown-support
  - yaml-support
            """,

            ".bmad-core/enhanced-ide-development-workflow.md": """# Enhanced IDE Development Workflow

This document outlines the enhanced development workflow for BMad Method projects.

## Workflow Overview

1. **Story Definition**: Create user stories in `docs/stories/`
2. **Technical Planning**: Define architecture and technical specifications
3. **Development**: Use Claude commands for implementation
4. **Quality Gates**: Run automated tests and validations
5. **Documentation**: Update living documentation

## Tools and Commands

- Use `/BMad` commands for common development tasks
- Leverage AI-assisted code generation and review
- Maintain quality with automated testing frameworks

## Best Practices

- Keep documentation up to date
- Use structured story formats
- Implement quality gates at each stage
- Leverage AI for code review and optimization
            """,

            ".bmad-core/working-in-the-brownfield.md": """# Working in the Brownfield

This guide covers best practices for applying BMad Method to existing codebases.

## Brownfield Challenges

- Legacy code integration
- Existing architecture constraints
- Technical debt management
- Gradual methodology adoption

## Strategies

1. **Incremental Adoption**: Start with new features and modules
2. **Documentation First**: Document existing systems before changes
3. **Quality Gates**: Implement testing for modified components
4. **Refactoring Plans**: Create structured improvement roadmaps

## Tools

- Code analysis and mapping tools
- Automated testing frameworks
- Documentation generation utilities
- Quality measurement dashboards
            """,

            # Claude commands for BMad
            ".claude/commands/BMad/tasks/create-story.md": """# Create Story Command

## Overview
Creates a new user story with proper BMad Method structure.

## Usage
```
/BMad create-story "Story Title" --epic="Epic Name" --priority=high
```

## Template Structure
- Story overview and acceptance criteria
- Technical requirements
- Quality gates and testing approach
- Documentation requirements

## Integration
Automatically integrates with:
- Story tracking system
- Documentation hierarchy
- Quality assurance framework
            """,

            ".claude/commands/BMad/tasks/generate-docs.md": """# Generate Documentation Command

## Overview
Generates comprehensive documentation from code and story definitions.

## Usage
```
/BMad generate-docs --type=api --format=markdown
```

## Features
- API documentation generation
- Architecture diagram creation
- Story-to-implementation traceability
- Quality metrics reporting

## Output Formats
- Markdown documentation
- HTML reports
- PDF exports
- Interactive dashboards
            """,

            ".claude/commands/BMad/tasks/run-quality-gates.md": """# Run Quality Gates Command

## Overview
Executes comprehensive quality checks and gates for BMad Method projects.

## Usage
```
/BMad run-quality-gates --stage=pre-commit --verbose
```

## Quality Checks
- Code quality and standards compliance
- Test coverage analysis
- Documentation completeness
- Architecture compliance
- Security vulnerability scanning

## Integration
- CI/CD pipeline integration
- Git hooks and pre-commit checks
- IDE real-time validation
- Quality dashboards and reporting
            """,

            ".claude/commands/BMad/tasks/deploy-environment.md": """# Deploy Environment Command

## Overview
Deployment automation for BMad Method projects across environments.

## Usage
```
/BMad deploy-environment --target=staging --validate=true
```

## Deployment Targets
- Development environment setup
- Staging environment deployment
- Production environment management
- Testing environment provisioning

## Validation
- Environment health checks
- Configuration validation
- Performance benchmarking
- Security compliance verification
            """,

            # Documentation files
            "docs/architecture.md": """# BMad Method Architecture Documentation

## Overview

The BMad Method framework provides a structured approach to AI-driven software development.

## Core Components

### Configuration Management
- `.bmad-core/core-config.yaml`: Central configuration
- Environment-specific overrides
- Feature flags and toggles

### Documentation Hierarchy
- Architecture documentation
- User guides and tutorials
- API references
- Story definitions

### Quality Assurance
- Automated testing frameworks
- Quality gates and validations
- Continuous integration pipelines
- Performance monitoring

### Development Workflow
- Story-driven development
- AI-assisted code generation
- Collaborative review processes
- Documentation-first approach
            """,

            "docs/getting-started.md": """# Getting Started with BMad Method

## Prerequisites

- Claude Code IDE or compatible environment
- Markdown and YAML support
- Git version control system

## Initial Setup

1. **Configure Core Settings**
   ```yaml
   # .bmad-core/core-config.yaml
   markdownExploder: true
   qa:
     qaLocation: "docs/qa"
   ```

2. **Create Documentation Structure**
   - `docs/stories/` - User stories and requirements
   - `docs/architecture/` - Technical architecture
   - `docs/qa/` - Quality assurance documentation

3. **Set Up Claude Commands**
   - Install BMad command suite
   - Configure project-specific commands
   - Test command integration

## First Steps

1. Create your first story using `/BMad create-story`
2. Define technical requirements
3. Set up quality gates
4. Begin development with AI assistance
            """,

            # Quality assurance documentation
            "docs/qa/testing-strategy.md": """# Testing Strategy

## Overview

Comprehensive testing approach for BMad Method projects.

## Testing Levels

### Unit Testing
- Component-level validation
- Business logic verification
- Edge case handling

### Integration Testing
- Service integration validation
- API contract testing
- Database interaction testing

### System Testing
- End-to-end workflow validation
- Performance testing
- Security testing

### Acceptance Testing
- Story completion validation
- User acceptance criteria
- Business value verification

## Quality Metrics

- Code coverage targets
- Performance benchmarks
- Security compliance scores
- Documentation completeness
            """,

            "docs/stories/sample-story.md": """# Sample User Story

## Story Overview

As a development team, we want to implement BMad Method practices so that we can deliver higher quality software with AI assistance.

## Acceptance Criteria

- [ ] Core configuration is properly set up
- [ ] Documentation structure is established
- [ ] Quality gates are functioning
- [ ] Claude commands are integrated
- [ ] Team training is completed

## Technical Requirements

- YAML configuration support
- Markdown processing capabilities
- Claude Code integration
- Quality assurance automation

## Quality Gates

- Configuration validation
- Documentation completeness check
- Command integration testing
- User acceptance validation

## Definition of Done

- All acceptance criteria met
- Technical requirements implemented
- Quality gates passing
- Documentation updated
- Team sign-off completed
            """,

            # Project configuration files
            ".gitignore": """.ai/
*.log
.DS_Store
temp/
.vscode/
.idea/
            """,

            "README.md": """# BMad Method Framework

An AI-driven development methodology for structured software planning and execution.

## Overview

The BMad Method combines intelligent planning with systematic execution to deliver high-quality software solutions through AI assistance.

## Features

- **Structured Planning**: Story-driven development approach
- **AI Integration**: Claude-powered development assistance
- **Quality Gates**: Automated quality assurance
- **Living Documentation**: Documentation that evolves with code
- **Workflow Automation**: Streamlined development processes

## Getting Started

1. Review the user guide in `.bmad-core/user-guide.md`
2. Configure your project using `.bmad-core/core-config.yaml`
3. Set up your documentation structure in `docs/`
4. Begin using `/BMad` commands for development tasks

## Documentation

- [User Guide](.bmad-core/user-guide.md)
- [Architecture Documentation](docs/architecture.md)
- [Getting Started Guide](docs/getting-started.md)
- [Quality Assurance](docs/qa/)

## License

MIT License - see LICENSE file for details.
            """
        }

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_magnet_repository_file_structure_preservation(self, git_service, magnet_repository_structure):
        """Test that magnet repository file structure is properly preserved during import."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create magnet repository structure
            for file_path, content in magnet_repository_structure.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                # All content is now text-based (YAML and Markdown)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Analyze repository structure
            repo_analysis = await git_service._analyze_repository(temp_dir)

            # Verify all files are counted
            assert repo_analysis["file_count"] == len(magnet_repository_structure)

            # Verify total size is reasonable (should have some content)
            assert repo_analysis["total_size"] > 5000  # Repository should have reasonable content

            # Verify description extraction from README
            assert repo_analysis["description"] is not None
            assert any(keyword in repo_analysis["description"].lower() for keyword in ["methodology", "development", "ai", "bmad"])

    @pytest.mark.unit
    def test_magnet_bmad_config_detection(self, git_service, magnet_repository_structure):
        """Test detection and parsing of BMad core configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create BMad core config
            config_path = os.path.join(temp_dir, ".bmad-core/core-config.yaml")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(magnet_repository_structure[".bmad-core/core-config.yaml"])

            # Verify file exists and is readable
            assert os.path.exists(config_path)

            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()

            # Verify BMad config content
            assert "markdownExploder" in config_content
            assert "slashPrefix: \"BMad\"" in config_content
            assert "docs/qa" in config_content
            assert "docs/stories" in config_content

    @pytest.mark.unit
    def test_magnet_bmad_file_detection(self, git_service, magnet_repository_structure):
        """Test detection of BMad framework files in magnet repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create BMad framework files
            bmad_files = {
                ".bmad-core/core-config.yaml": magnet_repository_structure[".bmad-core/core-config.yaml"],
                ".bmad-core/user-guide.md": magnet_repository_structure[".bmad-core/user-guide.md"],
                ".claude/commands/BMad/tasks/create-story.md": magnet_repository_structure[".claude/commands/BMad/tasks/create-story.md"]
            }

            for file_path, content in bmad_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Get repository files
            repo_id = "magnet-bmad-test"
            with patch.object(git_service, 'get_repository_storage_path') as mock_path:
                mock_path.return_value = temp_dir

                files = git_service.get_repository_files(repo_id)

                # Verify BMad files are detected
                bmad_file_extensions = ['.yaml', '.md']
                bmad_found = [f for f in files if any(f.endswith(ext) for ext in bmad_file_extensions)]

                assert len(bmad_found) == 3
                assert any(".bmad-core" in f for f in bmad_found)
                assert any(".claude" in f for f in bmad_found)
                assert any("user-guide.md" in f for f in bmad_found)

    @pytest.mark.unit
    def test_magnet_repository_size_calculation_accuracy(self, git_service, magnet_repository_structure):
        """Test accurate size calculation for magnet repository files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            total_expected_size = 0

            # Create files and track expected sizes
            for file_path, content in magnet_repository_structure.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                total_expected_size += len(content.encode('utf-8'))

            # Analyze repository
            file_count, total_size = git_service.analyze_repository_structure(temp_dir)

            # Verify size calculation
            assert file_count == len(magnet_repository_structure)
            assert total_size == total_expected_size

    @pytest.mark.unit
    def test_magnet_repository_branch_validation(self, git_service):
        """Test branch name validation for magnet repository."""
        repo_url = self.MAGNET_REPO_URL
        repo_info = git_service._parse_repository_info(repo_url)

        assert repo_info["name"] == "magnet"
        assert repo_info["owner"] == "twattier"

        # Test with .git suffix
        repo_url_git = self.MAGNET_REPO_URL + ".git"
        repo_info_git = git_service._parse_repository_info(repo_url_git)

        assert repo_info_git["name"] == "magnet"
        assert repo_info_git["owner"] == "twattier"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_magnet_repository_documentation_detection(self, git_service, magnet_repository_structure):
        """Test detection of documentation files in magnet repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create documentation files
            doc_files = {
                "README.md": magnet_repository_structure["README.md"],
                "docs/architecture.md": magnet_repository_structure["docs/architecture.md"],
                "docs/getting-started.md": magnet_repository_structure["docs/getting-started.md"]
            }

            for file_path, content in doc_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Analyze repository
            repo_analysis = await git_service._analyze_repository(temp_dir)

            # Verify documentation detection
            assert repo_analysis["description"] is not None
            assert any(keyword in repo_analysis["description"].lower() for keyword in ["methodology", "development", "ai", "bmad"])

            # Get file listing
            repo_id = "magnet-docs-test"
            with patch.object(git_service, 'get_repository_storage_path') as mock_path:
                mock_path.return_value = temp_dir

                files = git_service.get_repository_files(repo_id)

                # Verify documentation files are found
                doc_extensions = ['.md']
                doc_found = [f for f in files if any(f.endswith(ext) for ext in doc_extensions)]

                assert len(doc_found) == 3
                assert any("README.md" in f for f in doc_found)
                assert any("architecture.md" in f for f in doc_found)
                assert any("getting-started.md" in f for f in doc_found)

    @pytest.mark.unit
    def test_magnet_repository_yaml_file_detection(self, git_service, magnet_repository_structure):
        """Test detection of YAML configuration files in magnet repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create YAML files
            yaml_files = {
                ".bmad-core/core-config.yaml": magnet_repository_structure[".bmad-core/core-config.yaml"],
                ".bmad-core/install-manifest.yaml": magnet_repository_structure[".bmad-core/install-manifest.yaml"]
            }

            for file_path, content in yaml_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Get file listing
            repo_id = "magnet-yaml-detection"
            with patch.object(git_service, 'get_repository_storage_path') as mock_path:
                mock_path.return_value = temp_dir

                files = git_service.get_repository_files(repo_id)

                # Verify YAML files are detected
                yaml_found = [f for f in files if f.endswith(".yaml")]

                assert len(yaml_found) == 2
                assert any("core-config.yaml" in f for f in yaml_found)
                assert any("install-manifest.yaml" in f for f in yaml_found)

    @pytest.mark.unit
    def test_magnet_repository_claude_commands_detection(self, git_service, magnet_repository_structure):
        """Test detection of Claude command files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Claude command files
            command_files = {
                ".claude/commands/BMad/tasks/create-story.md": magnet_repository_structure[".claude/commands/BMad/tasks/create-story.md"],
                ".claude/commands/BMad/tasks/generate-docs.md": magnet_repository_structure[".claude/commands/BMad/tasks/generate-docs.md"],
                ".claude/commands/BMad/tasks/run-quality-gates.md": magnet_repository_structure[".claude/commands/BMad/tasks/run-quality-gates.md"]
            }

            for file_path, content in command_files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Get file listing
            repo_id = "magnet-commands-test"
            with patch.object(git_service, 'get_repository_storage_path') as mock_path:
                mock_path.return_value = temp_dir

                files = git_service.get_repository_files(repo_id)

                # Verify Claude command files are detected
                command_patterns = [".claude/commands/BMad/tasks/"]
                for pattern in command_patterns:
                    assert any(pattern in f for f in files), f"Command pattern {pattern} not found"

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.services.git_service.Repo.clone_from')
    async def test_magnet_repository_commit_hash_extraction(self, mock_clone, git_service):
        """Test commit hash extraction for magnet repository."""
        # Mock repository with specific commit hash
        mock_repo = Mock()
        mock_repo.active_branch.name = "master"  # BMad repos typically use master
        mock_repo.head.commit.hexsha = "a1b2c3d4e5f6789abc123def456789fedcba321"
        mock_clone.return_value = mock_repo

        with patch.object(git_service, '_analyze_repository') as mock_analyze:
            mock_analyze.return_value = {
                'file_count': 140,  # Approximately 140 files in BMad framework
                'total_size': 1700000,  # ~1.7MB
                'description': 'BMad Method framework for AI-driven development methodology'
            }

            # Clone repository
            result = await git_service.clone_repository(self.MAGNET_REPO_URL, "magnet-commit-test")

            # Verify commit hash extraction
            assert result.commit_hash == "a1b2c3d4e5f6789abc123def456789fedcba321"
            assert result.branch == "master"
            assert result.name == "magnet"
            assert result.owner == "twattier"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_magnet_repository_directory_structure_analysis(self, git_service, magnet_repository_structure):
        """Test analysis of magnet repository directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create complete directory structure
            expected_dirs = set()
            for file_path in magnet_repository_structure.keys():
                if "/" in file_path:
                    dir_path = os.path.dirname(file_path)
                    expected_dirs.add(dir_path)
                    full_dir = os.path.join(temp_dir, dir_path)
                    os.makedirs(full_dir, exist_ok=True)

                full_path = os.path.join(temp_dir, file_path)
                content = magnet_repository_structure[file_path]

                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Verify BMad directory structure
            assert os.path.exists(os.path.join(temp_dir, ".bmad-core"))
            assert os.path.exists(os.path.join(temp_dir, ".claude", "commands", "BMad", "tasks"))
            assert os.path.exists(os.path.join(temp_dir, "docs"))
            assert os.path.exists(os.path.join(temp_dir, "docs", "qa"))
            assert os.path.exists(os.path.join(temp_dir, "docs", "stories"))

            # Analyze repository
            file_count, total_size = git_service.analyze_repository_structure(temp_dir)

            # Verify analysis results
            assert file_count == len(magnet_repository_structure)
            assert total_size > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_magnet_repository_file_filtering(self, git_service, magnet_repository_structure):
        """Test that .git directories are properly filtered out."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository structure with .git directory
            git_dir = os.path.join(temp_dir, ".git")
            os.makedirs(git_dir)

            # Add some .git files
            git_files = {
                ".git/config": "[core]\nrepositoryformatversion = 0",
                ".git/HEAD": "ref: refs/heads/master",
                ".git/refs/heads/master": "a1b2c3d4e5f6"
            }

            for git_file, content in git_files.items():
                full_path = os.path.join(temp_dir, git_file)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Add regular BMad files (first 5 files only)
            for file_path, content in list(magnet_repository_structure.items())[:5]:
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Analyze repository (should exclude .git)
            repo_analysis = await git_service._analyze_repository(temp_dir)

            # Should only count the 5 regular files, not the .git files
            assert repo_analysis["file_count"] == 5

            # Verify .git files are not included in file listing
            repo_id = "magnet-git-filter-test"
            with patch.object(git_service, 'get_repository_storage_path') as mock_path:
                mock_path.return_value = temp_dir

                files = git_service.get_repository_files(repo_id)

                # Should not include any .git files
                git_files_found = [f for f in files if ".git" in f]
                assert len(git_files_found) == 0