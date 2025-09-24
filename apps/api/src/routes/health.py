"""
Health check endpoints for DocGraph API
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ..models.base import HealthCheckResponse
from ..database import health_check_postgres, health_check_redis, health_check_neo4j

router = APIRouter()




@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """
    Perform comprehensive health check of the API and its dependencies.
    """
    try:
        # Check all service dependencies
        database_health = await health_check_postgres()
        neo4j_health = await health_check_neo4j()
        redis_health = await health_check_redis()

        # Determine overall status
        all_services = [database_health, neo4j_health, redis_health]
        overall_status = "healthy" if all(
            service["status"] == "healthy" for service in all_services
        ) else "unhealthy"

        health_response = HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="0.1.0",
            services={
                "database": database_health,
                "neo4j": neo4j_health,
                "redis": redis_health
            }
        )

        status_code = (
            status.HTTP_200_OK if overall_status == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(
            content=health_response.model_dump(),
            status_code=status_code
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "0.1.0",
                "error": str(e),
                "services": {}
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )