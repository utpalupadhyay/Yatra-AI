/**
 * Yatra AI — Lightweight Markdown Renderer
 * Converts Gemma 4's markdown output to HTML for display.
 */

function renderMarkdown(text) {
  if (!text) return "";
  let html = text;

  // Escape HTML (security)
  html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Code blocks (before inline code)
  html = html.replace(/```[\w]*\n?([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

  // Headers
  html = html.replace(/^#### (.+)$/gm, "<h4>$1</h4>");
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Horizontal rule
  html = html.replace(/^---+$/gm, "<hr/>");

  // Bold & Italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Tables
  html = html.replace(/(\|.+\|[\r\n]+\|[-|: ]+\|[\r\n]+(?:\|.+\|[\r\n]*)+)/g, (match) => {
    const lines = match.trim().split(/\r?\n/);
    let tableHtml = "<table><thead><tr>";
    const headers = lines[0].split("|").filter((_, i, a) => i > 0 && i < a.length - 1);
    headers.forEach(h => { tableHtml += `<th>${h.trim()}</th>`; });
    tableHtml += "</tr></thead><tbody>";
    for (let i = 2; i < lines.length; i++) {
      const cells = lines[i].split("|").filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      tableHtml += "<tr>";
      cells.forEach(c => { tableHtml += `<td>${c.trim()}</td>`; });
      tableHtml += "</tr>";
    }
    tableHtml += "</tbody></table>";
    return tableHtml;
  });

  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");

  // Unordered lists
  html = html.replace(/^(\s*)([-*+]) (.+)$/gm, "$1<li>$3</li>");
  html = html.replace(/(<li>.*<\/li>(\s*\n)*)+/g, (match) => `<ul>${match}</ul>`);

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

  // Paragraphs (wrap remaining non-HTML lines)
  html = html.replace(/^(?!<[a-z]|$)(.+)$/gm, "<p>$1</p>");

  // Clean up multiple blank lines
  html = html.replace(/\n{3,}/g, "\n\n");

  return html;
}
