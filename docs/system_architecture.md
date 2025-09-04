# EcoTrack System Architecture

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js SPA    │    │  Mobile Apps    │    │   Admin Panel   │
│   (Frontend)    │    │   (Future)      │    │   (Django)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (nginx/ALB)   │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Django REST    │    │  Django REST    │    │  Django REST    │
│   API Server    │    │   API Server    │    │   API Server    │
│   (Instance 1)  │    │   (Instance 2)  │    │   (Instance N)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │      Redis      │
                    │  (Cache/Queue)  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Celery      │    │     Celery      │    │   PostgreSQL    │
│    Worker 1     │    │    Worker 2     │    │   (Primary)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┘                       │
                    │                                     │
          ┌─────────────────┐                  ┌─────────────────┐
          │  Celery Beat    │                  │   PostgreSQL    │
          │  (Scheduler)    │                  │   (Read Replica)│
          └─────────────────┘                  └─────────────────┘
```

## Component Details

### Frontend Layer
- **Vue.js SPA**: Single Page Application with Vue 3, Vue Router, Vuex/Pinia
- **UI Framework**: Tailwind CSS or Vuetify for mobile-first responsive design
- **Charts**: Chart.js for data visualizations, D3.js for advanced charts
- **Maps**: OpenStreetMap with Leaflet for location features
- **PWA**: Progressive Web App capabilities for mobile experience

### API Layer
- **Django REST Framework**: RESTful API with automatic OpenAPI documentation
- **Authentication**: JWT tokens with refresh mechanism
- **Serialization**: DRF serializers with validation
- **Permissions**: Role-based access control (RBAC)
- **Rate Limiting**: Django-ratelimit for API protection
- **CORS**: Django-cors-headers for cross-origin requests

### Business Logic Layer
- **Carbon Calculation Engine**: Pluggable calculation system with emission factors
- **AI Integration**: Abstracted AI service adapter for Gemini API
- **Recommendation System**: Rule-based fallback with AI enhancement
- **Challenge Engine**: Gamification and social features
- **Notification System**: Real-time updates via WebSockets (future)

### Data Layer
- **PostgreSQL**: Primary database with time-series optimizations
- **Time-Series Tables**: Partitioned tables for activity and metrics data
- **Indexing Strategy**: Optimized indexes for time-based queries
- **Data Retention**: Automated archival and cleanup policies

### Cache Layer
- **Redis**: Caching for frequently accessed data
- **Session Storage**: User sessions and temporary data
- **Rate Limiting**: Request throttling state
- **Background Jobs**: Celery task queue

### Background Processing
- **Celery Workers**: Asynchronous task processing
- **Celery Beat**: Scheduled tasks (aggregations, reports)
- **Task Types**: Carbon calculations, AI requests, data aggregation, notifications

## Data Flow

### Activity Logging Flow
1. User submits activity via frontend
2. Frontend validates and sends to API
3. API validates request and stores raw activity
4. Background job calculates carbon footprint
5. Results stored and user notified
6. Dashboard updated with new metrics

### AI Recommendation Flow
1. User requests recommendations
2. API gathers user context and history
3. Background job calls Gemini API with prompt
4. AI response processed and filtered
5. Recommendations cached and returned
6. Usage logged for monitoring

### Real-time Updates (Phase 4)
1. Activity logged triggers event
2. WebSocket server broadcasts to relevant users
3. Frontend receives update and refreshes UI
4. Leaderboards and challenges updated live

## Security Architecture

### Authentication & Authorization
- JWT tokens with short expiration (15 minutes)
- Refresh tokens with longer expiration (7 days)
- Role-based permissions (User, Admin, Corporate Admin)
- API key authentication for corporate integrations

### Data Protection
- Encryption at rest (database-level)
- TLS encryption in transit
- PII minimization and hashing
- Secure environment variable management
- Input sanitization and validation

### Privacy Compliance
- GDPR-compliant data handling
- User consent management
- Data export and deletion capabilities
- Audit logging for data access
- Anonymous usage analytics

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers behind load balancer
- Database read replicas for query scaling
- Redis cluster for cache scaling
- Celery worker auto-scaling

### Performance Optimizations
- Database query optimization
- API response caching
- CDN for static assets
- Database connection pooling
- Async processing for heavy operations

### Monitoring & Observability
- Application metrics (Prometheus)
- Log aggregation (ELK stack)
- Error tracking (Sentry)
- Performance monitoring (APM)
- Health checks and alerting

## Deployment Architecture

### Development Environment
- Docker Compose for local development
- Hot reload for rapid development
- Test database with sample data
- Mock external services

### Production Environment
- Kubernetes orchestration (future)
- Multi-zone deployment for HA
- Blue-green deployment strategy
- Automated backup and recovery
- Environment-specific configuration

## External Integrations

### AI Services
- Gemini API for recommendations
- Fallback to rule-based system
- Response caching and rate limiting
- Quality monitoring and filtering

### Data Sources
- Emission factor databases
- Geographic data services
- Weather APIs (future)
- Utility company APIs (future)

### Third-party Services
- Email delivery (SendGrid/SES)
- File storage (S3/CloudStorage)
- Analytics (Google Analytics)
- Error tracking (Sentry)