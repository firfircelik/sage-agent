#!/usr/bin/env python3
"""
HTTP Server for Sage Agent Plugins.

High-performance FastAPI server providing REST API for OpenCode and Claude Code plugins.
Features streaming, caching, metrics, and comprehensive error handling.
"""

import sys
import os
import json
import time
import asyncio
import traceback
from typing import Any, Dict, Optional, List
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    BackgroundTasks,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rlm import EnterpriseRLM


class QueryRequest(BaseModel):
    """Request model for query processing."""
    query: str = Field(..., description="The query to process")
    provider: str = Field(default="openai", description="LLM provider")
    model: Optional[str] = Field(default=None, description="Model name")
    use_advanced_optimization: bool = Field(default=True, description="Enable RLM optimization")

    @validator('provider')
    def validate_provider(cls, v):
        valid_providers = ['openai', 'anthropic', 'deepseek', 'glm', 'cohere']
        if v not in valid_providers:
            raise ValueError(f"Provider must be one of {valid_providers}")
        return v


class MemoryRecallRequest(BaseModel):
    """Request model for memory recall."""
    query: str = Field(..., description="Query to find similar interactions")
    limit: int = Field(default=5, ge=1, le=20, description="Max results")


class AddInteractionRequest(BaseModel):
    """Request model for adding interaction."""
    query: str = Field(..., description="The query")
    response: str = Field(..., description="The response")
    provider: str = Field(default="openai", description="LLM provider")
    model: str = Field(default="gpt-4", description="Model name")
    tokens_used: int = Field(default=0, ge=0, description="Tokens consumed")
    success: bool = Field(default=True, description="Whether interaction was successful")


class FeedbackRequest(BaseModel):
    """Request model for feedback."""
    query: str = Field(..., description="The query")
    response: str = Field(..., description="The response")
    feedback: str = Field(..., description="Feedback text")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")


class AddKnowledgeRequest(BaseModel):
    """Request model for adding knowledge."""
    id: str = Field(..., description="Unique identifier")
    category: str = Field(..., description="Category (coding, security, etc.)")
    title: str = Field(..., description="Title")
    content: str = Field(..., description="Content")
    tags: List[str] = Field(default_factory=list, description="Tags")
    priority: int = Field(default=5, ge=0, le=10, description="Priority 0-10")


class SearchKnowledgeRequest(BaseModel):
    """Request model for searching knowledge."""
    query: Optional[str] = Field(default=None, description="Search query")
    category: Optional[str] = Field(default=None, description="Filter by category")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    limit: int = Field(default=5, ge=1, le=20, description="Max results")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


rlm_instance: Optional[EnterpriseRLM] = None
metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "average_response_time": 0.0,
    "total_processing_time": 0.0,
    "start_time": time.time(),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global rlm_instance
    print("🚀 Starting Sage Agent HTTP Server...")

    try:
        rlm_instance = EnterpriseRLM()
        print("✅ RLM Engine initialized successfully")
    except Exception as e:
        print(f"⚠️  RLM Engine initialization warning: {e}")

    yield

    print("🛑 Shutting down Sage Agent HTTP Server...")


