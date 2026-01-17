"""
Enterprise-grade knowledge base for context management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from dataclasses import dataclass, field


@dataclass
class KnowledgeEntry:
    """Knowledge base entry."""
    id: str
    category: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    priority: int = 0  # 0-10, higher = more important
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeBase:
    """Enterprise knowledge base for storing and retrieving information."""
    
    def __init__(self, storage_dir: str = ".rlm_cache/knowledge"):
        self.storage_dir = storage_dir
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> entry_ids
        self.tags: Dict[str, List[str]] = {}  # tag -> entry_ids
        self._load()
    
    def add(
        self,
        id: str,
        category: str,
        title: str,
        content: str,
        tags: List[str] = None,
        priority: int = 5,
        metadata: Dict = None
    ) -> bool:
        """Add entry to knowledge base."""
        try:
            entry = KnowledgeEntry(
                id=id,
                category=category,
                title=title,
                content=content,
                tags=tags or [],
                priority=priority,
                metadata=metadata or {}
            )
            
            self.entries[id] = entry
            
            # Update category index
            if category not in self.categories:
                self.categories[category] = []
            if id not in self.categories[category]:
                self.categories[category].append(id)
            
            # Update tag index
            for tag in entry.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                if id not in self.tags[tag]:
                    self.tags[tag].append(id)
            
            self._save()
            return True
        
        except Exception as e:
            print(f"⚠️  Failed to add knowledge entry: {e}")
            return False
    
    def get(self, id: str) -> Optional[KnowledgeEntry]:
        """Get entry by ID."""
        entry = self.entries.get(id)
        if entry:
            entry.access_count += 1
            entry.updated_at = datetime.now()
            self._save()
        return entry
    
    def search(
        self,
        query: str = None,
        category: str = None,
        tags: List[str] = None,
        min_priority: int = 0,
        limit: int = 10
    ) -> List[KnowledgeEntry]:
        """Search knowledge base."""
        results = []
        
        for entry in self.entries.values():
            # Filter by category
            if category and entry.category != category:
                continue
            
            # Filter by tags
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # Filter by priority
            if entry.priority < min_priority:
                continue
            
            # Filter by query (simple keyword match)
            if query:
                query_lower = query.lower()
                if not (query_lower in entry.title.lower() or 
                       query_lower in entry.content.lower() or
                       any(query_lower in tag.lower() for tag in entry.tags)):
                    continue
            
            results.append(entry)
        
        # Sort by priority and access count
        results.sort(key=lambda e: (e.priority, e.access_count), reverse=True)
        return results[:limit]
    
    def get_by_category(self, category: str) -> List[KnowledgeEntry]:
        """Get all entries in category."""
        entry_ids = self.categories.get(category, [])
        return [self.entries[id] for id in entry_ids if id in self.entries]
    
    def get_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """Get all entries with tag."""
        entry_ids = self.tags.get(tag, [])
        return [self.entries[id] for id in entry_ids if id in self.entries]
    
    def update(self, id: str, **kwargs):
        """Update entry."""
        if id not in self.entries:
            return False
        
        entry = self.entries[id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.updated_at = datetime.now()
        self._save()
        return True
    
    def delete(self, id: str) -> bool:
        """Delete entry."""
        if id not in self.entries:
            return False
        
        entry = self.entries[id]
        
        # Remove from category index
        if entry.category in self.categories:
            self.categories[entry.category].remove(id)
        
        # Remove from tag index
        for tag in entry.tags:
            if tag in self.tags:
                self.tags[tag].remove(id)
        
        del self.entries[id]
        self._save()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        total_access = sum(e.access_count for e in self.entries.values())
        
        return {
            "total_entries": len(self.entries),
            "categories": len(self.categories),
            "tags": len(self.tags),
            "total_accesses": total_access,
            "avg_priority": sum(e.priority for e in self.entries.values()) / len(self.entries) if self.entries else 0
        }
    
    def _save(self):
        """Save to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "entries": {
                id: {
                    "category": e.category,
                    "title": e.title,
                    "content": e.content,
                    "tags": e.tags,
                    "priority": e.priority,
                    "created_at": e.created_at.isoformat(),
                    "updated_at": e.updated_at.isoformat(),
                    "access_count": e.access_count,
                    "metadata": e.metadata
                }
                for id, e in self.entries.items()
            },
            "categories": self.categories,
            "tags": self.tags
        }
        
        with open(os.path.join(self.storage_dir, "knowledge.json"), "w") as f:
            json.dump(data, f, indent=2)
    
    def _load(self):
        """Load from disk."""
        filepath = os.path.join(self.storage_dir, "knowledge.json")
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            for id, entry_data in data.get("entries", {}).items():
                entry = KnowledgeEntry(
                    id=id,
                    category=entry_data["category"],
                    title=entry_data["title"],
                    content=entry_data["content"],
                    tags=entry_data["tags"],
                    priority=entry_data["priority"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    updated_at=datetime.fromisoformat(entry_data["updated_at"]),
                    access_count=entry_data["access_count"],
                    metadata=entry_data["metadata"]
                )
                self.entries[id] = entry
            
            self.categories = data.get("categories", {})
            self.tags = data.get("tags", {})
        
        except Exception as e:
            print(f"⚠️  Failed to load knowledge base: {e}")
