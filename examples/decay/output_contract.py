# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Bounded reference harness, not a production discovery service or editor.

Pure metadata/argv interpretation is separate from local launch filesystem checks.
The 16 KiB document limit is deliberately narrower than SWSS. See VALIDATION.md.
"""
import hashlib
import math
import os
from pathlib import Path
import re
import stat
import tomllib

ID = r'[a-z][a-z0-9_]{0,63}'
ALIAS = r'(?:--[A-Za-z][A-Za-z0-9_-]*|-[A-Za-z])'
INTEGER = r'[+-]?[0-9]+'
FLOAT = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_path(value, parent=False):
    require(isinstance(value, str) and 0 < len(value.encode()) <= 1024, 'invalid path size/type')
    require(not any(c in value for c in '\\:~$*?[]') and
            not any(ord(c) < 32 or ord(c) == 127 for c in value), 'unsafe portable path')
    require(all(p not in ('', '.', '..') for p in value.split('/')), 'unsafe path components')
    return value


def scalar(value, kind):
    expected = {'string': str, 'integer': int, 'float': float, 'boolean': bool}.get(kind)
    return type(value) is expected and (kind != 'integer' or -(2**63) <= value < 2**63) and (
        kind != 'float' or math.isfinite(value))


def parse(metadata, supported=(2, 3)):
    """Parse supplied bytes only; filesystem association/binding is separate."""
    require(len(metadata) <= 16384, 'reference document limit: 16 KiB; manual-only')
    try:
        doc = tomllib.loads(metadata.decode('utf-8'))
    except (RecursionError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError('invalid/beyond reference parser capacity') from error
    count = 0
    def bounds(value, depth=1, multiline=False):
        nonlocal count
        require(depth <= 8, 'depth limit')
        if isinstance(value, dict):
            count += len(value)
            for k, v in value.items():
                bounds(k, depth, False)
                bounds(v, depth + isinstance(v, (list, dict)), multiline or k in ('help', 'extensions'))
        elif isinstance(value, list):
            count += len(value)
            for v in value:
                bounds(v, depth + isinstance(v, (list, dict)), multiline)
        elif isinstance(value, str):
            require(len(value.encode()) <= 4096 and not any(
                (ord(c) < 32 or ord(c) == 127) and not (multiline and c in '\n\t') for c in value), 'string safety limit')
        elif isinstance(value, float):
            require(math.isfinite(value), 'nonfinite metadata')
        require(count <= 4096, 'entry limit')
    bounds(doc)
    require(set(doc) <= {'swss', 'extensions'} and isinstance(doc.get('swss'), dict), 'invalid root tables')
    extensions = doc.get('extensions', {})
    require(isinstance(extensions, dict) and all(re.fullmatch(r'[a-z][a-z0-9_-]{0,63}', k)
            and isinstance(v, dict) for k, v in extensions.items()), 'invalid extensions')
    s = doc['swss']
    schema = s.get('schema_version')
    require(type(schema) is int and schema in supported, 'unsupported schema; manual-only')
    allowed = {'schema_version', 'entrypoint', 'simulation_version', 'parameters', 'source_files'}
    if schema == 3:
        allowed |= {'output_parent', 'output_parent_parameter'}
    require(set(s) <= allowed, 'unknown swss field')
    relative_path(s.get('entrypoint'))
    require(isinstance(s.get('simulation_version'), str) and bool(s['simulation_version']), 'invalid version')
    rows = s.get('parameters', [])
    require(isinstance(rows, list) and len(rows) <= 128, 'invalid parameters')
    ids, aliases, manual = {}, set(), set()
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('id'), str) and
                re.fullmatch(ID, row['id']) and row['id'] not in ids, 'invalid/duplicate parameter ID')
        # Nested/date values inside portable rows are document failures, unlike
        # ordinary scalar type mistakes, which leave an unrelated row manual.
        for key, value in row.items():
            require(type(value) in (str, int, float, bool, list), 'unsupported portable value')
            if isinstance(value, list):
                require(key in ('options', 'choices') and all(type(v) in (str, int, float, bool) for v in value), 'unsupported nested row value')
        ids[row['id']] = row
        if row.get('kind') == 'positional':
            require(isinstance(row.get('name'), str) and re.fullmatch(ID, row['name']), 'invalid positional name')
        else:
            opts = row.get('options')
            require(isinstance(opts, list) and 1 <= len(opts) <= 8, 'invalid aliases')
            for opt in opts:
                require(isinstance(opt, str) and len(opt.encode()) <= 128 and re.fullmatch(ALIAS, opt)
                        and opt not in aliases, 'invalid/duplicate alias')
                aliases.add(opt)
        choices = row.get('choices')
        if choices is not None:
            require(not isinstance(choices, list) or len(choices) <= 100, 'choice limit')
        valid = (set(row) <= {'id', 'kind', 'options', 'name', 'required', 'type', 'action', 'help', 'choices', 'default', 'repeatable'}
                 and row.get('kind') == 'option' and 'name' not in row
                 and type(row.get('required')) is bool and isinstance(row.get('help'), str)
                 and type(row.get('repeatable', False)) is bool and not row.get('repeatable', False)
                 and ((row.get('type') in ('string', 'integer', 'float') and row.get('action') == 'store')
                      or (row.get('type') == 'boolean' and row.get('action') in ('store_true', 'store_false'))))
        valid = valid and ('default' not in row or scalar(row['default'], row['type']))
        if choices is not None:
            valid = valid and (isinstance(choices, list) and bool(choices) and row['type'] != 'boolean'
                    and all(scalar(v, row['type']) for v in choices)
                    and len({(type(v), v) for v in choices}) == len(choices)
                    and ('default' not in row or row['default'] in choices))
        if not valid:
            manual.add(row['id'])
    if 'source_files' in s:
        files = s['source_files']
        require(isinstance(files, list) and len(files) <= 32, 'source manifest limit')
        paths = set()
        for f in files:
            require(isinstance(f, dict) and set(f) == {'path', 'sha256'}, 'invalid source row')
            relative_path(f['path'])
            require(f['path'] not in paths and isinstance(f['sha256'], str) and
                    re.fullmatch('[a-f0-9]{64}', f['sha256']), 'invalid source binding')
            paths.add(f['path'])
        require(s['entrypoint'] in paths, 'manifest must include entrypoint')
    if schema == 3:
        relative_path(s.get('output_parent', 'outputs'), parent=True)
        if 'output_parent_parameter' in s:
            key = s['output_parent_parameter']
            require(isinstance(key, str) and re.fullmatch(ID, key) and key in ids and key not in manual, 'invalid output binding')
            row = ids[key]
            require(row['type'] == 'string' and row['action'] == 'store' and not row['required']
                    and 'choices' not in row, 'ineligible output binding')
            require('default' not in row or row['default'] == s.get('output_parent', 'outputs'), 'output default mismatch')
    return s, manual


def runtime_path(root, value):
    require(isinstance(value, str) and value != '' and not any(ord(c) < 32 or ord(c) == 127 for c in value), 'empty/control path')
    require('..' not in value.split('/') and ':' not in value and '\\' not in value, 'traversal/URI/unsupported path')
    # Literal ~, $, and wildcard characters are not expanded.
    p = Path(value)
    return p if p.is_absolute() else Path(root) / p


def resolve_parent(metadata, argv, root, entrypoint, sources=None, local=None, supported=(2, 3)):
    """Pure discovery over caller-supplied bytes; never probe an external path.

    Call afresh for each preview/use. No cached destination is reused. The caller
    retains the exact bytes/argv and performs safe reads and launch checks.
    """
    require(Path(root).is_absolute() and '..' not in Path(root).parts, 'explicit absolute root required')
    require(all(isinstance(t, str) for t in argv), 'argv must contain strings')
    s, manual = parse(metadata, supported)
    require(s['entrypoint'] == entrypoint, 'entrypoint mismatch')
    binding = 'unverified'
    total = 0
    for f in s.get('source_files', []):
        data = (sources or {}).get(f['path'])
        require(data is not None and len(data) <= 16 * 1024**2, 'missing/over-budget source binding')
        total += len(data)
        require(total <= 64 * 1024**2 and hashlib.sha256(data).hexdigest() == f['sha256'], 'stale/over-budget source binding')
        binding = 'listed bytes match; behavior unverified'
    require(s['schema_version'] == 3, 'schema 2 has no automatic output semantics')
    rows = {alias: row for row in s.get('parameters', []) for alias in row.get('options', [])}
    seen, spans = set(), []
    value, origin = s.get('output_parent', 'outputs'), 'metadata' if 'output_parent' in s else 'schema-3 default'
    i = 0
    while i < len(argv):
        start = i
        token = argv[i]
        if token == '--' and i == len(argv) - 1:
            break
        alias, eq, supplied = token.partition('=') if token.startswith('--') else (token, '', '')
        require(alias in rows, 'unknown/manual token; automatic routing unavailable')
        row = rows[alias]
        require(row['id'] not in manual and row['id'] not in seen, 'manual/repeated control')
        seen.add(row['id'])
        if row['action'] == 'store':
            if not eq:
                i += 1
                require(i < len(argv), 'missing value')
                supplied = argv[i]
                require(not supplied.startswith('-') or (row['type'] in ('integer', 'float') and
                        re.fullmatch(INTEGER if row['type'] == 'integer' else FLOAT, supplied)), 'ambiguous option-looking value')
            parsed = supplied
            if row['type'] in ('integer', 'float'):
                require(re.fullmatch(INTEGER if row['type'] == 'integer' else FLOAT, supplied), 'invalid numeric token')
                parsed = int(supplied) if row['type'] == 'integer' else float(supplied)
                require(scalar(parsed, row['type']), 'numeric bounds')
            require('choices' not in row or parsed in row['choices'], 'invalid choice')
            if row['id'] == s.get('output_parent_parameter'):
                require(bool(supplied), 'empty output override')
                value, origin = supplied, 'bound CLI'
                spans.append([start, i + 1])
        else:
            require(not eq, 'flag cannot take value')
        i += 1
    parent = runtime_path(root, value)
    if local is not None:
        require(os.path.normpath(str(parent)) == os.path.normpath(str(runtime_path(root, local))), 'local destination conflict')
    return {'parent': str(parent), 'origin': origin, 'binding': binding,
            'binding_id': s.get('output_parent_parameter'), 'token_spans': spans,
            'schema_version': 3, 'metadata_sha256': hashlib.sha256(metadata).hexdigest(),
            'argv': list(argv), 'entrypoint': entrypoint, 'root': str(root)}


def identities(path):
    """Inspect existing ancestors without following symlinks; absent tails allowed."""
    p = Path(path)
    require(p.is_absolute(), 'selected root/path must be absolute')
    result = {}
    for part in [*reversed(p.parents), p]:
        try:
            st = part.lstat()
        except FileNotFoundError:
            break
        require(not stat.S_ISLNK(st.st_mode), 'symlink component')
        require(stat.S_ISDIR(st.st_mode), 'non-directory component')
        result[part] = (st.st_dev, st.st_ino)
    return result


def recheck(expected):
    for path, identity in expected.items():
        st = path.lstat()
        require(stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode) and
                (st.st_dev, st.st_ino) == identity, 'path identity changed')


def validate_parent(root, parent, protected):
    root, parent = Path(root), Path(parent)
    require(root.is_absolute() and parent.is_absolute() and '..' not in root.parts and '..' not in parent.parts, 'absolute traversal-free boundaries required')
    identity = identities(parent)
    require(not root.is_relative_to(parent), 'output parent contains selected root')
    for source in protected:
        source = Path(source)
        require(not source.is_relative_to(parent) and not parent.is_relative_to(source), 'output/source overlap')
    return identity


def read_source(path, limit=16 * 1024**2):
    """Bounded regular-file read with ancestor and open-file identity checks."""
    path = Path(path)
    guards = identities(path.parent)
    recheck(guards)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= limit, 'unsafe/oversized source')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        require((before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino), 'source identity changed')
        recheck(guards)
        data = stream.read(limit + 1)
    require(len(data) <= limit, 'source grew beyond limit')
    return data


def snapshot(root, parents, protected):
    """Small fixture snapshot; exclusions are established before file reads.

    No aliases followed. No process isolation or hostile-filesystem guarantee.
    """
    root = Path(root)
    guards = identities(root)
    boundaries = [Path(p) for p in parents]
    for parent in boundaries:
        guards.update(validate_parent(root, parent, protected))
    recheck(guards)
    result = {}
    total = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if not any((Path(directory) / d).is_relative_to(p) for p in boundaries)]
        for name in dirs + files:
            path = Path(directory) / name
            require(not path.is_symlink(), 'source alias refused')
        for name in files:
            path = Path(directory) / name
            recheck(guards)
            data = read_source(path)
            total += len(data)
            require(total <= 64 * 1024**2, 'snapshot byte budget')
            result[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
    return result
