# Information Architecture (IA)

## Site Map / Screen Inventory

```mermaid
graph TD
    A[Landing Page] --> B[Project Import]
    B --> C[Template Detection Dashboard]
    C --> D[Multi-Template Project Explorer]
    D --> E[Tree Visualization View]
    D --> F[Pipeline Visualization View]
    D --> G[Cross-Template Relationship Map]
    D --> H[Search & Navigation Interface]
    E --> I[Agent/Task Detail View]
    F --> J[Workflow Step Detail View]
    G --> K[Relationship Detail View]
    H --> L[Search Results Interface]
    D --> M[Export & Share Interface]
    M --> N[Mermaid Export Dialog]
    M --> O[GitHub Integration Panel]
    D --> P[Project Configuration]
    P --> Q[Template Mapping Editor]
    P --> R[Override Configuration Panel]
```

## Navigation Structure

**Primary Navigation**: Template-aware top navigation with visual indicators for current template zone (BMAD-METHOD, Claude Code, Generic). Includes project switcher, main view toggles (Tree/Pipeline/Cross-Template), and export actions.

**Secondary Navigation**: Context-sensitive sidebar showing hierarchical navigation within current template zone. Breadcrumb trail maintains cross-template navigation history with template zone indicators.

**Breadcrumb Strategy**: Multi-level breadcrumbs showing: Project → Template Zone → Current Section → Detail Level, with visual template zone badges for quick orientation and one-click zone switching.
