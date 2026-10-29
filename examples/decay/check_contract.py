# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Johnny Mongstad
"""Offline author check for this fixture's literal parser; not a SWSS consumer."""
import ast
import hashlib
import json
import sys
import tomllib
from pathlib import Path

from output_contract import parse

LIMIT = 65536  # Deliberately smaller author-tool limit, not an SWSS validity rule.


def source_contract(source):
    tree = ast.parse(source)
    version = next(ast.literal_eval(n.value) for n in tree.body
                   if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in n.targets))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build_parser')
    rows = []
    for statement in function.body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if not isinstance(call.func, ast.Attribute) or call.func.attr != 'add_argument':
            continue
        options = [ast.literal_eval(arg) for arg in call.args]
        kw = {k.arg: k.value.id if k.arg == 'type' and isinstance(k.value, ast.Name)
              else ast.literal_eval(k.value) for k in call.keywords}
        action = kw.get('action', 'store')
        kind = {'int': 'integer', 'float': 'float', 'str': 'string'}[kw.get('type', 'str')]
        if action in ('store_true', 'store_false'):
            kind = 'boolean'
        row = {'id': kw.get('dest', options[0][2:].replace('-', '_')), 'kind': 'option',
               'options': options, 'required': kw.get('required', False),
               'type': kind, 'action': action, 'help': kw['help']}
        if kw.get('default') is not None:
            row['default'] = kw['default']
        if 'choices' in kw:
            row['choices'] = kw['choices']
        rows.append(row)
    return version, rows


def compare(source, metadata, helper):
    """Compare bounded bytes; never import/execute the source being checked."""
    if any(len(data) > LIMIT for data in (source, metadata, helper)):
        raise ValueError('author check input exceeds 64 KiB')
    version, expected = source_contract(source)
    parse(metadata)
    document = tomllib.loads(metadata.decode('utf-8'))
    if set(document) != {'swss'}:
        raise ValueError('fixture uses only the swss root table')
    swss = document['swss']
    if set(swss) != {'schema_version', 'entrypoint', 'simulation_version', 'parameters', 'source_files', 'output_parent_parameter'}:
        raise ValueError('unexpected fixture header fields')
    if type(swss['schema_version']) is not int or swss['schema_version'] != 3:
        raise ValueError('schema version mismatch')
    if swss['entrypoint'] != 'simulate.py' or swss['simulation_version'] != version:
        raise ValueError('entrypoint/version mismatch')
    # JSON distinguishes 1, 1.0 and true, unlike ordinary Python equality.
    if json.dumps(swss['parameters'], sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('parser/metadata parameter mismatch')
    binding = [{'path': 'simulate.py', 'sha256': hashlib.sha256(source).hexdigest()}]
    binding.append({'path': 'output_contract.py', 'sha256': hashlib.sha256(helper).hexdigest()})
    if swss.get('output_parent_parameter') != 'output_parent':
        raise ValueError('output binding mismatch')
    if swss['source_files'] != binding:
        raise ValueError('stale source binding')
    return len(expected)


def check(root):
    def read(name):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('expected regular fixture file')
        with path.open('rb') as stream:
            return stream.read(LIMIT + 1)
    return compare(read('simulate.py'), read('swss.toml'), read('output_contract.py'))


if __name__ == '__main__':
    try:
        print(f'{check(Path(__file__).resolve().parent)} parameter declarations agree; source binding matches')
    except (ValueError, SyntaxError, KeyError, StopIteration, OSError) as error:
        sys.exit(f'contract check failed: {error}')
