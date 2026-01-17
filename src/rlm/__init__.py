"""
RLM (Retrieval-based Language Model) - Enterprise AI Optimization System.

Self-Improving AI that:
- Remembers everything (Long-term Memory)
- Never duplicates (Checks memory first)
- No hallucinations (Validates responses)
- Learns from mistakes (Self-improvement)
- Gets better over time (Like an LLM)

Components:
- Engine: Core optimization with compression, caching, deduplication
- Cache: LRU cache with TTL and compression
- Knowledge Base: Structured knowledge storage with categories and tags
- Vector Store: Semantic search with embeddings
- Intelligence: AI-powered pattern learning and recommendations
- Memory: Long-term memory that never forgets
- Self-Improvement: Learns from mistakes and feedback
- Advanced Optimizer: Next-level optimization strategies
- Enterprise: Complete integrated system
- Agent: RLM-enabled LLM agent
"""

from .cache import RLMCache, CachedResponse
from .engine import RLMOptimizer, TokenCounter, ContextRetriever
from .agent import RLMEnabledLLMAgent
from .knowledge_base import KnowledgeBase, KnowledgeEntry
from .vector_store import VectorStore, VectorEntry
from .intelligence import IntelligenceEngine, UsagePattern
from .memory import LongTermMemory, MemoryEntry
from .self_improvement import SelfImprovementEngine
from .advanced_optimizer import AdvancedOptimizer, AdaptiveCompressor
from .enterprise import EnterpriseRLM

__all__ = [
    # Core
    "RLMCache",
    "CachedResponse",
    "RLMOptimizer",
    "TokenCounter",
    "ContextRetriever",
    "RLMEnabledLLMAgent",
    # Enterprise
    "KnowledgeBase",
    "KnowledgeEntry",
    "VectorStore",
    "VectorEntry",
    "IntelligenceEngine",
    "UsagePattern",
    # Self-Improving AI
    "LongTermMemory",
    "MemoryEntry",
    "SelfImprovementEngine",
    # Advanced
    "AdvancedOptimizer",
    "AdaptiveCompressor",
    "EnterpriseRLM",
]
