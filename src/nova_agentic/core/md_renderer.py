# src/nova_agentic/core/md_renderer.py
import re
import base64
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
import markdown


class MarkdownRenderer:
    @staticmethod
    def to_html(md_text: str, theme: str = "dark") -> str:
        # 🌟 核心修复 1：统一换行符，把 Windows 的 \r\n 换成 \n，防止正则漏抓
        text = md_text.strip().replace("\r\n", "\n")

        if text.startswith("```markdown"):
            text = re.sub(r'^```markdown\n', '', text, count=1)
        elif text.startswith("```"):
            text = re.sub(r'^```[a-zA-Z]*\n', '', text, count=1)
        if text.endswith("```") and text.count("```") == 1:
            text = text[:-3]

        code_blocks = []

        def extract_code(match):
            lang = match.group(1).strip() if match.group(1) else ""
            code = match.group(2)

            try:
                lexer = get_lexer_by_name(lang) if lang else TextLexer()
            except Exception:
                lexer = TextLexer()

            pyg_style = 'monokai' if theme == 'dark' else 'default'
            formatter = HtmlFormatter(noclasses=True, style=pyg_style)
            highlighted_html = highlight(code, lexer, formatter)

            # 剥除 Pygments 的默认外壳
            highlighted_html = re.sub(r'<div class="highlight">.*?<pre>', '', highlighted_html, flags=re.DOTALL)
            highlighted_html = re.sub(r'</pre>\n?</div>', '', highlighted_html, flags=re.DOTALL)

            if theme == 'dark':
                bg_color, text_color, border_color = '#1e1e1e', '#f8f8f2', '#333'
            else:
                bg_color, text_color, border_color = '#f6f8fa', '#24292e', '#e1e4e8'

            b64_code = base64.urlsafe_b64encode(code.encode('utf-8')).decode('utf-8')
            copy_button = f'<div style="text-align: right; margin-bottom: 6px;"><a href="copy:{b64_code}" style="color: #ffffff; background-color: #4CAF50; padding: 3px 8px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: bold;">📋 复制代码</a></div>'

            block = f'<br><table width="100%" bgcolor="{bg_color}" cellspacing="0" cellpadding="10" style="margin-top: 8px; margin-bottom: 8px; border-radius: 6px; border: 1px solid {border_color};"><tr><td>{copy_button}<pre style="color: {text_color}; margin: 0; padding: 0; white-space: pre-wrap; font-family: Consolas, monospace; font-size: 13px;">{highlighted_html}</pre></td></tr></table><br>'
            code_blocks.append(block)
            return f"@@@CODE_BLOCK_{len(code_blocks) - 1}@@@"

        if text.count("```") % 2 != 0:
            text += "\n```"

        # 🌟 核心修复 2：修正正则，吸收 lang 后面可能多出来的空格，精准提取代码本体
        text = re.sub(r'```([a-zA-Z0-9_+-]*)\s*\n(.*?)```', extract_code, text, flags=re.DOTALL)

        html = markdown.markdown(text, extensions=['extra', 'tables', 'fenced_code', 'nl2br'])

        for i, block in enumerate(code_blocks):
            html = html.replace(f"<p>@@@CODE_BLOCK_{i}@@@</p>", block)
            html = html.replace(f"@@@CODE_BLOCK_{i}@@@", block)

        html = html.replace('<p>', '<p style="margin: 4px 0; word-break: break-all;">')
        return html
