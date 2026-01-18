/**
 * Knowledge base tools for OpenCode plugin
 */

import { tool } from '@opencode-ai/plugin';
import { getClient } from '../api/client.js';

export const sageSearchKnowledge: any = tool({
  description:
    'Search the structured knowledge base for relevant information. Knowledge base contains validated, prioritized entries added by users.',
  args: {
    query: tool.schema
      .string()
      .optional()
      .describe('Search query for knowledge'),
    category: tool.schema
      .string()
      .optional()
      .describe('Filter by category (e.g., coding, security, best-practices)'),
    tags: tool.schema
      .array(tool.schema.string())
      .optional()
      .describe('Filter by tags'),
    limit: tool.schema
      .number()
      .min(1)
      .max(20)
      .default(5)
      .describe('Maximum number of results'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.searchKnowledge({
        query: args.query,
        category: args.category,
        tags: args.tags,
        limit: args.limit,
      });

      if (!response.success) {
        throw new Error(response.error || 'Knowledge search failed');
      }

      const data = response.data;

      let result = `📚 Knowledge Base Search Results\n`;
      result += `═══════════════════════════════\n`;
      result += `Found ${data?.count || 0} entries\n\n`;

      if (data?.results && data.results.length > 0) {
        data.results.forEach((entry: any, idx: number) => {
          result += `Entry ${idx + 1}:\n`;
          result += `  ID: ${entry.id}\n`;
          result += `  Title: ${entry.title}\n`;
          result += `  Category: ${entry.category}\n`;
          result += `  Priority: ${entry.priority}/10\n`;
          if (entry.tags && entry.tags.length > 0) {
            result += `  Tags: ${entry.tags.join(', ')}\n`;
          }
          result += `  Content: ${entry.content}\n\n`;
        });
      } else {
        result += 'No matching knowledge entries found.\n';
        result += 'Use sage_add_knowledge to add new entries.';
      }

      return result;
    } catch (error) {
      throw new Error(`Failed to search knowledge: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

export const sageAddKnowledge: any = tool({
  description:
    'Add structured knowledge to the knowledge base. Entries are validated, categorized, and made available for future queries.',
  args: {
    id: tool.schema
      .string()
      .describe('Unique identifier for this knowledge entry'),
    category: tool.schema
      .string()
      .describe('Category (e.g., coding, security, best-practices, algorithms)'),
    title: tool.schema.string().describe('Title of the knowledge entry'),
    content: tool.schema
      .string()
      .describe('The actual knowledge content'),
    tags: tool.schema
      .array(tool.schema.string())
      .default([])
      .describe('Tags for easier searching and categorization'),
    priority: tool.schema
      .number()
      .min(0)
      .max(10)
      .default(5)
      .describe('Priority from 0 (low) to 10 (high)'),
  },
  async execute(args) {
    try {
      const client = getClient();

      const response = await client.addKnowledge({
        id: args.id,
        category: args.category,
        title: args.title,
        content: args.content,
        tags: args.tags,
        priority: args.priority,
      });

      if (!response.success) {
        throw new Error(response.error || 'Failed to add knowledge');
      }

      const stars = '⭐'.repeat(Math.round(args.priority / 2));
      let result = `📖 Knowledge added successfully\n\n`;
      result += `ID: ${args.id}\n`;
      result += `Title: ${args.title}\n`;
      result += `Category: ${args.category}\n`;
      result += `Priority: ${args.priority}/10 ${stars}\n`;
      if (args.tags && args.tags.length > 0) {
        result += `Tags: ${args.tags.join(', ')}\n`;
      }
      result += `\nThis knowledge will be used to enhance future queries and prevent mistakes.`;

      return result;
    } catch (error) {
      throw new Error(`Failed to add knowledge: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});
