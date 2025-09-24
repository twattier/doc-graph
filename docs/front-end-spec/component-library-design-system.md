# Component Library / Design System

**Design System Approach**: Custom design system built on shadcn/ui foundation, extended with DocGraph-specific components for template-aware visualization and Mermaid integration.

## Core Components

### TemplateZoneIndicator
**Purpose**: Visual indicator showing current template context with quick switching capabilities

**Variants**: Badge (compact), Bar (full-width), Breadcrumb (navigation)

**States**: Active, Inactive, Transitioning, Error

**Usage Guidelines**: Always visible during template exploration, color-coded by template type, includes confidence indicators for detected templates

### MermaidVisualization
**Purpose**: Container component for rendering and interacting with Mermaid diagrams

**Variants**: Tree, Pipeline, Graph, Flowchart

**States**: Loading, Rendered, Error, Exporting

**Usage Guidelines**: Maintains aspect ratio, supports zoom/pan gestures, includes export controls, handles progressive loading for large diagrams

### CrossTemplateLink
**Purpose**: Interactive element indicating relationships between different template zones

**Variants**: Inline (within text), Visual (on diagrams), Navigation (breadcrumbs)

**States**: Default, Hover, Active, Visited, Broken

**Usage Guidelines**: Distinctive styling from regular links, includes template destination indicators, smooth transition animations

### RelationshipViewer
**Purpose**: Detail panel showing connections and dependencies between documentation elements

**Variants**: Compact (sidebar), Expanded (modal), Inline (overlay)

**States**: Loading, Populated, Empty, Error

**Usage Guidelines**: Context-sensitive content, supports nested relationships, includes strength indicators and metadata

### ExportDialog
**Purpose**: Interface for generating and downloading Mermaid diagrams with format options

**Variants**: Quick (single diagram), Batch (multiple), Integration (GitHub)

**States**: Setup, Generating, Preview, Complete, Error

**Usage Guidelines**: Format preview before export, progress indicators for generation, integration options clearly labeled
