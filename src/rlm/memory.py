"""
Long-term memory system - Agent remembers everything.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from dataclasses import dataclass, field
import hashlib


@dataclass
class MemoryEntry:
    """Single memory entry."""
    id: str
    timestamp: datetime
    query: str
    response: str
    context: str
    provider: str
    model: str
    tokens_used: int
    success: bool
    feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LongTermMemory:
    """
    Agent's long-term memory - remembers everything forever.
    Never forgets, always learns.
    """
    
    def __init__(self, storage_dir: str = ".rlm_cache/memory"):
        self.storage_dir = storage_dir
        self.memories: Dict[str, MemoryEntry] = {}
        self.conversation_history: List[str] = []
        self.learned_patterns: Dict[str, Any] = {}
        self._load()
    
    def remember(
        self,
        query: str,
        response: str,
        context: str = "",
        provider: str = "",
        model: str = "",
        tokens_used: int = 0,
        success: bool = True,
        metadata: Dict = None
    ) -> str:
        """Remember interaction permanently."""
        # Create unique ID
        memory_id = self._generate_id(query, response)
        
        # Create memory entry
        memory = MemoryEntry(
            id=memory_id,
            timestamp=datetime.now(),
            query=query,
            response=response,
            context=context,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            success=success,
            metadata=metadata or {}
        )
        
        self.memories[memory_id] = memory
        self.conversation_history.append(memory_id)
        
        # Learn from this interaction
        self._learn_from_memory(memory)
        
        # Save immediately
        self._save()
        
        return memory_id
    
    def recall(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Recall similar past interactions."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_memories = []
        
        for memory in self.memories.values():
            # Calculate similarity
            memory_words = set(memory.query.lower().split())
            common_words = query_words & memory_words
            
            if common_words:
                score = len(common_words) / max(len(query_words), len(memory_words))
                scored_memories.append((score, memory))
        
        # Sort by score
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return [m for _, m in scored_memories[:limit]]
    
    def recall_exact(self, query: str) -> Optional[MemoryEntry]:
        """Check if exact query was asked before."""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        for memory in self.memories.values():
            memory_hash = hashlib.md5(memory.query.encode()).hexdigest()
            if memory_hash == query_hash:
                return memory
        
        return None
    
    def get_conversation_context(self, last_n: int = 10) -> str:
        """Get recent conversation context."""
        recent_ids = self.conversation_history[-last_n:]
        context_parts = []
        
        for memory_id in recent_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                context_parts.append(f"Q: {memory.query}\nA: {memory.response}")
        
        return "\n\n".join(context_parts)
    
    def _learn_from_memory(self, memory: MemoryEntry):
        """Learn patterns from memory."""
        # Extract key concepts
        words = memory.query.lower().split()
        
        for word in words:
            if len(word) > 3:  # Skip short words
                if word not in self.learned_patterns:
                    self.learned_patterns[word] = {
                        "count": 0,
                        "successful_responses": 0,
                        "providers": {},
                        "avg_tokens": 0
                    }
                
                pattern = self.learned_patterns[word]
                pattern["count"] += 1
                
                if memory.success:
                    pattern["successful_responses"] += 1
                
                if memory.provider:
                    pattern["providers"][memory.provider] = pattern["providers"].get(memory.provider, 0) + 1
                
                # Update average tokens
                pattern["avg_tokens"] = (
                    (pattern["avg_tokens"] * (pattern["count"] - 1) + memory.tokens_used) 
                    / pattern["count"]
                )
    
    def get_learned_insights(self) -> Dict[str, Any]:
        """Get insights from learned patterns."""
        if not self.learned_patterns:
            return {}
        
        # Most common topics
        top_topics = sorted(
            self.learned_patterns.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:10]
        
        # Best providers per topic
        provider_recommendations = {}
        for topic, data in top_topics:
            if data["providers"]:
                best_provider = max(data["providers"].items(), key=lambda x: x[1])[0]
                provider_recommendations[topic] = best_provider
        
        return {
            "total_memories": len(self.memories),
            "total_conversations": len(self.conversation_history),
            "learned_patterns": len(self.learned_patterns),
            "top_topics": [(t, d["count"]) for t, d in top_topics],
            "provider_recommendations": provider_recommendations,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.memories:
            return 0.0
        
        successful = sum(1 for m in self.memories.values() if m.success)
        return (successful / len(self.memories)) * 100
    
    def _generate_id(self, query: str, response: str) -> str:
        """Generate unique ID for memory."""
        content = f"{query}:{response}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save(self):
        """Save memories to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Save memories
        memories_data = {
            id: {
                "timestamp": m.timestamp.isoformat(),
                "query": m.query,
                "response": m.response,
                "context": m.context,
                "provider": m.provider,
                "model": m.model,
                "tokens_used": m.tokens_used,
                "success": m.success,
                "feedback": m.feedback,
                "metadata": m.metadata
            }
            for id, m in self.memories.items()
        }
        
        with open(os.path.join(self.storage_dir, "memories.json"), "w") as f:
            json.dump(memories_data, f, indent=2)
        
        # Save conversation history
        with open(os.path.join(self.storage_dir, "history.json"), "w") as f:
            json.dump(self.conversation_history, f, indent=2)
        
        # Save learned patterns
        with open(os.path.join(self.storage_dir, "patterns.json"), "w") as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def _load(self):
        """Load memories from disk."""
        memories_file = os.path.join(self.storage_dir, "memories.json")
        history_file = os.path.join(self.storage_dir, "history.json")
        patterns_file = os.path.join(self.storage_dir, "patterns.json")
        
        # Load memories
        if os.path.exists(memories_file):
            try:
                with open(memories_file, "r") as f:
                    data = json.load(f)
                
                for id, m in data.items():
                    memory = MemoryEntry(
                        id=id,
                        timestamp=datetime.fromisoformat(m["timestamp"]),
                        query=m["query"],
                        response=m["response"],
                        context=m["context"],
                        provider=m["provider"],
                        model=m["model"],
                        tokens_used=m["tokens_used"],
                        success=m["success"],
                        feedback=m.get("feedback"),
                        metadata=m.get("metadata", {})
                    )
                    self.memories[id] = memory
            except Exception as e:
                print(f"⚠️  Failed to load memories: {e}")
        
        # Load history
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    self.conversation_history = json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load history: {e}")
        
        # Load patterns
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, "r") as f:
                    self.learned_patterns = json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load patterns: {e}")
    
    def clear_old_memories(self, days: int = 365):
        """Clear memories older than specified days (default: keep 1 year)."""
        cutoff = datetime.now() - timedelta(days=days)
        
        old_ids = [
            id for id, m in self.memories.items()
            if m.timestamp < cutoff
        ]
        
        for id in old_ids:
            del self.memories[id]
            if id in self.conversation_history:
                self.conversation_history.remove(id)
        
        self._save()
        return len(old_ids)


from datetime import timedelta
