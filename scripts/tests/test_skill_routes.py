"""Isolated route/config tests; no real user config or remote services."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
from unittest.mock import patch
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('routes', ROOT/'skills/skill-toolkit/scripts/skill_routes.py')
routes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(routes)


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skill-route-test-')
        self.home = Path(self.temp.name)
        self.base = self.home/'.agents/skills'
        self.put(self.base/'skill-toolkit/SKILL.md', '---\nname: skill-toolkit\n---\n'+routes.MARKER)
        self.put(self.base/'skill-toolkit/scripts/skill_routes.py', '# helper')

    def tearDown(self):
        assert self.home.resolve().parent == Path(tempfile.gettempdir()).resolve()
        assert self.home.name.startswith('skill-route-test-')
        self.temp.cleanup()

    def put(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def variant(self, bucket='one', name='docx', body='original'):
        p = self.base/f'synced/{bucket}/{name}/SKILL.md'
        self.put(p, f'---\nname: {name}\n---\n{body}')
        for f in routes.REQUIRED[name]: self.put(p.parent/f, 'resource')
        return p

    def primary(self, name='docx'):
        self.put(self.base/name/'SKILL.md', f'---\nname: {name}\n---\n'+routes.MARKER)

    def test_missing(self):
        self.assertEqual(routes.resolve(self.home, 'docx')['status'], 'unavailable')

    def test_full_variant(self):
        p = self.variant()
        self.assertEqual(routes.resolve(self.home, 'docx')['entry'], str(p))

    def test_missing_resources(self):
        self.put(self.base/'synced/one/docx/SKILL.md', '---\nname: docx\n---')
        self.assertEqual(routes.resolve(self.home, 'docx')['status'], 'unavailable')

    def test_ambiguous_resources(self):
        self.variant(); p=self.variant('two')
        self.put(p.parent/'scripts/comment.py', 'customized')
        self.assertEqual(routes.resolve(self.home, 'docx')['status'], 'ambiguous')
        self.primary()
        self.assertEqual(routes.plan(self.home)['planned'], [])

    def test_identical_variants_both_routed(self):
        self.variant(); self.variant('two'); self.primary()
        self.assertEqual(len(routes.plan(self.home)['planned']), 2)

    def test_no_routed_primary_preserves_variant(self):
        self.variant()
        self.assertEqual(routes.plan(self.home)['planned'], [])

    def test_dry_run_no_writes(self):
        self.variant(); self.primary()
        self.assertFalse(routes.configure(self.home)['changed'])
        self.assertFalse((self.home/'.codex').exists())

    def test_apply_idempotent_backup_and_unrelated_config(self):
        p=self.variant(); self.primary(); before=p.read_bytes()
        config=self.put(self.home/'.codex/config.toml', 'model = "example"\n[features]\nexample = true\n')
        original=config.read_bytes()
        result=routes.configure(self.home, True)
        self.assertEqual(Path(result['backup']).read_bytes(), original)
        saved=config.read_bytes();self.assertFalse(routes.configure(self.home, True)['changed'])
        self.assertEqual(config.read_bytes(), saved);self.assertEqual(p.read_bytes(), before)
        parsed=tomllib.loads(config.read_text(encoding='utf-8'))
        self.assertEqual(parsed.pop('skills')['config'][0]['enabled'], False)
        self.assertEqual(parsed,tomllib.loads(original.decode()))

    def test_removes_stale_owned_entries(self):
        old=routes.rewrite('model = "example"\n',['/old/SKILL.md'])
        new=routes.rewrite(old, [])
        self.assertNotIn('/old/SKILL.md',new)
        self.assertEqual(tomllib.loads(new), {'model':'example'})

    def test_malformed_markers_rejected(self):
        with self.assertRaises(ValueError):routes.rewrite(routes.BEGIN, [])

    def test_concurrent_config_change_rejected(self):
        self.variant();self.primary()
        config=self.put(self.home/'.codex/config.toml','model = "before"\n')
        original_plan=routes.plan;calls=[]
        def mutate(home):
            calls.append(1)
            result=original_plan(home)
            if len(calls)==2:config.write_text('model = "other"\n',encoding='utf-8')
            return result
        with patch.object(routes,'plan',side_effect=mutate):
            with self.assertRaises(ValueError):routes.configure(self.home,True)
        self.assertEqual(tomllib.loads(config.read_text())['model'],'other')

    def test_custom_dual_model_preserved(self):
        self.put(self.base/'local-dual-model/SKILL.md','name: local-dual-model')
        self.put(self.home/'.codex/skills/local-dual-model/SKILL.md','customized')
        self.assertEqual(routes.plan(self.home)['planned'],[])
        self.assertTrue(any('distinct' in s for s in routes.plan(self.home)['skipped']))

    def test_harness_known_repair(self):
        primary=self.put(self.base/'harness-purge/SKILL.md','Claude／Codex references/claude-codex.md')
        self.put(primary.parent/'references/claude-codex.md','reference')
        other=self.put(self.home/'.codex/skills/harness-purge/SKILL.md','Codex／Codex references/Codex-codex.md')
        self.put(other.parent/'references/claude-codex.md','reference')
        self.assertIn(str(other),routes.plan(self.home)['planned'])

    def test_unknown_plugin_version_preserved(self):
        self.primary('x-bookmarks-radar')
        p=self.put(self.home/'.codex/plugins/cache/personal/second-brain-radar/9.0/skills/x-bookmarks-radar/SKILL.md','new version')
        self.assertNotIn(str(p),routes.plan(self.home)['planned'])

    def test_symlink_config_rejected(self):
        outside=self.put(self.home/'outside.toml','model = "safe"')
        config=self.home/'.codex/config.toml';config.parent.mkdir()
        try:config.symlink_to(outside)
        except OSError:self.skipTest('Symlink privilege unavailable')
        with self.assertRaises(ValueError):routes.configure(self.home,True)


if __name__ == '__main__': unittest.main()
