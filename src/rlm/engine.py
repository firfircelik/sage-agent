"""
RLM (Retrieval-based Language Model) engine for token optimization.
"""

from typing import List, Dict, Any
from datetime import datetime
import re
from .cache import RLMCache


class TokenCounter:
    """Advanced token counter with multiple strategies."""

    @staticmethod
    def count_tokens(text: str, method: str = "accurate") -> int:
        """
        Count tokens with different methods.

        Methods:
        - accurate: Better estimation (1 token ≈ 0.75 words)
        - fast: Quick estimation (1 token ≈ 4 chars)
        - tiktoken: Use tiktoken library if available
        """
        if method == "tiktoken":
            try:
                import tiktoken

                enc = tiktoken.get_encoding("cl100k_base")
                return len(enc.encode(text))
            except ImportError:
                method = "accurate"

        if method == "accurate":
            # Better estimation: count words and adjust
            words = len(text.split())
            return int(words * 1.3)  # ~1.3 tokens per word
        else:  # fast
            return len(text) // 4

    @staticmethod
    def count_prompt_tokens(prompt: str, system_prompt: str = "") -> int:
        """Count prompt tokens."""
        total = TokenCounter.count_tokens(prompt)
        if system_prompt:
            total += TokenCounter.count_tokens(system_prompt)
        return total

    @staticmethod
    def count_response_tokens(response: str) -> int:
        """Count response tokens."""
        return TokenCounter.count_tokens(response)


