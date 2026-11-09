#!/usr/bin/env python3
"""Multi-product binary distribution. Python standard library + GitHub CLI only."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = 'unzooai/awesome-unzoo'
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?')
RESERVED = {'SHA256SUMS.txt', 'release.json'}


def is_metadata(name):
    return name in RESERVED or bool(re.fullmatch(r'(?:release-[a-z0-9-]+\.json|SHA256SUMS-[a-z0-9-]+\.txt)', name))


def supplement_metadata(suffix):
    if not ID.fullmatch(suffix):
        raise ValueError('Supplement suffix must be an id such as macos')
    return f'release-{suffix}.json', f'SHA256SUMS-{suffix}.txt'


def validate_products(products):
    if not isinstance(products, list):
        raise ValueError('software.json must contain an array')
    ids = set()
    for product in products:
        key = product.get('id', '')
        if not isinstance(key, str) or not ID.fullmatch(key) or key in ids:
            raise ValueError(f'Invalid or duplicate software id: {key!r}')
        ids.add(key)


def load_products():
    products = json.loads((ROOT / 'software.json').read_text())
    validate_products(products)
    for product in products:
        for key in ('name', 'description', 'license'):
            if not isinstance(product.get(key), str) or not product[key].strip():
                raise ValueError(f'{product["id"]}: {key} must be nonempty text')
        if not isinstance(product.get('platforms'), list) or not product['platforms'] or not all(isinstance(p, str) and p.strip() for p in product['platforms']):
            raise ValueError(f'{product["id"]}: platforms must be a nonempty list of text')
    return products


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def plan_release(product_id, version, files):
    if not ID.fullmatch(product_id) or not VERSION.fullmatch(version):
        raise ValueError('Use an id such as my-app and a version such as 1.2.3 or 1.2.3-beta.1')
    if not files:
        raise ValueError('At least one installer is required')
    assets = []
    names = set(RESERVED)
    for item in files:
        path = Path(item).resolve()
        if not path.is_file() or not 0 < path.stat().st_size < 2 * 1024**3:
            raise ValueError(f'Asset must exist, be nonempty, and be smaller than 2 GiB: {path}')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+-]*', path.name) or path.name in names or is_metadata(path.name):
            raise ValueError(f'Unsafe, duplicate, or reserved asset filename: {path.name}')
        names.add(path.name)
        assets.append(dict(path=str(path), name=path.name, size=path.stat().st_size, sha256=digest(path)))
    return dict(software=product_id, version=version, tag=f'{product_id}/v{version}', assets=assets)


def gh(*args):
    command = ['gh', *map(str, args)]
    if args[0] != 'api':
        command.extend(['--repo', REPO])
    return subprocess.run(command, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def api(endpoint):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'awesome-unzoo-distribution'}
    if token := os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = f'Bearer {token}'
    with urlopen(Request('https://api.github.com' + endpoint, headers=headers), timeout=60) as response:
        return json.load(response)


def fetch_releases():
    releases = []
    page = 1
    while True:
        batch = api(f'/repos/{REPO}/releases?per_page=100&page={page}')
        releases.extend(batch)
        if len(batch) < 100:
            return releases
        page += 1


def build_catalog(products, releases):
    validate_products(products)
    result = []
    for product in products:
        item = dict(product, latest=None, preview=None)
        candidates = {'latest': [], 'preview': []}
        prefix = product['id'] + '/v'
        for release in releases:
            if release.get('draft') or not release.get('tag_name', '').startswith(prefix):
                continue
            version = release['tag_name'][len(prefix):]
            match = VERSION.fullmatch(version)
            assets = release.get('assets', [])
            if not match or not any(not is_metadata(a['name']) for a in assets):
                continue
            channel = 'preview' if release.get('prerelease') or match[4] else 'latest'
            value = dict(version=version, tag=release['tag_name'], url=release['html_url'],
                         published_at=release.get('published_at'),
                         assets=[{k: a.get(k) for k in ('name', 'size', 'browser_download_url', 'digest')} for a in assets])
            # Stable versions compare numerically; previews of the same base use publication time.
            key = (*map(int, match.group(1, 2, 3)), release.get('published_at') or '')
            candidates[channel].append((key, value))
        for channel, values in candidates.items():
            if values:
                item[channel] = max(values, key=lambda pair: pair[0])[1]
        result.append(item)
    return result


def cell(value):
    return html.escape(str(value), quote=True).replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')


def render_readme(content, catalog):
    start, end = '<!-- catalog:start -->', '<!-- catalog:end -->'
    if content.count(start) != 1 or content.count(end) != 1 or content.index(start) >= content.index(end):
        raise ValueError('README catalog markers must appear once, in order')
    lines = ['| 软件 | 简介 | 平台 | 稳定版 | 预览版 |', '| --- | --- | --- | --- | --- |']
    for product in catalog:
        links = []
        for channel in ('latest', 'preview'):
            release = product.get(channel)
            links.append(f'[{cell(release["version"])}]({release["url"]})' if release else '待发布')
        lines.append('| ' + ' | '.join([cell(product['name']), cell(product['description']),
                                       cell(' / '.join(product['platforms'])), *links]) + ' |')
    if not catalog:
        lines = ['尚未发布软件。首款软件发布后，这里会自动显示下载入口。']
    return content.split(start)[0] + start + '\n\n' + '\n'.join(lines) + '\n\n' + end + content.split(end)[1]


def sync(releases=None):
    catalog = build_catalog(load_products(), fetch_releases() if releases is None else releases)
    readme = ROOT / 'README.md'
    rendered = render_readme(readme.read_text(), catalog)
    (ROOT / 'catalog.json').write_text(json.dumps(dict(repository=REPO, software=catalog), ensure_ascii=False, indent=2) + '\n')
    readme.write_text(rendered)
    print(f'Updated catalog: {len(catalog)} software entries')


def publish(plan, name, notes, prerelease, draft, runner=gh):
    with tempfile.TemporaryDirectory(prefix='unzoo-release-') as tmp:
        stage = Path(tmp)
        for asset in plan['assets']:
            target = stage / asset['name']
            shutil.copyfile(asset['path'], target)
            if digest(target) != asset['sha256']:
                raise ValueError('Asset changed while staging; no release created')
        manifest = {k: v for k, v in plan.items() if k != 'assets'}
        manifest['assets'] = [{k: v for k, v in a.items() if k != 'path'} for a in plan['assets']]
        (stage / 'release.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        (stage / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(stage.iterdir()) if p.is_file()))
        notes_file = stage / 'notes.md'
        notes_file.write_text(notes.strip() + '\n\n软件授权：见 software.json 中该软件的 license 字段及安装包内的许可说明。\n\n下载后可用 SHA256SUMS.txt 校验文件完整性。\n')
        # Upload complete assets while still private to the draft; never replace a published release.
        args = ['release', 'create', plan['tag'], *[str(p) for p in sorted(stage.iterdir()) if p != notes_file],
                '--draft', '--latest=false', '--target', 'main', '--title', f'{name} {plan["version"]}', '--notes-file', str(notes_file)]
        if prerelease or '-' in plan['version']:
            args.append('--prerelease')
        runner(*args)
        # The REST tag endpoint excludes draft releases. gh release view resolves
        # drafts as well; use the numeric id to read their uploaded asset digests.
        release_id = json.loads(runner('release', 'view', plan['tag'], '--json', 'databaseId'))['databaseId']
        uploaded = json.loads(runner('api', f'repos/{REPO}/releases/{release_id}'))['assets']
        expected = {p.name: p for p in stage.iterdir() if p != notes_file}
        if {a['name'] for a in uploaded} != set(expected):
            raise ValueError('Uploaded asset list mismatch; release remains a draft')
        for asset in uploaded:
            path = expected[asset['name']]
            if asset['size'] != path.stat().st_size or (asset.get('digest') and asset['digest'] != 'sha256:' + digest(path)):
                raise ValueError('Uploaded size or SHA-256 mismatch; release remains a draft')
        if not draft:
            runner('release', 'edit', plan['tag'], '--draft=false', '--latest=false')
        print(f'https://github.com/{REPO}/releases/tag/{plan["tag"]}')


def attach(plan, suffix, notes, replace_notes=False, runner=gh):
    """Add a new platform to a published version without replacing any assets."""
    manifest_name, sums_name = supplement_metadata(suffix)
    release_id = json.loads(runner('release', 'view', plan['tag'], '--json', 'databaseId'))['databaseId']
    endpoint = f'repos/{REPO}/releases/{release_id}'
    remote = json.loads(runner('api', endpoint))
    if remote.get('draft') or remote.get('tag_name') != plan['tag']:
        raise ValueError('Supplement requires the exact existing, published release')
    original = {a['name']: a for a in remote['assets']}
    with tempfile.TemporaryDirectory(prefix='unzoo-supplement-') as tmp:
        stage = Path(tmp)
        for asset in plan['assets']:
            target = stage / asset['name']
            shutil.copyfile(asset['path'], target)
            if digest(target) != asset['sha256']:
                raise ValueError('Asset changed while staging; nothing uploaded')
        manifest = {k: v for k, v in plan.items() if k != 'assets'}
        manifest['supplement'] = suffix
        manifest['assets'] = [{k: v for k, v in a.items() if k != 'path'}
                              for a in sorted(plan['assets'], key=lambda a: a['name'])]
        (stage / manifest_name).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        (stage / sums_name).write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(stage.iterdir())))
        expected = {p.name: p for p in stage.iterdir()}

        def verify(asset, path):
            if (asset.get('state') != 'uploaded' or asset['size'] != path.stat().st_size
                    or asset.get('digest') != 'sha256:' + digest(path)):
                raise ValueError(f'Existing or uploaded asset differs or is incomplete; never replaced: {path.name}')

        missing = []
        for name, path in expected.items():
            if name in original:
                verify(original[name], path)
            else:
                missing.append(str(path))
        if missing:
            runner('release', 'upload', plan['tag'], *sorted(missing))
        uploaded = json.loads(runner('api', endpoint))
        if uploaded.get('draft') or uploaded.get('tag_name') != plan['tag']:
            raise ValueError('Release identity or publication state changed during upload')
        current = {a['name']: a for a in uploaded['assets']}
        for name, before in original.items():
            after = current.get(name)
            if after is None or any(after.get(k) != before.get(k) for k in ('id', 'size', 'digest', 'state')):
                raise ValueError('Existing release assets changed during supplement upload')
        for name, path in expected.items():
            if name not in current:
                raise ValueError(f'Supplement upload incomplete: {name}; retry only after inspecting remote state')
            verify(current[name], path)
        marker = f'<!-- supplement:{suffix} -->'
        body = uploaded.get('body') or ''
        if replace_notes:
            updated = notes.strip()
            if marker not in updated:
                updated += '\n\n' + marker
            updated += '\n'
        elif marker not in body:
            updated = body.rstrip() + '\n\n' + marker + '\n\n' + notes.strip() + '\n'
        else:
            updated = body
        if updated != body:
            notes_file = stage / '.notes-for-edit.md'
            notes_file.write_text(updated)
            runner('release', 'edit', plan['tag'], '--notes-file', str(notes_file))
        print(f'https://github.com/{REPO}/releases/tag/{plan["tag"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check')
    commands.add_parser('sync')
    add = commands.add_parser('add')
    for key in ('id', 'name', 'description', 'license'):
        add.add_argument('--' + key, required=True)
    add.add_argument('--platform', action='append', required=True)
    release = commands.add_parser('publish')
    release.add_argument('id')
    release.add_argument('version')
    release.add_argument('files', nargs='+', type=Path)
    release.add_argument('--notes-file', type=Path, required=True)
    for flag in ('dry-run', 'prerelease', 'draft'):
        release.add_argument('--' + flag, action='store_true')
    supplement = commands.add_parser('attach', help='Append a new platform to an existing release without overwriting assets')
    supplement.add_argument('id')
    supplement.add_argument('version')
    supplement.add_argument('files', nargs='+', type=Path)
    supplement.add_argument('--suffix', required=True)
    supplement.add_argument('--notes-file', type=Path, required=True)
    supplement.add_argument('--replace-notes', action='store_true')
    supplement.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    products = load_products()
    if args.command == 'add':
        products.append(dict(id=args.id, name=args.name, description=args.description, platforms=args.platform, license=args.license))
        validate_products(products)
        (ROOT / 'software.json').write_text(json.dumps(products, ensure_ascii=False, indent=2) + '\n')
        print('Registered software. Commit and push software.json before publishing.')
    elif args.command == 'check':
        render_readme((ROOT / 'README.md').read_text(), build_catalog(products, []))
        print(f'Configuration valid: {len(products)} software entries')
    elif args.command == 'sync':
        sync()
    else:
        product = next((p for p in products if p['id'] == args.id), None)
        if product is None:
            raise ValueError('Register the software using add before publishing')
        notes = args.notes_file.read_text()
        if not notes.strip():
            raise ValueError('Release notes cannot be empty')
        plan = plan_release(args.id, args.version, args.files)
        if args.command == 'attach':
            supplement_metadata(args.suffix)
        if args.dry_run:
            output = dict(plan, supplement=args.suffix, metadata=list(supplement_metadata(args.suffix))) if args.command == 'attach' else plan
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # Require the remote metadata before any upload, so automation can identify the software.
            remote = api(f'/repos/{REPO}/contents/software.json?ref=main')
            import base64
            registered = json.loads(base64.b64decode(remote['content']))
            if product not in registered:
                raise ValueError('Commit and push the current software metadata before publishing')
            if args.command == 'attach':
                attach(plan, args.suffix, notes, args.replace_notes)
                sync()
            else:
                publish(plan, product['name'], notes, args.prerelease, args.draft)
                if not args.draft:
                    sync()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
