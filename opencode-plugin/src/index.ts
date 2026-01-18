/**
 * Main entry point for Sage Agent OpenCode Plugin
 *
 * This plugin provides self-improving AI capabilities with:
 * - RLM (Reinforcement Learning Mechanism) optimization
 * - Long-term memory with instant recall
 * - Token optimization (30-60% reduction)
 * - Continuous learning from every interaction
 * - Multi-provider LLM support
 * - Knowledge base management
 * - Comprehensive analytics
 */

import type { Plugin } from '@opencode-ai/plugin';

import * as QueryTools from './tools/query.js';
import * as MemoryTools from './tools/memory.js';
import * as KnowledgeTools from './tools/knowledge.js';
import * as LearningTools from './tools/learning.js';
import * as StatsTools from './tools/stats.js';
import { loadCommands } from './commands/loader.js';

export const SageAgentPlugin: Plugin = async () => {
  const commands = await loadCommands();

  return {
    tool: {
      sage_process_query: QueryTools.sageProcessQuery,
      sage_stream_query: QueryTools.sageStreamQuery,
      sage_recall_memory: MemoryTools.sageRecallMemory,
      sage_add_interaction: MemoryTools.sageAddInteraction,
      sage_provide_feedback: MemoryTools.sageProvideFeedback,
      sage_search_knowledge: KnowledgeTools.sageSearchKnowledge,
      sage_add_knowledge: KnowledgeTools.sageAddKnowledge,
      sage_get_patterns: LearningTools.sageGetPatterns,
      sage_get_stats: StatsTools.sageGetStats,
      sage_optimization_insights: StatsTools.sageOptimizationInsights,
      sage_health_check: StatsTools.sageHealthCheck,
    },

    async config(config) {
      config.command = config.command ?? {};

      for (const cmd of commands) {
        config.command[`sage-${cmd.name}`] = {
          template: cmd.template,
          description: cmd.frontmatter.description,
          agent: cmd.frontmatter.agent,
          model: cmd.frontmatter.model,
          subtask: cmd.frontmatter.subtask,
        };
      }
    },
  };
};

export default SageAgentPlugin;
