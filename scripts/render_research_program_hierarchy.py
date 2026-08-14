#!/usr/bin/env python3

import json
import os
import re
import textwrap
import urllib.request
from collections import defaultdict
from html import escape
from pathlib import Path

MODEL_PATH = Path('.research-elo/idea-map.json')
STATE_PATH = Path('.research-elo/ratings.json')
PROGRAM_PATH = Path('assets/research-program.svg')
PROVISIONAL_GAMES = 10
NODE_WIDTH = 230
NODE_HEIGHT = 86
H_GAP = 52
V_GAP = 105
TOP_MARGIN = 120
SIDE_MARGIN = 55
BOTTOM_MARGIN = 80
RELATION_COLORS = {
    'subquestion': '#2563eb',
    'method': '#7c3aed',
    'testbed': '#059669',
    'alternative': '#dc2626',
}


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


def label_lines(title, width=30, max_lines=2):
    cleaned = re.sub(r'^\[Idea\]\s*', '', title or '', flags=re.I)
    return textwrap.wrap(cleaned, width=width)[:max_lines] or ['Untitled']


def load_ratings():
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding='utf-8')).get('ratings', {})


def subquestion_depths(issue_numbers, relations):
    parents = defaultdict(list)
    for rel in relations:
        if rel.get('type') == 'subquestion':
            parents[int(rel['target'])].append(int(rel['source']))

    memo = {}
    visiting = set()

    def depth(node):
        if node in memo:
            return memo[node]
        if node in visiting:
            return 0
        visiting.add(node)
        candidate_parents = [p for p in parents.get(node, []) if p in issue_numbers]
        value = 0 if not candidate_parents else 1 + max(depth(parent) for parent in candidate_parents)
        visiting.remove(node)
        memo[node] = value
        return value

    return {node: depth(node) for node in issue_numbers}


def hierarchy_levels(issue_numbers, relations):
    levels = subquestion_depths(issue_numbers, relations)

    # Methods and testbeds should visually sit below the research question they serve.
    # Repeating a few times lets short chains settle without changing relation inference.
    for _ in range(len(issue_numbers)):
        changed = False
        for rel in relations:
            if rel.get('type') not in {'method', 'testbed'}:
                continue
            source, target = int(rel['source']), int(rel['target'])
            if source not in levels or target not in levels:
                continue
            desired = levels[source] + 1
            if levels[target] < desired:
                levels[target] = desired
                changed = True
        if not changed:
            break

    connected = set()
    for rel in relations:
        connected.add(int(rel['source']))
        connected.add(int(rel['target']))
    if connected:
        isolated_level = max(levels[n] for n in connected if n in levels) + 1
        for node in issue_numbers:
            if node not in connected:
                levels[node] = isolated_level
    return levels


def ordered_layers(issue_numbers, relations, levels):
    layers = defaultdict(list)
    for node in issue_numbers:
        layers[levels[node]].append(node)

    parents = defaultdict(list)
    for rel in relations:
        if rel.get('type') in {'subquestion', 'method', 'testbed'}:
            parents[int(rel['target'])].append(int(rel['source']))

    ordered = {}
    previous_rank = {}
    for level in sorted(layers):
        nodes = layers[level]
        if not previous_rank:
            nodes = sorted(nodes)
        else:
            def key(node):
                ranks = [previous_rank[p] for p in parents.get(node, []) if p in previous_rank]
                barycenter = sum(ranks) / len(ranks) if ranks else 10_000 + node
                return (barycenter, node)
            nodes = sorted(nodes, key=key)
        ordered[level] = nodes
        previous_rank.update({node: idx for idx, node in enumerate(nodes)})
    return ordered


def layout(issue_numbers, relations):
    levels = hierarchy_levels(issue_numbers, relations)
    layers = ordered_layers(issue_numbers, relations, levels)
    max_per_layer = max((len(nodes) for nodes in layers.values()), default=1)
    width = max(1200, SIDE_MARGIN * 2 + max_per_layer * NODE_WIDTH + max(0, max_per_layer - 1) * H_GAP)
    max_level = max(layers, default=0)
    height = TOP_MARGIN + (max_level + 1) * NODE_HEIGHT + max_level * V_GAP + BOTTOM_MARGIN

    positions = {}
    for level, nodes in layers.items():
        row_width = len(nodes) * NODE_WIDTH + max(0, len(nodes) - 1) * H_GAP
        start_x = (width - row_width) / 2 + NODE_WIDTH / 2
        y = TOP_MARGIN + NODE_HEIGHT / 2 + level * (NODE_HEIGHT + V_GAP)
        for idx, node in enumerate(nodes):
            positions[node] = (start_x + idx * (NODE_WIDTH + H_GAP), y)
    return width, height, positions, levels, layers


