#!/usr/bin/env python3
"""
MCP Server for Claude Code CLI integration.

This allows Claude Code users to use the self-improving agent as an MCP tool.
"""

import sys
import json
from typing import Any, Dict

# Add current directory to path
sys.path.insert(0, '.')

from src.rlm import EnterpriseRLM


class MCPServer:
    """MCP Server for Claude Code integration."""
    
    def __init__(self):
        self.rlm = EnterpriseRLM()
        self.tools = {
            "process_query": self.process_query,
            "remember_interaction": self.remember_interaction,
            "provide_feedback": self.provide_feedback,
            "add_knowledge": self.add_knowledge,
            "get_stats": self.get_stats,
            "search_knowledge": self.search_knowledge,
            "recall_memory": self.recall_memory,
        }
    
    def process_query(self, query: str, provider: str = "openai", model: str = "gpt-4") -> Dict[str, Any]:
        """
        Process query with self-improving AI and RLM optimization.
        
        Args:
            query: The query to process
            provider: LLM provider (openai, anthropic, deepseek, etc.)
            model: Model name
        
        Returns:
            Optimized result with context and recommendations
        """
        result = self.rlm.process_query(query, provider, model)
        
        return {
            "success": True,
            "from_memory": result.get("from_memory", False),
            "tokens_saved": result.get("tokens_saved", 0),
            "context": result.get("context_enhanced", ""),
            "ai_analysis": result.get("ai_analysis"),
            "processing_time": result.get("processing_time", 0),
            "message": result.get("message", "Query processed successfully")
        }
    
    def remember_interaction(
        self,
        query: str,
        response: str,
        provider: str = "openai",
        model: str = "gpt-4",
        tokens_used: int = 0,
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Remember interaction for learning.
        
        Args:
            query: The query
            response: The response
            provider: LLM provider used
            model: Model used
            tokens_used: Tokens consumed
            success: Whether interaction was successful
        
        Returns:
            Memory confirmation with validation
        """
        memory = self.rlm.remember_interaction(
            query=query,
            response=response,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            success=success
        )
        
        return {
            "success": True,
            "memory_id": memory["memory_id"],
            "validated": memory["validation"]["is_valid"] if memory["validation"] else None,
            "confidence": memory["validation"]["confidence"] if memory["validation"] else None,
            "learned": memory["learned"]
        }
    
    def provide_feedback(
        self,
        query: str,
        response: str,
        feedback: str,
        rating: int
    ) -> Dict[str, Any]:
        """
        Provide feedback for self-improvement.
        
        Args:
            query: The query
            response: The response
            feedback: Feedback text
            rating: Rating 1-5
        
        Returns:
            Confirmation
        """
        self.rlm.provide_feedback(query, response, feedback, rating)
        
        return {
            "success": True,
            "message": "Feedback recorded for self-improvement"
        }
    
    def add_knowledge(
        self,
        id: str,
        category: str,
        title: str,
        content: str,
        tags: list = None,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Add knowledge to knowledge base.
        
        Args:
            id: Unique identifier
            category: Category (coding, security, etc.)
            title: Title
            content: Content
            tags: Tags list
            priority: Priority 0-10
        
        Returns:
            Confirmation
        """
        success = self.rlm.add_knowledge(
            id=id,
            category=category,
            title=title,
            content=content,
            tags=tags or [],
            priority=priority
        )
        
        return {
            "success": success,
            "message": f"Knowledge '{title}' added successfully" if success else "Failed to add knowledge"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.
        
        Returns:
            System statistics
        """
        stats = self.rlm.get_comprehensive_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    def search_knowledge(
        self,
        query: str = None,
        category: str = None,
        tags: list = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Max results
        
        Returns:
            Search results
        """
        results = self.rlm.knowledge.search(
            query=query,
            category=category,
            tags=tags,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(results),
            "results": [
                {
                    "id": r.id,
                    "category": r.category,
                    "title": r.title,
                    "content": r.content,
                    "tags": r.tags,
                    "priority": r.priority
                }
                for r in results
            ]
        }
    
    def recall_memory(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Recall similar past interactions.
        
        Args:
            query: Query to find similar interactions
            limit: Max results
        
        Returns:
            Similar memories
        """
        memories = self.rlm.memory.recall(query, limit)
        
        return {
            "success": True,
            "count": len(memories),
            "memories": [
                {
                    "query": m.query,
                    "response": m.response[:200] + "..." if len(m.response) > 200 else m.response,
                    "provider": m.provider,
                    "model": m.model,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in memories
            ]
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method not in self.tools:
            return {
                "success": False,
                "error": f"Unknown method: {method}"
            }
        
        try:
            result = self.tools[method](**params)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self):
        """Run MCP server (stdio mode)."""
        print("Multi-Agent RLM MCP Server started", file=sys.stderr)
        print("Available tools:", list(self.tools.keys()), file=sys.stderr)
        
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e)
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == "__main__":
    server = MCPServer()
    server.run()
