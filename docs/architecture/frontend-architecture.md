# Frontend Architecture

## Component Architecture

### Component Organization
```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui base components
│   ├── visualization/   # Template-aware visualization components
│   │   ├── MermaidViewer.tsx
│   │   ├── TemplateZoneIndicator.tsx
│   │   └── CrossTemplateLink.tsx
│   ├── navigation/      # Navigation and routing components
│   └── forms/           # Form components with validation
├── pages/               # Next.js pages or React Router routes
│   ├── dashboard/       # Project dashboard
│   ├── project/         # Project exploration views
│   └── import/          # Repository import flow
├── hooks/               # Custom React hooks
│   ├── useProject.ts    # Project data management
│   ├── useVisualization.ts # Visualization state
│   └── useTemplateDetection.ts
├── services/            # API client and external integrations
│   ├── api.ts           # Base API client configuration
│   ├── projects.ts      # Project-related API calls
│   └── visualizations.ts
├── stores/              # Zustand state management
│   ├── projectStore.ts  # Project state
│   ├── visualizationStore.ts
│   └── uiStore.ts       # UI state and preferences
├── types/               # TypeScript type definitions
│   ├── api.ts           # API response types
│   ├── project.ts       # Project domain types
│   └── visualization.ts
└── utils/               # Utility functions
    ├── templateDetection.ts
    ├── mermaidHelpers.ts
    └── formatters.ts
```

### Component Template
```typescript
import React from 'react';
import { cn } from '@/lib/utils';

interface VisualizationViewerProps {
  projectId: string;
  templateZoneId?: string;
  visualizationType: 'tree' | 'pipeline' | 'graph' | 'cross-template';
  className?: string;
  onExport?: (format: 'mermaid' | 'svg' | 'png') => void;
}

export const VisualizationViewer: React.FC<VisualizationViewerProps> = ({
  projectId,
  templateZoneId,
  visualizationType,
  className,
  onExport
}) => {
  // Component implementation following shadcn/ui patterns
  return (
    <div className={cn('flex flex-col space-y-4', className)}>
      {/* Template-aware visualization component */}
    </div>
  );
};
```

## State Management Architecture

### State Structure
```typescript
// Project Store
interface ProjectState {
  currentProject: Project | null;
  projects: Project[];
  templateZones: TemplateZone[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentProject: (project: Project) => void;
  loadProject: (projectId: string) => Promise<void>;
  importProject: (githubUrl: string, name: string) => Promise<Project>;
  updateTemplateMapping: (projectId: string, mappings: TemplateMapping[]) => Promise<void>;
}

// Visualization Store
interface VisualizationState {
  visualizations: Map<string, Visualization>;
  currentVisualization: Visualization | null;
  generationProgress: number;
  isGenerating: boolean;

  // Actions
  generateVisualization: (config: VisualizationConfig) => Promise<Visualization>;
  exportVisualization: (id: string, format: ExportFormat) => Promise<string>;
  cacheVisualization: (visualization: Visualization) => void;
}

// UI Store for interface state
interface UIState {
  activeTemplateZone: string | null;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  breadcrumbHistory: BreadcrumbItem[];

  // Actions
  setActiveTemplateZone: (zoneId: string | null) => void;
  addBreadcrumb: (item: BreadcrumbItem) => void;
  toggleSidebar: () => void;
}
```

### State Management Patterns
- **Optimistic Updates**: UI updates immediately, rollback on API failure
- **Selective Reactivity**: Component subscriptions to specific state slices
- **Persist Configuration**: User preferences and project settings in localStorage
- **Error Boundaries**: Graceful error handling with state recovery
- **Loading States**: Granular loading indicators for different operations

## Routing Architecture

### Route Organization
```
/                           # Landing page
/dashboard                  # User project dashboard
/projects/import            # Repository import flow
/projects/:id               # Project overview
/projects/:id/explore       # Multi-template exploration
/projects/:id/zones/:zoneId # Template zone specific view
/projects/:id/search        # Template-aware search interface
/projects/:id/config        # Project configuration
/visualizations/:id         # Individual visualization view
/visualizations/:id/export  # Export interface
/settings                   # User preferences
```

### Protected Route Pattern
```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = []
}) => {
  const { user, isAuthenticated, hasPermissions } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredPermissions.length > 0 && !hasPermissions(requiredPermissions)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

## Frontend Services Layer

### API Client Setup
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuth } from '@/hooks/useAuth';

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth token
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }

  // Additional HTTP methods...
}

export const apiClient = new ApiClient();
```

### Service Example
```typescript
import { apiClient } from './api';
import { Project, TemplateZone, Visualization } from '@/types';

export class ProjectService {
  static async getProjects(): Promise<Project[]> {
    return apiClient.get<{ projects: Project[] }>('/projects')
      .then(response => response.projects);
  }

  static async importProject(githubUrl: string, name: string): Promise<Project> {
    return apiClient.post<Project>('/projects', { githubUrl, name });
  }

  static async getTemplateZones(projectId: string): Promise<TemplateZone[]> {
    return apiClient.get<{ templateZones: TemplateZone[] }>(`/projects/${projectId}/template-zones`)
      .then(response => response.templateZones);
  }

  static async generateVisualization(projectId: string, config: VisualizationConfig): Promise<Visualization> {
    return apiClient.post<Visualization>(`/projects/${projectId}/visualizations`, config);
  }

  static async searchDocuments(projectId: string, query: string, filters: SearchFilters): Promise<SearchResult[]> {
    const params = new URLSearchParams({ query, ...filters });
    return apiClient.get<{ results: SearchResult[] }>(`/projects/${projectId}/search?${params}`)
      .then(response => response.results);
  }
}
```
