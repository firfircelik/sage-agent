/**
 * Type definitions for Sage Agent API
 */

export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface QueryRequest {
  query: string;
  provider: 'openai' | 'anthropic' | 'deepseek' | 'glm' | 'cohere';
  model?: string;
  use_advanced_optimization: boolean;
}

export interface QueryResult {
  from_memory: boolean;
  tokens_saved: number;
  message: string;
  context_enhanced: string;
  ai_analysis?: string;
  similar_memories: Memory[];
  improvement_suggestions: string[];
  processing_time: number;
}

export interface Memory {
  query: string;
  response: string;
  provider: string;
  model: string;
  timestamp: string;
  similarity?: number;
}

export interface MemoryRecallRequest {
  query: string;
  limit: number;
}

export interface AddInteractionRequest {
  query: string;
  response: string;
  provider: string;
  model: string;
  tokens_used: number;
  success: boolean;
}

export interface FeedbackRequest {
  query: string;
  response: string;
  feedback: string;
  rating: number;
}

export interface KnowledgeEntry {
  id: string;
  category: string;
  title: string;
  content: string;
  tags: string[];
  priority: number;
}

export interface AddKnowledgeRequest {
  id: string;
  category: string;
  title: string;
  content: string;
  tags: string[];
  priority: number;
}

export interface SearchKnowledgeRequest {
  query?: string;
  category?: string;
  tags?: string[];
  limit: number;
}

export interface Statistics {
  total_queries: number;
  total_tokens_saved: number;
  average_savings_percentage: number;
  cache_hit_rate: number;
  memory_size: number;
  quality_trend: {
    trend: 'improving' | 'stable' | 'declining';
    current_quality: number;
    improvement: number;
  };
  usage: {
    patterns: Record<string, number>;
    providers: Record<string, number>;
  };
  improvement: {
    learning_metrics: Record<string, number>;
    quality_trend: Record<string, unknown>;
  };
}

export interface LearnedPatterns {
  total_memories: number;
  learned_patterns: string[];
  success_patterns: string[];
  common_mistakes: string[];
  success_rate: number;
  top_topics: string[];
  recommendations: string[];
}

export interface APIMetrics {
  uptime_seconds: number;
  requests_total: number;
  requests_successful: number;
  requests_failed: number;
  success_rate: string;
  average_response_time: string;
  requests_per_second: number;
}

export interface HealthCheck {
  status: string;
  uptime_seconds: number;
  rlm_initialized: boolean;
  metrics: {
    requests_total: number;
    success_rate: number;
    avg_response_time: number;
  };
}
