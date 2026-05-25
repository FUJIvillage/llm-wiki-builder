import { describe, it, expect } from 'vitest'
import { extractHeadings } from './markdown'

describe('extractHeadings', () => {
  it('returns empty array for empty string', () => {
    expect(extractHeadings('')).toEqual([])
  })

  it('extracts h2 headings', () => {
    const md = '## Hello World'
    expect(extractHeadings(md)).toEqual([
      { level: 2, text: 'Hello World', id: 'hello-world' },
    ])
  })

  it('extracts multiple headings', () => {
    const md = `## First\n## Second`
    expect(extractHeadings(md)).toEqual([
      { level: 2, text: 'First', id: 'first' },
      { level: 2, text: 'Second', id: 'second' },
    ])
  })

  it('ignores h1 and h3+ by default', () => {
    const md = `# Title\n## Section\n### Subsection`
    expect(extractHeadings(md)).toEqual([
      { level: 1, text: 'Title', id: 'title' },
      { level: 2, text: 'Section', id: 'section' },
    ])
  })

  it('generates kebab-case ids', () => {
    const md = '## Hello World 123'
    expect(extractHeadings(md)[0].id).toBe('hello-world-123')
  })
})
