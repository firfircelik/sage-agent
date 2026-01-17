"""
RLM cache for storing and retrieving cached responses.
"""

import json
import hashlib
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CachedResponse:
    """Cached LLM response."""
    query_hash: str
    query: str
    response: str
    tokens_saved: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RLMCache:
    """Advanced cache with TTL, size limits, and LRU eviction."""
    
    def __init__(
        self,
        cache_dir: str = ".rlm_cache",
        max_size: int = 1000,
        ttl_hours: int = 24,
        enable_compression: bool = True
    ):
        self.cache_dir = cache_dir
        self.cache: Dict[str, CachedResponse] = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.enable_compression = enable_compression
        self.access_order = []  # For LRU
        self._load_cache()
    
    def _get_query_hash(self, query: str) -> str:
        """Generate hash for query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _load_cache(self):
        """Load cache from disk."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        cache_file = os.path.join(self.cache_dir, "cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.cache[key] = CachedResponse(**value)
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk."""
        cache_file = os.path.join(self.cache_dir, "cache.json")
        try:
            data = {}
            for key, response in self.cache.items():
                data[key] = {
                    "query_hash": response.query_hash,
                    "query": response.query,
                    "response": response.response,
                    "tokens_saved": response.tokens_saved,
                    "timestamp": response.timestamp.isoformat(),
                    "metadata": response.metadata
                }
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def get(self, query: str) -> Optional[CachedResponse]:
        """Get cached response with TTL check."""
        query_hash = self._get_query_hash(query)
        cached = self.cache.get(query_hash)
        
        if cached:
            # Check TTL
            if self._is_expired(cached):
                del self.cache[query_hash]
                self._save_cache()
                return None
            
            # Update LRU
            if query_hash in self.access_order:
                self.access_order.remove(query_hash)
            self.access_order.append(query_hash)
            
            return cached
        
        return None
    
    def _is_expired(self, cached: CachedResponse) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_hours <= 0:
            return False
        
        age_hours = (datetime.now() - cached.timestamp).total_seconds() / 3600
        return age_hours > self.ttl_hours
    
    def set(self, query: str, response: str, tokens_saved: int = 0, metadata: Dict = None):
        """Cache response with size limit and LRU eviction."""
        query_hash = self._get_query_hash(query)
        
        # Check size limit
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Compress response if enabled
        if self.enable_compression:
            response = self._compress(response)
        
        cached = CachedResponse(
            query_hash=query_hash,
            query=query,
            response=response,
            tokens_saved=tokens_saved,
            metadata=metadata or {}
        )
        self.cache[query_hash] = cached
        
        # Update LRU
        if query_hash in self.access_order:
            self.access_order.remove(query_hash)
        self.access_order.append(query_hash)
        
        self._save_cache()
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if self.access_order:
            lru_hash = self.access_order.pop(0)
            if lru_hash in self.cache:
                del self.cache[lru_hash]
    
    def _compress(self, text: str) -> str:
        """Compress text for storage."""
        import zlib
        import base64
        compressed = zlib.compress(text.encode())
        return base64.b64encode(compressed).decode()
    
    def _decompress(self, text: str) -> str:
        """Decompress text from storage."""
        try:
            import zlib
            import base64
            compressed = base64.b64decode(text.encode())
            return zlib.decompress(compressed).decode()
        except:
            return text  # Return as-is if not compressed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_tokens_saved = sum(r.tokens_saved for r in self.cache.values())
        cache_file = os.path.join(self.cache_dir, "cache.json")
        cache_size = 0
        if os.path.exists(cache_file):
            cache_size = os.path.getsize(cache_file) / (1024 * 1024)
        
        # Calculate average age
        if self.cache:
            ages = [(datetime.now() - r.timestamp).total_seconds() / 3600 
                   for r in self.cache.values()]
            avg_age = sum(ages) / len(ages)
        else:
            avg_age = 0
        
        return {
            "cached_queries": len(self.cache),
            "max_size": self.max_size,
            "utilization": f"{(len(self.cache) / self.max_size) * 100:.1f}%",
            "total_tokens_saved": total_tokens_saved,
            "cache_size_mb": f"{cache_size:.2f}",
            "avg_age_hours": f"{avg_age:.1f}",
            "ttl_hours": self.ttl_hours,
            "compression_enabled": self.enable_compression
        }
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.access_order.clear()
        self._save_cache()
    
    def prune_expired(self):
        """Remove expired entries."""
        expired = [
            hash for hash, cached in self.cache.items()
            if self._is_expired(cached)
        ]
        for hash in expired:
            del self.cache[hash]
            if hash in self.access_order:
                self.access_order.remove(hash)
        
        if expired:
            self._save_cache()
        
        return len(expired)
