#!/usr/bin/env python3

import json
from pathlib import Path

README_PATH = Path('README.md')
MODEL_PATH = Path('.research-elo/idea-map.json')
START_MARKER = '<!-- RESEARCH_MAPS_START -->'
END_MARKER = '<!-- RESEARCH_MAPS_END -->'
PAGES_ROOT = 'https://inoue0426.github.io/research_ideas/'


def main():
    model = json.loads(MODEL_PATH.read_text(encoding='utf-8')) if MODEL_PATH.exists() else {}
    themes = ', '.join(str(t.get('label', t.get('id', ''))) for t in model.get('themes', []))
    relations = len(model.get('relations', []))

    section = '\n'.join([
        START_MARKER,
        '## Research Maps',
        '',
        'A compact overview is kept here; the full exploration views live on GitHub Pages.',
        '',
        f'- 🗺️ [Idea Landscape]({PAGES_ROOT}idea_landscape.html) — semantic similarity and theme clusters',
        f'- 🧭 [Research Program Graph]({PAGES_ROOT}research_programs.html) — typed research relationships',
        '',
        f'<a href="{PAGES_ROOT}idea_landscape.html"><img src="assets/idea-landscape.svg" alt="Idea Landscape overview" width="720"></a>',
        '',
        f'_Current themes: {themes}. Typed program relations: {relations}. Maps are organizational aids, not measures of scientific importance._',
        END_MARKER,
    ])

    readme = README_PATH.read_text(encoding='utf-8')
    if START_MARKER in readme and END_MARKER in readme:
        start = readme.index(START_MARKER)
        end = readme.index(END_MARKER) + len(END_MARKER)
        readme = readme[:start] + section + readme[end:]
    else:
        anchor = '<!-- RESEARCH_ELO_END -->'
        if anchor in readme:
            readme = readme.replace(anchor, anchor + '\n\n' + section, 1)
        else:
            readme = readme.rstrip() + '\n\n' + section + '\n'
    README_PATH.write_text(readme, encoding='utf-8')


if __name__ == '__main__':
    main()
