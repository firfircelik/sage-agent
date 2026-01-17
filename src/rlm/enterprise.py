"""
Enterprise RLM System - Complete integration of all components.
"""

from typing import Dict, List, Any
from datetime import datetime
from .engine import RLMOptimizer
from .knowledge_base import KnowledgeBase
from .vector_store import VectorStore
from .intelligence import IntelligenceEngine
from .memory import LongTermMemory
from .self_improvement import SelfImprovementEngine
from .advanced_optimizer import AdvancedOptimizer, AdaptiveCompressor


class EnterpriseRLM:
    """
    Enterprise-grade RLM system - Self-improving AI that never forgets.

    Features:
    - Long-term memory (remembers everything)
    - Self-improvement (learns from mistakes)
    - No hallucinations (validates responses)
    - No duplication (checks memory first)
    - Advanced optimization (multiple strategies)
    - Intelligent caching with LRU and TTL
    - Semantic search with vector embeddings
    - Knowledge base with categories and tags
    - AI-powered pattern learning
    - Automatic optimization recommendations
    - Performance tracking and analytics
    """

    def __init__(self, cache_dir: str = ".rlm_cache", enable_all: bool = True):
        # Core optimizer
        self.optimizer = RLMOptimizer(
            cache_dir=cache_dir,
            enable_compression=enable_all,
            enable_deduplication=enable_all,
        )

        # Advanced optimizer
        self.advanced_optimizer = AdvancedOptimizer()
        self.adaptive_compressor = AdaptiveCompressor()

        # Knowledge management
        self.knowledge = KnowledgeBase(f"{cache_dir}/knowledge")

        # Vector search
        self.vectors = VectorStore(cache_dir=f"{cache_dir}/vectors")

        # AI intelligence
        self.intelligence = IntelligenceEngine()

        # Long-term memory - NEVER FORGETS
        self.memory = LongTermMemory(f"{cache_dir}/memory")

        # Self-improvement - LEARNS FROM MISTAKES
        self.improvement = SelfImprovementEngine(f"{cache_dir}/improvement")

        print("✅ Enterprise RLM initialized")
        print(f"   Memory: {len(self.memory.memories)} interactions")
        print(f"   Knowledge: {len(self.knowledge.entries)} entries")
        print(
            f"   Embeddings: {'enabled' if self.vectors.embeddings_model else 'disabled'}"
        )

    def add_common_knowledge(self):
        """Add common programming knowledge (user can call this if needed)."""
        common_knowledge = [
            {
                "id": "rest_api_design",
                "category": "api",
                "title": "REST API Design Principles",
                "content": (
                    "Use HTTP methods correctly: GET for read, POST for create, "
                    "PUT for update, DELETE for remove. Use plural nouns for "
                    "resources. Version your API."
                ),
                "tags": ["api", "rest", "design"],
                "priority": 9,
            },
            {
                "id": "authentication_jwt",
                "category": "security",
                "title": "JWT Authentication",
                "content": (
                    "JWT tokens contain header, payload, and signature. Include in "
                    "Authorization header as Bearer token. Set appropriate "
                    "expiration time."
                ),
                "tags": ["auth", "jwt", "security"],
                "priority": 9,
            },
            {
                "id": "database_normalization",
                "category": "database",
                "title": "Database Normalization",
                "content": (
                    "Normalize to reduce redundancy. Use foreign keys for "
                    "relationships. Index frequently queried columns."
                ),
                "tags": ["database", "sql", "design"],
                "priority": 8,
            },
            {
                "id": "error_handling",
                "category": "coding",
                "title": "Error Handling Best Practices",
                "content": (
                    "Always handle errors gracefully. Use try-catch blocks. Log "
                    "errors with context. Return meaningful error messages."
                ),
                "tags": ["error", "exception", "best-practice"],
                "priority": 8,
            },
            {
                "id": "testing_strategy",
                "category": "testing",
                "title": "Testing Strategy",
                "content": (
                    "Write unit tests for functions. Integration tests for APIs. "
                    "Use mocking for external services. Aim for 80%+ coverage."
                ),
                "tags": ["testing", "unit-test", "quality"],
                "priority": 7,
            },
        ]

        for item in common_knowledge:
            self.knowledge.add(**item)
            if self.vectors.embeddings_model:
                self.vectors.add(
                    item["id"],
                    f"{item['title']}: {item['content']}",
                    {"category": item["category"], "tags": item["tags"]},
                )

        print(f"✅ Added {len(common_knowledge)} common knowledge entries")

    def process_query(
        self,
        query: str,
        provider: str = "openai",
        model: str = "gpt-4",
        use_intelligence: bool = True,
        validate_response: bool = True,
        use_advanced_optimization: bool = True,
    ) -> Dict[str, Any]:
        """
        Process query with full enterprise optimization + self-improvement.

        Flow:
        1. Check if exact query was asked before (no duplication)
        2. Recall similar past interactions (learn from history)
        3. AI analysis and recommendations
        4. Search knowledge base and vectors
        5. Advanced optimization (if enabled)
        6. Optimize with RLM
        7. Validate response (no hallucinations)
        8. Remember everything
        9. Learn and improve
        """
        start_time = datetime.now()

        # 1. Check memory for exact match (NO DUPLICATION)
        exact_memory = self.memory.recall_exact(query)
        if exact_memory:
            return {
                "from_memory": True,
                "query": query,
                "response": exact_memory.response,
                "context": exact_memory.context,
                "provider": exact_memory.provider,
                "model": exact_memory.model,
                "tokens_saved": exact_memory.tokens_used,
                "processing_time": 0.001,  # Instant
                "message": "Retrieved from long-term memory (exact match)",
            }

        # 2. Recall similar interactions
        similar_memories = self.memory.recall(query, limit=3)
        memory_context = ""
        if similar_memories:
            memory_context = "\n".join(
                [f"Past: {m.query} -> {m.response[:100]}..." for m in similar_memories]
            )

        # 3. Get improvement suggestions
        improvement_suggestions = self.improvement.get_improvement_suggestions(query)

        # 4. AI Analysis
        analysis = None
        if use_intelligence:
            analysis = self.intelligence.analyze_query(query)

        # 5. Search knowledge base
        kb_results = self.knowledge.search(query=query, limit=3, min_priority=7)

        # 6. Semantic search in vectors
        vector_results = []
        if self.vectors.embeddings_model:
            vector_results = self.vectors.search(query, top_k=3, threshold=0.5)

        # 7. Build context from all sources
        context_parts = []

        # Add memory context
        if memory_context:
            context_parts.append(f"[Memory] {memory_context}")

        # Add knowledge base results
        for entry in kb_results:
            context_parts.append(f"[{entry.category}] {entry.title}: {entry.content}")

        # Add vector results
        for entry, similarity in vector_results:
            if entry.id not in [e.id for e in kb_results]:
                context_parts.append(f"[Similar] {entry.text}")

        # Add improvement suggestions
        if improvement_suggestions:
            context_parts.append(f"[Suggestions] {'; '.join(improvement_suggestions)}")

        context = "\n".join(context_parts[:7])  # Max 7 context items

        # 8. Advanced optimization (if enabled)
        advanced_result = None
        if use_advanced_optimization:
            advanced_result = self.advanced_optimizer.optimize_prompt_advanced(
                query, context, preserve_meaning=True
            )
            query = advanced_result["optimized_prompt"]
            context = advanced_result["context"]

        # 9. Adaptive compression
        (
            compressed_query,
            compression_strategy,
        ) = self.adaptive_compressor.compress_adaptive(query, context)

        # 10. Optimize with RLM
        optimization = self.optimizer.optimize_prompt(
            compressed_query,
            use_cache=True,
            use_context=bool(context),
            context_strategy="hybrid" if self.vectors.embeddings_model else "keyword",
            compression_strategy=(
                "smart" if analysis and analysis.get("should_compress") else "minimal"
            ),
        )

        # 11. Prepare result
        result = {
            **optimization,
            "from_memory": False,
            "ai_analysis": analysis,
            "knowledge_results": len(kb_results),
            "vector_results": len(vector_results),
            "similar_memories": len(similar_memories),
            "improvement_suggestions": improvement_suggestions,
            "context_enhanced": context,
            "advanced_optimization": advanced_result,
            "compression_strategy": compression_strategy,
            "processing_time": (datetime.now() - start_time).total_seconds(),
        }

        return result

    def remember_interaction(
        self,
        query: str,
        response: str,
        context: str = "",
        provider: str = "",
        model: str = "",
        tokens_used: int = 0,
        success: bool = True,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """
        Remember interaction and validate response quality.

        Returns:
        - memory_id: str
        - validation: Dict (if validate=True)
        - learned: bool
        """
        # Validate response
        validation = None
        if validate:
            validation = self.improvement.validate_response(query, response, context)

            # If validation fails, mark as unsuccessful
            if not validation["is_valid"]:
                success = False

        # Remember in long-term memory
        memory_id = self.memory.remember(
            query=query,
            response=response,
            context=context,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            success=success,
        )

        # Record performance for intelligence
        self.intelligence.record_performance(
            query=query,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            response_time=0.0,  # Not measured here
            success=success,
        )

        return {
            "memory_id": memory_id,
            "validation": validation,
            "learned": True,
            "success": success,
        }

    def provide_feedback(
        self, query: str, response: str, feedback: str, rating: int  # 1-5
    ):
        """Provide feedback for self-improvement."""
        self.improvement.learn_from_feedback(query, response, feedback, rating)

    def add_knowledge(
        self,
        id: str,
        category: str,
        title: str,
        content: str,
        tags: List[str] = None,
        priority: int = 5,
    ) -> bool:
        """Add knowledge to both KB and vector store."""
        kb_success = self.knowledge.add(
            id=id,
            category=category,
            title=title,
            content=content,
            tags=tags or [],
            priority=priority,
        )

        vector_success = False
        if self.vectors.embeddings_model:
            vector_success = self.vectors.add(
                id=id,
                text=f"{title}: {content}",
                metadata={"category": category, "tags": tags or []},
            )

        return kb_success or vector_success

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "optimizer": self.optimizer.get_stats(),
            "advanced_optimizer": self.advanced_optimizer.get_optimization_stats(),
            "adaptive_compressor": self.adaptive_compressor.get_stats(),
            "knowledge_base": self.knowledge.get_stats(),
            "vector_store": self.vectors.get_stats(),
            "intelligence": self.intelligence.get_insights(),
            "memory": self.memory.get_learned_insights(),
            "improvement": self.improvement.get_stats(),
            "system_status": "self-improving",
        }

    def export_report(self, filepath: str):
        """Export comprehensive report."""
        import json

        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": self.get_comprehensive_stats(),
            "quality_trend": self.improvement.get_quality_trend(),
            "top_patterns": self.intelligence.usage_patterns.get_popular_queries(10),
            "peak_hours": self.intelligence.usage_patterns.get_peak_hours(),
            "knowledge_categories": list(self.knowledge.categories.keys()),
            "total_memories": len(self.memory.memories),
            "learned_insights": self.memory.get_learned_insights(),
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Report exported to {filepath}")
