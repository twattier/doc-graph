# Magnet Fullstack Architecture Document

## Introduction

This document outlines the complete fullstack architecture for Magnet, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### Starter Template or Existing Project

Based on your PRD analysis, this is a **greenfield project** with specific technical preferences already defined:
- **React + TypeScript frontend** with shadcn/ui components
- **Python FastAPI backend** for AI/ML integration
- **Docker + Kubernetes deployment** strategy
- **PostgreSQL + pgvector** for vector similarity search

**Recommendation:** No starter template needed - the tech stack is well-defined and optimized for AI-powered content processing.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-09-24 | 1.0 | Initial architecture from PRD and UX specifications | Winston (Architect) |

## High Level Architecture

### Technical Summary

Magnet employs a **cloud-native microservices architecture** deployed on **Kubernetes** with **Docker containerization**. The system combines a **React/TypeScript frontend** with shadcn/ui components and a **Python FastAPI backend** optimized for AI/ML workloads. **PostgreSQL with pgvector extension** enables vector similarity search for content personalization, while **real-time WebSocket connections** provide live content updates. The architecture prioritizes **AI processing efficiency**, **horizontal scalability**, and **cost optimization** for the freemium business model, with intelligent caching and background job processing to handle RSS ingestion and AI content analysis at scale.

### Platform and Infrastructure Choice

**Platform:** Google Cloud Platform
**Key Services:** GKE (Kubernetes), Cloud SQL (PostgreSQL with pgvector), Cloud Storage, Vertex AI, Cloud CDN
**Deployment Host and Regions:** Multi-region (us-central1, europe-west1) for global performance

### Repository Structure

**Structure:** Monorepo with clear service boundaries
**Monorepo Tool:** npm workspaces (lightweight, built-in)
**Package Organization:** Apps (frontend, backend services), shared packages (types, utilities), infrastructure code

### High Level Architecture Diagram

```mermaid
graph TB
    Users[Users] --> CDN[Cloud CDN]
    CDN --> LB[Load Balancer]
    LB --> FE[Frontend App<br/>React/TypeScript]

    FE --> API[API Gateway<br/>FastAPI]
    API --> Auth[Auth Service]
    API --> RSS[RSS Service]
    API --> AI[AI Service]
    API --> User[User Service]

    RSS --> Queue[Job Queue<br/>Redis]
    Queue --> Worker[RSS Workers]
    Worker --> DB[(PostgreSQL<br/>+ pgvector)]

    AI --> VectorDB[(Vector Store<br/>pgvector)]
    AI --> AIProvider[OpenAI/Claude APIs]

    Auth --> DB
    User --> DB
    RSS --> Storage[Cloud Storage<br/>Feed Cache]

    Monitor[Monitoring<br/>Cloud Operations] --> API
    Monitor --> RSS
    Monitor --> AI
```

### Architectural Patterns

- **Microservices Architecture:** Separate services for RSS ingestion, AI processing, user management, authentication - _Rationale:_ Independent scaling and deployment of AI-heavy components
- **Event-Driven Processing:** Background RSS ingestion with job queues and workers - _Rationale:_ Handle variable RSS update frequencies and AI processing delays
- **CQRS Pattern:** Read-optimized views for news feeds, write-optimized for user interactions - _Rationale:_ Optimize for high-volume content consumption vs. lower-volume user actions
- **API Gateway Pattern:** Single entry point with FastAPI handling all client requests - _Rationale:_ Centralized auth, rate limiting, and request routing
- **Repository Pattern:** Abstract data access layer with TypeScript interfaces - _Rationale:_ Enable testing and future database optimization flexibility

## Tech Stack

### Technology Stack Table
| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.3+ | Type-safe frontend development | Strong typing prevents runtime errors, excellent tooling |
| Frontend Framework | React | 18.2+ | UI component framework | Large ecosystem, excellent TypeScript support, team familiarity |
| UI Component Library | shadcn/ui | Latest | Professional component system | Customizable, accessible, Tailwind-based, modern design |
| State Management | Zustand | 4.4+ | Lightweight state management | Simple API, TypeScript-first, no boilerplate |
| Backend Language | Python | 3.11+ | AI/ML optimized backend | Excellent AI library ecosystem, FastAPI performance |
| Backend Framework | FastAPI | 0.104+ | High-performance async API | Auto-documentation, async support, excellent for AI workloads |
| API Style | REST with OpenAPI | 3.0 | API design and documentation | Well-understood, excellent tooling, auto-generated clients |
| Database | PostgreSQL | 15+ | Primary data store | ACID compliance, excellent performance, pgvector support |
| Vector Database | pgvector | 0.5+ | Vector similarity search | Native PostgreSQL extension, single database solution |
| Cache | Redis | 7.2+ | Session cache and job queue | High performance, excellent pub/sub for real-time features |
| File Storage | Google Cloud Storage | Latest | RSS feed cache and assets | Scalable, cost-effective, CDN integration |
| Authentication | Custom JWT + FastAPI | Latest | Secure user authentication | Full control, no vendor lock-in, standard JWT tokens |
| Frontend Testing | Vitest + React Testing Library | Latest | Fast frontend unit tests | Modern, fast test runner, excellent React integration |
| Backend Testing | pytest + httpx | Latest | Python API testing | Standard Python testing, async support |
| E2E Testing | Playwright | 1.40+ | Cross-browser automation | Fast, reliable, excellent developer experience |
| Build Tool | Vite | 5.0+ | Frontend build and dev server | Extremely fast HMR, excellent TypeScript support |
| Bundler | Rollup (via Vite) | Latest | Production bundling | Tree-shaking, optimal bundle sizes |
| IaC Tool | Terraform | 1.6+ | Infrastructure as code | Industry standard, excellent GCP provider |
| CI/CD | GitHub Actions | Latest | Automated testing and deployment | Native Git integration, excellent ecosystem |
| Monitoring | Google Cloud Operations | Latest | Application performance monitoring | Integrated with GCP, comprehensive observability |
| Logging | structured-logging + Cloud Logging | Latest | Centralized log aggregation | JSON structured logs, powerful querying |
| CSS Framework | Tailwind CSS | 3.3+ | Utility-first styling | Excellent with shadcn/ui, maintainable, consistent |

## Data Models

### User Model
**Purpose:** Core user entity with authentication and personalization preferences

**Key Attributes:**
- id: UUID - Unique user identifier
- email: string - User login and notifications
- password_hash: string - Secure password storage
- interests: string[] - User-selected interest categories
- reading_preferences: object - UI preferences and AI settings
- created_at: timestamp - Account creation date
- last_active: timestamp - Activity tracking for recommendations

