import { CSSProperties, ReactNode } from "react";

const BLOCK_STYLE: CSSProperties = {
  maxWidth: "72ch",
  lineHeight: 1.56,
  color: "var(--cg-text)",
};

const PARAGRAPH_STYLE: CSSProperties = {
  margin: "0 0 10px",
  whiteSpace: "pre-wrap",
};

const LIST_STYLE: CSSProperties = {
  margin: "0 0 10px 20px",
  padding: 0,
};

const PRE_STYLE: CSSProperties = {
  margin: "0 0 10px",
  padding: "10px 12px",
  borderRadius: 10,
  background: "#f3f4f6",
  border: "1px solid var(--cg-border)",
  overflowX: "auto",
  whiteSpace: "pre",
};

const INLINE_CODE_STYLE: CSSProperties = {
  fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
  fontSize: "0.92em",
  padding: "0.1em 0.34em",
  borderRadius: 6,
  background: "#eef1f5",
};

const LINK_STYLE: CSSProperties = {
  color: "var(--cg-link)",
  textDecoration: "underline",
  textUnderlineOffset: 2,
};

const AUTOLINK_TRAILING_RE = /[.,!?;:]+$/;

type LinkParts = {
  clean: string;
  trailing: string;
};

function normalizeAutolink(candidate: string): LinkParts {
  let clean = candidate;
  let trailing = "";

  const punctMatch = clean.match(AUTOLINK_TRAILING_RE);
  if (punctMatch) {
    trailing = punctMatch[0] + trailing;
    clean = clean.slice(0, -punctMatch[0].length);
  }

  while (clean.endsWith(")")) {
    const opens = (clean.match(/\(/g) ?? []).length;
    const closes = (clean.match(/\)/g) ?? []).length;
    if (closes <= opens) {
      break;
    }
    clean = clean.slice(0, -1);
    trailing = ")" + trailing;
  }

  return { clean, trailing };
}

function safeHttpUrl(raw: string): string | null {
  try {
    const parsed = new URL(raw);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}

function parseInline(text: string, keyPrefix = "inline"): ReactNode[] {
  const nodes: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < text.length) {
    const rest = text.slice(i);

    const markdownLink = rest.match(/^\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/);
    if (markdownLink) {
      const href = safeHttpUrl(markdownLink[2]);
      if (href) {
        nodes.push(
          <a key={`${keyPrefix}-lnk-${key++}`} href={href} target="_blank" rel="noopener noreferrer" style={LINK_STYLE}>
            {markdownLink[1]}
          </a>,
        );
        i += markdownLink[0].length;
        continue;
      }
    }

    const inlineCode = rest.match(/^`([^`\n]+)`/);
    if (inlineCode) {
      nodes.push(
        <code key={`${keyPrefix}-code-${key++}`} style={INLINE_CODE_STYLE}>
          {inlineCode[1]}
        </code>,
      );
      i += inlineCode[0].length;
      continue;
    }

    const bold = rest.match(/^\*\*([^*\n]+)\*\*/);
    if (bold) {
      nodes.push(<strong key={`${keyPrefix}-b-${key++}`}>{bold[1]}</strong>);
      i += bold[0].length;
      continue;
    }

    const italic = rest.match(/^\*([^*\n]+)\*/);
    if (italic) {
      nodes.push(<em key={`${keyPrefix}-i-${key++}`}>{italic[1]}</em>);
      i += italic[0].length;
      continue;
    }

    const rawUrl = rest.match(/^(https?:\/\/[^\s<]+)/);
    if (rawUrl) {
      const { clean, trailing } = normalizeAutolink(rawUrl[1]);
      const href = safeHttpUrl(clean);

      if (href) {
        nodes.push(
          <a key={`${keyPrefix}-auto-${key++}`} href={href} target="_blank" rel="noopener noreferrer" style={LINK_STYLE}>
            {clean}
          </a>,
        );
        if (trailing) {
          nodes.push(trailing);
        }
        i += rawUrl[0].length;
        continue;
      }
    }

    nodes.push(text[i]);
    i += 1;
  }

  return nodes;
}

function renderParagraph(text: string, key: string): ReactNode {
  const lines = text.split("\n");
  const content: ReactNode[] = [];

  lines.forEach((line, idx) => {
    content.push(...parseInline(line, `${key}-line-${idx}`));
    if (idx < lines.length - 1) {
      content.push(<br key={`${key}-br-${idx}`} />);
    }
  });

  return (
    <p key={key} style={PARAGRAPH_STYLE}>
      {content}
    </p>
  );
}

export function renderAssistantMarkdown(content: string): ReactNode {
  const lines = content.split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (/^```/.test(line)) {
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !/^```/.test(lines[i])) {
        code.push(lines[i]);
        i += 1;
      }
      if (i < lines.length && /^```/.test(lines[i])) {
        i += 1;
      }

      blocks.push(
        <pre key={`pre-${key++}`} style={PRE_STYLE}>
          <code>{code.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    if (/^\s*[-*]\s+/.test(line)) {
      const items: ReactNode[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        const value = lines[i].replace(/^\s*[-*]\s+/, "");
        items.push(<li key={`li-${key++}`}>{parseInline(value, `li-${key}`)}</li>);
        i += 1;
      }
      blocks.push(
        <ul key={`ul-${key++}`} style={LIST_STYLE}>
          {items}
        </ul>,
      );
      continue;
    }

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    const paragraph: string[] = [line];
    i += 1;
    while (i < lines.length && lines[i].trim() !== "" && !/^```/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i])) {
      paragraph.push(lines[i]);
      i += 1;
    }

    blocks.push(renderParagraph(paragraph.join("\n"), `p-${key++}`));
  }

  return <div style={BLOCK_STYLE}>{blocks}</div>;
}
