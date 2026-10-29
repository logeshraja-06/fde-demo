import React, { useMemo } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import './MarkdownRenderer.css'

// Configure marked parser for clean GitHub-Flavored Markdown
marked.setOptions({
  gfm: true,
  breaks: true,
})

/**
 * Preprocesses text before markdown parsing to eliminate common LLM artifacts:
 * - Fixes '***Heading:**' into bullet items '* **Heading:**'
 * - Converts Unicode bullets ('•', '·') into standard markdown list bullets ('*')
 * - Ensures space after '#' headings (e.g. '###Heading' -> '### Heading')
 * - Upgrades 'CRITICAL CONFLICT DETECTED' into styled alert banners
 */
function preprocessMarkdown(rawText = '') {
  if (!rawText || typeof rawText !== 'string') return ''

  let text = rawText

  // 1. Ensure space after '#' headings (e.g. '###Heading' -> '### Heading')
  text = text.replace(/^(#{1,6})([^\s#])/gm, '$1 $2')

  // 2. Ensure blank line before headings so they always parse as headers
  text = text.replace(/([^\n])\n(#{1,6}\s+)/g, '$1\n\n$2')

  // 3. Convert lines starting with 3+ asterisks followed by bold title:
  // e.g. '***Heading:**' or '****Heading:**' -> '* **Heading:**'
  text = text.replace(/^(\s*)\*{3,}\s*([^*]+)\*\*/gm, '$1* **$2**')

  // 4. Convert raw '*** ' at start of lines into '* '
  text = text.replace(/^(\s*)\*{3,}\s+/gm, '$1* ')

  // 5. Convert unicode bullets into standard markdown list bullets
  text = text.replace(/^(\s*)[•·▪▸►]\s*/gm, '$1* ')

  // 6. Ensure blank line before the first bullet item if preceded by a regular sentence
  text = text.replace(/([^\n*+-\d])\n(\s*[*+-]\s+)/g, '$1\n\n$2')

  // 7. Wrap prominent conflict headers in custom styled alert banner
  text = text.replace(
    /\*\*(CRITICAL CONFLICT DETECTED[^*]*|Adversarial (?:Policy )?Conflict Detected[^*]*)\*\*/gi,
    '<div class="markdown-conflict-banner">$1</div>'
  )

  return text
}

export default function MarkdownRenderer({ content = '' }) {
  const sanitizedHtml = useMemo(() => {
    if (!content) return ''
    const preprocessed = preprocessMarkdown(content)
    const rawHtml = marked.parse(preprocessed)
    return DOMPurify.sanitize(rawHtml, {
      ADD_TAGS: ['div', 'span', 'strong', 'em', 'p', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'code', 'pre', 'blockquote', 'hr', 'a'],
      ADD_ATTR: ['class', 'style', 'target', 'rel', 'href'],
    })
  }, [content])

  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  )
}
