/**
 * Statistics and analytics tools for OpenCode plugin
 */

import { tool } from '@opencode-ai/plugin';
import { getClient } from '../api/client.js';

export const sageGetStats = tool({
  description:
    'Get comprehensive statistics including token optimization results, memory size, quality trends, and performance metrics.',
  async execute() {
    try {
      const client = getClient();

      const response = await client.getStats();

      if (!response.success) {
        throw new Error(response.error || 'Failed to get statistics');
      }

      const data = response.data;

      let result = `📊 Sage Agent Statistics\n`;
      result += `═════════════════════════════\n\n`;

      result += `📈 Overall Performance\n`;
      result += `Total Queries: ${data?.total_queries || 0}\n`;
      result += `Memory Size: ${data?.memory_size || 0} interactions\n`;
      result += `Cache Hit Rate: ${((data?.cache_hit_rate || 0) * 100).toFixed(1)}%\n\n`;

      result += `💰 Token Optimization\n`;
      result += `Total Tokens Saved: ${data?.total_tokens_saved || 0}\n`;
      result += `Average Savings: ${(data?.average_savings_percentage || 0).toFixed(1)}%\n\n`;

      if (data?.quality_trend) {
        const trend = data.quality_trend;
        result += `📊 Quality Trend\n`;
        result += `Trend: ${trend.trend === 'improving' ? '📈 Improving' : trend.trend === 'declining' ? '📉 Declining' : '➡️  Stable'}\n`;
        result += `Current Quality: ${(trend.current_quality || 0).toFixed(1)}%\n`;
        if (trend.improvement) {
          result += `Change: ${trend.improvement > 0 ? '+' : ''}${(trend.improvement || 0).toFixed(1)}%\n`;
        }
        result += '\n';
      }

      if (data?.usage?.patterns) {
        result += `🔍 Usage Patterns\n`;
        Object.entries(data.usage.patterns).forEach(([pattern, count]) => {
          result += `  ${pattern}: ${count as number}\n`;
        });
        result += '\n';
      }

      if (data?.usage?.providers) {
        result += `🤖 Provider Performance\n`;
        Object.entries(data.usage.providers).forEach(([provider, count]) => {
          result += `  ${provider}: ${count as number} queries\n`;
        });
        result += '\n';
      }

      if (data?.improvement?.learning_metrics) {
        result += `🧠 Learning Metrics\n`;
        Object.entries(data.improvement.learning_metrics).forEach(([metric, value]) => {
          result += `  ${metric}: ${value as number}\n`;
        });
      }

      return result;
    } catch (error) {
      throw new Error(`Failed to get statistics: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageOptimizationInsights = tool({
  description:
    'Get detailed token optimization insights showing compression strategies, cache performance, and recommendations for further optimization.',
  async execute() {
    try {
      const client = getClient();

      const response = await client.getStatsTrends();

      if (!response.success) {
        throw new Error(response.error || 'Failed to get optimization insights');
      }

      const data = response.data as any;

      let result = `💡 Token Optimization Insights\n`;
      result += `═══════════════════════════════\n\n`;

      if (data?.quality_trend) {
        result += `📊 Quality Metrics\n`;
        const trend = data.quality_trend;
        result += `Trend: ${trend.trend}\n`;
        result += `Quality: ${trend.current_quality}%\n\n`;
      }

      if (data?.usage_patterns) {
        result += `🔍 Usage Patterns\n`;
        Object.entries(data.usage_patterns).forEach(([pattern, count]) => {
          result += `  ${pattern}: ${count as number}\n`;
        });
        result += '\n';
      }

      if (data?.provider_performance) {
        result += `🤖 Provider Comparison\n`;
        Object.entries(data.provider_performance).forEach(([provider, count]) => {
          result += `  ${provider}: ${count as number} queries\n`;
        });
        result += '\n';
      }

      if (data?.learning_metrics) {
        result += `🧠 Learning Progress\n`;
        Object.entries(data.learning_metrics).forEach(([metric, value]) => {
          result += `  ${metric}: ${value as number}\n`;
        });
        result += '\n';
      }

      result += `💡 Optimization Tips\n`;
      result += `  • High cache hit rate = less redundant queries\n`;
      result += `  • Regular feedback = better learning\n`;
      result += `  • Adding knowledge = faster responses\n`;
      result += `  • Review learned patterns = avoid mistakes`;

      return result;
    } catch (error) {
      throw new Error(`Failed to get optimization insights: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageHealthCheck = tool({
  description:
    'Check Sage Agent API health, uptime, and server metrics. Verifies the backend is running optimally.',
  async execute() {
    try {
      const client = getClient();

      const response = await client.healthCheck();

      let result = `🏥 Sage Agent Health Check\n`;
      result += `══════════════════════════\n\n`;

      result += `Status: ${response.status === 'healthy' ? '✅ Healthy' : '⚠️  Degraded'}\n`;
      result += `RLM Initialized: ${response.rlm_initialized ? '✅ Yes' : '❌ No'}\n`;
      result += `Uptime: ${response.uptime_seconds.toFixed(1)}s (${(response.uptime_seconds / 60).toFixed(1)} min)\n\n`;

      result += `📊 Server Metrics\n`;
      result += `Total Requests: ${response.metrics.requests_total}\n`;
      result += `Success Rate: ${(response.metrics.success_rate * 100).toFixed(1)}%\n`;
      result += `Avg Response Time: ${response.metrics.avg_response_time.toFixed(3)}s\n\n`;

      result += `API Documentation:\n`;
      result += `  • Swagger UI: http://localhost:8000/docs\n`;
      result += `  • ReDoc: http://localhost:8000/redoc\n`;
      result += `  • Health: http://localhost:8000/health`;

      return result;
    } catch (error) {
      throw new Error(`Health check failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});
