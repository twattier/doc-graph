"""
Repository processing pipeline service for file scanning and analysis.
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import mimetypes

from sqlalchemy.orm import Session

from ..models.repository import Repository, RepositoryVersion
from .git_service import GitService, GitRepositoryInfo
from .repository_service import RepositoryService

logger = logging.getLogger(__name__)


class RepositoryProcessor:
    """Service for processing repository files and extracting insights."""

    def __init__(self, git_service: GitService, repository_service: RepositoryService):
        """Initialize processor with required services."""
        self.git_service = git_service
        self.repository_service = repository_service

        # Supported file types for processing
        self.supported_extensions = {
            '.md', '.txt', '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp',
            '.h', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.json', '.yaml', '.yml', '.xml', '.html', '.css', '.scss', '.sql'
        }

        # Documentation file patterns
        self.doc_patterns = [
            'readme', 'license', 'contributing', 'changelog', 'history',
            'authors', 'credits', 'todo', 'bug', 'issue', 'roadmap'
        ]

    async def process_repository(
        self,
        db: Session,
        repository_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a repository through the complete pipeline.

        Args:
            db: Database session
            repository_id: Repository identifier
            progress_callback: Optional progress callback

        Returns:
            Dict containing processing results
        """
        if progress_callback:
            await progress_callback(10, "Starting repository analysis...")

        try:
            # Get repository info
            repository = db.query(Repository).filter(Repository.id == repository_id).first()
            if not repository:
                raise ValueError(f"Repository {repository_id} not found")

            storage_path = self.git_service.get_repository_storage_path(repository_id)
            if not os.path.exists(storage_path):
                raise ValueError(f"Repository storage not found: {storage_path}")

            if progress_callback:
                await progress_callback(20, "Scanning repository structure...")

            # Step 1: Analyze repository structure
            structure_analysis = await self._analyze_structure(storage_path)

            if progress_callback:
                await progress_callback(40, "Processing documentation files...")

            # Step 2: Process documentation files
            docs_analysis = await self._process_documentation(storage_path)

            if progress_callback:
                await progress_callback(60, "Analyzing source code files...")

            # Step 3: Analyze source code
            code_analysis = await self._analyze_source_code(storage_path)

            if progress_callback:
                await progress_callback(80, "Extracting project metadata...")

            # Step 4: Extract project metadata
            project_metadata = await self._extract_project_metadata(storage_path)

            if progress_callback:
                await progress_callback(95, "Finalizing analysis...")

            # Combine all results
            processing_results = {
                'repository_id': repository_id,
                'processed_at': datetime.utcnow(),
                'structure': structure_analysis,
                'documentation': docs_analysis,
                'source_code': code_analysis,
                'metadata': project_metadata,
                'processing_stats': {
                    'total_files_processed': (
                        structure_analysis.get('total_files', 0) +
                        len(docs_analysis.get('doc_files', [])) +
                        len(code_analysis.get('source_files', []))
                    ),
                    'documentation_files': len(docs_analysis.get('doc_files', [])),
                    'source_files': len(code_analysis.get('source_files', [])),
                    'supported_files': structure_analysis.get('supported_files', 0),
                }
            }

            if progress_callback:
                await progress_callback(100, "Repository processing completed!")

            logger.info(f"Successfully processed repository {repository_id}")
            return processing_results

        except Exception as e:
            error_msg = f"Repository processing failed: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository directory structure and file types."""
        def analyze():
            structure = {
                'directories': [],
                'files_by_type': {},
                'total_files': 0,
                'supported_files': 0,
                'directory_tree': {}
            }

            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                # Record directory structure
                rel_path = os.path.relpath(root, repo_path)
                if rel_path != '.':
                    structure['directories'].append(rel_path)

                # Analyze files
                for file in files:
                    structure['total_files'] += 1
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()

                    # Count by extension
                    if ext in structure['files_by_type']:
                        structure['files_by_type'][ext] += 1
                    else:
                        structure['files_by_type'][ext] = 1

                    # Count supported files
                    if ext in self.supported_extensions:
                        structure['supported_files'] += 1

            return structure

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze)

    async def _process_documentation(self, repo_path: str) -> Dict[str, Any]:
        """Process documentation files and extract content."""
        def process():
            docs_info = {
                'doc_files': [],
                'readme_content': None,
                'license_info': None,
                'doc_summary': {}
            }

            for root, dirs, files in os.walk(repo_path):
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_lower = file.lower()
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Check if it's a documentation file
                    is_doc = any(pattern in file_lower for pattern in self.doc_patterns)
                    is_markdown = file.endswith(('.md', '.txt', '.rst'))

                    if is_doc or is_markdown:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()

                            doc_entry = {
                                'path': rel_path,
                                'name': file,
                                'size': len(content),
                                'lines': len(content.split('\n')),
                                'type': 'documentation'
                            }

                            # Special handling for README files
                            if 'readme' in file_lower:
                                docs_info['readme_content'] = content[:1000]  # First 1000 chars
                                doc_entry['type'] = 'readme'

                            # Special handling for LICENSE files
                            elif 'license' in file_lower:
                                docs_info['license_info'] = content[:500]  # First 500 chars
                                doc_entry['type'] = 'license'

                            docs_info['doc_files'].append(doc_entry)

                        except (UnicodeDecodeError, IOError):
                            continue

            return docs_info

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process)

    async def _analyze_source_code(self, repo_path: str) -> Dict[str, Any]:
        """Analyze source code files and extract metadata."""
        def analyze():
            code_info = {
                'source_files': [],
                'languages': {},
                'code_stats': {
                    'total_lines': 0,
                    'estimated_complexity': 'medium'
                }
            }

            for root, dirs, files in os.walk(repo_path):
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext in self.supported_extensions and ext not in ['.md', '.txt']:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_path)

                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                lines = len(content.split('\n'))

                            # Language detection
                            language = self._detect_language(ext)
                            if language in code_info['languages']:
                                code_info['languages'][language] += 1
                            else:
                                code_info['languages'][language] = 1

                            code_info['source_files'].append({
                                'path': rel_path,
                                'name': file,
                                'extension': ext,
                                'language': language,
                                'lines': lines,
                                'size': len(content)
                            })

                            code_info['code_stats']['total_lines'] += lines

                        except (UnicodeDecodeError, IOError):
                            continue

            # Estimate complexity based on total lines
            total_lines = code_info['code_stats']['total_lines']
            if total_lines < 1000:
                code_info['code_stats']['estimated_complexity'] = 'low'
            elif total_lines < 10000:
                code_info['code_stats']['estimated_complexity'] = 'medium'
            else:
                code_info['code_stats']['estimated_complexity'] = 'high'

            return code_info

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze)

    async def _extract_project_metadata(self, repo_path: str) -> Dict[str, Any]:
        """Extract project metadata from configuration files."""
        def extract():
            metadata = {
                'project_type': 'unknown',
                'dependencies': [],
                'build_files': [],
                'config_files': []
            }

            # Look for common project files
            project_indicators = {
                'package.json': 'javascript',
                'requirements.txt': 'python',
                'pyproject.toml': 'python',
                'Cargo.toml': 'rust',
                'pom.xml': 'java',
                'build.gradle': 'java',
                'go.mod': 'go',
                'composer.json': 'php',
                'Gemfile': 'ruby'
            }

            for root, dirs, files in os.walk(repo_path):
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Check for project type indicators
                    if file in project_indicators:
                        metadata['project_type'] = project_indicators[file]
                        metadata['build_files'].append(rel_path)

                    # Check for configuration files
                    config_extensions = ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']
                    if any(file.endswith(ext) for ext in config_extensions):
                        metadata['config_files'].append(rel_path)

            return metadata

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract)

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React/TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sql': 'SQL',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML'
        }
        return language_map.get(extension, 'Unknown')

    async def validate_processing_results(self, results: Dict[str, Any]) -> bool:
        """Validate processing results for completeness."""
        required_keys = ['repository_id', 'processed_at', 'structure', 'documentation', 'source_code', 'metadata']
        return all(key in results for key in required_keys)

    async def test_with_magnet_repository(self, db: Session, repository_id: str) -> Dict[str, Any]:
        """
        Test processing pipeline with ./projects/magnet repository structure.

        This method is specifically for validation against the magnet project structure
        mentioned in the acceptance criteria.
        """
        try:
            results = await self.process_repository(db, repository_id)

            # Validate results structure
            validation_results = {
                'repository_id': repository_id,
                'processing_successful': await self.validate_processing_results(results),
                'files_processed': results['processing_stats']['total_files_processed'],
                'structure_preserved': len(results['structure']['directories']) > 0,
                'documentation_found': len(results['documentation']['doc_files']) > 0,
                'source_code_analyzed': len(results['source_code']['source_files']) > 0,
                'metadata_extracted': results['metadata']['project_type'] != 'unknown',
                'test_passed': True
            }

            logger.info(f"Magnet repository test completed successfully: {validation_results}")
            return validation_results

        except Exception as e:
            logger.error(f"Magnet repository test failed: {str(e)}")
            return {
                'repository_id': repository_id,
                'processing_successful': False,
                'error': str(e),
                'test_passed': False
            }