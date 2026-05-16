import gc
from contextlib import asynccontextmanager
from fastapi import FastAPI


from app.core.config import get_settings
from app.core.logging import logger
from app.core.exceptions import (AppException, app_exception_handler, generic_exception_handler)

from app.api.routes.genai import router as genai_router
from app.api.routes.predict import router as predict_router
from app.api.routes.jobs import router as jobs_router


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    #---Startup---
    app.state.ready = False
    app.state.startup_error = None
    app.state.settings = settings
    
    try:    
        logger.info("Starting API in %s environment", settings.app_env)

        # Future startup initialization goes here
        # Example:
        # app.state.model = load_model()

        app.state.ready = True
        logger.info("API startup completed successfully")

    except Exception as e:
        # Handle initialization failure
        app.state.ready = False
        app.state.startup_error = str(e)
        app.state.settings = None
        logger.exception(f"Startup initialization failed: {str(e)}")

        # Fail fast for production readiness
        raise

    yield
    #--shutdown--
    logger.info("Shutting down API")
    # Future cleanup and teardown goes here
    # Example:
    # app.state.model = None
    # teardown_model()

    gc.collect()
    logger.info("API shutdown completed")

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan) 

# Register exception handlers from centralized exceptions module
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register API routes
app.include_router(genai_router)

# Note: The predict router is intentionally registered after the genai router to ensure that 
# the /predict/async endpoint is available for testing and does not conflict with any potential /genai endpoints. 
# This ordering allows for clear separation of concerns and avoids any unintended route overlaps.
app.include_router(predict_router)

# Register the Jobs router
app.include_router(jobs_router)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Cloud ML GenAI Deploy API is running",
        "environment": settings.app_env,
        "version": settings.app_version,
    }

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy" if app.state.ready else "not_ready",
        "app": settings.app_name,
        "environment": settings.app_env,
        "startup_error": app.state.startup_error,
    }

@app.get("/error-test")
async def error_test():
    raise AppException("This is a test application error", status_code=400)