/**
 * HTTP Client for Sage Agent API
 */

import type {
  APIResponse,
  QueryRequest,
  QueryResult,
  MemoryRecallRequest,
  AddInteractionRequest,
  FeedbackRequest,
  AddKnowledgeRequest,
  SearchKnowledgeRequest,
  Statistics,
  LearnedPatterns,
  APIMetrics,
  HealthCheck,
} from '../types.js';
import type { ClientConfig, RequestOptions } from './types.js';
import { LRUCache } from './cache.js';

export class SageAgentClient {
  private baseURL: string;
  private timeout: number;
  private retries: number;
  private cache: LRUCache<APIResponse>;
  private enableCache: boolean;

  constructor(config: Partial<ClientConfig> = {}) {
    this.baseURL = config.baseURL || 'http://localhost:8000';
    this.timeout = config.timeout || 30000;
    this.retries = config.retries || 3;
    this.enableCache = config.enableCache !== false;

    this.cache = new LRUCache({
      maxSize: 1000,
      defaultTTL: 300000,
      cleanupInterval: 60000,
    });
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requestOptions: RequestOptions = {},
  ): Promise<T> {
    const { signal, timeout = this.timeout, useCache = this.enableCache } = requestOptions;

    const cacheKey = `${endpoint}:${JSON.stringify(options)}`;

    if (useCache && options.method !== 'POST' && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (cached) {
        return cached as T;
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    if (signal) {
      signal.addEventListener('abort', () => controller.abort());
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const error = await response.text();
          throw new Error(`API Error (${response.status}): ${error}`);
        }

        const data = (await response.json()) as T;

        if (useCache && options.method !== 'POST' && (data as any).success) {
          this.cache.set(cacheKey, data, 300000);
        }

        return data;
      } catch (error) {
        lastError = error as Error;

        if (attempt < this.retries) {
          await this.delay(Math.pow(2, attempt) * 1000);
        }
      }
    }

    throw lastError || new Error('Request failed after retries');
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>('/health');
  }

  async processQuery(request: QueryRequest): Promise<APIResponse<QueryResult>> {
    return this.request<APIResponse<QueryResult>>('/api/v1/query/process', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async streamQuery(
    request: QueryRequest,
    onMessage: (data: unknown) => void,
    onError: (error: Error) => void,
    onComplete: () => void,
  ): Promise<void> {
    const response = await fetch(`${this.baseURL}/api/v1/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Stream error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        onComplete();
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onMessage(data);
          } catch (e) {
            onError(new Error(`Failed to parse SSE data: ${e}`));
          }
        }
      }
    }
  }

  async recallMemory(request: MemoryRecallRequest): Promise<APIResponse<{ count: number; memories: unknown[] }>> {
    return this.request<APIResponse<{ count: number; memories: unknown[] }>>(
      `/api/v1/memory/recall?query=${encodeURIComponent(request.query)}&limit=${request.limit}`,
    );
  }

  async addInteraction(request: AddInteractionRequest): Promise<APIResponse<unknown>> {
    return this.request<APIResponse<unknown>>('/api/v1/memory/add', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async provideFeedback(request: FeedbackRequest): Promise<APIResponse<unknown>> {
    return this.request<APIResponse<unknown>>('/api/v1/memory/feedback', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async searchKnowledge(
    request: SearchKnowledgeRequest,
  ): Promise<APIResponse<{ count: number; results: unknown[] }>> {
    const params = new URLSearchParams();
    if (request.query) params.append('query', request.query);
    if (request.category) params.append('category', request.category);
    if (request.tags) params.append('tags', request.tags.join(','));
    params.append('limit', request.limit.toString());

    return this.request<APIResponse<{ count: number; results: unknown[] }>>(
      `/api/v1/knowledge/search?${params.toString()}`,
    );
  }

  async addKnowledge(request: AddKnowledgeRequest): Promise<APIResponse<unknown>> {
    return this.request<APIResponse<unknown>>('/api/v1/knowledge/add', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getStats(): Promise<APIResponse<Statistics>> {
    return this.request<APIResponse<Statistics>>('/api/v1/stats');
  }

  async getStatsTrends(): Promise<APIResponse<unknown>> {
    return this.request<APIResponse<unknown>>('/api/v1/stats/trends');
  }

  async getLearnedPatterns(): Promise<APIResponse<LearnedPatterns>> {
    return this.request<APIResponse<LearnedPatterns>>('/api/v1/learned/patterns');
  }

  async getAPIMetrics(): Promise<APIResponse<APIMetrics>> {
    return this.request<APIResponse<APIMetrics>>('/api/v1/metrics');
  }

  getCache(): LRUCache<APIResponse> {
    return this.cache;
  }

  clearCache(): void {
    this.cache.clear();
  }
}

let clientInstance: SageAgentClient | null = null;

export function getClient(): SageAgentClient {
  if (!clientInstance) {
    clientInstance = new SageAgentClient();
  }
  return clientInstance;
}

export function setClient(client: SageAgentClient): void {
  clientInstance = client;
}
