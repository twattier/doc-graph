# Testing Strategy

## Testing Pyramid
```
        E2E Tests (10%)
       /              \
      Integration Tests (30%)
     /                    \
  Frontend Unit (30%)   Backend Unit (30%)
```

## Test Organization

### Frontend Tests
```
apps/web/tests/
├── components/           # Component unit tests
│   ├── ui/              # shadcn/ui component tests
│   ├── visualization/   # Visualization component tests
│   └── navigation/      # Navigation component tests
├── hooks/               # Custom hook tests
│   ├── useProject.test.ts
│   ├── useVisualization.test.ts
│   └── useAuth.test.ts
├── services/            # API service tests
│   ├── projects.test.ts
│   └── visualizations.test.ts
├── stores/              # State management tests
│   ├── projectStore.test.ts
│   └── visualizationStore.test.ts
├── utils/               # Utility function tests
└── __mocks__/           # Test mocks and fixtures
```

### Backend Tests
```
apps/api/tests/
├── unit/                # Unit tests
│   ├── services/        # Service layer tests
│   ├── models/          # Data model tests
│   └── utils/           # Utility tests
├── integration/         # Integration tests
│   ├── handlers/        # Lambda handler tests
│   ├── database/        # Database integration tests
│   └── github/          # GitHub API integration tests
├── fixtures/            # Test data fixtures
│   ├── projects.json
│   ├── documents.json
│   └── visualizations.json
└── conftest.py          # pytest configuration
```

### E2E Tests
```
e2e/
├── specs/               # Test specifications
│   ├── project-import.spec.ts
│   ├── visualization-generation.spec.ts
│   └── cross-template-navigation.spec.ts
├── fixtures/            # Test data
├── page-objects/        # Page object models
└── playwright.config.ts
```

## Test Examples

### Frontend Component Test
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { VisualizationViewer } from '@/components/visualization/VisualizationViewer';
import { useVisualization } from '@/hooks/useVisualization';

// Mock the hook
vi.mock('@/hooks/useVisualization');
const mockUseVisualization = vi.mocked(useVisualization);

describe('VisualizationViewer', () => {
  const mockVisualization = {
    id: '123',
    mermaidCode: 'graph TD\nA-->B',
    visualizationType: 'tree' as const,
    generationMetadata: {
      generatedAt: new Date(),
      generationTimeMs: 1500,
      nodeCount: 10,
      relationshipCount: 5,
      cacheHit: false,
    },
  };

  beforeEach(() => {
    mockUseVisualization.mockReturnValue({
      visualization: mockVisualization,
      isLoading: false,
      error: null,
      generateVisualization: vi.fn(),
      exportVisualization: vi.fn(),
    });
  });

  it('renders visualization with Mermaid diagram', async () => {
    render(
      <VisualizationViewer
        projectId="project-123"
        visualizationType="tree"
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('img', { name: /mermaid diagram/i })).toBeInTheDocument();
    });

    expect(screen.getByText('10 nodes')).toBeInTheDocument();
    expect(screen.getByText('5 relationships')).toBeInTheDocument();
  });

  it('handles export functionality', async () => {
    const mockExport = vi.fn().mockResolvedValue('exported-content');
    mockUseVisualization.mockReturnValue({
      ...mockUseVisualization(),
      exportVisualization: mockExport,
    });

    render(
      <VisualizationViewer
        projectId="project-123"
        visualizationType="tree"
        onExport={vi.fn()}
      />
    );

    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    expect(mockExport).toHaveBeenCalledWith('123', 'mermaid');
  });
});
```

### Backend API Test
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app
from src.services.ProjectService import ProjectService

client = TestClient(app)

class TestProjectEndpoints:
    @pytest.fixture
    def mock_auth_context(self):
        return {
            "userId": "user-123",
            "email": "test@example.com",
            "permissions": []
        }

    @patch.object(ProjectService, 'import_project')
    def test_import_project_success(self, mock_import, mock_auth_context):
        # Arrange
        mock_project = {
            "id": "project-123",
            "name": "Test Project",
            "github_url": "https://github.com/user/repo",
            "status": "importing"
        }
        mock_import.return_value = mock_project

        # Act
        response = client.post(
            "/projects",
            json={
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["project"]["name"] == "Test Project"
        assert data["project"]["status"] == "importing"
        mock_import.assert_called_once_with(
            "user-123",
            {
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            }
        )

    def test_import_project_unauthorized(self):
        # Act
        response = client.post(
            "/projects",
            json={
                "name": "Test Project",
                "githubUrl": "https://github.com/user/repo"
            }
        )

        # Assert
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["error"]

    @patch.object(ProjectService, 'search_documents')
    def test_search_documents(self, mock_search, mock_auth_context):
        # Arrange
        mock_results = [
            {
                "document": {
                    "id": "doc-123",
                    "filePath": "docs/prd.md",
                    "templateType": "bmad-method"
                },
                "relevanceScore": 0.95,
                "matchContext": "...project requirements..."
            }
        ]
        mock_search.return_value = mock_results

        # Act
        response = client.get(
            "/projects/project-123/search?query=requirements&templateType=bmad-method",
            headers={"Authorization": "Bearer valid-token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["document"]["templateType"] == "bmad-method"
```

