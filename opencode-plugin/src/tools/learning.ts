/**
 * Learning and pattern discovery tools for OpenCode plugin
 */

import { tool } from '@opencode-ai/plugin';
import { getClient } from '../api/client.js';

export const sageGetPatterns = tool({
  description:
    'View learned patterns and discovered insights. Shows what the agent has learned from all interactions, including success strategies, common mistakes, and optimal approaches.',
  args: {},
  async execute() {
    try {
      const client = getClient();

      const response = await client.getLearnedPatterns();

      if (!response.success) {
        throw new Error(response.error || 'Failed to get patterns');
      }

      const data = response.data;

      let result = `🧠 Sage Agent Learning Insights\n`;
      result += `═══════════════════════════\n\n`;

      result += `📊 Overview\n`;
      result += `Total Memories: ${data?.total_memories || 0}\n`;
      result += `Success Rate: ${(data?.success_rate || 0).toFixed(1)}%\n\n`;

      if (data?.learned_patterns && data.learned_patterns.length > 0) {
        result += `💡 Learned Patterns\n`;
        data.learned_patterns.forEach((pattern: string, idx: number) => {
          result += `  ${idx + 1}. ${pattern}\n`;
        });
        result += '\n';
      }

      if (data?.success_patterns && data.success_patterns.length > 0) {
        result += `✅ Success Strategies\n`;
        data.success_patterns.forEach((strategy: string, idx: number) => {
          result += `  ${idx + 1}. ${strategy}\n`;
        });
        result += '\n';
      }

      if (data?.common_mistakes && data.common_mistakes.length > 0) {
        result += `⚠️  Common Mistakes (to avoid)\n`;
        data.common_mistakes.forEach((mistake: string, idx: number) => {
          result += `  ${idx + 1}. ${mistake}\n`;
        });
        result += '\n';
      }

      if (data?.top_topics && data.top_topics.length > 0) {
        result += `📚 Top Topics\n`;
        data.top_topics.forEach((topic: string, idx: number) => {
          result += `  ${idx + 1}. ${topic}\n`;
        });
        result += '\n';
      }

      if (data?.recommendations && data.recommendations.length > 0) {
        result += `🎯 Recommendations\n`;
        data.recommendations.forEach((rec: string, idx: number) => {
          result += `  ${idx + 1}. ${rec}\n`;
        });
      }

      return result;
    } catch (error) {
      throw new Error(`Failed to get patterns: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});
