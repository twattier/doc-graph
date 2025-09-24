# Unified Project Structure

```plaintext
docgraph/
├── .github/                        # CI/CD workflows and GitHub configuration
│   └── workflows/
│       ├── ci.yaml                 # Continuous integration pipeline
│       ├── deploy-staging.yaml     # Staging environment deployment
│       └── deploy-production.yaml  # Production deployment pipeline
├── apps/                           # Application packages
│   ├── web/                        # React frontend application
│   │   ├── src/
│   │   │   ├── components/         # Reusable UI components
│   │   │   │   ├── ui/             # shadcn/ui base components
│   │   │   │   ├── visualization/  # Template-aware visualization
│   │   │   │   ├── navigation/     # Navigation components
│   │   │   │   └── forms/          # Form components
│   │   │   ├── pages/              # Application pages/routes
│   │   │   │   ├── dashboard/      # Project dashboard
│   │   │   │   ├── project/        # Project exploration views
│   │   │   │   └── import/         # Repository import flow
│   │   │   ├── hooks/              # Custom React hooks
│   │   │   │   ├── useProject.ts   # Project data management
│   │   │   │   ├── useVisualization.ts
│   │   │   │   └── useAuth.ts      # Authentication hook
│   │   │   ├── services/           # API client services
│   │   │   │   ├── api.ts          # Base API configuration
│   │   │   │   ├── projects.ts     # Project API calls
│   │   │   │   └── visualizations.ts
│   │   │   ├── stores/             # Zustand state management
│   │   │   │   ├── projectStore.ts # Project state
│   │   │   │   ├── visualizationStore.ts
│   │   │   │   └── uiStore.ts      # UI preferences
│   │   │   ├── styles/             # Tailwind CSS styles
│   │   │   └── utils/              # Frontend utilities
│   │   ├── public/                 # Static assets
│   │   ├── tests/                  # Frontend tests (Vitest)
│   │   ├── next.config.js          # Next.js configuration
│   │   ├── tailwind.config.js      # Tailwind configuration
│   │   └── package.json
│   └── api/                        # Python FastAPI backend
│       ├── src/
│       │   ├── handlers/           # Lambda function handlers
│       │   │   ├── projects/       # Project management endpoints
│       │   │   ├── templates/      # Template detection endpoints
│       │   │   ├── visualizations/ # Visualization generation
│       │   │   └── search/         # Search and relationships
│       │   ├── services/           # Business logic services
│       │   │   ├── ProjectService.py
│       │   │   ├── TemplateService.py
│       │   │   ├── VisualizationService.py
│       │   │   └── SearchService.py
│       │   ├── models/             # Data access layer
│       │   │   ├── Project.py      # Project data model
│       │   │   ├── Document.py     # Document data model
│       │   │   └── database.py     # Database connections
│       │   ├── utils/              # Backend utilities
│       │   │   ├── github.py       # GitHub API integration
│       │   │   ├── mermaid.py      # Mermaid generation
│       │   │   └── embeddings.py   # Vector embeddings
│       │   └── types/              # Python type definitions
│       ├── tests/                  # Backend tests (pytest)
│       ├── requirements.txt        # Python dependencies
│       └── serverless.yml          # Serverless Framework config
├── packages/                       # Shared packages
│   ├── shared/                     # Shared TypeScript types and utilities
│   │   ├── src/
│   │   │   ├── types/              # Shared type definitions
│   │   │   │   ├── project.ts      # Project domain types
│   │   │   │   ├── visualization.ts # Visualization types
│   │   │   │   └── api.ts          # API contract types
│   │   │   ├── constants/          # Shared constants
│   │   │   │   ├── templateTypes.ts
│   │   │   │   └── apiEndpoints.ts
│   │   │   └── utils/              # Shared utility functions
│   │   │       ├── validation.ts   # Input validation
│   │   │       └── formatting.ts   # Data formatting
│   │   └── package.json
│   ├── ui/                         # Shared UI component library
│   │   ├── src/
│   │   │   ├── components/         # Reusable components
│   │   │   │   ├── TemplateZoneIndicator/
│   │   │   │   ├── MermaidViewer/
│   │   │   │   └── CrossTemplateLink/
│   │   │   └── styles/             # Component styles
│   │   └── package.json
│   └── config/                     # Shared configuration
│       ├── eslint/                 # ESLint configurations
│       │   ├── base.js
│       │   ├── react.js
│       │   └── node.js
│       ├── typescript/             # TypeScript configurations
│       │   ├── base.json
│       │   ├── react.json
│       │   └── node.json
│       └── jest/                   # Jest test configurations
├── infrastructure/                 # AWS CDK infrastructure definitions
│   ├── lib/
│   │   ├── database-stack.ts       # PostgreSQL and Neo4j setup
│   │   ├── api-stack.ts            # API Gateway and Lambda functions
│   │   ├── frontend-stack.ts       # CloudFront and S3 setup
│   │   └── monitoring-stack.ts     # CloudWatch and alerting
│   ├── bin/
│   │   └── docgraph.ts             # CDK app entry point
│   ├── cdk.json                    # CDK configuration
│   └── package.json
├── scripts/                        # Build and deployment scripts
│   ├── build.sh                    # Full project build
│   ├── deploy-staging.sh           # Staging deployment
│   ├── deploy-production.sh        # Production deployment
│   └── setup-dev.sh                # Development environment setup
├── docs/                           # Project documentation
│   ├── prd.md                      # Product Requirements Document
│   ├── front-end-spec.md           # UI/UX Specification
│   ├── architecture.md             # This document
│   └── api-documentation.md        # API reference
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── nx.json                         # Nx monorepo configuration
├── package.json                    # Root package.json with workspace config
├── README.md                       # Project overview and setup
└── tsconfig.json                   # Root TypeScript configuration
```