app = FastAPI(
    title="Sage Agent API",
    description="Self-improving AI agent with RLM optimization and long-term memory",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def update_metrics(success: bool, processing_time: float):
    """Update performance metrics."""
    metrics["requests_total"] += 1
    if success:
        metrics["requests_successful"] += 1
    else:
        metrics["requests_failed"] += 1

    metrics["total_processing_time"] += processing_time
    metrics["average_response_time"] = (
        metrics["total_processing_time"] / metrics["requests_total"]
    )


def create_response(
    success: bool,
    data: Any = None,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> APIResponse:
    """Create standardized API response."""
    return APIResponse(
        success=success,
        data=data,
        error=error,
        metadata=metadata,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - metrics["start_time"]
    return {
        "status": "healthy",
        "uptime_seconds": uptime,
        "rlm_initialized": rlm_instance is not None,
        "metrics": {
            "requests_total": metrics["requests_total"],
            "success_rate": (
                metrics["requests_successful"] / metrics["requests_total"]
                if metrics["requests_total"] > 0
                else 0.0
            ),
            "avg_response_time": metrics["average_response_time"],
        },
    }


@app.post("/api/v1/query/process")
async def process_query(request: QueryRequest):
    """Process query with RLM optimization."""
    start_time = time.time()

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        result = rlm_instance.process_query(
            query=request.query,
            provider=request.provider,
            model=request.model,
            use_advanced_optimization=request.use_advanced_optimization,
        )

        processing_time = time.time() - start_time
        update_metrics(True, processing_time)

        return create_response(
            success=True,
            data={
                "from_memory": result.get("from_memory", False),
                "tokens_saved": result.get("tokens_saved", 0),
                "message": result.get("message", ""),
                "context_enhanced": result.get("context_enhanced", ""),
                "ai_analysis": result.get("ai_analysis"),
                "similar_memories": result.get("similar_memories", []),
                "improvement_suggestions": result.get("improvement_suggestions", []),
            },
            metadata={
                "processing_time": processing_time,
                "provider": request.provider,
                "model": request.model,
                "rlm_enabled": True,
            },
        )

    except Exception as e:
        processing_time = time.time() - start_time
        update_metrics(False, processing_time)

        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}",
        )


@app.post("/api/v1/query/stream")
async def process_query_stream(request: QueryRequest):
    """Process query with streaming response."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    async def generate():
        try:
            yield "event: start\n"
            yield f"data: {json.dumps({'status': 'processing', 'query': request.query})}\n\n"

            result = rlm_instance.process_query(
                query=request.query,
                provider=request.provider,
                model=request.model,
                use_advanced_optimization=request.use_advanced_optimization,
            )

            yield "event: result\n"
            yield f"data: {json.dumps({'success': True, 'result': result})}\n\n"

            yield "event: complete\n"
            yield f"data: {json.dumps({'status': 'complete', 'processing_time': result.get('processing_time', 0)})}\n\n"

        except Exception as e:
            error_msg = {"error": str(e), "traceback": traceback.format_exc()}
            yield "event: error\n"
            yield f"data: {json.dumps(error_msg)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@app.get("/api/v1/memory/recall")
async def recall_memory(query: str, limit: int = 5):
    """Recall similar past interactions."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        memories = rlm_instance.memory.recall(query, limit=limit)

        return create_response(
            success=True,
            data={
                "count": len(memories),
                "memories": [
                    {
                        "query": m.query,
                        "response": (
                            m.response[:200] + "..."
                            if len(m.response) > 200
                            else m.response
                        ),
                        "provider": m.provider,
                        "model": m.model,
                        "timestamp": m.timestamp.isoformat(),
                        "similarity": getattr(m, "similarity", 0.0),
                    }
                    for m in memories
                ],
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Memory recall failed: {str(e)}",
        )


@app.post("/api/v1/memory/add")
async def add_interaction(request: AddInteractionRequest):
    """Add interaction to memory."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        memory = rlm_instance.remember_interaction(
            query=request.query,
            response=request.response,
            provider=request.provider,
            model=request.model,
            tokens_used=request.tokens_used,
            success=request.success,
        )

        return create_response(
            success=True,
            data={
                "memory_id": memory["memory_id"],
                "validated": memory["validation"]["is_valid"] if memory["validation"] else None,
                "confidence": memory["validation"]["confidence"] if memory["validation"] else None,
                "learned": memory["learned"],
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add interaction: {str(e)}",
        )


@app.post("/api/v1/memory/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback for learning."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        rlm_instance.provide_feedback(
            query=request.query,
            response=request.response,
            feedback=request.feedback,
            rating=request.rating,
        )

        return create_response(
            success=True,
            data={"message": "Feedback recorded for self-improvement"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback: {str(e)}",
        )


@app.get("/api/v1/knowledge/search")
async def search_knowledge(
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 5,
):
    """Search knowledge base."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        results = rlm_instance.knowledge.search(
            query=query,
            category=category,
            tags=tags,
            limit=limit,
        )

        return create_response(
            success=True,
            data={
                "count": len(results),
                "results": [
                    {
                        "id": r.id,
                        "category": r.category,
                        "title": r.title,
                        "content": r.content,
                        "tags": r.tags,
                        "priority": r.priority,
                    }
                    for r in results
                ],
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge search failed: {str(e)}",
        )


@app.post("/api/v1/knowledge/add")
async def add_knowledge(request: AddKnowledgeRequest):
    """Add knowledge to knowledge base."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        success = rlm_instance.add_knowledge(
            id=request.id,
            category=request.category,
            title=request.title,
            content=request.content,
            tags=request.tags,
            priority=request.priority,
        )

        return create_response(
            success=success,
            data={"message": f"Knowledge '{request.title}' added successfully"}
            if success
            else {"message": "Failed to add knowledge"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add knowledge: {str(e)}",
        )


@app.get("/api/v1/stats")
async def get_stats():
    """Get comprehensive statistics."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        stats = rlm_instance.get_comprehensive_stats()

        return create_response(
            success=True,
            data=stats,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}",
        )


@app.get("/api/v1/stats/trends")
async def get_stats_trends():
    """Get quality and usage trends."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        stats = rlm_instance.get_comprehensive_stats()
        improvement_stats = stats.get("improvement", {})

        return create_response(
            success=True,
            data={
                "quality_trend": improvement_stats.get("quality_trend", {}),
                "usage_patterns": stats.get("usage", {}).get("patterns", {}),
                "provider_performance": stats.get("usage", {}).get("providers", {}),
                "learning_metrics": improvement_stats.get("learning_metrics", {}),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trends: {str(e)}",
        )


@app.get("/api/v1/learned/patterns")
async def get_learned_patterns():
    """View learned patterns."""

    if not rlm_instance:
        raise HTTPException(
            status_code=503,
            detail="RLM Engine not initialized",
        )

    try:
        insights = rlm_instance.memory.get_learned_insights()

        return create_response(
            success=True,
            data={
                "total_memories": insights.get("total_memories", 0),
                "learned_patterns": insights.get("learned_patterns", []),
                "success_patterns": insights.get("success_patterns", []),
                "common_mistakes": insights.get("common_mistakes", []),
                "success_rate": insights.get("success_rate", 0),
                "top_topics": insights.get("top_topics", []),
                "recommendations": insights.get("recommendations", []),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get learned patterns: {str(e)}",
        )


@app.get("/api/v1/metrics")
async def get_api_metrics():
    """Get API server metrics."""

    uptime = time.time() - metrics["start_time"]
    success_rate = (
        metrics["requests_successful"] / metrics["requests_total"]
        if metrics["requests_total"] > 0
        else 0.0
    )

    return create_response(
        success=True,
        data={
            "uptime_seconds": uptime,
            "requests_total": metrics["requests_total"],
            "requests_successful": metrics["requests_successful"],
            "requests_failed": metrics["requests_failed"],
            "success_rate": f"{success_rate * 100:.2f}%",
            "average_response_time": f"{metrics['average_response_time']:.3f}s",
            "requests_per_second": metrics["requests_total"] / uptime if uptime > 0 else 0,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        },
    )


def main():
    """Run the HTTP server."""
    print("=" * 60)
    print("🚀 Sage Agent HTTP Server")
    print("=" * 60)
    print("📊 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("💚 Health Check: http://localhost:8000/health")
    print("=" * 60)
    print()

    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
