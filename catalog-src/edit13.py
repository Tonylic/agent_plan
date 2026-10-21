#!/usr/bin/env python3
"""Helpers for the hand edits of 13 Oct 2026 (Tony's helper pattern, and the wave A runbook's findings).

Cards:  every edit lives in data/review/r13.owner.json as a full new field value ("set"), on top of r12.json.
        c = Cards(); e = c.edit('G015'); c.sub(e, 'how', old, new); c.add(e, 'unverified', text); c.save()
        then:  python3 apply_owner.py 13
Waves:  data/review/waves/final.json is edited in place (the state before 13 Oct is final.pre-13oct.json).
        w = Waves(); w.rep('A', old, new); w.save()
Rebuild: python3 finalize_review.py && python3 frame.py && python3 render.py local > ../home-agent-capability-catalog.html
"""
import json

from review_lib import REV, dump, load


class Cards:
    def __init__(self):
        self.base = {it['id']: it for it in load(f'{REV}/r12.json')}
        self.spec = load(f'{REV}/r13.owner.json')
        self.by = {e['id']: e for e in self.spec['edits']}

    def edit(self, cid, note=None):
        e = self.by.get(cid)
        if e is None:
            assert note, f'{cid}: a new edit needs a note'
            e = {'id': cid, 'note': note, 'set': {}}
            self.spec['edits'].append(e)
            self.by[cid] = e
        return e

    def cur(self, e, field):
        return e['set'].get(field, self.base[e['id']].get(field))

    def sub(self, e, field, old, new):
        cur = self.cur(e, field)
        if isinstance(cur, str):
            assert cur.count(old) == 1, (e['id'], field, cur.count(old), old[:70])
            e['set'][field] = cur.replace(old, new)
        else:
            cur = list(cur)
            hits = [n for n, x in enumerate(cur) if old in x]
            assert len(hits) == 1, (e['id'], field, hits, old[:70])
            cur[hits[0]] = cur[hits[0]].replace(old, new)
            e['set'][field] = cur

    def add(self, e, field, text):
        cur = list(self.cur(e, field) or [])
        cur.append(text)
        e['set'][field] = cur

    def save(self):
        json.dump(self.spec, open(f'{REV}/r13.owner.json', 'w'), indent=1, ensure_ascii=False)


def _strings(obj, path=()):
    if isinstance(obj, str):
        yield path
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            yield from _strings(x, path + (i,))
    elif isinstance(obj, dict):
        for k, x in obj.items():
            yield from _strings(x, path + (k,))


def _get(obj, path):
    for k in path:
        obj = obj[k]
    return obj


def _set(obj, path, val):
    for k in path[:-1]:
        obj = obj[k]
    obj[path[-1]] = val


class Waves:
    PATH = f'{REV}/waves/final.json'

    def __init__(self):
        self.w = load(self.PATH)
        self.by = {x['wave']: x for x in self.w['waves']}

    def rep(self, wave, old, new, count=1):
        """Replace `old` inside one wave ('A'..'J') or inside the notes ('notes'); it must occur `count` times."""
        root = self.w['notes'] if wave == 'notes' else self.by[wave]
        hits = [p for p in _strings(root) if old in _get(root, p)]
        tot = sum(_get(root, p).count(old) for p in hits)
        assert tot == count, (wave, tot, old[:80])
        for p in hits:
            _set(root, p, _get(root, p).replace(old, new))

    def save(self):
        dump(self.w, self.PATH)
