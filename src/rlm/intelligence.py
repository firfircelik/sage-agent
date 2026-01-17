"""
Enterprise AI Intelligence Layer - learns from usage patterns.
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
import json
import os


class UsagePattern:
    """Track and analyze usage patterns."""

    def __init__(self, storage_dir: str = ".rlm_cache/patterns"):
        self.storage_dir = storage_dir
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.time_patterns: Dict[int, int] = defaultdict(int)  # hour -> count
        self.provider_usage: Dict[str, int] = defaultdict(int)
        self.model_usage: Dict[str, int] = defaultdict(int)
        self.category_patterns: Dict[str, int] = defaultdict(int)
        self._load()

    def record_query(
        self,
        query: str,
        provider: str,
        model: str,
        category: str = "general",
        tokens_used: int = 0,
    ):
        """Record query for pattern analysis."""
        # Extract keywords
        keywords = self._extract_keywords(query)
        for keyword in keywords:
            self.query_patterns[keyword] += 1

        # Time pattern
        hour = datetime.now().hour
        self.time_patterns[hour] += 1

        # Provider and model
        self.provider_usage[provider] += 1
        self.model_usage[model] += 1

        # Category
        self.category_patterns[category] += 1

        self._save()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter common words
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords[:10]  # Top 10

    def get_popular_queries(self, top_k: int = 10) -> List[tuple]:
        """Get most popular query patterns."""
        sorted_patterns = sorted(
            self.query_patterns.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_patterns[:top_k]

    def get_peak_hours(self) -> List[int]:
        """Get peak usage hours."""
        if not self.time_patterns:
            return []

        avg_usage = sum(self.time_patterns.values()) / len(self.time_patterns)
        peak_hours = [
            hour for hour, count in self.time_patterns.items() if count > avg_usage
        ]
        return sorted(peak_hours)

    def get_preferred_provider(self) -> str:
        """Get most used provider."""
        if not self.provider_usage:
            return "unknown"
        return max(self.provider_usage.items(), key=lambda x: x[1])[0]

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_queries": sum(self.query_patterns.values()),
            "unique_keywords": len(self.query_patterns),
            "popular_queries": self.get_popular_queries(5),
            "peak_hours": self.get_peak_hours(),
            "preferred_provider": self.get_preferred_provider(),
            "provider_distribution": dict(self.provider_usage),
            "category_distribution": dict(self.category_patterns),
        }

    def _save(self):
        """Save patterns to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)

        data = {
            "query_patterns": dict(self.query_patterns),
            "time_patterns": {str(k): v for k, v in self.time_patterns.items()},
            "provider_usage": dict(self.provider_usage),
            "model_usage": dict(self.model_usage),
            "category_patterns": dict(self.category_patterns),
        }

        with open(os.path.join(self.storage_dir, "patterns.json"), "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Load patterns from disk."""
        filepath = os.path.join(self.storage_dir, "patterns.json")
        if not os.path.exists(filepath):
            return

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            self.query_patterns = defaultdict(int, data.get("query_patterns", {}))
            self.time_patterns = defaultdict(
                int, {int(k): v for k, v in data.get("time_patterns", {}).items()}
            )
            self.provider_usage = defaultdict(int, data.get("provider_usage", {}))
            self.model_usage = defaultdict(int, data.get("model_usage", {}))
            self.category_patterns = defaultdict(int, data.get("category_patterns", {}))
        except Exception as e:
            print(f"⚠️  Failed to load patterns: {e}")


class IntelligenceEngine:
    """AI-powered intelligence for optimization decisions."""

    def __init__(self):
        self.usage_patterns = UsagePattern()
        self.performance_history: List[Dict] = []

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query and provide recommendations."""
        keywords = self.usage_patterns._extract_keywords(query)

        # Check if similar queries exist
        similar_patterns = []
        for keyword in keywords:
            if keyword in self.usage_patterns.query_patterns:
                similar_patterns.append(
                    (keyword, self.usage_patterns.query_patterns[keyword])
                )

        # Determine category
        category = self._categorize_query(query)

        # Recommend provider based on category and patterns
        recommended_provider = self._recommend_provider(category)

        # Estimate complexity
        complexity = self._estimate_complexity(query)

        return {
            "category": category,
            "complexity": complexity,
            "recommended_provider": recommended_provider,
            "similar_patterns": similar_patterns[:3],
            "keywords": keywords[:5],
            "should_cache": complexity < 5,  # Cache simple queries
            "should_compress": len(query) > 200,  # Compress long queries
        }

    def _categorize_query(self, query: str) -> str:
        """Categorize query by content."""
        query_lower = query.lower()

        if any(
            word in query_lower
            for word in ["code", "function", "class", "api", "implement"]
        ):
            return "coding"
        elif any(word in query_lower for word in ["explain", "what", "how", "why"]):
            return "explanation"
        elif any(word in query_lower for word in ["fix", "error", "bug", "issue"]):
            return "debugging"
        elif any(
            word in query_lower for word in ["design", "architecture", "structure"]
        ):
            return "design"
        elif any(word in query_lower for word in ["test", "verify", "check"]):
            return "testing"
        else:
            return "general"

    def _estimate_complexity(self, query: str) -> int:
        """Estimate query complexity (1-10)."""
        # Simple heuristic
        length_score = min(len(query) // 50, 5)
        question_marks = query.count("?")
        complexity_words = sum(
            1
            for word in ["complex", "advanced", "detailed", "comprehensive"]
            if word in query.lower()
        )

        complexity = length_score + question_marks + complexity_words
        return min(max(complexity, 1), 10)

    def _recommend_provider(self, category: str) -> str:
        """Recommend best provider for category."""
        # Check usage patterns first
        preferred = self.usage_patterns.get_preferred_provider()
        if preferred != "unknown":
            return preferred

        # Default recommendations by category
        recommendations = {
            "coding": "deepseek",
            "explanation": "anthropic",
            "debugging": "openai",
            "design": "anthropic",
            "testing": "openai",
            "general": "openai",
        }

        return recommendations.get(category, "openai")

    def record_performance(
        self,
        query: str,
        provider: str,
        model: str,
        tokens_used: int,
        response_time: float,
        success: bool,
    ):
        """Record performance for learning."""
        category = self._categorize_query(query)

        self.usage_patterns.record_query(query, provider, model, category, tokens_used)

        self.performance_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "provider": provider,
                "model": model,
                "tokens_used": tokens_used,
                "response_time": response_time,
                "success": success,
            }
        )

        # Keep only last 1000 records
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]

    def get_insights(self) -> Dict[str, Any]:
        """Get AI insights and recommendations."""
        patterns_stats = self.usage_patterns.get_stats()

        # Calculate average performance
        if self.performance_history:
            avg_tokens = sum(p["tokens_used"] for p in self.performance_history) / len(
                self.performance_history
            )
            avg_time = sum(p["response_time"] for p in self.performance_history) / len(
                self.performance_history
            )
            success_rate = sum(
                1 for p in self.performance_history if p["success"]
            ) / len(self.performance_history)
        else:
            avg_tokens = 0
            avg_time = 0
            success_rate = 0

        return {
            **patterns_stats,
            "avg_tokens_per_query": f"{avg_tokens:.0f}",
            "avg_response_time": f"{avg_time:.2f}s",
            "success_rate": f"{success_rate * 100:.1f}%",
            "total_performance_records": len(self.performance_history),
        }
