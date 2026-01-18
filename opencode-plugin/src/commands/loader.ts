/**
 * Command loader for OpenCode plugin
 * Loads .md files from command/ directory as slash commands
 */

import path from 'path';

interface CommandFrontmatter {
  description?: string;
  agent?: string;
  model?: string;
  subtask?: boolean;
}

interface ParsedCommand {
  name: string;
  frontmatter: CommandFrontmatter;
  template: string;
}

function parseFrontmatter(content: string): { frontmatter: CommandFrontmatter; body: string } {
  const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
  const match = content.match(frontmatterRegex);

  if (!match) {
    return { frontmatter: {}, body: content.trim() };
  }

  const [, yamlContent, body] = match;
  const frontmatter: CommandFrontmatter = {};

  for (const line of yamlContent.split('\n')) {
    const colonIndex = line.indexOf(':');
    if (colonIndex === -1) continue;

    const key = line.slice(0, colonIndex).trim();
    const value = line.slice(colonIndex + 1).trim();

    if (key === 'description') frontmatter.description = value;
    if (key === 'agent') frontmatter.agent = value;
    if (key === 'model') frontmatter.model = value;
    if (key === 'subtask') frontmatter.subtask = value === 'true';
  }

  return { frontmatter, body: body.trim() };
}

export async function loadCommands(): Promise<ParsedCommand[]> {
  const commands: ParsedCommand[] = [];

  try {
    const commandDir = path.join(import.meta.dir!, 'command');
    const files = ['sage.md', 'memory.md', 'stats.md', 'learn.md', 'optimize.md', 'teach.md'];

    for (const file of files) {
      const filePath = path.join(commandDir, file);
      const content = await Bun.file(filePath).text();
      const { frontmatter, body } = parseFrontmatter(content);

      const name = file.replace('.md', '');

      commands.push({
        name,
        frontmatter,
        template: body,
      });
    }
  } catch (error) {
    // Error loading commands - will use empty list
  }

  return commands;
}
