export interface Heading {
  level: number
  text: string
  id: string
}

export function extractHeadings(
  markdown: string,
  options: { maxLevel?: number } = {}
): Heading[] {
  const { maxLevel = 2 } = options
  const headings: Heading[] = []

  const lines = markdown.split('\n')
  for (const line of lines) {
    const match = line.match(/^(#{1,6})\s+(.+)$/)
    if (!match) continue

    const level = match[1].length
    if (level > maxLevel) continue

    const text = match[2].trim()
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '-')

    headings.push({ level, text, id })
  }

  return headings
}
