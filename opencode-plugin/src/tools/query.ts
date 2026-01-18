/**
 * Query processing tools for OpenCode plugin
 */

import { tool } from '@opencode-ai/plugin';
import { getClient } from '../api/client.js';

export const sageProcessQuery: any = tool({
  description:
    'Process a query with Sage Agent self-improving AI, RLM optimization, and long-term memory. Returns optimized response with token savings, memory recall, and improvement suggestions.',
  args: {
    query: tool.schema
      .string()
      .describe('The query to process with self-improving AI'),
    provider: tool.schema
      .enum(['openai', 'anthropic', 'deepseek', 'glm', 'cohere'])
      .default('openai')
      .describe('LLM provider to use for processing'),
    model: tool.schema
      .string()
      .optional()
      .describe('Specific model name (e.g., gpt-4, claude-3-sonnet)'),
    use_advanced_optimization: tool.schema
      .boolean()
      .default(true)
      .describe('Enable advanced RLM optimization and learning'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.processQuery({
        query: args.query,
        provider: args.provider,
        model: args.model,
        use_advanced_optimization: args.use_advanced_optimization,
      });

      if (!response.success) {
        throw new Error(response.error || 'Query processing failed');
      }

      const data = response.data;

      let result = `✅ Query processed successfully\n\n`;

      if (data?.from_memory) {
        result += `🧠 Retrieved from memory (instant recall)\n`;
        result += `💰 Tokens saved: ${data.tokens_saved}\n\n`;
      } else {
        result += `🔄 New query processed with RLM optimization\n`;
        result += `💰 Tokens saved: ${data?.tokens_saved || 0}\n\n`;
      }

      if (data?.context_enhanced) {
        result += `📚 Context: ${data.context_enhanced}\n\n`;
      }

      if (data?.ai_analysis) {
        result += `🤖 AI Analysis: ${data.ai_analysis}\n\n`;
      }

      if (data?.similar_memories && data.similar_memories.length > 0) {
        result += `🔍 Similar memories found: ${data.similar_memories.length}\n`;
        data.similar_memories.forEach((mem: any, idx: number) => {
          result += `  ${idx + 1}. ${mem.query.substring(0, 50)}...\n`;
        });
        result += '\n';
      }

      if (data?.improvement_suggestions && data.improvement_suggestions.length > 0) {
        result += `💡 Improvement suggestions:\n`;
        data.improvement_suggestions.forEach((suggestion: string, idx: number) => {
          result += `  ${idx + 1}. ${suggestion}\n`;
        });
      }

      result += `\n📊 Processing time: ${data?.processing_time?.toFixed(3)}s`;

      return result;
    } catch (error) {
      throw new Error(`Failed to process query: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageStreamQuery: any = tool({
  description:
    'Process a query with real-time streaming, showing progress updates and partial results as they arrive.',
  args: {
    query: tool.schema
      .string()
      .describe('The query to process with streaming'),
    provider: tool.schema
      .enum(['openai', 'anthropic', 'deepseek', 'glm', 'cohere'])
      .default('openai')
      .describe('LLM provider to use'),
    model: tool.schema
      .string()
      .optional()
      .describe('Specific model name'),
  },
  async execute(args) {
    try {
      const client = getClient();

      let output = '';

      await client.streamQuery(
        {
          query: args.query,
          provider: args.provider,
          model: args.model,
          use_advanced_optimization: true,
        },
        (data) => {
          output += `📡 ${JSON.stringify(data)}\n`;
        },
        (error) => {
          output += `❌ Error: ${error.message}\n`;
        },
        () => {
          output += '✅ Stream complete\n';
        },
      );

      return output;
    } catch (error) {
      throw new Error(`Failed to stream query: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});