class ContextRetriever:
    """Advanced context retrieval with semantic search."""

    def __init__(self, max_context_length: int = 2000):
        self.max_context_length = max_context_length
        self.memory_store: List[Dict[str, Any]] = []
        self.use_embeddings = False
        self._init_embeddings()

    def _init_embeddings(self):
        """Initialize embeddings if available."""
        try:
            from sentence_transformers import SentenceTransformer

            self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.use_embeddings = True
        except ImportError:
            self.use_embeddings = False

    def add_to_memory(self, key: str, content: str, metadata: Dict = None):
        """Add content to memory with optional embedding."""
        item = {
            "key": key,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None,
        }

        if self.use_embeddings:
            item["embedding"] = self.embeddings_model.encode(content)

        self.memory_store.append(item)

    def retrieve_relevant_context(
        self, query: str, top_k: int = 3, strategy: str = "hybrid"
    ) -> str:
        """
        Retrieve relevant context with multiple strategies.

        Strategies:
        - keyword: Simple keyword matching
        - semantic: Embedding-based similarity (if available)
        - hybrid: Combine both (default)
        - frequency: Most frequently accessed
        - recent: Most recently accessed
        """
        if not self.memory_store:
            return ""

        if strategy == "semantic" and self.use_embeddings:
            return self._retrieve_semantic(query, top_k)
        elif strategy == "frequency":
            return self._retrieve_by_frequency(top_k)
        elif strategy == "recent":
            return self._retrieve_recent(top_k)
        elif strategy == "hybrid" and self.use_embeddings:
            return self._retrieve_hybrid(query, top_k)
        else:
            return self._retrieve_keyword(query, top_k)

    def _retrieve_keyword(self, query: str, top_k: int) -> str:
        """Keyword-based retrieval."""
        query_words = set(query.lower().split())
        scored_items = []

        for item in self.memory_store:
            content_words = set(item["content"].lower().split())
            score = len(query_words & content_words)
            if score > 0:
                scored_items.append((score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return self._format_context(scored_items[:top_k])

    def _retrieve_semantic(self, query: str, top_k: int) -> str:
        """Semantic similarity-based retrieval."""
        query_embedding = self.embeddings_model.encode(query)
        scored_items = []

        for item in self.memory_store:
            if "embedding" in item:
                similarity = self._cosine_similarity(query_embedding, item["embedding"])
                scored_items.append((similarity, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return self._format_context(scored_items[:top_k])

    def _retrieve_hybrid(self, query: str, top_k: int) -> str:
        """Hybrid retrieval combining keyword and semantic."""
        query_words = set(query.lower().split())
        query_embedding = self.embeddings_model.encode(query)
        scored_items = []

        for item in self.memory_store:
            # Keyword score
            content_words = set(item["content"].lower().split())
            keyword_score = len(query_words & content_words) / max(len(query_words), 1)

            # Semantic score
            semantic_score = 0
            if "embedding" in item:
                semantic_score = self._cosine_similarity(
                    query_embedding, item["embedding"]
                )

            # Combined score (weighted)
            combined_score = 0.4 * keyword_score + 0.6 * semantic_score
            scored_items.append((combined_score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return self._format_context(scored_items[:top_k])

    def _retrieve_by_frequency(self, top_k: int) -> str:
        """Retrieve most frequently accessed items."""
        sorted_items = sorted(
            self.memory_store, key=lambda x: x["access_count"], reverse=True
        )
        return self._format_context([(0, item) for item in sorted_items[:top_k]])

    def _retrieve_recent(self, top_k: int) -> str:
        """Retrieve most recently accessed items."""
        sorted_items = sorted(
            self.memory_store,
            key=lambda x: x.get("last_accessed") or x["timestamp"],
            reverse=True,
        )
        return self._format_context([(0, item) for item in sorted_items[:top_k]])

    def _format_context(self, scored_items: List) -> str:
        """Format context from scored items."""
        context = ""
        for score, item in scored_items:
            # Update access stats
            item["access_count"] += 1
            item["last_accessed"] = datetime.now().isoformat()

            context += f"\n[Context] {item['key']}:\n{item['content']}\n"
            if len(context) > self.max_context_length:
                break

        return context[: self.max_context_length]

    @staticmethod
    def _cosine_similarity(a, b):
        """Calculate cosine similarity."""
        import numpy as np

        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class PromptCompressor:
    """Compress prompts to reduce tokens."""

    @staticmethod
    def compress(text: str, strategy: str = "smart") -> str:
        """
        Compress text using various strategies.

        Strategies:
        - smart: Remove redundancy while keeping meaning
        - aggressive: Maximum compression
        - minimal: Light compression
        """
        if strategy == "aggressive":
            # Remove extra whitespace, articles, etc.
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\b(a|an|the)\b", "", text, flags=re.IGNORECASE)
            text = re.sub(r"[,;:]", "", text)
        elif strategy == "smart":
            # Remove extra whitespace and redundant phrases
            text = re.sub(r"\s+", " ", text)
            text = re.sub(
                r"\b(please|kindly|could you)\b", "", text, flags=re.IGNORECASE
            )
        else:  # minimal
            text = re.sub(r"\s+", " ", text)

        return text.strip()


class RLMOptimizer:
    """Advanced RLM optimizer with multiple strategies."""

    def __init__(
        self,
        cache_dir: str = ".rlm_cache",
        enable_compression: bool = True,
        enable_deduplication: bool = True,
        token_method: str = "accurate",  # nosec B107
    ):
        self.context_retriever = ContextRetriever()
        self.cache = RLMCache(cache_dir)
        self.token_counter = TokenCounter()
        self.compressor = PromptCompressor()
        self.enable_compression = enable_compression
        self.enable_deduplication = enable_deduplication
        self.token_method = token_method

        # Statistics
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "total_tokens_saved": 0,
            "compression_savings": 0,
            "context_savings": 0,
        }

    def optimize_prompt(
        self,
        query: str,
        system_prompt: str = "",
        use_cache: bool = True,
        use_context: bool = True,
        context_strategy: str = "hybrid",
        compression_strategy: str = "smart",
    ) -> Dict[str, Any]:
        """Advanced prompt optimization."""

        self.stats["total_queries"] += 1
        original_query = query

        # 1. Check cache first
        if use_cache:
            cached = self.cache.get(query)
            if cached:
                self.stats["cache_hits"] += 1
                self.stats["total_tokens_saved"] += cached.tokens_saved
                return {
                    "optimized_prompt": query,
                    "context": "",
                    "tokens_original": self.token_counter.count_tokens(
                        query, self.token_method
                    ),
                    "tokens_optimized": 0,
                    "tokens_saved": cached.tokens_saved,
                    "from_cache": True,
                    "cached_response": cached.response,
                    "compression_used": False,
                    "context_used": False,
                }

        # 2. Compress prompt if enabled
        compression_savings = 0
        if self.enable_compression:
            compressed = self.compressor.compress(query, compression_strategy)
            original_tokens = self.token_counter.count_tokens(query, self.token_method)
            compressed_tokens = self.token_counter.count_tokens(
                compressed, self.token_method
            )
            compression_savings = original_tokens - compressed_tokens
            if compression_savings > 0:
                query = compressed
                self.stats["compression_savings"] += compression_savings

        # 3. Retrieve relevant context
        context = ""
        context_savings = 0
        if use_context:
            context = self.context_retriever.retrieve_relevant_context(
                query, top_k=3, strategy=context_strategy
            )
            if context:
                # Context can replace parts of the query
                context_savings = len(context.split()) // 2
                self.stats["context_savings"] += context_savings

        # 4. Deduplicate if enabled
        if self.enable_deduplication and context:
            query, context = self._deduplicate(query, context)

        # Calculate final tokens
        original_tokens = self.token_counter.count_tokens(
            original_query, self.token_method
        )
        optimized_tokens = self.token_counter.count_tokens(
            query + context, self.token_method
        )

        # If optimization made it worse, revert
        if optimized_tokens > original_tokens:
            query = original_query
            context = ""
            optimized_tokens = original_tokens

        tokens_saved = original_tokens - optimized_tokens
        self.stats["total_tokens_saved"] += tokens_saved

        return {
            "optimized_prompt": query,
            "context": context,
            "tokens_original": original_tokens,
            "tokens_optimized": optimized_tokens,
            "tokens_saved": tokens_saved,
            "compression_savings": compression_savings,
            "context_savings": context_savings,
            "from_cache": False,
            "cached_response": None,
            "compression_used": self.enable_compression,
            "context_used": bool(context),
        }

    def _deduplicate(self, query: str, context: str) -> tuple:
        """Remove duplicate information between query and context."""
        query_words = set(query.lower().split())
        context_words = context.lower().split()

        # Remove words from context that are in query
        filtered_context = [w for w in context_words if w.lower() not in query_words]

        return query, " ".join(filtered_context)

    def add_context(
        self, key: str, content: str, metadata: Dict = None, auto_compress: bool = True
    ):
        """Add context with optional compression."""
        if auto_compress and self.enable_compression:
            content = self.compressor.compress(content, "minimal")

        self.context_retriever.add_to_memory(key, content, metadata)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        cache_stats = self.cache.get_stats()

        cache_hit_rate = 0
        if self.stats["total_queries"] > 0:
            cache_hit_rate = (
                self.stats["cache_hits"] / self.stats["total_queries"]
            ) * 100

        avg_savings = 0
        if self.stats["total_queries"] > 0:
            avg_savings = self.stats["total_tokens_saved"] / self.stats["total_queries"]

        return {
            **self.stats,
            **cache_stats,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "avg_tokens_saved_per_query": f"{avg_savings:.1f}",
            "context_items": len(self.context_retriever.memory_store),
            "embeddings_enabled": self.context_retriever.use_embeddings,
        }

    def clear_cache(self):
        """Clear cache."""
        self.cache.clear()

    def export_stats(self, filepath: str):
        """Export statistics to file."""
        import json

        with open(filepath, "w") as f:
            json.dump(self.get_stats(), f, indent=2)
