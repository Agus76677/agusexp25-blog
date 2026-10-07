import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { parse } from 'node-html-parser'

// Reading-time input for HTML-derived MDX; ordinary posts retain the original path.
export function paperReadingText(file) {
  if (file.data?.astro?.frontmatter?.paperBody !== 'content.json') return undefined
  const blocks = JSON.parse(readFileSync(join(dirname(file.path), 'content.json'), 'utf8'))
  if (!Array.isArray(blocks) || !blocks.every((block) => typeof block === 'string')) {
    throw new Error('Paper content.json must be an array of HTML strings')
  }
  return blocks.map((block) => parse(block).textContent).join('\n')
}
