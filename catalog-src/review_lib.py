#!/usr/bin/env python3
"""Shared helpers for the review loop: index, chunk files, paths."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REV = HERE + '/data/review'
CHUNK_MAX = 18
CHUNK_BYTES = 95000


def load(path, default=None):
    try:
        return json.load(open(path))
    except Exception:  # noqa: BLE001
        return default


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=1, ensure_ascii=False)


def one_line(s, n):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def write_index(items, k):
    """One line per item, so a reviewer can see the whole catalog at once."""
    lines = [f'# Catalog index after round {k}: {len(items)} items',
             'Columns: id | tier | section | wave | readiness | risk | value/5 | effort | name: description [includes]', '']
    for it in items:
        inc = ''
        if it.get('includes'):
            inc = ' [includes ' + ', '.join(m['id'] for m in it['includes']) + ']'
        lines.append(f"{it['id']} | T{it['tier']} | {it['section']} | {it.get('wave')} | {it.get('readiness')} | "
                     f"{it.get('risk')} | {it.get('value')} | {it.get('effort')} | {it['name']}: "
                     f"{one_line(it.get('description'), 220)}{inc}")
    open(f'{REV}/r{k}.index.md', 'w').write('\n'.join(lines) + '\n')


def write_chunks(items, k):
    """Chunks of at most CHUNK_MAX items and about CHUNK_BYTES of JSON, in catalog order."""
    for old in os.listdir(REV):
        if re.match(rf'^r{k}\.chunk-\d+\.json$', old):
            os.remove(f'{REV}/{old}')
    chunks, cur, size = [], [], 0
    for it in items:
        n = len(json.dumps(it, ensure_ascii=False))
        if cur and (len(cur) >= CHUNK_MAX or size + n > CHUNK_BYTES):
            chunks.append(cur)
            cur, size = [], 0
        cur.append(it)
        size += n
    if cur:
        chunks.append(cur)
    if len(chunks) > 1 and len(chunks[-1]) < 5:
        chunks[-2].extend(chunks.pop())
    for i, ch in enumerate(chunks, 1):
        dump(ch, f'{REV}/r{k}.chunk-{i}.json')
    return len(chunks)
