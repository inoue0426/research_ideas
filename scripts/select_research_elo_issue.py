#!/usr/bin/env python3

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path('.research-elo/ratings.json')


def github_request(path):
    token = os.environ['GITHUB_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']
    req = urllib.request.Request(f'https://api.github.com{path}')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_open_owner_issues():
    repo = os.environ['GITHUB_REPOSITORY']
    owner = repo.split('/', 1)[0]
    issues = []
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
            issues.append(item)
        if len(batch) < 100:
            break
        page += 1
    return issues


def load_state():
    if not STATE_PATH.exists():
        return {'ratings': {}, 'history': []}
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def main():
    issues = fetch_open_owner_issues()
    if not issues:
        raise RuntimeError('No open owner-authored issues found.')

    state = load_state()
    ratings = state.get('ratings', {})
    history = state.get('history', [])

    last_target = {}
    for event in history:
        try:
            target = int(event.get('target'))
            ts = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        except (TypeError, ValueError, KeyError):
            continue
        if target not in last_target or ts > last_target[target]:
            last_target[target] = ts

    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def priority(issue):
        number = int(issue['number'])
        entry = ratings.get(str(number), {})
        games = int(entry.get('games', 0))
        # Unrated/least-played ideas first, then the one least recently used as target.
        return (games, last_target.get(number, epoch), number)

    selected = min(issues, key=priority)
    print(selected['number'])


if __name__ == '__main__':
    main()
