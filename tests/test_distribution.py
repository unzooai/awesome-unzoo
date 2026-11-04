import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'distribute.py'


class DistributionTests(unittest.TestCase):
    def load(self):
        self.assertTrue(SCRIPT.exists(), 'distribution tool must exist')
        spec = importlib.util.spec_from_file_location('distribute', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_catalog_keeps_products_separate_and_orders_versions(self):
        m = self.load()
        products = [{'id': 'alpha', 'name': 'Alpha', 'description': 'A', 'platforms': ['Android'], 'license': 'Proprietary'},
                    {'id': 'beta', 'name': 'Beta', 'description': 'B', 'platforms': ['macOS'], 'license': 'MIT'}]
        releases = [self.release('alpha/v1.9.0'), self.release('alpha/v1.10.0'), self.release('beta/v2.0.0'),
                    self.release('alpha/v3.0.0-beta.1', prerelease=True), self.release('alpha/v9.0.0', draft=True)]
        catalog = m.build_catalog(products, releases)
        self.assertEqual(catalog[0]['latest']['version'], '1.10.0')
        self.assertEqual(catalog[1]['latest']['version'], '2.0.0')
        self.assertEqual(catalog[0]['preview']['version'], '3.0.0-beta.1')

    def release(self, tag, **values):
        return dict(tag_name=tag, html_url='https://github.com/unzooai/awesome-unzoo/releases/tag/' + tag,
                    assets=[dict(name='app.apk', size=3, browser_download_url='https://example.com/app.apk')],
                    published_at='2026-11-04T00:00:00Z', **values)

    def test_release_without_installers_is_not_downloadable(self):
        m = self.load()
        release = self.release('alpha/v1.0.0')
        release['assets'] = [dict(name='SHA256SUMS.txt', size=3, browser_download_url='https://example.com/hash')]
        item = m.build_catalog([{'id': 'alpha', 'name': 'Alpha'}], [release])[0]
        self.assertIsNone(item['latest'])

    def test_duplicate_ids_and_invalid_ids_are_rejected(self):
        m = self.load()
        for products in [[{'id': '../x'}], [{'id': 'alpha'}, {'id': 'alpha'}]]:
            with self.assertRaises(ValueError):
                m.validate_products(products)

    def test_publish_plan_hashes_real_bytes_and_never_overwrites_input(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / 'app.apk'
            asset.write_bytes(b'abc')
            plan = m.plan_release('alpha', '1.2.3', [asset])
            self.assertEqual(plan['tag'], 'alpha/v1.2.3')
            self.assertEqual(plan['assets'][0]['sha256'], 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertEqual(asset.read_bytes(), b'abc')

    def test_publish_plan_rejects_missing_empty_duplicate_and_reserved_assets(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'app.apk'
            asset.write_bytes(b'abc')
            reserved = root / 'SHA256SUMS.txt'
            reserved.write_text('x')
            for files in [[], [root / 'missing.apk'], [asset, asset], [reserved]]:
                with self.assertRaises(ValueError):
                    m.plan_release('alpha', '1.0.0', files)

    def test_unsafe_tags_and_asset_names_rejected(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / 'bad#label.apk'
            asset.write_bytes(b'abc')
            with self.assertRaises(ValueError):
                m.plan_release('alpha', '1.0.0', [asset])
            for version in ['latest', '../v1', '01.0.0', '1.0', '1.0.0;bad']:
                with self.assertRaises(ValueError):
                    m.plan_release('alpha', version, [asset])

    def test_sync_preserves_handwritten_readme_and_escapes_metadata(self):
        m = self.load()
        content = 'Header\n<!-- catalog:start -->\nold\n<!-- catalog:end -->\nFooter\n'
        result = m.render_readme(content, [{'id': 'alpha', 'name': 'A | B', 'description': '<script>\nx',
                                           'platforms': ['Android'], 'latest': None, 'preview': None}])
        self.assertTrue(result.startswith('Header\n'))
        self.assertTrue(result.endswith('\nFooter\n'))
        self.assertNotIn('<script>', result)
        self.assertIn('A &#124; B', result)

    def test_publish_checks_uploads_before_publishing_and_keeps_failed_draft(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'app.apk'
            asset.write_bytes(b'abc')
            plan = m.plan_release('alpha', '1.0.0', [asset])
            calls = []
            def gh(*args):
                calls.append(args)
                if args[0] == 'api':
                    return json.dumps({'assets': []})
                return ''
            with self.assertRaises(ValueError):
                m.publish(plan, 'Alpha', 'notes', False, False, gh)
            self.assertTrue(any(c[:2] == ('release', 'create') and '--draft' in c for c in calls))
            self.assertFalse(any(c[:2] == ('release', 'edit') for c in calls))

    def test_publish_success_excludes_local_paths_and_checks_every_asset(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / 'app.apk'
            asset.write_bytes(b'abc')
            plan = m.plan_release('alpha', '1.0.0-beta.1', [asset])
            calls, uploaded = [], []
            def gh(*args):
                calls.append(args)
                if args[:2] == ('release', 'create'):
                    self.assertIn('--prerelease', args)
                    files = [Path(p) for p in args if Path(p).is_file()]
                    # notes file is an option value, not a release asset.
                    files = [p for p in files if p.name != 'notes.md']
                    for path in files:
                        uploaded.append(dict(name=path.name, size=path.stat().st_size, digest='sha256:' + m.digest(path)))
                    manifest = json.loads(next(p for p in files if p.name == 'release.json').read_text())
                    self.assertNotIn('path', manifest['assets'][0])
                    sums = next(p for p in files if p.name == 'SHA256SUMS.txt').read_text()
                    self.assertIn('  app.apk\n', sums)
                    self.assertIn('  release.json\n', sums)
                if args[0] == 'api':
                    return json.dumps({'assets': uploaded})
                return ''
            m.publish(plan, 'Alpha', 'notes', False, False, gh)
            self.assertEqual(calls[-1], ('release', 'edit', 'alpha/v1.0.0-beta.1', '--draft=false', '--latest=false'))

    def test_corrupt_remote_digest_prevents_publication(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            asset = Path(tmp) / 'app.apk'
            asset.write_bytes(b'abc')
            calls, uploaded = [], []
            def gh(*args):
                calls.append(args)
                if args[:2] == ('release', 'create'):
                    for value in args:
                        path = Path(value)
                        if path.is_file() and path.name != 'notes.md':
                            uploaded.append(dict(name=path.name, size=path.stat().st_size, digest='sha256:wrong'))
                if args[0] == 'api':
                    return json.dumps({'assets': uploaded})
                return ''
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                m.publish(m.plan_release('alpha', '1.0.0', [asset]), 'Alpha', 'notes', False, False, gh)
            self.assertFalse(any(c[:2] == ('release', 'edit') for c in calls))


if __name__ == '__main__':
    unittest.main()