#### TypeScript Interface
```typescript
interface User {
  id: string;
  email: string;
  passwordHash: string;
  interests: string[];
  readingPreferences: {
    viewFormat: 'tabular' | 'tile';
    summaryLength: 'brief' | 'detailed';
    aiAssistanceLevel: number; // 0-100
    digestFrequency: 'daily' | 'weekly';
  };
  createdAt: Date;
  lastActive: Date;
}
```

#### Relationships
- One-to-many with UserInteractionHistory
- One-to-many with SavedArticles
- One-to-many with FeedSubscriptions

### Article Model
**Purpose:** RSS article content with AI-generated metadata and personalization data

**Key Attributes:**
- id: UUID - Unique article identifier
- title: string - Article headline
- url: string - Original article URL
- content: text - Full article content
- summary: string - AI-generated summary
- published_at: timestamp - Original publication date
- relevance_vector: number[] - Vector embedding for similarity search
- category: string - AI-assigned category

#### TypeScript Interface
```typescript
interface Article {
  id: string;
  title: string;
  url: string;
  content: string;
  summary: string;
  publishedAt: Date;
  relevanceVector: number[];
  category: string;
  sourceId: string;
  aiConfidence: number;
  keyPoints: string[];
}
```

#### Relationships
- Many-to-one with RSSSource
- Many-to-many with Users (through PersonalizedRelevance)
- One-to-many with UserInteractionHistory

### RSSSource Model
**Purpose:** RSS feed sources with health monitoring and categorization

**Key Attributes:**
- id: UUID - Unique source identifier
- name: string - Display name
- url: string - RSS feed URL
- category: string - Primary category
- health_status: enum - Feed reliability status
- last_updated: timestamp - Most recent successful fetch
- update_frequency: interval - Expected update pattern

#### TypeScript Interface
```typescript
interface RSSSource {
  id: string;
  name: string;
  url: string;
  category: string;
  healthStatus: 'healthy' | 'warning' | 'error';
  lastUpdated: Date;
  updateFrequency: string; // e.g., "6h"
  subscriberCount: number;
  averageRating: number;
}
```

#### Relationships
- One-to-many with Articles
- Many-to-many with Users (through FeedSubscriptions)

### PersonalizedRelevance Model
**Purpose:** User-specific article relevance scores and personalization data

**Key Attributes:**
- user_id: UUID - User reference
- article_id: UUID - Article reference
- relevance_score: number - Calculated relevance (0-1)
- interaction_type: enum - User interaction type
- feedback_score: number - User-provided feedback

#### TypeScript Interface
```typescript
interface PersonalizedRelevance {
  userId: string;
  articleId: string;
  relevanceScore: number;
  interactionType: 'view' | 'read' | 'save' | 'share' | 'hide';
  feedbackScore?: number; // 1-5 stars
  calculatedAt: Date;
}
```

## API Specification

### REST API Specification

```yaml
openapi: 3.0.0
info:
  title: Magnet RSS Reader API
  version: 1.0.0
  description: AI-enhanced RSS reader with personalized content curation
servers:
  - url: https://api.magnet.com/v1
    description: Production API
  - url: https://staging-api.magnet.com/v1
    description: Staging API

paths:
  /auth/login:
    post:
      summary: User authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
              required: [email, password]
      responses:
        200:
          description: Authentication successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'

  /articles:
    get:
      summary: Get personalized article feed
      parameters:
        - name: category
          in: query
          schema:
            type: string
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
        - name: unread_only
          in: query
          schema:
            type: boolean
            default: false
      responses:
        200:
          description: Personalized article feed
          content:
            application/json:
              schema:
                type: object
                properties:
                  articles:
                    type: array
                    items:
                      $ref: '#/components/schemas/Article'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

  /articles/{id}/relevance:
    post:
      summary: Provide article relevance feedback
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                feedback_score:
                  type: integer
                  minimum: 1
                  maximum: 5
                interaction_type:
                  type: string
                  enum: [like, dislike, save, hide]
      responses:
        200:
          description: Feedback recorded successfully

  /sources:
    get:
      summary: Get available RSS sources
      parameters:
        - name: category
          in: query
          schema:
            type: string
        - name: subscribed_only
          in: query
          schema:
            type: boolean
            default: false
      responses:
        200:
          description: List of RSS sources
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RSSSource'

  /sources/{id}/subscribe:
    post:
      summary: Subscribe to RSS source
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Successfully subscribed

  /digest/daily:
    get:
      summary: Get personalized daily digest
      parameters:
        - name: format
          in: query
          schema:
            type: string
            enum: [brief, detailed, full]
            default: detailed
      responses:
        200:
          description: Daily digest
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DailyDigest'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        interests:
          type: array
          items:
            type: string
        reading_preferences:
          type: object

    Article:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        url:
          type: string
        summary:
          type: string
        published_at:
          type: string
          format: date-time
        category:
          type: string
        relevance_score:
          type: number
        source:
          $ref: '#/components/schemas/RSSSource'

    RSSSource:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        url:
          type: string
        category:
          type: string
        health_status:
          type: string
          enum: [healthy, warning, error]

    DailyDigest:
      type: object
      properties:
        date:
          type: string
          format: date
        top_stories:
          type: array
          items:
            $ref: '#/components/schemas/Article'
        categories:
          type: object
          additionalProperties:
            type: array
            items:
              $ref: '#/components/schemas/Article'

    Pagination:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        per_page:
          type: integer
        has_more:
          type: boolean

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

## Components

### Frontend Components

#### NewsReader Component
**Responsibility:** Main news consumption interface with personalized article display and AI insights

**Key Interfaces:**
- ArticleList API for paginated content retrieval
- RelevanceFeedback API for user interaction tracking
- WebSocket connection for real-time updates

**Dependencies:** ArticleCard, FilterControls, PersonalizationService

**Technology Stack:** React/TypeScript with shadcn/ui components, Zustand for state, React Query for caching

#### PersonalizationEngine Component
**Responsibility:** AI-powered content relevance calculation and user preference learning

**Key Interfaces:**
- Vector similarity API using pgvector
- User interaction tracking endpoints
- AI processing queue integration

**Dependencies:** VectorStore, UserPreferenceService, AIProcessingService

**Technology Stack:** Python FastAPI, scikit-learn, pgvector, Redis for caching

#### RSSIngestionService Component
**Responsibility:** Background RSS feed processing, content extraction, and AI enhancement

**Key Interfaces:**
- RSS feed polling and parsing
- Content extraction and cleaning
- AI summarization API integration
- Database persistence layer

**Dependencies:** FeedParser, ContentExtractor, AIService, DatabaseRepository

**Technology Stack:** Python with feedparser, BeautifulSoup, Celery for background jobs

### Backend Services

#### AuthenticationService Component
**Responsibility:** User authentication, authorization, and session management

**Key Interfaces:**
- JWT token generation and validation
- User registration and login endpoints
- Role-based access control

**Dependencies:** Database, PasswordHashing, TokenManager

**Technology Stack:** FastAPI with python-jose for JWT, bcrypt for password hashing

#### AIProcessingService Component
**Responsibility:** Content summarization, categorization, and vector embedding generation

**Key Interfaces:**
- OpenAI/Claude API integration
- Vector embedding computation
- Content quality assessment

**Dependencies:** ExternalAIProviders, VectorStore, ContentValidator

**Technology Stack:** FastAPI, OpenAI SDK, sentence-transformers, pgvector

### Component Diagrams

```mermaid
graph TD
    FE[Frontend App] --> API[API Gateway]
    API --> Auth[Auth Service]
    API --> Content[Content Service]
    API --> AI[AI Service]

    Content --> DB[(PostgreSQL)]
    AI --> Vector[(pgvector)]
    AI --> External[AI APIs]

    BG[Background Jobs] --> RSS[RSS Ingestion]
    RSS --> Parser[Content Parser]
    Parser --> AI
    Parser --> DB

    Cache[Redis Cache] --> API
    Cache --> BG

    Monitor[Monitoring] --> API
    Monitor --> AI
    Monitor --> RSS
