"""
Vector store for semantic search and similarity matching.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import os
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VectorEntry:
    """Vector entry with metadata."""
    id: str
    text: str
    vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class VectorStore:
    """High-performance vector store for semantic search."""
    
    def __init__(self, dimension: int = 384, cache_dir: str = ".rlm_cache/vectors"):
        self.dimension = dimension
        self.cache_dir = cache_dir
        self.entries: Dict[str, VectorEntry] = {}
        self.embeddings_model = None
        self._init_embeddings()
        self._load_store()
    
    def _init_embeddings(self):
        """Initialize embeddings model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embeddings model loaded")
        except ImportError:
            print("⚠️  sentence-transformers not installed. Install: pip install sentence-transformers")
            self.embeddings_model = None
    
    def add(self, id: str, text: str, metadata: Dict = None) -> bool:
        """Add text to vector store."""
        if not self.embeddings_model:
            return False
        
        try:
            vector = self.embeddings_model.encode(text)
            entry = VectorEntry(
                id=id,
                text=text,
                vector=vector,
                metadata=metadata or {}
            )
            self.entries[id] = entry
            self._save_store()
            return True
        except Exception as e:
            print(f"⚠️  Failed to add to vector store: {e}")
            return False
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.3,
        filter_metadata: Dict = None
    ) -> List[Tuple[VectorEntry, float]]:
        """Search for similar entries."""
        if not self.embeddings_model or not self.entries:
            return []
        
        try:
            query_vector = self.embeddings_model.encode(query)
            results = []
            
            for entry in self.entries.values():
                # Apply metadata filter
                if filter_metadata:
                    if not all(entry.metadata.get(k) == v for k, v in filter_metadata.items()):
                        continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(query_vector, entry.vector)
                
                if similarity >= threshold:
                    # Update access stats
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    results.append((entry, similarity))
            
            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            print(f"⚠️  Search failed: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _save_store(self):
        """Save vector store to disk."""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Save metadata
        metadata = {
            id: {
                "text": entry.text,
                "metadata": entry.metadata,
                "created_at": entry.created_at.isoformat(),
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None
            }
            for id, entry in self.entries.items()
        }
        
        with open(os.path.join(self.cache_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save vectors
        vectors = {id: entry.vector.tolist() for id, entry in self.entries.items()}
        with open(os.path.join(self.cache_dir, "vectors.json"), "w") as f:
            json.dump(vectors, f)
    
    def _load_store(self):
        """Load vector store from disk."""
        metadata_file = os.path.join(self.cache_dir, "metadata.json")
        vectors_file = os.path.join(self.cache_dir, "vectors.json")
        
        if not os.path.exists(metadata_file) or not os.path.exists(vectors_file):
            return
        
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            with open(vectors_file, "r") as f:
                vectors = json.load(f)
            
            for id, meta in metadata.items():
                if id in vectors:
                    entry = VectorEntry(
                        id=id,
                        text=meta["text"],
                        vector=np.array(vectors[id]),
                        metadata=meta["metadata"],
                        created_at=datetime.fromisoformat(meta["created_at"]),
                        access_count=meta["access_count"],
                        last_accessed=datetime.fromisoformat(meta["last_accessed"]) if meta["last_accessed"] else None
                    )
                    self.entries[id] = entry
        
        except Exception as e:
            print(f"⚠️  Failed to load vector store: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "embeddings_enabled": self.embeddings_model is not None
            }
        
        total_access = sum(e.access_count for e in self.entries.values())
        avg_access = total_access / len(self.entries) if self.entries else 0
        
        return {
            "total_entries": len(self.entries),
            "total_accesses": total_access,
            "avg_access_per_entry": f"{avg_access:.1f}",
            "embeddings_enabled": self.embeddings_model is not None,
            "dimension": self.dimension
        }
    
    def clear(self):
        """Clear all entries."""
        self.entries.clear()
        self._save_store()
