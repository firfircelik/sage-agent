"""
Self-improvement system - Agent learns and improves like an LLM.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os


class SelfImprovementEngine:
    """
    Agent self-improvement system.
    
    Features:
    - Learns from mistakes
    - Improves responses over time
    - Detects hallucinations
    - Validates responses
    - Adapts to user preferences
    """
    
    def __init__(self, storage_dir: str = ".rlm_cache/improvement"):
        self.storage_dir = storage_dir
        self.improvement_log: List[Dict] = []
        self.mistake_patterns: Dict[str, int] = {}
        self.success_patterns: Dict[str, int] = {}
        self.hallucination_indicators: List[str] = []
        self.quality_scores: List[float] = []
        self._load()
        self._init_hallucination_detection()
    
    def _init_hallucination_detection(self):
        """Initialize hallucination detection patterns."""
        self.hallucination_indicators = [
            "i think", "probably", "maybe", "might be",
            "i'm not sure", "could be", "possibly",
            "as far as i know", "to my knowledge",
            "i believe", "i assume"
        ]
    
    def validate_response(
        self,
        query: str,
        response: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Validate response quality and detect issues.
        
        Returns validation result with:
        - is_valid: bool
        - confidence: float (0-1)
        - issues: List[str]
        - suggestions: List[str]
        """
        issues = []
        suggestions = []
        confidence = 1.0
        
        # 1. Check for hallucination indicators
        response_lower = response.lower()
        hallucination_count = sum(
            1 for indicator in self.hallucination_indicators
            if indicator in response_lower
        )
        
        if hallucination_count > 0:
            issues.append(f"Uncertainty detected ({hallucination_count} indicators)")
            confidence -= 0.1 * hallucination_count
            suggestions.append("Provide more factual, confident responses")
        
        # 2. Check response length
        if len(response) < 50:
            issues.append("Response too short")
            confidence -= 0.2
            suggestions.append("Provide more detailed explanation")
        
        # 3. Check if response addresses query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words)
        
        if overlap < len(query_words) * 0.3:
            issues.append("Response may not address query")
            confidence -= 0.3
            suggestions.append("Ensure response directly answers the question")
        
        # 4. Check for contradictions
        if self._detect_contradiction(response):
            issues.append("Potential contradiction detected")
            confidence -= 0.4
            suggestions.append("Review response for consistency")
        
        # 5. Check context usage
        if context and context not in response:
            issues.append("Context not utilized")
            confidence -= 0.1
            suggestions.append("Incorporate provided context")
        
        confidence = max(0.0, min(1.0, confidence))
        is_valid = confidence >= 0.7
        
        return {
            "is_valid": is_valid,
            "confidence": confidence,
            "issues": issues,
            "suggestions": suggestions,
            "hallucination_risk": hallucination_count > 2
        }
    
    def _detect_contradiction(self, text: str) -> bool:
        """Detect potential contradictions in text."""
        contradiction_pairs = [
            ("yes", "no"),
            ("true", "false"),
            ("always", "never"),
            ("all", "none"),
            ("correct", "incorrect")
        ]
        
        text_lower = text.lower()
        
        for word1, word2 in contradiction_pairs:
            if word1 in text_lower and word2 in text_lower:
                # Check if they're close together (potential contradiction)
                pos1 = text_lower.find(word1)
                pos2 = text_lower.find(word2)
                if abs(pos1 - pos2) < 100:  # Within 100 chars
                    return True
        
        return False
    
    def learn_from_feedback(
        self,
        query: str,
        response: str,
        feedback: str,
        rating: int  # 1-5
    ):
        """Learn from user feedback."""
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "feedback": feedback,
            "rating": rating
        }
        
        self.improvement_log.append(improvement)
        
        # Track patterns
        if rating >= 4:
            # Success pattern
            keywords = self._extract_keywords(query)
            for keyword in keywords:
                self.success_patterns[keyword] = self.success_patterns.get(keyword, 0) + 1
        elif rating <= 2:
            # Mistake pattern
            keywords = self._extract_keywords(query)
            for keyword in keywords:
                self.mistake_patterns[keyword] = self.mistake_patterns.get(keyword, 0) + 1
        
        # Track quality
        self.quality_scores.append(rating / 5.0)
        
        self._save()
    
    def get_improvement_suggestions(self, query: str) -> List[str]:
        """Get suggestions based on past mistakes."""
        suggestions = []
        keywords = self._extract_keywords(query)
        
        # Check for known mistake patterns
        for keyword in keywords:
            if keyword in self.mistake_patterns:
                count = self.mistake_patterns[keyword]
                if count > 2:
                    suggestions.append(
                        f"Be careful with '{keyword}' - {count} past issues"
                    )
        
        # Check for success patterns
        for keyword in keywords:
            if keyword in self.success_patterns:
                count = self.success_patterns[keyword]
                if count > 3:
                    suggestions.append(
                        f"Good track record with '{keyword}' - continue approach"
                    )
        
        return suggestions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        words = text.lower().split()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords[:10]
    
    def get_quality_trend(self) -> Dict[str, Any]:
        """Get quality improvement trend."""
        if not self.quality_scores:
            return {
                "trend": "no_data",
                "current_quality": 0.0,
                "improvement": 0.0
            }
        
        # Calculate trend
        recent_scores = self.quality_scores[-10:]
        older_scores = self.quality_scores[-20:-10] if len(self.quality_scores) > 10 else []
        
        current_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores) if older_scores else current_avg
        
        improvement = current_avg - older_avg
        
        if improvement > 0.1:
            trend = "improving"
        elif improvement < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_quality": f"{current_avg * 100:.1f}%",
            "improvement": f"{improvement * 100:+.1f}%",
            "total_feedbacks": len(self.quality_scores)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get improvement statistics."""
        quality_trend = self.get_quality_trend()
        
        return {
            "total_improvements": len(self.improvement_log),
            "mistake_patterns": len(self.mistake_patterns),
            "success_patterns": len(self.success_patterns),
            "quality_trend": quality_trend,
            "top_mistakes": sorted(
                self.mistake_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "top_successes": sorted(
                self.success_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def _save(self):
        """Save improvement data."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "improvement_log": self.improvement_log,
            "mistake_patterns": self.mistake_patterns,
            "success_patterns": self.success_patterns,
            "quality_scores": self.quality_scores
        }
        
        with open(os.path.join(self.storage_dir, "improvement.json"), "w") as f:
            json.dump(data, f, indent=2)
    
    def _load(self):
        """Load improvement data."""
        filepath = os.path.join(self.storage_dir, "improvement.json")
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            self.improvement_log = data.get("improvement_log", [])
            self.mistake_patterns = data.get("mistake_patterns", {})
            self.success_patterns = data.get("success_patterns", {})
            self.quality_scores = data.get("quality_scores", [])
        except Exception as e:
            print(f"⚠️  Failed to load improvement data: {e}")