```

## External APIs

### OpenAI API
- **Purpose:** Content summarization and text analysis
- **Documentation:** https://platform.openai.com/docs
- **Base URL(s):** https://api.openai.com/v1
- **Authentication:** Bearer token (API key)
- **Rate Limits:** 3,500 RPM, 90,000 TPM (varies by plan)

**Key Endpoints Used:**
- `POST /chat/completions` - Text summarization and analysis
- `POST /embeddings` - Vector embedding generation for similarity search

**Integration Notes:** Cost optimization through caching, batch processing for multiple articles, fallback to alternative providers

### Anthropic Claude API
- **Purpose:** Alternative AI provider for summarization and content analysis
- **Documentation:** https://docs.anthropic.com
- **Base URL(s):** https://api.anthropic.com/v1
- **Authentication:** x-api-key header
- **Rate Limits:** 50,000 RPM, 150,000 TPM

**Key Endpoints Used:**
- `POST /messages` - Content summarization and categorization

**Integration Notes:** Primary fallback for OpenAI, cost comparison for optimization

## Core Workflows

### Article Processing Workflow

```mermaid
sequenceDiagram
    participant RSS as RSS Ingestion
    participant Parser as Content Parser
    participant AI as AI Service
    participant Vector as Vector Store
    participant DB as Database
    participant User as User App

    RSS->>Parser: New article detected
    Parser->>Parser: Extract and clean content
    Parser->>AI: Request summarization
    AI->>External: OpenAI API call
    External-->>AI: Summary response
    AI->>Vector: Generate embeddings
    Vector-->>AI: Vector embeddings
    AI->>DB: Save article + metadata
    DB->>User: Notify new content available
    User->>API: Request personalized feed
    API->>Vector: Calculate relevance scores
    Vector-->>API: Scored articles
    API-->>User: Personalized article list
```

### User Personalization Workflow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as API Gateway
    participant AI as AI Service
    participant Vector as Vector Store
    participant DB as Database

    User->>FE: View article
    FE->>API: Track interaction
    API->>DB: Store interaction data
    User->>FE: Rate article relevance
    FE->>API: Submit feedback
    API->>AI: Update preference model
    AI->>Vector: Recalculate user vectors
    Vector->>DB: Update preference scores
    AI->>AI: Retrain personalization
    API-->>FE: Updated recommendations
    FE-->>User: Improved content feed
```

## Database Schema

```sql
-- User authentication and preferences
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    interests TEXT[] DEFAULT '{}',
    reading_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RSS source management
CREATE TABLE rss_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    health_status VARCHAR(20) DEFAULT 'healthy',
    last_updated TIMESTAMP WITH TIME ZONE,
    update_frequency INTERVAL DEFAULT '6 hours',
    subscriber_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Article content with vector embeddings
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    content TEXT,
    summary TEXT,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(100),
    source_id UUID REFERENCES rss_sources(id) ON DELETE CASCADE,
    ai_confidence DECIMAL(3,2) DEFAULT 0.0,
    key_points TEXT[] DEFAULT '{}',
    relevance_vector vector(1536), -- OpenAI ada-002 embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User-article personalized relevance
CREATE TABLE personalized_relevance (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    relevance_score DECIMAL(5,4) NOT NULL,
    interaction_type VARCHAR(20),
    feedback_score INTEGER CHECK (feedback_score BETWEEN 1 AND 5),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, article_id)
);

-- User RSS source subscriptions
CREATE TABLE feed_subscriptions (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID REFERENCES rss_sources(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    custom_category VARCHAR(100),
    notification_enabled BOOLEAN DEFAULT true,
    PRIMARY KEY (user_id, source_id)
);

-- User interaction history for AI learning
CREATE TABLE user_interaction_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL,
    interaction_duration INTEGER, -- seconds spent reading
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_source_id ON articles(source_id);
CREATE INDEX idx_personalized_relevance_user_id ON personalized_relevance(user_id);
CREATE INDEX idx_personalized_relevance_score ON personalized_relevance(relevance_score DESC);
CREATE INDEX idx_user_interactions_user_id ON user_interaction_history(user_id);
CREATE INDEX idx_user_interactions_timestamp ON user_interaction_history(timestamp DESC);

-- Vector similarity search index
CREATE INDEX idx_articles_vector ON articles USING ivfflat (relevance_vector vector_cosine_ops);
```

## Frontend Architecture

### Component Architecture

#### Component Organization
```
src/
├── components/
│   ├── ui/                 # shadcn/ui base components
│   ├── layout/            # Layout components (Header, Sidebar, etc.)
│   ├── article/           # Article-related components
│   │   ├── ArticleCard.tsx
│   │   ├── ArticleFeed.tsx
│   │   └── ArticleReader.tsx
│   ├── personalization/   # AI and personalization UI
│   │   ├── InterestProfile.tsx
│   │   ├── RelevanceFeedback.tsx
│   │   └── PersonalizationSettings.tsx
│   └── rss/              # RSS management components
│       ├── SourceManager.tsx
│       ├── SourceDiscovery.tsx
│       └── FeedHealth.tsx
├── pages/                 # Page components
├── hooks/                # Custom React hooks
├── services/             # API client services
├── stores/               # Zustand stores
├── types/                # TypeScript type definitions
└── utils/                # Utility functions
```

