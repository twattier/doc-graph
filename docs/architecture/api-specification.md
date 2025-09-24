# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: DocGraph API
  version: 1.0.0
  description: Template-aware documentation exploration and visualization API
servers:
  - url: https://api.docgraph.dev
    description: Production API server
paths:
  /projects:
    get:
      summary: List user projects
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [importing, processing, ready, error]
      responses:
        '200':
          description: List of projects
          content:
            application/json:
              schema:
                type: object
                properties:
                  projects:
                    type: array
                    items:
                      $ref: '#/components/schemas/Project'
    post:
      summary: Import new project from GitHub
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                githubUrl:
                  type: string
                  format: uri
                name:
                  type: string
                templateMappings:
                  type: array
                  items:
                    $ref: '#/components/schemas/TemplateMapping'
      responses:
        '201':
          description: Project import started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Project'

  /projects/{projectId}/template-zones:
    get:
      summary: Get template zones for project
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Template zones with document counts
          content:
            application/json:
              schema:
                type: object
                properties:
                  templateZones:
                    type: array
                    items:
                      $ref: '#/components/schemas/TemplateZone'

  /projects/{projectId}/visualizations:
    get:
      summary: Get available visualizations for project
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: templateZoneId
          in: query
          schema:
            type: string
            format: uuid
        - name: visualizationType
          in: query
          schema:
            type: string
            enum: [tree, pipeline, graph, cross-template]
      responses:
        '200':
          description: Available visualizations
          content:
            application/json:
              schema:
                type: object
                properties:
                  visualizations:
                    type: array
                    items:
                      $ref: '#/components/schemas/Visualization'
    post:
      summary: Generate new visualization
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                visualizationType:
                  type: string
                  enum: [tree, pipeline, graph, cross-template]
                templateZoneId:
                  type: string
                  format: uuid
                config:
                  type: object
      responses:
        '201':
          description: Visualization generated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Visualization'

  /projects/{projectId}/search:
    get:
      summary: Search project documents with template-aware filtering
      parameters:
        - name: projectId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: query
          in: query
          required: true
          schema:
            type: string
        - name: templateType
          in: query
          schema:
            type: string
            enum: [bmad-method, claude-code, generic]
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Search results with template context
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        document:
                          $ref: '#/components/schemas/Document'
                        relevanceScore:
                          type: number
                        matchContext:
                          type: string

  /visualizations/{visualizationId}/export:
    get:
      summary: Export visualization as Mermaid code or image
      parameters:
        - name: visualizationId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: format
          in: query
          schema:
            type: string
            enum: [mermaid, svg, png]
            default: mermaid
      responses:
        '200':
          description: Exported visualization
          content:
            text/plain:
              schema:
                type: string
            image/svg+xml:
              schema:
                type: string
            image/png:
              schema:
                type: string
                format: binary

components:
  schemas:
    Project:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        githubUrl:
          type: string
          format: uri
        status:
          type: string
          enum: [importing, processing, ready, error]
        templateMappings:
          type: array
          items:
            $ref: '#/components/schemas/TemplateMapping'
        metadata:
          type: object
          properties:
            fileCount:
              type: integer
            lastCommit:
              type: string
              format: date-time
            detectionConfidence:
              type: number
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    TemplateMapping:
      type: object
      properties:
        pathPattern:
          type: string
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        confidence:
          type: number
        override:
          type: boolean

    Document:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        filePath:
          type: string
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        extractedMetadata:
          type: object
        detectionConfidence:
          type: number
        processingStatus:
          type: string
          enum: [pending, processed, failed]

    TemplateZone:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        templateType:
          type: string
          enum: [bmad-method, claude-code, generic]
        rootPath:
          type: string
        completenessScore:
          type: number
        documentCount:
          type: integer
        visualizationConfig:
          type: object

    Visualization:
      type: object
      properties:
        id:
          type: string
          format: uuid
        projectId:
          type: string
          format: uuid
        visualizationType:
          type: string
          enum: [tree, pipeline, graph, cross-template]
        mermaidCode:
          type: string
        generationMetadata:
          type: object
          properties:
            generatedAt:
              type: string
              format: date-time
            generationTimeMs:
              type: integer
            nodeCount:
              type: integer
            relationshipCount:
              type: integer
            cacheHit:
              type: boolean

  securitySchemes:
    CognitoAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - CognitoAuth: []
```
