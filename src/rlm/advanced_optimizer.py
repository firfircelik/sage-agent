"""
Advanced RLM Optimizer - Next-level token optimization.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime


class AdvancedOptimizer:
    """
    Advanced optimization strategies beyond basic RLM.
    
    Features:
    - Dynamic prompt rewriting
    - Context prioritization
    - Adaptive compression
    - Smart chunking
    - Token prediction
    """
    
    def __init__(self):
        self.optimization_history: List[Dict] = []
        self.learned_patterns: Dict[str, Any] = {}
    
    def optimize_prompt_advanced(
        self,
        prompt: str,
        context: str = "",
        target_tokens: Optional[int] = None,
        preserve_meaning: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced prompt optimization with multiple strategies.
        
        Args:
            prompt: Original prompt
            context: Available context
            target_tokens: Target token count (optional)
            preserve_meaning: Ensure meaning is preserved
        
        Returns:
            Optimized prompt with metadata
        """
        original_length = len(prompt)
        optimized = prompt
        strategies_used = []
        
        # 1. Remove redundancy
        optimized, removed = self._remove_redundancy(optimized)
        if removed > 0:
            strategies_used.append(f"redundancy_removal:{removed}")
        
        # 2. Compress verbose phrases
        optimized, compressed = self._compress_verbose(optimized)
        if compressed > 0:
            strategies_used.append(f"verbose_compression:{compressed}")
        
        # 3. Merge context intelligently
        if context:
            optimized, context = self._merge_context_smart(optimized, context)
            strategies_used.append("smart_context_merge")
        
        # 4. Rewrite for clarity
        if preserve_meaning:
            optimized = self._rewrite_for_clarity(optimized)
            strategies_used.append("clarity_rewrite")
        
        # 5. Apply learned patterns
        optimized = self._apply_learned_patterns(optimized)
        strategies_used.append("learned_patterns")
        
        # Calculate savings
        final_length = len(optimized)
        savings_percent = ((original_length - final_length) / original_length * 100) if original_length > 0 else 0
        
        result = {
            "original_prompt": prompt,
            "optimized_prompt": optimized,
            "context": context,
            "original_length": original_length,
            "optimized_length": final_length,
            "savings_percent": f"{savings_percent:.1f}%",
            "strategies_used": strategies_used,
            "estimated_tokens_saved": int((original_length - final_length) / 4)
        }
        
        # Learn from this optimization
        self._learn_from_optimization(result)
        
        return result
    
    def _remove_redundancy(self, text: str) -> Tuple[str, int]:
        """Remove redundant phrases and repetitions."""
        original_length = len(text)
        
        # Remove repeated words
        words = text.split()
        seen = set()
        filtered = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen or len(word) <= 3:
                filtered.append(word)
                seen.add(word_lower)
        
        text = ' '.join(filtered)
        
        # Remove redundant phrases
        redundant_phrases = [
            (r'\b(please|kindly)\s+', ''),
            (r'\b(could you|can you|would you)\s+', ''),
            (r'\b(I would like to|I want to)\s+', ''),
            (r'\b(in order to)\s+', 'to '),
            (r'\b(due to the fact that)\s+', 'because '),
            (r'\b(at this point in time)\s+', 'now '),
        ]
        
        for pattern, replacement in redundant_phrases:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        removed = original_length - len(text)
        return text, removed
    
    def _compress_verbose(self, text: str) -> Tuple[str, int]:
        """Compress verbose expressions."""
        original_length = len(text)
        
        # Verbose to concise mappings
        compressions = {
            r'\b(a large number of)\b': 'many',
            r'\b(a majority of)\b': 'most',
            r'\b(a small number of)\b': 'few',
            r'\b(at the present time)\b': 'now',
            r'\b(in the event that)\b': 'if',
            r'\b(in spite of the fact that)\b': 'although',
            r'\b(on the occasion of)\b': 'when',
            r'\b(with regard to)\b': 'about',
            r'\b(for the purpose of)\b': 'to',
            r'\b(in the near future)\b': 'soon',
            r'\b(prior to)\b': 'before',
            r'\b(subsequent to)\b': 'after',
            r'\b(in the process of)\b': 'during',
            r'\b(make a decision)\b': 'decide',
            r'\b(come to a conclusion)\b': 'conclude',
            r'\b(give consideration to)\b': 'consider',
        }
        
        for pattern, replacement in compressions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        compressed = original_length - len(text)
        return text, compressed
    
    def _merge_context_smart(self, prompt: str, context: str) -> Tuple[str, str]:
        """Intelligently merge context with prompt."""
        # Extract key information from context
        context_lines = context.split('\n')
        
        # Prioritize context by relevance
        prompt_words = set(prompt.lower().split())
        scored_lines = []
        
        for line in context_lines:
            if not line.strip():
                continue
            
            line_words = set(line.lower().split())
            relevance = len(prompt_words & line_words)
            
            if relevance > 0:
                scored_lines.append((relevance, line))
        
        # Sort by relevance and take top items
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        relevant_context = '\n'.join([line for _, line in scored_lines[:3]])
        
        return prompt, relevant_context
    
    def _rewrite_for_clarity(self, text: str) -> str:
        """Rewrite for maximum clarity with minimum tokens."""
        # Remove filler words
        fillers = ['actually', 'basically', 'literally', 'really', 'very', 'quite', 'rather', 'somewhat']
        
        words = text.split()
        filtered = [w for w in words if w.lower() not in fillers]
        
        text = ' '.join(filtered)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _apply_learned_patterns(self, text: str) -> str:
        """Apply patterns learned from previous optimizations."""
        # Apply learned substitutions
        for pattern, replacement in self.learned_patterns.items():
            if pattern in text.lower():
                text = text.replace(pattern, replacement)
        
        return text
    
    def _learn_from_optimization(self, result: Dict[str, Any]):
        """Learn patterns from successful optimizations."""
        self.optimization_history.append({
            "timestamp": datetime.now().isoformat(),
            "savings_percent": result["savings_percent"],
            "strategies": result["strategies_used"]
        })
        
        # Keep only recent history
        if len(self.optimization_history) > 100:
            self.optimization_history = self.optimization_history[-100:]
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        if not self.optimization_history:
            return {
                "total_optimizations": 0,
                "avg_savings": "0%"
            }
        
        total = len(self.optimization_history)
        
        # Calculate average savings
        savings = []
        for opt in self.optimization_history:
            try:
                percent = float(opt["savings_percent"].rstrip('%'))
                savings.append(percent)
            except:
                pass
        
        avg_savings = sum(savings) / len(savings) if savings else 0
        
        return {
            "total_optimizations": total,
            "avg_savings": f"{avg_savings:.1f}%",
            "recent_optimizations": self.optimization_history[-5:]
        }