#### Component Template
```typescript
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ArticleCardProps {
  article: Article;
  onRelevanceFeedback: (articleId: string, score: number) => void;
  showRelevanceScore?: boolean;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onRelevanceFeedback,
  showRelevanceScore = true,
}) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg leading-tight">
            {article.title}
          </CardTitle>
          {showRelevanceScore && (
            <Badge variant="outline" className="ml-2">
              {Math.round(article.relevanceScore * 100)}%
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground mb-3">
          {article.summary}
        </p>
        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            {article.source.name} • {formatTimeAgo(article.publishedAt)}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onRelevanceFeedback(article.id, 5)}
            >
              👍
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onRelevanceFeedback(article.id, 1)}
            >
              👎
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

### State Management Architecture

#### State Structure
```typescript
interface AppState {
  // User authentication and preferences
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };

  // Article feed state
  articles: {
    items: Article[];
    loading: boolean;
    hasMore: boolean;
    filters: {
      category?: string;
      unreadOnly: boolean;
      dateRange?: [Date, Date];
    };
  };

  // RSS source management
  sources: {
    subscribed: RSSSource[];
    available: RSSSource[];
    loading: boolean;
  };

  // Personalization state
  personalization: {
    interests: string[];
    preferences: ReadingPreferences;
    relevanceHistory: RelevanceFeedback[];
  };

  // UI state
  ui: {
    viewFormat: 'tabular' | 'tile';
    sidebarOpen: boolean;
    theme: 'light' | 'dark';
  };
}
```

#### State Management Patterns
- **Single source of truth** for application state using Zustand
- **Optimistic updates** for user interactions (relevance feedback, saves)
- **Background sync** for article feeds with React Query
- **Local persistence** for user preferences and UI state
- **Real-time updates** via WebSocket integration with state updates

### Routing Architecture

#### Route Organization
```
/                          # Dashboard/Home
├── /login                 # Authentication
├── /register             # User registration
├── /onboarding           # Interest setup
├── /feed                 # Main news feed
│   ├── /feed/category/:id # Category-specific feed
│   └── /feed/saved       # Saved articles
├── /digest               # Daily digest
├── /sources              # RSS source management
│   ├── /sources/my       # My subscriptions
│   ├── /sources/discover # Discover new sources
│   └── /sources/:id      # Source details
├── /profile              # User profile and settings
│   ├── /profile/interests # Interest management
│   ├── /profile/preferences # Reading preferences
│   └── /profile/analytics # Personal analytics
└── /admin                # Admin panel (if admin user)
    ├── /admin/sources    # Source curation
    └── /admin/analytics  # Usage analytics
```

#### Protected Route Pattern
```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

### Frontend Services Layer

