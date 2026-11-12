#!/usr/bin/env python3
"""Resolve installed variants and optionally configure exact Codex skill paths.

Python 3.11+, standard library only. Never executes or copies external skills.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib

BEGIN = '# BEGIN toolkit-skill-routing-v1'
END = '# END toolkit-skill-routing-v1'
MARKER = '<!-- skill-routing-v1 -->'
NAMES = ('docx', 'pdf', 'pptx', 'xlsx', 'skill-creator')
RADARS = ('content-radar', 'github-stars-radar', 'threads-bookmarks-radar', 'x-bookmarks-radar')
REQUIRED = {
    'docx': ('scripts/comment.py', 'scripts/merge_runs.py', 'scripts/accept_changes.py', 'scripts/office/validate.py'),
    'pdf': ('FORMS.md', 'REFERENCE.md'),
    'pptx': ('scripts/add_slide.py', 'scripts/clean.py', 'scripts/office/validate.py'),
    'xlsx': ('scripts/recalc.py',),
    'skill-creator': ('scripts/run_eval.py', 'eval-viewer/generate_review.py'),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(entry: Path, repair_harness: bool = False) -> dict[str, str]:
    result = {}
    for path in sorted(entry.parent.rglob('*')):
        if '__pycache__' in path.parts or path.name.startswith('._') or path.name == '.DS_Store':
            continue
        if path.is_symlink():
            raise ValueError(f'Variant resource is a symlink: {path}')
        if not path.is_file():
            continue
        rel = path.relative_to(entry.parent).as_posix()
        if rel.startswith('variants/'):
            continue  # Added routing snapshots are not part of the base implementation.
        if path.suffix in ('.pyc', '.pyo'):
            continue
        data = path.read_bytes()
        if path == entry:
            rel = 'SKILL.md'
            text = data.decode('utf-8-sig').replace('\r\n', '\n')
            if repair_harness:
                text = text.replace('Codex／Codex', 'Claude／Codex')
                text = text.replace('references/Codex-codex.md', 'references/claude-codex.md')
                text = text.replace('`AGENTS.md`、`AGENTS.md`', '`AGENTS.md`、`CLAUDE.md`')
            data = text.encode('utf-8')
        result[rel] = digest(data)
    return result


def resolve(home: Path, name: str) -> dict:
    if name not in NAMES:
        raise ValueError('Unsupported variant name')
    base = home / '.agents/skills'
    candidates = sorted((base / 'synced').glob(f'*/{name}/SKILL.md'))
    candidates = [p for p in candidates if not any(part.startswith('.') for part in p.relative_to(base/'synced').parts)]
    if not candidates:
        fallback = (base / 'skill-toolkit/variants/evaluation/WORKFLOW.md' if name == 'skill-creator'
                    else base / name / 'variants/synced/WORKFLOW.md')
        if fallback.is_file():
            candidates = [fallback]
    signatures = {}
    for path in candidates:
        text = path.read_text(encoding='utf-8-sig')
        if not re.search(r'^name:\s*[\"\x27]?' + re.escape(name) + r'[\"\x27]?\s*$', text, re.M):
            continue
        if not all((path.parent / required).is_file() for required in REQUIRED[name]):
            continue
        signatures[str(path)] = inventory(path)
    unique = {json.dumps(v, sort_keys=True) for v in signatures.values()}
    status = 'available' if len(unique) == 1 else ('ambiguous' if unique else 'unavailable')
    result = {'status': status, 'skill': name, 'candidates': list(signatures)}
    if status == 'available':
        result['entry'] = next(iter(signatures))
        result['fingerprint'] = digest(next(iter(unique)).encode())
    return result


def routed(entry: Path) -> bool:
    return entry.is_file() and MARKER in entry.read_text(encoding='utf-8-sig')


def plan(home: Path) -> dict:
    base = home / '.agents/skills'
    selected, skipped = [], []
    toolkit = base / 'skill-toolkit/SKILL.md'
    helper = base / 'skill-toolkit/scripts/skill_routes.py'
    if not routed(toolkit) or not helper.is_file():
        return {'planned': [], 'skipped': ['Install this release of skill-toolkit first']}
    for name in NAMES:
        primary = toolkit if name == 'skill-creator' else base/name/'SKILL.md'
        resolved = resolve(home, name)
        if routed(primary) and resolved['status'] == 'available':
            selected += [p for p in resolved['candidates'] if Path(p).name == 'SKILL.md']
        elif resolved['candidates']:
            skipped.append(f'{name}: primary not routed or variants ambiguous')
    # The toolkit explicitly reads this source, including all of its local customizations.
    original_creator = base/'skill-creator/SKILL.md'
    system_creator = home/'.codex/skills/.system/skill-creator/SKILL.md'
    if original_creator.is_file() and system_creator.is_file():
        selected.append(str(original_creator))
    else:
        skipped.append('skill-creator: keep original when bundled creator is unavailable')
    for name in ('harness-purge', 'local-dual-model'):
        primary, other = base/name/'SKILL.md', home/'.codex/skills'/name/'SKILL.md'
        if primary.is_file() and other.is_file():
            if inventory(primary, name == 'harness-purge') == inventory(other, name == 'harness-purge'):
                # A broken primary must not suppress the usable alternative.
                if name == 'harness-purge' and not (primary.parent/'references/claude-codex.md').is_file():
                    skipped.append('harness-purge: primary reference missing')
                elif 'references/Codex-codex.md' in primary.read_text(encoding='utf-8-sig'):
                    skipped.append('harness-purge: repair primary before disabling duplicate')
                else:
                    selected.append(str(other))
            else:
                skipped.append(f'{name}: distinct local resources preserved')
    for name in RADARS:
        primary = base/name/'SKILL.md'
        if not primary.is_file():
            continue
        legacy = primary.parent/'variants/legacy/WORKFLOW.md'
        roots = [primary]
        if routed(primary) and legacy.is_file():
            roots.append(legacy)
        for other in sorted((home/'.codex/plugins/cache').glob(f'*/second-brain-radar/*/skills/{name}/SKILL.md')):
            if any(inventory(p) == inventory(other) for p in roots):
                selected.append(str(other))
            else:
                skipped.append(f'{name}: plugin version differs; retained {other}')
    return {'planned': sorted(set(selected)), 'skipped': skipped}


def rewrite(raw: str, paths: list[str]) -> str:
    if raw.count(BEGIN) != raw.count(END) or raw.count(BEGIN) > 1:
        raise ValueError('Malformed managed config markers')
    block = BEGIN + '\n'
    for path in paths:
        block += '\n[[skills.config]]\npath = ' + json.dumps(Path(path).as_posix()) + '\nenabled = false\n'
    block += '\n' + END
    if BEGIN in raw:
        start, end = raw.index(BEGIN), raw.index(END) + len(END)
        if start >= end:
            raise ValueError('Reversed config markers')
        updated = raw[:start] + block + raw[end:]
    elif paths:
        updated = raw + ('\n' if raw else '') + block + '\n'
    else:
        updated = raw
    tomllib.loads(updated)
    return updated


def configure(home: Path, apply: bool = False) -> dict:
    home = home.resolve()
    config = home/'.codex/config.toml'
    # The mutation target must remain inside the explicitly selected home.
    for p in (config, config.parent, config.parent/'skills-backups'):
        if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
            raise ValueError(f'Refusing redirected config/backup target: {p}')
        if not p.resolve().is_relative_to(home):
            raise ValueError('Config target escaped selected home')
    before = config.read_bytes() if config.exists() else None
    raw = before.decode('utf-8-sig') if before is not None else ''
    snapshot = plan(home)
    watched = {}
    for path in snapshot['planned']:
        watched[path] = inventory(Path(path))
    result = dict(snapshot)
    updated = rewrite(raw, result['planned'])
    result['mode'] = 'apply' if apply else 'dry-run'
    if not apply or updated == raw:
        result['changed'] = False
        return result
    # Re-evaluate discovered sources immediately before changing config.
    if plan(home) != snapshot or any(inventory(Path(path)) != value for path, value in watched.items()):
        raise ValueError('Installed variants changed; rerun dry-run')
    if (config.read_bytes() if config.exists() else None) != before:
        raise ValueError('Config changed; rerun dry-run')
    config.parent.mkdir(parents=True, exist_ok=True)
    if before is not None:
        backup_dir = config.parent/'skills-backups'
        backup_dir.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = backup_dir/f'config-routing-{stamp}.toml'
        descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'wb') as f:
            f.write(before)
        result['backup'] = str(backup)
    fd, temporary = tempfile.mkstemp(prefix='skill-routing-', suffix='.toml', dir=config.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(updated.encode('utf-8'))
        if (config.read_bytes() if config.exists() else None) != before:
            raise ValueError('Config changed before replace; stopped')
        os.replace(temporary, config)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)  # Exactly the file allocated by mkstemp above.
    assert tomllib.loads(config.read_text(encoding='utf-8')) == tomllib.loads(updated)
    result['changed'] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    res = sub.add_parser('resolve')
    res.add_argument('--kind', choices=['synced'], required=True)
    res.add_argument('--skill', choices=NAMES, required=True)
    res.add_argument('--home', type=Path, default=Path.home())
    config = sub.add_parser('configure')
    config.add_argument('--home', type=Path, default=Path.home())
    config.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = resolve(args.home, args.skill) if args.command == 'resolve' else configure(args.home, args.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(result.get('status') in ('ambiguous', 'unavailable'))
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
