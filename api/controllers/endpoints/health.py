from fastapi import APIRouter
from datetime import datetime
import psutil
import logging
from config.paths import (
    DATA_PATH,
    LAST_UPDATE_PATH,
    OUTPUTS_PATH,
    PROPERTIES_PATH,
    IS_API_CONTAINER,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": "container" if IS_API_CONTAINER else "local",
        "checks": {},
    }

    try:
        paths_check = {
            "data_path": {
                "path": str(DATA_PATH),
                "exists": DATA_PATH.exists(),
                "readable": DATA_PATH.exists() and DATA_PATH.is_dir(),
            },
            "last_update_path": {
                "path": str(LAST_UPDATE_PATH),
                "exists": LAST_UPDATE_PATH.exists(),
                "readable": LAST_UPDATE_PATH.exists() and LAST_UPDATE_PATH.is_dir(),
            },
            "outputs_path": {
                "path": str(OUTPUTS_PATH),
                "exists": OUTPUTS_PATH.exists(),
                "readable": OUTPUTS_PATH.exists() and OUTPUTS_PATH.is_dir(),
            },
            "properties_path": {
                "path": str(PROPERTIES_PATH),
                "exists": PROPERTIES_PATH.exists(),
                "readable": PROPERTIES_PATH.exists() and PROPERTIES_PATH.is_dir(),
            },
        }

        all_paths_ok = all(check["exists"] for check in paths_check.values())
        health_status["checks"]["data_paths"] = {
            "status": "ok" if all_paths_ok else "warning",
            "details": paths_check,
        }

        if not all_paths_ok:
            health_status["status"] = "degraded"

    except Exception as e:
        health_status["checks"]["data_paths"] = {"status": "error", "error": str(e)}
        health_status["status"] = "unhealthy"

    # System metrics
    try:
        health_status["checks"]["system"] = {
            "status": "ok",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": (
                psutil.disk_usage("/").percent if psutil.disk_usage("/") else 0
            ),
        }
    except Exception as e:
        health_status["checks"]["system"] = {"status": "warning", "error": str(e)}

    return health_status


@router.get("/ready")
async def readiness_check():
    """Simple readiness check for load balancers"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}


@router.get("/live")
async def liveness_check():
    """Simple liveness check for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