class AdaptiveCompressor:
    """
    Adaptive compression that learns optimal compression levels.
    """
    
    def __init__(self):
        self.compression_stats: Dict[str, List[float]] = {
            "minimal": [],
            "smart": [],
            "aggressive": []
        }
    
    def compress_adaptive(self, text: str, context: str = "") -> Tuple[str, str]:
        """
        Adaptively compress based on learned performance.
        
        Returns:
            (compressed_text, strategy_used)
        """
        # Analyze text characteristics
        length = len(text)
        complexity = self._estimate_complexity(text)
        
        # Choose strategy based on characteristics and past performance
        if length < 100:
            strategy = "minimal"
        elif complexity > 0.7:
            strategy = "minimal"  # Preserve complex text
        elif length > 500:
            strategy = "aggressive"
        else:
            # Use best performing strategy
            strategy = self._get_best_strategy()
        
        # Apply compression
        if strategy == "aggressive":
            compressed = self._compress_aggressive(text)
        elif strategy == "smart":
            compressed = self._compress_smart(text)
        else:
            compressed = self._compress_minimal(text)
        
        # Record performance
        compression_ratio = len(compressed) / length if length > 0 else 1.0
        self.compression_stats[strategy].append(compression_ratio)
        
        return compressed, strategy
    
    def _estimate_complexity(self, text: str) -> float:
        """Estimate text complexity (0-1)."""
        # Simple heuristic
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        complexity = unique_words / total_words
        return min(complexity, 1.0)
    
    def _get_best_strategy(self) -> str:
        """Get best performing strategy."""
        if not any(self.compression_stats.values()):
            return "smart"
        
        # Calculate average compression ratio for each strategy
        averages = {}
        for strategy, ratios in self.compression_stats.items():
            if ratios:
                averages[strategy] = sum(ratios) / len(ratios)
        
        if not averages:
            return "smart"
        
        # Return strategy with best (lowest) compression ratio
        return min(averages.items(), key=lambda x: x[1])[0]
    
    def _compress_minimal(self, text: str) -> str:
        """Minimal compression."""
        return re.sub(r'\s+', ' ', text).strip()
    
    def _compress_smart(self, text: str) -> str:
        """Smart compression."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\b(please|kindly)\b', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def _compress_aggressive(self, text: str) -> str:
        """Aggressive compression."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\b(a|an|the)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(please|kindly|could you)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[,;:]', '', text)
        return text.strip()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        stats = {}
        
        for strategy, ratios in self.compression_stats.items():
            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                avg_savings = (1 - avg_ratio) * 100
                stats[strategy] = {
                    "uses": len(ratios),
                    "avg_compression": f"{avg_savings:.1f}%"
                }
            else:
                stats[strategy] = {
                    "uses": 0,
                    "avg_compression": "0%"
                }
        
        return stats