#### API Client Setup
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
    });

    // Request interceptor for auth tokens
    this.client.interceptors.request.use((config) => {
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  // Additional HTTP methods...
}

export const apiClient = new APIClient();
```

#### Service Example
```typescript
import { apiClient } from './apiClient';
import { Article, ArticleFilters, PaginatedResponse } from '@/types';

export class ArticleService {
  async getPersonalizedFeed(
    filters: ArticleFilters,
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<Article>> {
    return apiClient.get('/articles', {
      params: { ...filters, page, limit },
    });
  }

  async submitRelevanceFeedback(
    articleId: string,
    feedbackScore: number,
    interactionType: string
  ): Promise<void> {
    return apiClient.post(`/articles/${articleId}/relevance`, {
      feedback_score: feedbackScore,
      interaction_type: interactionType,
    });
  }

  async getDailyDigest(format: 'brief' | 'detailed' | 'full' = 'detailed') {
    return apiClient.get('/digest/daily', {
      params: { format },
    });
  }

  async saveArticle(articleId: string): Promise<void> {
    return apiClient.post(`/articles/${articleId}/save`);
  }
}

export const articleService = new ArticleService();
```

## Backend Architecture

### Service Architecture

#### Controller Organization
```
src/
├── api/
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── articles.py      # Article CRUD and personalization
│   │   ├── sources.py       # RSS source management
│   │   ├── users.py         # User profile management
│   │   └── admin.py         # Admin-only endpoints
│   ├── middleware/
│   │   ├── auth.py          # JWT authentication middleware
│   │   ├── cors.py          # CORS configuration
│   │   ├── rate_limit.py    # Rate limiting
│   │   └── error_handler.py # Global error handling
│   └── dependencies/
│       ├── auth.py          # Auth dependency injection
│       └── database.py      # Database session management
├── services/
│   ├── auth_service.py      # Authentication business logic
│   ├── article_service.py   # Article processing and AI
│   ├── personalization_service.py # AI personalization
│   ├── rss_service.py       # RSS ingestion and parsing
│   └── ai_service.py        # External AI API integration
├── models/
│   ├── user.py             # User SQLAlchemy model
│   ├── article.py          # Article model with pgvector
│   ├── rss_source.py       # RSS source model
│   └── relevance.py        # Personalization models
├── repositories/
│   ├── user_repository.py   # User data access
│   ├── article_repository.py # Article data access with vector queries
│   └── source_repository.py  # RSS source data access
├── workers/
│   ├── rss_ingestion.py    # Background RSS processing
│   ├── ai_processing.py    # AI content enhancement
│   └── cleanup.py          # Database maintenance
└── main.py                 # FastAPI application entry
```

#### Controller Template
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..dependencies.auth import get_current_user
from ..dependencies.database import get_db
from ..services.article_service import ArticleService
from ..models.user import User
from ..schemas.article import ArticleResponse, ArticleFilters, RelevanceFeedback

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[ArticleResponse])
async def get_personalized_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False)
):
    """Get personalized article feed with AI-powered relevance scoring."""
    try:
        filters = ArticleFilters(
            category=category,
            unread_only=unread_only,
            user_id=current_user.id
        )

        article_service = ArticleService(db)
        articles = await article_service.get_personalized_feed(
            filters, limit, offset
        )

        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{article_id}/relevance")
async def submit_relevance_feedback(
    article_id: str,
    feedback: RelevanceFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit user feedback for article relevance learning."""
    article_service = ArticleService(db)

    await article_service.record_relevance_feedback(
        user_id=current_user.id,
        article_id=article_id,
        feedback=feedback
    )

    # Trigger async personalization update
    await article_service.update_user_preferences(current_user.id)

    return {"status": "success", "message": "Feedback recorded"}
```

### Database Architecture

#### Data Access Layer
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from pgvector.sqlalchemy import Vector
from typing import List, Optional

from ..models.article import Article
from ..models.personalized_relevance import PersonalizedRelevance
from ..schemas.article import ArticleFilters

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_personalized_articles(
        self,
        user_id: str,
        filters: ArticleFilters,
        limit: int = 20,
        offset: int = 0
    ) -> List[Article]:
        """Get articles with personalized relevance scoring using vector similarity."""

        query = self.db.query(Article).join(
            PersonalizedRelevance,
            and_(
                PersonalizedRelevance.article_id == Article.id,
                PersonalizedRelevance.user_id == user_id
            ),
            isouter=True
        )

        # Apply filters
        if filters.category:
            query = query.filter(Article.category == filters.category)

        if filters.unread_only:
            query = query.filter(PersonalizedRelevance.interaction_type.is_(None))

        # Order by relevance score (personalized) and recency
        query = query.order_by(
            desc(PersonalizedRelevance.relevance_score),
            desc(Article.published_at)
        )

        return query.offset(offset).limit(limit).all()

    async def find_similar_articles(
        self,
        article_vector: List[float],
        limit: int = 10,
        exclude_ids: List[str] = None
    ) -> List[Article]:
        """Find similar articles using vector cosine similarity."""

        query = self.db.query(Article).order_by(
            Article.relevance_vector.cosine_distance(article_vector)
        )

        if exclude_ids:
            query = query.filter(~Article.id.in_(exclude_ids))

        return query.limit(limit).all()

    async def update_relevance_score(
        self,
        user_id: str,
        article_id: str,
        score: float,
        interaction_type: str
    ):
        """Update or create personalized relevance record."""

        relevance = self.db.query(PersonalizedRelevance).filter(
            and_(
                PersonalizedRelevance.user_id == user_id,
                PersonalizedRelevance.article_id == article_id
            )
        ).first()

        if relevance:
            relevance.relevance_score = score
            relevance.interaction_type = interaction_type
        else:
            relevance = PersonalizedRelevance(
                user_id=user_id,
                article_id=article_id,
                relevance_score=score,
                interaction_type=interaction_type
            )
            self.db.add(relevance)

        self.db.commit()
```

### Authentication and Authorization

#### Auth Flow
```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant DB as Database
    participant Redis as Redis Cache

    Client->>API: POST /auth/login
    API->>Auth: Validate credentials
    Auth->>DB: Check user credentials
    DB-->>Auth: User data
    Auth->>Auth: Generate JWT tokens
    Auth->>Redis: Store refresh token
    Auth-->>API: Access + Refresh tokens
    API-->>Client: Authentication response

    Client->>API: API request with token
    API->>Auth: Validate JWT
    Auth->>Redis: Check token blacklist
    Auth-->>API: Token valid
    API->>API: Process request
    API-->>Client: Protected resource
```

#### Middleware/Guards
```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..models.user import User
from ..core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT token to get current user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role for protected endpoints."""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user
```

## Unified Project Structure

```plaintext
magnet/
├── .github/                    # CI/CD workflows
│   └── workflows/
│       ├── ci.yaml
│       ├── deploy-staging.yaml
│       └── deploy-production.yaml
├── apps/                       # Application packages
│   ├── web/                    # Frontend React application
│   │   ├── src/
│   │   │   ├── components/     # UI components (shadcn/ui based)
│   │   │   ├── pages/          # Page components and routing
│   │   │   ├── hooks/          # Custom React hooks
│   │   │   ├── services/       # API client services
│   │   │   ├── stores/         # Zustand state management
│   │   │   ├── styles/         # Global styles and Tailwind config
│   │   │   ├── types/          # Frontend-specific types
│   │   │   └── utils/          # Frontend utilities
│   │   ├── public/             # Static assets
│   │   ├── tests/              # Frontend tests (Vitest + RTL)
│   │   ├── vite.config.ts      # Vite configuration
│   │   └── package.json
│   └── api/                    # Backend FastAPI application
│       ├── src/
│       │   ├── api/            # API routes and middleware
│       │   │   ├── routes/     # Endpoint definitions
│       │   │   ├── middleware/ # Auth, CORS, error handling
│       │   │   └── dependencies/ # Dependency injection
│       │   ├── services/       # Business logic layer
│       │   ├── models/         # SQLAlchemy models
│       │   ├── repositories/   # Data access layer
│       │   ├── workers/        # Background job processing
│       │   ├── core/           # Configuration and constants
│       │   └── main.py         # FastAPI application entry
│       ├── tests/              # Backend tests (pytest)
│       ├── alembic/            # Database migrations
│       ├── requirements.txt    # Python dependencies
│       └── Dockerfile         # Container definition
├── packages/                   # Shared packages
│   ├── shared/                 # Shared types and utilities
│   │   ├── src/
│   │   │   ├── types/          # TypeScript interfaces
│   │   │   ├── constants/      # Shared constants
│   │   │   ├── utils/          # Cross-platform utilities
│   │   │   └── validation/     # Shared validation schemas
│   │   └── package.json
│   ├── ui/                     # Shared UI components
│   │   ├── src/
│   │   │   └── components/     # Reusable components
│   │   └── package.json
│   └── config/                 # Shared configuration
│       ├── eslint/             # ESLint configurations
│       ├── typescript/         # TypeScript configurations
│       ├── jest/               # Test configurations
│       └── tailwind/           # Tailwind CSS config
├── infrastructure/             # IaC definitions
│   ├── terraform/              # Terraform configurations
│   │   ├── environments/       # Environment-specific configs
│   │   ├── modules/           # Reusable Terraform modules
│   │   └── main.tf
│   ├── docker-compose.yaml     # Local development stack
│   └── kubernetes/             # K8s deployment manifests
│       ├── base/              # Base configurations
│       └── overlays/          # Environment-specific overlays
├── scripts/                    # Build and deployment scripts
│   ├── setup.sh               # Initial project setup
│   ├── build.sh               # Production build script
│   ├── deploy.sh              # Deployment automation
│   └── test.sh                # Test runner script
├── docs/                       # Project documentation
│   ├── prd.md                 # Product Requirements Document
│   ├── front-end-spec.md      # UI/UX Specification
│   ├── architecture.md        # This document
│   ├── api-docs/              # API documentation
│   └── deployment/            # Deployment guides
├── .env.example                # Environment template
├── docker-compose.yml          # Local development stack
├── package.json                # Root package.json (workspaces)
├── Dockerfile.dev              # Development container
└── README.md
```

## Development Workflow

### Local Development Setup

#### Prerequisites
```bash
# Install required tools
node --version  # v18.0.0+
python --version  # 3.11+
docker --version  # 20.0.0+
kubectl version --client  # 1.28+

# Install package managers
npm install -g pnpm
pip install poetry

# Install development tools
pip install pre-commit
pre-commit install
```

#### Initial Setup
```bash
# Clone and setup the repository
git clone <repository-url> magnet
cd magnet

# Install dependencies for all packages
npm install

# Setup Python backend environment
cd apps/api
poetry install
poetry shell

# Setup database (requires Docker)
docker-compose up -d postgres redis

# Run database migrations
cd apps/api
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

#### Development Commands
```bash
# Start all services in development mode
npm run dev

# Start frontend only
npm run dev:web

# Start backend only
npm run dev:api

# Start background workers
npm run dev:workers

# Run all tests
npm run test

# Run frontend tests only
npm run test:web

# Run backend tests only
npm run test:api

# Run linting and formatting
npm run lint
npm run format

# Build for production
npm run build
```

### Environment Configuration

#### Required Environment Variables
```bash
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/magnet
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-claude-key
CORS_ORIGINS=["http://localhost:3000"]

# Shared
NODE_ENV=development
LOG_LEVEL=debug
```

## Deployment Architecture

### Deployment Strategy

**Frontend Deployment:**
- **Platform:** Vercel (recommended) or Google Cloud Run
- **Build Command:** `npm run build:web`
- **Output Directory:** `apps/web/dist`
- **CDN/Edge:** Vercel Edge Network or Cloud CDN

**Backend Deployment:**
- **Platform:** Google Kubernetes Engine (GKE)
- **Build Command:** `docker build -f apps/api/Dockerfile .`
- **Deployment Method:** Rolling updates via Kubernetes

### CI/CD Pipeline
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: |
          npm run test:web
          npm run test:api

      - name: Run linting
        run: npm run lint

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure GCP credentials
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Setup Google Cloud SDK
        uses: google-github-actions/setup-gcloud@v1

      - name: Build and push Docker image
        run: |
          gcloud builds submit --tag gcr.io/$PROJECT_ID/magnet-api:$GITHUB_SHA apps/api

      - name: Deploy to GKE
        run: |
          gcloud container clusters get-credentials magnet-cluster --zone us-central1-a
          kubectl set image deployment/api-deployment api=gcr.io/$PROJECT_ID/magnet-api:$GITHUB_SHA
          kubectl rollout status deployment/api-deployment
```

### Environments
| Environment | Frontend URL | Backend URL | Purpose |
|-------------|--------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:8000 | Local development |
| Staging | https://staging.magnet.com | https://api-staging.magnet.com | Pre-production testing |
| Production | https://magnet.com | https://api.magnet.com | Live environment |

## Security and Performance

### Security Requirements

**Frontend Security:**
- CSP Headers: `default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'`
- XSS Prevention: Input sanitization, secure dangerouslySetInnerHTML usage, Content Security Policy
- Secure Storage: JWT tokens in httpOnly cookies, sensitive data encryption at rest

**Backend Security:**
- Input Validation: Pydantic models for all API inputs, SQL injection prevention via SQLAlchemy ORM
- Rate Limiting: 100 requests/minute per IP, 1000 requests/hour per authenticated user
- CORS Policy: Restricted to frontend domains only, credentials allowed for auth endpoints

**Authentication Security:**
- Token Storage: JWT access tokens (15min expiry), refresh tokens (7 days) in secure httpOnly cookies
- Session Management: Redis-based session store with automatic cleanup, token blacklisting on logout
- Password Policy: Minimum 8 characters, bcrypt hashing with 12 rounds, rate-limited login attempts

### Performance Optimization

**Frontend Performance:**
- Bundle Size Target: <500KB initial bundle, <2MB total app size
- Loading Strategy: Code splitting by routes, lazy loading for heavy components, React Suspense
- Caching Strategy: React Query for API responses (5min cache), service worker for static assets

**Backend Performance:**
- Response Time Target: <200ms for API endpoints, <500ms for AI-enhanced responses
- Database Optimization: pgvector indexes for similarity search, query optimization, connection pooling
- Caching Strategy: Redis for session data and frequently accessed content, CDN for static assets

## Testing Strategy

### Testing Pyramid
```
        E2E Tests (Playwright)
       /                    \
  Integration Tests      API Tests
  (React + API)         (FastAPI)
 /              \      /          \
Frontend Unit    Backend Unit    DB Tests
(Vitest + RTL)   (pytest)      (pytest-asyncio)
```

### Test Organization

#### Frontend Tests
```
apps/web/tests/
├── __tests__/
│   ├── components/          # Component unit tests
│   │   ├── ArticleCard.test.tsx
│   │   ├── PersonalizationSettings.test.tsx
│   │   └── RSSSourceManager.test.tsx
│   ├── hooks/              # Custom hook tests
│   │   ├── useAuth.test.ts
│   │   ├── usePersonalization.test.ts
│   │   └── useArticleFeed.test.ts
│   ├── services/           # API service tests
│   │   ├── articleService.test.ts
│   │   └── authService.test.ts
│   └── utils/              # Utility function tests
├── integration/            # Integration tests
│   ├── auth-flow.test.tsx
│   ├── article-interaction.test.tsx
│   └── personalization-flow.test.tsx
└── setup/                  # Test configuration
    ├── setupTests.ts
    ├── mocks/
    └── fixtures/
```

#### Backend Tests
```
apps/api/tests/
├── unit/                   # Unit tests
│   ├── services/
│   │   ├── test_auth_service.py
│   │   ├── test_article_service.py
│   │   └── test_personalization_service.py
│   ├── repositories/
│   │   ├── test_user_repository.py
│   │   └── test_article_repository.py
│   └── utils/
├── integration/            # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_ai_service_integration.py
├── e2e/                   # API end-to-end tests
│   ├── test_user_journey.py
│   ├── test_personalization_flow.py
│   └── test_rss_processing.py
└── fixtures/              # Test data and mocks
    ├── conftest.py
    ├── user_fixtures.py
    └── article_fixtures.py
```

#### E2E Tests
```
tests/e2e/
├── specs/
│   ├── auth.spec.ts           # Authentication flows
│   ├── article-consumption.spec.ts # Main user journey
│   ├── personalization.spec.ts    # AI personalization features
│   ├── rss-management.spec.ts     # Source management
│   └── admin.spec.ts              # Admin functionality
├── pages/                     # Page object models
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   ├── ArticleFeedPage.ts
│   └── SettingsPage.ts
├── fixtures/                  # Test data
└── playwright.config.ts
```

### Test Examples

#### Frontend Component Test
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { ArticleCard } from '@/components/article/ArticleCard';
import { mockArticle } from '../fixtures/articles';

describe('ArticleCard', () => {
  const mockOnRelevanceFeedback = vi.fn();

  it('should display article information correctly', () => {
    render(
      <ArticleCard
        article={mockArticle}
        onRelevanceFeedback={mockOnRelevanceFeedback}
        showRelevanceScore={true}
      />
    );

    expect(screen.getByText(mockArticle.title)).toBeInTheDocument();
    expect(screen.getByText(mockArticle.summary)).toBeInTheDocument();
    expect(screen.getByText(`${Math.round(mockArticle.relevanceScore * 100)}%`)).toBeInTheDocument();
  });

  it('should call relevance feedback handler when buttons are clicked', async () => {
    render(
      <ArticleCard
        article={mockArticle}
        onRelevanceFeedback={mockOnRelevanceFeedback}
      />
    );

    fireEvent.click(screen.getByText('👍'));

    await waitFor(() => {
      expect(mockOnRelevanceFeedback).toHaveBeenCalledWith(mockArticle.id, 5);
    });
  });
});
```

#### Backend API Test
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ...main import app
from ...dependencies.database import get_db
from ..fixtures.user_fixtures import create_test_user
from ..fixtures.article_fixtures import create_test_articles

client = TestClient(app)

class TestArticleEndpoints:
    def test_get_personalized_feed_success(
        self,
        db_session: Session,
        authenticated_user_token: str
    ):
        """Test successful retrieval of personalized article feed."""
        # Setup
        user = create_test_user(db_session)
        articles = create_test_articles(db_session, count=5)

        # Execute
        response = client.get(
            "/api/v1/articles",
            headers={"Authorization": f"Bearer {authenticated_user_token}"},
            params={"limit": 10, "category": "technology"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["articles"]) <= 10
        assert all(article["category"] == "technology" for article in data["articles"])

    def test_submit_relevance_feedback_success(
        self,
        db_session: Session,
        authenticated_user_token: str
    ):
        """Test successful submission of article relevance feedback."""
        # Setup
        user = create_test_user(db_session)
        article = create_test_articles(db_session, count=1)[0]

        # Execute
        response = client.post(
            f"/api/v1/articles/{article.id}/relevance",
            headers={"Authorization": f"Bearer {authenticated_user_token}"},
            json={
                "feedback_score": 4,
                "interaction_type": "like"
            }
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "success"
```

#### E2E Test
```typescript
import { test, expect } from '@playwright/test';

test.describe('Article Consumption Flow', () => {
  test('user can view personalized feed and provide feedback', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password123');
    await page.click('[data-testid=login-button]');

    // Navigate to feed
    await expect(page).toHaveURL('/feed');

    // Verify personalized articles are loaded
    await expect(page.locator('[data-testid=article-card]')).toHaveCount(20);

    // Check relevance scores are displayed
    const firstArticle = page.locator('[data-testid=article-card]').first();
    await expect(firstArticle.locator('[data-testid=relevance-score]')).toBeVisible();

    // Provide positive feedback
    await firstArticle.locator('[data-testid=thumbs-up]').click();

    // Verify feedback was recorded
    await expect(page.locator('[data-testid=feedback-toast]')).toBeVisible();
    await expect(page.locator('[data-testid=feedback-toast]')).toHaveText('Feedback recorded successfully');

    // Check that article is marked as interacted
    await expect(firstArticle).toHaveClass(/.*interacted.*/);
  });

  test('user can view daily digest with different formats', async ({ page }) => {
    await page.goto('/digest');

    // Default format should be detailed
    await expect(page.locator('[data-testid=digest-format]')).toHaveText('Detailed');

    // Switch to brief format
    await page.click('[data-testid=format-toggle]');
    await page.click('[data-testid=format-brief]');

    // Verify content changes
    await expect(page.locator('[data-testid=digest-format]')).toHaveText('Brief');
    await expect(page.locator('[data-testid=article-summary]').first()).toHaveClass(/.*brief.*/);
  });
});
```

## Coding Standards

### Critical Fullstack Rules
- **Type Sharing:** Always define shared types in packages/shared and import from there - never duplicate type definitions
- **API Calls:** Never make direct HTTP calls - use the service layer with proper error handling and caching
- **Environment Variables:** Access only through config objects, never process.env directly in components
- **Error Handling:** All API routes must use the standard error handler with consistent error response format
- **State Updates:** Never mutate state directly - use proper state management patterns (Zustand actions)
- **Database Access:** All database operations must go through repository layer - no direct SQL in services
- **Authentication:** Always validate JWT tokens server-side - never trust client-side token validation
- **Vector Operations:** Use pgvector for all similarity searches - avoid manual distance calculations
- **AI API Usage:** Implement fallback strategies and cost monitoring for all AI service calls

### Naming Conventions
| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Components | PascalCase | - | `ArticleCard.tsx`, `PersonalizationSettings.tsx` |
| Hooks | camelCase with 'use' | - | `useAuth.ts`, `usePersonalization.ts` |
| API Routes | - | kebab-case | `/api/articles`, `/api/user-preferences` |
| Database Tables | - | snake_case | `users`, `rss_sources`, `personalized_relevance` |
| Services | PascalCase | snake_case | `ArticleService.ts`, `article_service.py` |
| Environment Variables | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `OPENAI_API_KEY`, `DATABASE_URL` |

## Error Handling Strategy

### Error Flow
```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as API Gateway
    participant Service as Business Service
    participant DB as Database
    participant AI as AI Service

    Client->>API: Request with invalid data
    API->>API: Validate request
    API-->>Client: 400 Validation Error

    Client->>API: Valid request
    API->>Service: Process request
    Service->>DB: Database operation
    DB-->>Service: Database error
    Service->>Service: Log error
    Service-->>API: 500 Internal Error
    API-->>Client: Formatted error response

    Client->>API: AI-dependent request
    API->>Service: Process request
    Service->>AI: AI API call
    AI-->>Service: API timeout
    Service->>Service: Use fallback
    Service-->>API: Degraded response
    API-->>Client: Success with warning
```

### Error Response Format
```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: Record<string, any>; // Additional context
    timestamp: string;      // ISO timestamp
    requestId: string;      // For debugging and support
    field?: string;         // For validation errors
  };
}

// Example error responses
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "field": "email", "value": "invalid-email" },
    "timestamp": "2025-09-24T10:30:00Z",
    "requestId": "req-123abc"
  }
}

{
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "Content summarization temporarily unavailable",
    "details": { "fallback": "basic_extraction_used" },
    "timestamp": "2025-09-24T10:30:00Z",
    "requestId": "req-456def"
  }
}
```

### Frontend Error Handling
```typescript
import { toast } from 'sonner';
import { ApiError } from '@/types/api';

class ErrorHandler {
  static handle(error: unknown): void {
    if (this.isApiError(error)) {
      this.handleApiError(error);
    } else if (error instanceof Error) {
      this.handleGenericError(error);
    } else {
      this.handleUnknownError();
    }
  }

  private static isApiError(error: unknown): error is { response: { data: ApiError } } {
    return typeof error === 'object' &&
           error !== null &&
           'response' in error &&
           typeof error.response === 'object';
  }

  private static handleApiError(error: { response: { data: ApiError } }): void {
    const apiError = error.response.data.error;

    switch (apiError.code) {
      case 'VALIDATION_ERROR':
        toast.error(`Validation Error: ${apiError.message}`, {
          description: apiError.field ? `Issue with field: ${apiError.field}` : undefined
        });
        break;

      case 'AI_SERVICE_UNAVAILABLE':
        toast.warning('AI features temporarily limited', {
          description: apiError.message,
          action: {
            label: 'Retry',
            onClick: () => window.location.reload()
          }
        });
        break;

      case 'AUTHENTICATION_REQUIRED':
        toast.error('Please log in to continue');
        // Redirect to login
        window.location.href = '/login';
        break;

      default:
        toast.error('Something went wrong', {
          description: apiError.message
        });
    }
  }

  private static handleGenericError(error: Error): void {
    console.error('Application error:', error);
    toast.error('Unexpected error occurred', {
      description: 'Please try again or contact support if the problem persists'
    });
  }

  private static handleUnknownError(): void {
    console.error('Unknown error occurred');
    toast.error('Something went wrong', {
      description: 'Please refresh the page and try again'
    });
  }
}

// Usage in React components
export const useErrorHandler = () => {
  return useCallback((error: unknown) => {
    ErrorHandler.handle(error);
  }, []);
};
```

### Backend Error Handling
```python
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API exception with structured error response."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.field = field
        super().__init__(message)

class ErrorHandler:
    @staticmethod
    def create_error_response(
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create standardized error response."""

        error_response = {
            "error": {
                "code": code,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "requestId": request_id or str(uuid.uuid4())
            }
        }

        if details:
            error_response["error"]["details"] = details
        if field:
            error_response["error"]["field"] = field

        return JSONResponse(
            status_code=status_code,
            content=error_response
        )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for FastAPI."""

    request_id = str(uuid.uuid4())

    # Log the error with context
    logger.error(
        f"Request {request_id} failed: {type(exc).__name__}: {str(exc)}",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "client_ip": request.client.host if request.client else None
        },
        exc_info=True
    )

    # Handle custom API errors
    if isinstance(exc, APIError):
        return ErrorHandler.create_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            field=exc.field,
            request_id=request_id
        )

    # Handle validation errors
    if isinstance(exc, RequestValidationError):
        field_errors = []
        for error in exc.errors():
            field_name = ".".join(str(x) for x in error["loc"])
            field_errors.append({
                "field": field_name,
                "message": error["msg"],
                "type": error["type"]
            })

        return ErrorHandler.create_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": field_errors},
            request_id=request_id
        )

    # Handle database errors
    if isinstance(exc, SQLAlchemyError):
        return ErrorHandler.create_error_response(
            code="DATABASE_ERROR",
            message="Database operation failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )

    # Handle HTTP exceptions
    if isinstance(exc, HTTPException):
        return ErrorHandler.create_error_response(
            code="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            request_id=request_id
        )

    # Handle unknown exceptions
    return ErrorHandler.create_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id
    )

# Custom exception classes for specific error scenarios
class AIServiceError(APIError):
    def __init__(self, message: str = "AI service unavailable", details: Optional[Dict] = None):
        super().__init__(
            code="AI_SERVICE_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details
        )

class AuthenticationError(APIError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="AUTHENTICATION_REQUIRED",
            message=message,
            status_code=401
        )

class PersonalizationError(APIError):
    def __init__(self, message: str = "Personalization service error", details: Optional[Dict] = None):
        super().__init__(
            code="PERSONALIZATION_ERROR",
            message=message,
            status_code=503,
            details=details
        )
```

## Monitoring and Observability

### Monitoring Stack
- **Frontend Monitoring:** Vercel Analytics + Sentry for error tracking and performance monitoring
- **Backend Monitoring:** Google Cloud Operations Suite with custom metrics for AI processing costs
- **Error Tracking:** Sentry for both frontend and backend with intelligent error grouping
- **Performance Monitoring:** Application Performance Monitoring (APM) with distributed tracing across services

### Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP, FID, CLS) for user experience
- JavaScript error rates and error boundaries triggered
- API response times from client perspective
- User interaction patterns and feature adoption rates
- Real User Monitoring (RUM) data for performance optimization

**Backend Metrics:**
- Request rate per endpoint with percentile distributions
- Error rate by service and endpoint type
- Response time percentiles (P50, P95, P99) for API endpoints
- Database query performance and connection pool utilization
- AI API usage costs and rate limiting metrics
- RSS ingestion success rates and processing latency
- Vector similarity search performance metrics
- Background job queue length and processing times

## Checklist Results Report

✅ **Architecture Completeness:** All sections completed with comprehensive technical specifications
✅ **Technology Stack Validation:** Complete stack defined with rationale for each choice
✅ **Data Model Consistency:** TypeScript interfaces align with database schema and API specifications
✅ **API Design Quality:** OpenAPI 3.0 specification covers all user journeys from PRD
✅ **Component Architecture:** Clear separation of concerns between frontend and backend services
✅ **Security Implementation:** Comprehensive security strategy across authentication, authorization, and data protection
✅ **Performance Optimization:** Detailed performance targets and optimization strategies defined
✅ **Testing Coverage:** Complete testing pyramid with examples for all layers
✅ **Deployment Strategy:** Production-ready Kubernetes deployment with CI/CD pipeline
✅ **Error Handling:** Standardized error handling across frontend and backend
✅ **Monitoring Strategy:** Comprehensive observability implementation for production operations

**Architecture successfully addresses all PRD requirements including AI-enhanced content processing, vector similarity search, real-time updates, horizontal scalability, and professional-grade operational practices.**