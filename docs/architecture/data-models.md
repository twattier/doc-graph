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
  createdBy: string; // User ID who created the project
  createdAt: Date;
  updatedAt: Date;
}

interface ProjectUser {
  id: string;
  projectId: string;
  userId: string;
  role: 'owner' | 'editor' | 'viewer';
  permissions: {
    read: boolean;
    write: boolean;
    admin: boolean;
  };
  addedBy?: string;
  addedAt: Date;
}
```

### Relationships
- Has many Documents
- Has many ProjectDocsType
- Has many Users (through ProjectUser)
- Created by one User (createdBy)

## Document
**Purpose:** Individual file within a project with template classification and extracted metadata

**Key Attributes:**
- id: string (UUID) - Unique document identifier
- projectId: string - Parent project reference
- filePath: string - Relative path within repository
- content: string - Document content
- docType: DocType - Detected documentation type classification
- extractedMetadata: DocumentMetadata - Documentation type-specific metadata
- embeddingVector: number[] - pgvector embedding for similarity search
- processingStatus: ProcessingStatus - Current processing state

### TypeScript Interface
```typescript
interface Document {
  id: string;
  projectId: string;
  projectDocsTypeId?: string;
  filePath: string;
  content: string;
  docType: 'bmad-method' | 'claude-code' | 'generic';
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
- Has many CrossDocTypeRelationships (source and target)
- Part of ProjectDocsType

## ProjectDocsType
**Purpose:** Logical grouping of documents within a project that share the same documentation type

**Key Attributes:**
- id: string (UUID) - Unique identifier
- projectId: string - Parent project reference
- docType: DocType - Documentation type classification
- rootPath: string - Base directory path for this documentation type
- visualizationConfig: VisualizationConfig - Type-specific visualization settings
- completenessScore: number - Assessment of documentation completeness

### TypeScript Interface
```typescript
interface ProjectDocsType {
  id: string;
  projectId: string;
  docType: 'bmad-method' | 'claude-code' | 'generic';
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

## CrossDocTypeRelationship
**Purpose:** Represents connections and dependencies between documents from different documentation types

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
interface CrossDocTypeRelationship {
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
**Purpose:** Generated Mermaid diagram representing documentation type-specific or cross-type relationships

**Key Attributes:**
- id: string (UUID) - Unique visualization identifier
- projectId: string - Parent project reference
- projectDocsTypeId: string - Associated documentation type (if applicable)
- visualizationType: VisualizationType - Type of diagram generated
- mermaidCode: string - Generated Mermaid diagram syntax
- generationMetadata: GenerationMetadata - Creation details and performance metrics
- cacheStatus: CacheStatus - Cache state for performance optimization

### TypeScript Interface
```typescript
interface Visualization {
  id: string;
  projectId: string;
  projectDocsTypeId?: string;
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
- May belong to ProjectDocsType
- Generated from Documents and CrossDocTypeRelationships
