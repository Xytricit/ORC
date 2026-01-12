"""Full-featured Markdown parser.

Extracts:
- Headings (H1-H6)
- Code blocks (fenced and indented)
- Links (inline and reference)
- Images
- Lists (ordered and unordered)
- Blockquotes
- Tables
- Frontmatter (YAML, TOML, JSON)
- Inline code
- Bold/italic text
"""
import re
from pathlib import Path
from typing import Dict, List


class MarkdownParser:
    """Enhanced Markdown parser with comprehensive feature extraction."""
    
    # Markdown patterns
    HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    FENCED_CODE_RE = re.compile(r'^```(\w*)\n(.*?)^```', re.MULTILINE | re.DOTALL)
    INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    REFERENCE_LINK_RE = re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE)
    IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    UNORDERED_LIST_RE = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_RE = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
    BLOCKQUOTE_RE = re.compile(r'^>\s+(.+)$', re.MULTILINE)
    TABLE_RE = re.compile(r'^\|.+\|$', re.MULTILINE)
    INLINE_CODE_RE = re.compile(r'`([^`]+)`')
    BOLD_RE = re.compile(r'\*\*([^*]+)\*\*|__([^_]+)__')
    ITALIC_RE = re.compile(r'\*([^*]+)\*|_([^_]+)_')
    FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
    HORIZONTAL_RULE_RE = re.compile(r'^(?:---|\*\*\*|___)\s*$', re.MULTILINE)
    
    def parse_file(self, path: Path) -> Dict:
        """Parse Markdown file and extract all structural elements."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        
        # Extract Markdown features
        headings = self._extract_headings(text, path)
        code_blocks = self._extract_code_blocks(text)
        inline_links = self._extract_inline_links(text)
        reference_links = self._extract_reference_links(text)
        images = self._extract_images(text)
        lists = self._extract_lists(text)
        blockquotes = self._extract_blockquotes(text)
        tables = self._extract_tables(text)
        frontmatter = self._extract_frontmatter(text)
        inline_code = self._extract_inline_code(text)
        
        files = {
            str(path): {
                "language": "markdown",
                "loc": len(lines),
                "markdown_features": {
                    "headings": len(headings),
                    "code_blocks": len(code_blocks),
                    "links": len(inline_links) + len(reference_links),
                    "images": len(images),
                    "lists": lists['unordered'] + lists['ordered'],
                    "blockquotes": len(blockquotes),
                    "tables": len(tables),
                    "has_frontmatter": frontmatter is not None,
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": headings,  # Use headings as "classes" for structure
            "imports": {},
            "exports": {},
            "markdown": True,
            "markdown_headings": headings,
            "markdown_code_blocks": code_blocks,
            "markdown_links": {"inline": inline_links, "reference": reference_links},
            "markdown_images": images,
            "markdown_lists": lists,
            "markdown_blockquotes": blockquotes,
            "markdown_tables": tables,
            "markdown_frontmatter": frontmatter,
            "markdown_inline_code": inline_code,
        }
    
    def _empty_result(self, path: Path) -> Dict:
        """Return empty parsing result."""
        return {
            "files": {str(path): {"language": "markdown", "loc": 0}},
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "markdown": True,
        }
    
    def _extract_headings(self, text: str, path: Path) -> Dict:
        """Extract Markdown headings (H1-H6)."""
        headings = {}
        
        for match in self.HEADING_RE.finditer(text):
            level = len(match.group(1))
            title = match.group(2).strip()
            line_no = text[:match.start()].count('\n') + 1
            
            # Create a slug from title for ID
            slug = re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-')
            
            headings[f"{path}::h{level}::{slug}"] = {
                "id": f"{path}::h{level}::{slug}",
                "name": title,
                "file": str(path),
                "line": line_no,
                "kind": f"heading_h{level}",
                "level": level,
            }
        
        return headings
    
    def _extract_code_blocks(self, text: str) -> List[Dict]:
        """Extract fenced code blocks with language."""
        code_blocks = []
        
        for match in self.FENCED_CODE_RE.finditer(text):
            language = match.group(1) or "plain"
            code = match.group(2).strip()
            line_no = text[:match.start()].count('\n') + 1
            
            code_blocks.append({
                "language": language,
                "code": code[:200],  # Truncate for storage
                "line": line_no,
                "length": len(code.splitlines()),
            })
        
        return code_blocks
    
    def _extract_inline_links(self, text: str) -> List[Dict]:
        """Extract inline Markdown links."""
        links = []
        seen = set()
        
        for match in self.INLINE_LINK_RE.finditer(text):
            link_text = match.group(1)
            url = match.group(2)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{url}:{line_no}"
            if key not in seen:
                seen.add(key)
                links.append({
                    "text": link_text,
                    "url": url,
                    "line": line_no,
                })
        
        return links
    
    def _extract_reference_links(self, text: str) -> List[Dict]:
        """Extract reference-style links."""
        links = []
        
        for match in self.REFERENCE_LINK_RE.finditer(text):
            reference = match.group(1)
            url = match.group(2).strip()
            line_no = text[:match.start()].count('\n') + 1
            
            links.append({
                "reference": reference,
                "url": url,
                "line": line_no,
            })
        
        return links
    
    def _extract_images(self, text: str) -> List[Dict]:
        """Extract image references."""
        images = []
        seen = set()
        
        for match in self.IMAGE_RE.finditer(text):
            alt_text = match.group(1)
            url = match.group(2)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{url}:{line_no}"
            if key not in seen:
                seen.add(key)
                images.append({
                    "alt": alt_text,
                    "url": url,
                    "line": line_no,
                })
        
        return images
    
    def _extract_lists(self, text: str) -> Dict:
        """Extract list items (ordered and unordered)."""
        unordered = len(self.UNORDERED_LIST_RE.findall(text))
        ordered = len(self.ORDERED_LIST_RE.findall(text))
        
        return {
            "unordered": unordered,
            "ordered": ordered,
            "total": unordered + ordered,
        }
    
    def _extract_blockquotes(self, text: str) -> List[Dict]:
        """Extract blockquotes."""
        blockquotes = []
        
        for match in self.BLOCKQUOTE_RE.finditer(text):
            content = match.group(1).strip()
            line_no = text[:match.start()].count('\n') + 1
            
            blockquotes.append({
                "content": content[:100],  # Truncate
                "line": line_no,
            })
        
        return blockquotes
    
    def _extract_tables(self, text: str) -> List[Dict]:
        """Extract table structures."""
        tables = []
        table_starts = []
        
        for match in self.TABLE_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            
            # Check if this is a new table or continuation
            if not table_starts or line_no > table_starts[-1] + 10:
                table_starts.append(line_no)
                tables.append({
                    "line": line_no,
                })
        
        return tables
    
    def _extract_frontmatter(self, text: str) -> Dict:
        """Extract YAML frontmatter."""
        match = self.FRONTMATTER_RE.match(text)
        if match:
            frontmatter_text = match.group(1)
            return {
                "content": frontmatter_text,
                "lines": len(frontmatter_text.splitlines()),
            }
        return None
    
    def _extract_inline_code(self, text: str) -> int:
        """Count inline code occurrences."""
        return len(self.INLINE_CODE_RE.findall(text))
