# Wireframes & Mockups

**Primary Design Files**: Figma workspace at [DocGraph Design System - TBD]

## Key Screen Layouts

### Multi-Template Project Explorer
**Purpose**: Central hub for template-aware project exploration with unified navigation and visualization switching

**Key Elements**:
- Template zone indicator bar with color-coded sections (BMAD=blue, Claude Code=green, Generic=gray)
- Visualization type toggle (Tree/Pipeline/Cross-Template) with preview thumbnails
- Project metadata panel showing import date, template detection confidence, completeness metrics
- Context-sensitive navigation sidebar adapting to current template zone
- Main visualization canvas with zoom, pan, and export controls
- Cross-template relationship highlights overlaid on visualizations

**Interaction Notes**: Hover states reveal relationship details, click-to-drill into specific nodes, smooth template zone transitions with visual continuity

**Design File Reference**: [Frame: Multi-Template Explorer - TBD]

### Tree Visualization View
**Purpose**: Display hierarchical relationships within Claude Code .bmad-core structures and BMAD-METHOD directory hierarchies

**Key Elements**:
- Mermaid-rendered tree diagram with interactive nodes
- Expandable/collapsible branches with visual state indicators
- Node detail overlay on hover/click with metadata and relationships
- Template-specific styling (agents=circles, tasks=rectangles, templates=diamonds)
- Relationship strength indicators through line weight and color
- Export controls with live Mermaid code preview

**Interaction Notes**: Click-to-expand maintains visual stability, right-click context menu for node actions, keyboard navigation support

**Design File Reference**: [Frame: Tree Visualization - TBD]

### Pipeline Visualization View
**Purpose**: Show sequential workflow progression for BMAD-METHOD documentation stages and process flows

**Key Elements**:
- Horizontal Mermaid pipeline with completion status indicators
- Stage detail panels showing document metadata, completion status, dependencies
- Cross-stage relationship connectors with dependency types
- Progress indicators showing workflow completeness percentage
- Timeline view toggle showing chronological progression
- Stage-specific actions (view document, check dependencies, export stage)

**Interaction Notes**: Click stages for detail view, drag timeline slider for historical views, export individual stages or complete pipeline

**Design File Reference**: [Frame: Pipeline Visualization - TBD]

### Template Detection Dashboard
**Purpose**: Review and configure automatic template detection results with override capabilities

**Key Elements**:
- Detection confidence matrix showing template assignments with confidence scores
- Override interface for correcting misclassified documents
- Template mapping rules editor with pattern preview
- Detection statistics showing coverage and accuracy metrics
- Validation warnings for conflicts or missing patterns
- Save/export configuration options for reuse

**Interaction Notes**: Drag-and-drop for template reassignment, inline editing for mapping rules, real-time validation feedback

**Design File Reference**: [Frame: Template Detection - TBD]