### E2E Test
```typescript
import { test, expect } from '@playwright/test';

test.describe('Project Import and Visualization', () => {
  test('complete project import and visualization workflow', async ({ page }) => {
    // Navigate to application
    await page.goto('/dashboard');

    // Import new project
    await page.click('button:has-text("Import Project")');
    await page.fill('input[name="githubUrl"]', 'https://github.com/test/magnet');
    await page.fill('input[name="name"]', 'Magnet Test Project');
    await page.click('button:has-text("Import")');

    // Wait for import completion
    await page.waitForSelector('text=Project imported successfully', { timeout: 30000 });

    // Navigate to project
    await page.click('text=Magnet Test Project');

    // Wait for template detection
    await page.waitForSelector('text=Template detection complete', { timeout: 60000 });

    // Verify template zones are detected
    await expect(page.locator('[data-testid="template-zone-bmad-method"]')).toBeVisible();
    await expect(page.locator('[data-testid="template-zone-claude-code"]')).toBeVisible();

    // Generate tree visualization
    await page.click('[data-testid="visualization-type-tree"]');
    await page.waitForSelector('[data-testid="mermaid-diagram"]', { timeout: 10000 });

    // Verify visualization is generated
    const diagram = page.locator('[data-testid="mermaid-diagram"]');
    await expect(diagram).toBeVisible();

    // Test export functionality
    await page.click('button:has-text("Export")');
    await page.click('text=Mermaid Code');

    // Verify export dialog
    const exportDialog = page.locator('[data-testid="export-dialog"]');
    await expect(exportDialog).toBeVisible();

    const mermaidCode = page.locator('[data-testid="export-content"]');
    await expect(mermaidCode).toContainText('graph TD');

    // Test cross-template navigation
    await page.click('[data-testid="template-zone-claude-code"]');
    await page.waitForSelector('[data-testid="claude-code-visualization"]');

    // Verify context preservation
    await expect(page.locator('[data-testid="breadcrumb"]')).toContainText('Claude Code');
    await expect(page.locator('[data-testid="template-indicator"]')).toHaveClass(/claude-code/);
  });

  test('handles large repository import gracefully', async ({ page }) => {
    await page.goto('/dashboard');

    // Import large repository
    await page.click('button:has-text("Import Project")');
    await page.fill('input[name="githubUrl"]', 'https://github.com/large/repository');
    await page.fill('input[name="name"]', 'Large Repository');
    await page.click('button:has-text("Import")');

    // Verify progressive loading indicators
    await expect(page.locator('[data-testid="import-progress"]')).toBeVisible();

    // Wait for processing to complete (extended timeout for large repos)
    await page.waitForSelector('text=Project ready', { timeout: 120000 });

    // Verify performance meets requirements
    const startTime = Date.now();
    await page.click('[data-testid="generate-visualization"]');
    await page.waitForSelector('[data-testid="mermaid-diagram"]');
    const endTime = Date.now();

    // Visualization should generate within 2 seconds per requirements
    expect(endTime - startTime).toBeLessThan(2000);
  });
});
```
