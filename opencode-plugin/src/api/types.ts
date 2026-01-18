/**
 * API Client Types
 */

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export interface CacheConfig {
  maxSize: number;
  defaultTTL: number;
  cleanupInterval: number;
}

export interface ClientConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  enableCache: boolean;
  cacheConfig: CacheConfig;
}

export interface RequestOptions {
  signal?: AbortSignal;
  timeout?: number;
  retries?: number;
  useCache?: boolean;
}
