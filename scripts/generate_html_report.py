import os
import re

def convert_md_to_html(md_path, html_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into lines
    lines = content.split('\n')
    html_lines = []
    
    in_code_block = False
    in_table = False
    in_list = False
    
    for line in lines:
        # Code block check
        if line.strip().startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = line.strip()[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            continue
            
        if in_code_block:
            # Escape HTML
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(escaped)
            continue

        # Table check
        if line.startswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
                # Parse header
                cols = [c.strip() for c in line.split('|')[1:-1]]
                html_lines.append('<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr></thead>')
                html_lines.append('<tbody>')
            else:
                if '---' in line:
                    continue  # Separator line
                cols = [c.strip() for c in line.split('|')[1:-1]]
                html_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cols) + '</tr>')
            continue
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False

        # Blockquote check
        if line.startswith('>'):
            # Process content in blockquote
            processed = line[1:].strip()
            processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed)
            processed = re.sub(r'`(.*?)`', r'<code>\1</code>', processed)
            html_lines.append(f'<blockquote>{processed}</blockquote>')
            continue

        # Header check
        h_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if h_match:
            level = len(h_match.group(1))
            header_text = h_match.group(2)
            # Process formatting inside headers
            header_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', header_text)
            header_text = re.sub(r'`(.*?)`', r'<code>\1</code>', header_text)
            html_lines.append(f'<h{level}>{header_text}</h{level}>')
            continue

        # List check
        list_match = re.match(r'^[-*]\s+(.*)$', line)
        if list_match:
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content_list = list_match.group(1)
            content_list = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content_list)
            content_list = re.sub(r'`(.*?)`', r'<code>\1</code>', content_list)
            html_lines.append(f'<li>{content_list}</li>')
            continue
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False

        # Paragraph
        if line.strip():
            # Check bold and code in paragraph
            processed = line
            processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed)
            processed = re.sub(r'`(.*?)`', r'<code>\1</code>', processed)
            processed = re.sub(r'➔\s*(.*)', r'<span class="badge">➔</span> \1', processed)
            html_lines.append(f'<p>{processed}</p>')
        else:
            html_lines.append('')
            
    if in_table:
        html_lines.append('</tbody></table>')
    if in_list:
        html_lines.append('</ul>')
        
    body_content = '\n'.join(html_lines)
    
    # Inline replacement of standard icons
    body_content = body_content.replace('📝', '<span class="icon">📝</span>')
    body_content = body_content.replace('➔', '<span class="icon">➔</span>')
    
    template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Thực nghiệm: Single-Agent vs. Multi-Agent</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #eff6ff;
            --primary-accent: #2563eb;
            --slate-50: #f8fafc;
            --slate-100: #f1f5f9;
            --slate-200: #e2e8f0;
            --slate-700: #334155;
            --slate-800: #1e293b;
            --slate-900: #0f172a;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--slate-50);
            color: var(--slate-800);
            line-height: 1.7;
            margin: 0;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
            border: 1px solid var(--slate-200);
        }}
        h1 {{
            color: var(--slate-900);
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-top: 0;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--slate-200);
        }}
        h2 {{
            color: var(--primary);
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            border-bottom: 1px solid var(--slate-200);
            padding-bottom: 0.5rem;
        }}
        h3 {{
            color: var(--slate-900);
            font-size: 1.25rem;
            font-weight: 700;
            margin-top: 2rem;
            padding: 0.5rem 1rem;
            background-color: var(--slate-100);
            border-radius: 8px;
            border-left: 4px solid var(--primary-accent);
        }}
        h4 {{
            color: var(--primary-accent);
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        p {{
            margin-top: 0;
            margin-bottom: 1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            font-size: 0.95rem;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--slate-200);
        }}
        th {{
            background-color: var(--primary);
            color: #ffffff;
            font-weight: 600;
            text-align: left;
            padding: 14px 16px;
        }}
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--slate-200);
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:nth-child(even) {{
            background-color: var(--slate-50);
        }}
        pre {{
            background-color: var(--slate-900);
            color: #f1f5f9;
            padding: 1.25rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Fira Code', 'Courier New', Courier, monospace;
            font-size: 0.875rem;
            margin: 1.25rem 0;
            border: 1px solid #334155;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
        }}
        code {{
            font-family: 'Fira Code', 'Courier New', Courier, monospace;
            background-color: var(--slate-200);
            color: var(--slate-900);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
            font-size: inherit;
        }}
        blockquote {{
            border-left: 4px solid var(--primary-accent);
            background-color: var(--primary-light);
            color: #1e40af;
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }}
        ul {{
            padding-left: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        li {{
            margin-bottom: 0.5rem;
        }}
        .icon {{
            margin-right: 0.5rem;
            font-size: 1.1em;
        }}
        .badge {{
            display: inline-block;
            background-color: var(--primary-light);
            color: var(--primary-accent);
            padding: 0.1rem 0.5rem;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_content}
    </div>
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(template)

if __name__ == '__main__':
    convert_md_to_html('reports/benchmark_report.md', 'reports/benchmark_report.html')
    print("HTML report successfully generated at reports/benchmark_report.html")
