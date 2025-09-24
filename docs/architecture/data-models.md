# Data Models

## Project
**Purpose:** Represents a GitHub repository imported for template-aware analysis and visualization

**Key Attributes:**
- id: string (UUID) - Unique project identifier
- name: string - Human-readable project name
- githubUrl: string - Source repository URL
- importDate: Date - When project was imported
- templateMappings: TemplateMapping[] - Template detection configuration
- status: ProjectStatus - Processing status (importing, processing, ready, error)
- metadata: ProjectMetadata - Repository statistics and configuration

### TypeScript Interface
```typescript
interface Project {
  id: string;
  name: string;
  githubUrl: string;
  importDate: Date;
  templateMappings: TemplateMapping[];
  status: 'importing' | 'processing' | 'ready' | 'error';
  metadata: {
    fileCount: number;
    lastCommit: Date;
    primaryBranch: string;
    detectionConfidence: number;
  };
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Has many Documents
- Has many TemplateZones
- Belongs to User

## Document
**Purpose:** Individual file within a project with template classification and extracted metadata

**Key Attributes:**
- id: string (UUID) - Unique document identifier
- projectId: string - Parent project reference
- filePath: string - Relative path within repository
- content: string - Document content
- templateType: TemplateType - Detected template classification
- extractedMetadata: DocumentMetadata - Template-specific metadata
- embeddingVector: number[] - pgvector embedding for similarity search
- processingStatus: ProcessingStatus - Current processing state

### TypeScript Interface
```typescript
interface Document {
  id: string;
  projectId: string;
  filePath: string;
  content: string;
  templateType: 'bmad-method' | 'claude-code' | 'generic';
  extractedMetadata: Record<string, any>;
  embeddingVector?: number[];
  processingStatus: 'pending' | 'processed' | 'failed';
  detectionConfidence: number;
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Belongs to Project
- Has many CrossTemplateRelationships (source and target)
- Part of TemplateZone

## TemplateZone
**Purpose:** Logical grouping of documents within a project that share the same template type

**Key Attributes:**
- id: string (UUID) - Unique zone identifier
- projectId: string - Parent project reference
- templateType: TemplateType - Template classification for this zone
- rootPath: string - Base directory path for this template zone
- visualizationConfig: VisualizationConfig - Zone-specific visualization settings
- completenessScore: number - Assessment of template completeness

### TypeScript Interface
```typescript
interface TemplateZone {
  id: string;
  projectId: string;
  templateType: 'bmad-method' | 'claude-code' | 'generic';
  rootPath: string;
  visualizationConfig: {
    preferredLayout: 'tree' | 'pipeline' | 'graph';
    colorScheme: string;
    nodeStyles: Record<string, any>;
  };
  completenessScore: number;
  documentCount: number;
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Belongs to Project
- Contains many Documents
- Has many Visualizations

## CrossTemplateRelationship
**Purpose:** Represents connections and dependencies between documents from different template zones

**Key Attributes:**
- id: string (UUID) - Unique relationship identifier
- sourceDocumentId: string - Source document reference
- targetDocumentId: string - Target document reference
- relationshipType: RelationshipType - Type of connection
- strength: number - Relationship strength score (0-1)
- metadata: RelationshipMetadata - Additional relationship context
- detectedBy: string - Detection method used

### TypeScript Interface
```typescript
interface CrossTemplateRelationship {
  id: string;
  sourceDocumentId: string;
  targetDocumentId: string;
  relationshipType: 'reference' | 'dependency' | 'implementation' | 'workflow';
  strength: number;
  metadata: {
    detectionMethod: string;
    confidence: number;
    contextualInfo?: Record<string, any>;
  };
  detectedBy: 'automatic' | 'manual' | 'ai-enhanced';
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Links two Documents
- Part of relationship analysis for Visualizations

## Visualization
**Purpose:** Generated Mermaid diagram representing template-specific or cross-template relationships

**Key Attributes:**
- id: string (UUID) - Unique visualization identifier
- projectId: string - Parent project reference
- templateZoneId: string - Associated template zone (if applicable)
- visualizationType: VisualizationType - Type of diagram generated
- mermaidCode: string - Generated Mermaid diagram syntax
- generationMetadata: GenerationMetadata - Creation details and performance metrics
- cacheStatus: CacheStatus - Cache state for performance optimization

### TypeScript Interface
```typescript
interface Visualization {
  id: string;
  projectId: string;
  templateZoneId?: string;
  visualizationType: 'tree' | 'pipeline' | 'graph' | 'cross-template';
  mermaidCode: string;
  generationMetadata: {
    generatedAt: Date;
    generationTimeMs: number;
    nodeCount: number;
    relationshipCount: number;
    cacheHit: boolean;
  };
  cacheStatus: 'fresh' | 'stale' | 'expired';
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Belongs to Project
- May belong to TemplateZone
- Generated from Documents and CrossTemplateRelationships
