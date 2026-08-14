#!/usr/bin/env python3

import argparse
import html
import re
from pathlib import Path

README_PATH = Path('README.md')
START_MARKER = '<!-- RESEARCH_ELO_START -->'
END_MARKER = '<!-- RESEARCH_ELO_END -->'
PLACEHOLDER = '<!-- ELO_TABLE -->'
LINK_PATTERN = re.compile(r'\[(.+?)\]\((https://[^)]+)\)')


def clean_text(text):
    return text.replace('\\[', '[').replace('\\]', ']').replace('**', '')


def inline_md(text):
    text = text.strip()
    out = []
    cursor = 0
    for match in LINK_PATTERN.finditer(text):
        out.append(html.escape(clean_text(text[cursor:match.start()]), quote=True))
        label = html.escape(clean_text(match.group(1)), quote=True)
        url = html.escape(match.group(2), quote=True)
        out.append(f'<a href="{url}">{label}</a>')
        cursor = match.end()
    out.append(html.escape(clean_text(text[cursor:]), quote=True))
    return ''.join(out)


def extract_table(readme):
    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError('Research Elo markers not found in README.md')
    section = readme.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    lines = [line.rstrip() for line in section.splitlines()]
    table_lines = [line for line in lines if line.startswith('|')]
    if len(table_lines) < 3:
        raise RuntimeError('Research Elo table not found in README.md')

    rows = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        rows.append(cells)

    headers = rows[0]
    body = rows[2:]
    updated = next((line.strip('_') for line in lines if line.startswith('_Updated automatically')), '')
    return headers, body, updated


def render_table(headers, body, updated):
    out = ['<div class="table-wrap">', '<table class="elo-table">', '<thead><tr>']
    for header in headers:
        out.append(f'<th>{inline_md(header)}</th>')
    out.extend(['</tr></thead>', '<tbody>'])
    for row in body:
        if len(row) != len(headers):
            continue
        out.append('<tr>')
        for cell in row:
            out.append(f'<td>{inline_md(cell)}</td>')
        out.append('</tr>')
    out.extend(['</tbody>', '</table>', '</div>'])
    if updated:
        out.append(f'<p class="elo-updated">{html.escape(updated)}</p>')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', required=True)
    args = parser.parse_args()

    page_path = Path(args.page)
    page = page_path.read_text(encoding='utf-8')
    if PLACEHOLDER not in page:
        raise RuntimeError(f'{PLACEHOLDER} not found in {page_path}')

    headers, body, updated = extract_table(README_PATH.read_text(encoding='utf-8'))
    page = page.replace(PLACEHOLDER, render_table(headers, body, updated), 1)
    page_path.write_text(page, encoding='utf-8')
    print(f'Rendered {len(body)} Elo rows into {page_path}.')


if __name__ == '__main__':
    main()
