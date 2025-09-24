# Monitoring and Observability

## Monitoring Stack
- **Frontend Monitoring:** Vercel Analytics + DataDog RUM for client-side performance and error tracking
- **Backend Monitoring:** AWS CloudWatch + DataDog APM for server-side performance and infrastructure metrics
- **Error Tracking:** DataDog Error Tracking with source map support for both frontend and backend
- **Performance Monitoring:** DataDog Synthetic Monitoring for end-to-end user journey validation

## Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP <2.5s, FID <100ms, CLS <0.1) for user experience optimization
- JavaScript errors and unhandled promise rejections for reliability tracking
- API response times from client perspective for performance monitoring
- User interactions and feature adoption rates for product insights

**Backend Metrics:**
- Request rate per endpoint and service for capacity planning
- Error rate by service and error type for reliability monitoring
- P50/P95/P99 response times for performance SLA compliance
- Database query performance and connection pool utilization for optimization
- GitHub API rate limit consumption and remaining quota for integration health
- Template detection accuracy and processing time for core feature monitoring
- Mermaid diagram generation time and cache hit rates for visualization performance
