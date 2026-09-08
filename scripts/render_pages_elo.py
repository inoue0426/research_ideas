#!/usr/bin/env python3

import argparse
import html
import json
import os
import re
import urllib.request
from pathlib import Path

README_PATH = Path('README.md')
START_MARKER = '<!-- RESEARCH_ELO_START -->'
END_MARKER = '<!-- RESEARCH_ELO_END -->'
PLACEHOLDER = '<!-- ELO_TABLE -->'
CLOSED_PLACEHOLDER = '<!-- CLOSED_IDEAS -->'
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


def github_request(path):
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        return None
    url = f'https://api.github.com{path}'
    req = urllib.request.Request(url)
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_closed_owner_issues():
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        return []
    owner = repo.split('/', 1)[0]
    issues = []
    page = 1
    while True:
        batch = github_request(f'/repos/{repo}/issues?state=closed&sort=updated&direction=desc&per_page=100&page={page}') or []
        if not batch:
            break
        for item in batch:
            if 'pull_request' in item:
                continue
            if (item.get('user') or {}).get('login') != owner:
                continue
            issues.append(item)
        if len(batch) < 100:
            break
        page += 1
    return issues


def strip_markdown(text):
    text = re.sub(r'```.*?```', ' ', text or '', flags=re.S)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'^\s{0,3}[#>*+-]+\s*', '', text, flags=re.M)
    text = re.sub(r'[*_~]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def summarize_reason(text, limit=520):
    text = strip_markdown(text)
    if not text:
        return 'Closed without a written decision note.'
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0]
    return cut + '…'


def closed_reason(issue, owner):
    repo = os.environ['GITHUB_REPOSITORY']
    comments = github_request(f'/repos/{repo}/issues/{issue["number"]}/comments?per_page=100') or []
    owner_comments = [c for c in comments if (c.get('user') or {}).get('login') == owner and (c.get('body') or '').strip()]
    if owner_comments:
        return summarize_reason(owner_comments[-1]['body'])
    return summarize_reason(issue.get('body') or '')


def render_closed_ideas():
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        return '<p class="note">Closed-idea archive unavailable in this build.</p>'
    owner = repo.split('/', 1)[0]
    issues = fetch_closed_owner_issues()
    if not issues:
        return '<p class="note">No closed research ideas yet.</p>'

    out = ['<div class="closed-grid">']
    for issue in issues:
        number = int(issue['number'])
        title = html.escape(issue.get('title') or f'Issue #{number}')
        url = html.escape(issue.get('html_url') or f'https://github.com/{repo}/issues/{number}', quote=True)
        reason = html.escape(closed_reason(issue, owner))
        closed_at = (issue.get('closed_at') or '')[:10]
        state_reason = issue.get('state_reason') or 'closed'
        badge = 'Completed' if state_reason == 'completed' else 'Not planned' if state_reason == 'not_planned' else 'Closed'
        meta = f'{badge}' + (f' · {closed_at}' if closed_at else '')
        out.extend([
            '<article class="closed-card">',
            f'<div class="closed-meta">{html.escape(meta)}</div>',
            f'<h3><a href="{url}">#{number} — {title}</a></h3>',
            f'<p>{reason}</p>',
            '</article>',
        ])
    out.append('</div>')
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
    if CLOSED_PLACEHOLDER in page:
        page = page.replace(CLOSED_PLACEHOLDER, render_closed_ideas(), 1)
    page_path.write_text(page, encoding='utf-8')
    print(f'Rendered {len(body)} Elo rows into {page_path}.')


if __name__ == '__main__':
    main()