def edge_path(source_xy, target_xy, rtype):
    x1, y1 = source_xy
    x2, y2 = target_xy
    if abs(y2 - y1) < 20:
        start_x = x1 + (NODE_WIDTH / 2 if x2 >= x1 else -NODE_WIDTH / 2)
        end_x = x2 - (NODE_WIDTH / 2 if x2 >= x1 else -NODE_WIDTH / 2)
        return f'M {start_x:.1f} {y1:.1f} L {end_x:.1f} {y2:.1f}', ((start_x + end_x) / 2, y1 - 10)

    start_y = y1 + NODE_HEIGHT / 2
    end_y = y2 - NODE_HEIGHT / 2
    mid_y = (start_y + end_y) / 2
    path = f'M {x1:.1f} {start_y:.1f} L {x1:.1f} {mid_y:.1f} L {x2:.1f} {mid_y:.1f} L {x2:.1f} {end_y:.1f}'
    label_y = mid_y - 8 if rtype != 'alternative' else mid_y + 14
    return path, ((x1 + x2) / 2, label_y)


def render():
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        raise RuntimeError('GITHUB_REPOSITORY is required')
    model = json.loads(MODEL_PATH.read_text(encoding='utf-8'))
    relations = [rel for rel in model.get('relations', []) if rel.get('type') in RELATION_COLORS]
    issue_numbers = {int(node['issue']) for node in model.get('nodes', [])}
    issues = fetch_open_owner_issues(repo)
    issue_numbers &= set(issues)
    ratings = load_ratings()

    width, height, positions, levels, layers = layout(issue_numbers, relations)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="40" y="48" font-family="Arial, sans-serif" font-size="27" font-weight="700" fill="#111827">Research Program Graph</text>',
        '<text x="40" y="76" font-family="Arial, sans-serif" font-size="14" fill="#6b7280">Hierarchical layout only; relation inference is unchanged. Broader questions are placed above derived questions, methods, and testbeds.</text>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="context-stroke"/></marker></defs>',
    ]

    for level, nodes in sorted(layers.items()):
        if not nodes:
            continue
        y = positions[nodes[0]][1]
        label = 'Broader / parent questions' if level == 0 else f'Program layer {level + 1}'
        out.append(f'<text x="24" y="{y - NODE_HEIGHT/2 - 18:.1f}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#94a3b8">{escape(label)}</text>')

    # Edges are drawn first so nodes sit on top of routing lines.
    for rel in relations:
        source, target = int(rel['source']), int(rel['target'])
        if source not in positions or target not in positions:
            continue
        rtype = rel['type']
        color = RELATION_COLORS[rtype]
        path, (lx, ly) = edge_path(positions[source], positions[target], rtype)
        dash = ' stroke-dasharray="7 5"' if rtype == 'alternative' else ''
        out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.2" opacity="0.72" marker-end="url(#arrow)"{dash}/>')
        label_width = max(76, 10 + len(rtype) * 7)
        out.append(f'<rect x="{lx-label_width/2:.1f}" y="{ly-11:.1f}" width="{label_width}" height="19" rx="8" fill="#ffffff" opacity="0.94"/>')
        out.append(f'<text x="{lx:.1f}" y="{ly+3:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="{color}">{escape(rtype)}</text>')

    for issue in sorted(issue_numbers, key=lambda n: (levels[n], positions[n][0])):
        x, y = positions[issue]
        entry = ratings.get(str(issue), {})
        rating = round(float(entry.get('rating', 1500)))
        games = int(entry.get('games', 0))
        dash = ' stroke-dasharray="6 4"' if games < PROVISIONAL_GAMES else ''
        out.append(f'<a href="https://github.com/{escape(repo)}/issues/{issue}" target="_blank">')
        out.append(f'<rect x="{x-NODE_WIDTH/2:.1f}" y="{y-NODE_HEIGHT/2:.1f}" width="{NODE_WIDTH}" height="{NODE_HEIGHT}" rx="16" fill="#ffffff" stroke="#334155" stroke-width="2"{dash}/>')
        out.append(f'<text x="{x:.1f}" y="{y-17:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#111827">#{issue} · Elo {rating}</text>')
        for idx, line in enumerate(label_lines(issues[issue].get('title', ''))):
            out.append(f'<text x="{x:.1f}" y="{y+3+idx*15:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10.5" fill="#475569">{escape(line)}</text>')
        out.append('</a>')

    legend_y = height - 30
    x = 50
    for rtype in ['subquestion', 'method', 'testbed', 'alternative']:
        color = RELATION_COLORS[rtype]
        dash = ' stroke-dasharray="7 5"' if rtype == 'alternative' else ''
        out.append(f'<line x1="{x}" y1="{legend_y}" x2="{x+34}" y2="{legend_y}" stroke="{color}" stroke-width="3"{dash}/>')
        out.append(f'<text x="{x+42}" y="{legend_y+4}" font-family="Arial, sans-serif" font-size="11" fill="#334155">{rtype}</text>')
        x += 190

    out.append('</svg>')
    PROGRAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRAM_PATH.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'Rendered hierarchical Research Program Graph with {len(issue_numbers)} nodes and {len(relations)} typed relations.')


if __name__ == '__main__':
    render()
