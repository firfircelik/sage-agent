/**
 * Memory management tools for OpenCode plugin
 */

import { tool } from '@opencode-ai/plugin';
import { getClient } from '../api/client.js';

export const sageRecallMemory: any = tool({
  description:
    'Recall similar past interactions from long-term memory. Instantly retrieves related queries and responses (<1ms). Essential for leveraging learned experiences.',
  args: {
    query: tool.schema
      .string()
      .describe('Query to find similar past interactions'),
    limit: tool.schema
      .number()
      .min(1)
      .max(20)
      .default(5)
      .describe('Maximum number of similar memories to return'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.recallMemory({
        query: args.query,
        limit: args.limit,
      });

      if (!response.success) {
        throw new Error(response.error || 'Memory recall failed');
      }

      const data = response.data;

      let result = `🧠 Memory Recall Results\n`;
      result += `═════════════════════\n`;
      result += `Found ${data?.count || 0} similar memories\n\n`;

      if (data?.memories && data.memories.length > 0) {
        data.memories.forEach((mem: any, idx: number) => {
          result += `Memory ${idx + 1}:\n`;
          result += `  Query: ${mem.query}\n`;
          result += `  Response: ${mem.response}\n`;
          result += `  Provider: ${mem.provider}/${mem.model}\n`;
          result += `  Timestamp: ${mem.timestamp}\n`;
          if (mem.similarity) {
            result += `  Similarity: ${(mem.similarity * 100).toFixed(1)}%\n`;
          }
          result += '\n';
        });
      } else {
        result += 'No similar memories found. This query will be learned after processing.\n';
      }

      return result;
    } catch (error) {
      throw new Error(`Failed to recall memory: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageAddInteraction: any = tool({
  description:
    'Manually add an interaction to long-term memory for learning. The agent will validate, learn patterns, and prevent future mistakes.',
  args: {
    query: tool.schema.string().describe('The query that was asked'),
    response: tool.schema.string().describe('The response that was provided'),
    provider: tool.schema
      .string()
      .default('openai')
      .describe('LLM provider used'),
    model: tool.schema
      .string()
      .default('gpt-4')
      .describe('Model name used'),
    tokens_used: tool.schema
      .number()
      .min(0)
      .default(0)
      .describe('Number of tokens consumed'),
    success: tool.schema
      .boolean()
      .default(true)
      .describe('Whether the interaction was successful'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.addInteraction({
        query: args.query,
        response: args.response,
        provider: args.provider,
        model: args.model,
        tokens_used: args.tokens_used,
        success: args.success,
      });

      if (!response.success) {
        throw new Error(response.error || 'Failed to add interaction');
      }

      const data = response.data as any;

      let result = `💾 Interaction added to memory\n\n`;
      result += `Memory ID: ${data?.memory_id}\n`;
      result += `Validated: ${data?.validated ? '✅' : '❌'}\n`;
      if (data?.confidence) {
        result += `Confidence: ${(data.confidence * 100).toFixed(1)}%\n`;
      }
      result += `Learned: ${data?.learned ? '✅' : '⏳'}\n\n`;
      result += `The agent will use this interaction for future learning and pattern discovery.`;

      return result;
    } catch (error) {
      throw new Error(`Failed to add interaction: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageProvideFeedback: any = tool({
  description:
    'Provide feedback on an interaction for continuous self-improvement. Feedback directly influences learning patterns and prevents similar mistakes.',
  args: {
    query: tool.schema.string().describe('The query that was processed'),
    response: tool.schema.string().describe('The response that was provided'),
    feedback: tool.schema.string().describe('Detailed feedback text'),
    rating: tool.schema
      .number()
      .min(1)
      .max(5)
      .describe('Quality rating from 1 (poor) to 5 (excellent)'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.provideFeedback({
        query: args.query,
        response: args.response,
        feedback: args.feedback,
        rating: args.rating,
      });

      if (!response.success) {
        throw new Error(response.error || 'Failed to record feedback');
      }

      const stars = '⭐'.repeat(args.rating);
      let result = `📝 Feedback recorded for self-improvement\n\n`;
      result += `Rating: ${stars} (${args.rating}/5)\n`;
      result += `Feedback: ${args.feedback}\n\n`;
      result += `This feedback will be used to:\n`;
      result += `  • Identify success patterns\n`;
      result += `  • Learn from mistakes\n`;
      result += `  • Optimize future responses\n`;
      result += `  • Update quality trends`;

      return result;
    } catch (error) {
      throw new Error(`Failed to record feedback: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});
