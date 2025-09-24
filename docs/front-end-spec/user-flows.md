# User Flows

## Flow 1: Initial Project Import & Assessment

**User Goal**: Import the Magnet project repository and quickly assess its documentation completeness for development readiness.

**Entry Points**: Landing page CTA, direct URL with repository parameter

**Success Criteria**: User confidently determines project development readiness within 15 minutes

### Flow Diagram
```mermaid
graph TD
    A[Enter GitHub URL] --> B[Repository Validation]
    B --> C{Valid Repository?}
    C -->|No| D[Error: Invalid URL/Access]
    C -->|Yes| E[Import Processing]
    E --> F[Template Detection]
    F --> G[Detection Results Dashboard]
    G --> H[Review Template Mappings]
    H --> I{Mappings Correct?}
    I -->|No| J[Adjust Template Configuration]
    I -->|Yes| K[Enter Multi-Template Explorer]
    J --> K
    K --> L[High-Level Project Overview]
    L --> M[Assess Completeness]
    M --> N[Export Assessment Summary]
```

### Edge Cases & Error Handling:
- Private repository access denied → Clear message explaining public repository requirement
- Large repository timeout → Progress indicators with partial loading capabilities
- Malformed template detection → Manual override options with guidance
- Network interruption during import → Resume capability with progress preservation

**Notes**: This flow establishes the foundational user experience and validates DocGraph's core value proposition with real project assessment.

## Flow 2: Template-Aware Visualization Exploration

**User Goal**: Navigate between BMAD-METHOD documentation and Claude Code configuration while maintaining context of their relationship analysis.

**Entry Points**: Multi-Template Project Explorer, search results, direct links

**Success Criteria**: User maintains context across template zones and discovers cross-template relationships

### Flow Diagram
```mermaid
graph TD
    A[Start in Template Zone A] --> B[View Visualization]
    B --> C[Identify Cross-Reference]
    C --> D[Click Cross-Template Link]
    D --> E[Template Transition Animation]
    E --> F[Arrive in Template Zone B]
    F --> G[Context Preservation Indicators]
    G --> H[Explore Related Content]
    H --> I{Return to Origin?}
    I -->|Yes| J[Use Breadcrumb Navigation]
    I -->|No| K[Continue Exploration]
    J --> L[Smooth Return Transition]
    K --> M[Discover New Relationships]
```

### Edge Cases & Error Handling:
- Broken cross-template references → Clear error indication with alternative navigation
- Deep navigation stack overflow → Smart breadcrumb condensation
- Template zone confusion → Prominent template indicators and "Where am I?" help
- Performance degradation → Progressive loading with skeleton states

**Notes**: This flow is critical for DocGraph's differentiation - seamless cross-template navigation while preserving user mental models.

## Flow 3: Mermaid Export & GitHub Integration

**User Goal**: Export visualization insights as Mermaid diagrams for GitHub documentation or stakeholder communication.

**Entry Points**: Export buttons throughout interface, batch export options

**Success Criteria**: User successfully exports and integrates diagrams in external documentation within 2 minutes

### Flow Diagram
```mermaid
graph TD
    A[Select Export Option] --> B[Choose Export Type]
    B --> C[Mermaid Code Generation]
    C --> D[Preview Generated Diagram]
    D --> E{Preview Acceptable?}
    E -->|No| F[Adjust Export Settings]
    E -->|Yes| G[Copy/Download Options]
    F --> C
    G --> H[GitHub Integration Prompt]
    H --> I{Direct GitHub Integration?}
    I -->|Yes| J[User Registration/Login]
    I -->|No| K[Manual Copy/Download]
    J --> L[Select Target Repository]
    L --> M[Choose Integration Method]
    M --> N[Execute Integration]
    K --> O[Export Complete]
    N --> O
```

### Edge Cases & Error Handling:
- Mermaid generation failure → Fallback export formats with clear error messaging
- GitHub integration API errors → Graceful fallback to manual export with troubleshooting guidance
- Large diagram export timeout → Progressive generation with partial export options
- Invalid repository URL → Clear format requirements and validation guidance

**Notes**: Export functionality is essential for DocGraph's integration into existing workflows and stakeholder communication.
