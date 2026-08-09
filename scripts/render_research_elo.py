#!/usr/bin/env python3

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path('.research-elo/ratings.json')
README_PATH = Path('README.md')
START_MARKER = '<!-- RESEARCH_ELO_START -->'
END_MARKER = '<!-- RESEARCH_ELO_END -->'


def github_request(path):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required')

    req = urllib.request.Request(f'https://api.github.com{path}')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_open_owner_issues(repo):
    owner = repo.split('/', 1)[0]
    issues = {}
    page = 1
    while True:
        batch = github_request(f'/repos/{repo}/issues?state=open&per_page=100&page={page}')
        if not batch:
            break
        for item in batch:
            if 'pull_request' in item:
                continue
            if (item.get('user') or {}).get('login') != owner:
                continue
            issues[int(item['number'])] = item
        if len(batch) < 100:
            break
        page += 1
    return issues


def escape_markdown(text):
    return (
        str(text)
        .replace('\\', '\\\\')
        .replace('|', '\\|')
        .replace('[', '\\[')
        .replace(']', '\\]')
        .replace('\n', ' ')
    )


def build_section(state, issues, repo):
    rows = []
    for key, entry in state.get('ratings', {}).items():
        number = int(key)
        issue = issues.get(number)
        if issue is None:
            continue
        rows.append((number, entry, issue))

    rows.sort(key=lambda x: (-float(x[1].get('rating', 1500)), x[0]))

    lines = [
        START_MARKER,
        '## Research Elo',
        '',
        'Relative LLM-judge ranking of open research ideas. Ratings are comparative feedback, **not an objective measure of scientific value**.',
        '',
    ]

    if rows:
        lines.extend([
            '| Rank | Issue | Rating | Games | Record |',
            '|---:|---|---:|---:|---:|',
        ])
        for rank, (number, entry, issue) in enumerate(rows, start=1):
            title = escape_markdown(issue.get('title', ''))
            url = f'https://github.com/{repo}/issues/{number}'
            rating = round(float(entry.get('rating', 1500)))
            games = int(entry.get('games', 0))
            wins = int(entry.get('wins', 0))
            draws = int(entry.get('draws', 0))
            losses = int(entry.get('losses', 0))
            lines.append(
                f'| {rank} | [#{number} — {title}]({url}) | **{rating}** | {games} | {wins}W / {draws}D / {losses}L |'
            )
    else:
        lines.append('_No open issues have been rated yet._')

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines.extend([
        '',
        f'_Updated automatically after owner-authored issues are opened, edited, or reopened. Last update: {timestamp}._',
        END_MARKER,
    ])
    return '\n'.join(lines)


def main():
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        raise RuntimeError('GITHUB_REPOSITORY is required')

    state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
    issues = fetch_open_owner_issues(repo)
    section = build_section(state, issues, repo)
    readme = README_PATH.read_text(encoding='utf-8')

    if START_MARKER in readme and END_MARKER in readme:
        start = readme.index(START_MARKER)
        end = readme.index(END_MARKER) + len(END_MARKER)
        updated = readme[:start] + section + readme[end:]
    else:
        anchor = '\n## Language\n'
        if anchor in readme:
            updated = readme.replace(anchor, f'\n\n{section}\n{anchor}', 1)
        else:
            updated = readme.rstrip() + f'\n\n{section}\n'

    README_PATH.write_text(updated, encoding='utf-8')
    print(f'Rendered Research Elo table with {len([n for n in state.get("ratings", {}) if int(n) in issues])} open rated issues.')


if __name__ == '__main__':
    main()
