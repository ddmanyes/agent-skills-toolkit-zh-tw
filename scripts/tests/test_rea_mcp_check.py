"""Protocol tests: a fake stdio server never executes analysis tools."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECK = Path(__file__).resolve().parents[1] / 'rea/check_codex_mcp.py'
spec = importlib.util.spec_from_file_location('rea_check', CHECK)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SERVER = '''import sys,json
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m:continue
 if m['method']=='initialize':r={'serverInfo':{'version':'fixture'}}
 elif m['method']=='tools/list':
  if not m['params'].get('cursor'):r={'tools':[{'name':'one'}],'nextCursor':'page2'}
  else:r={'tools':[{'name':'two'}]}
 else:raise RuntimeError('Unexpected analysis call')
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':r}),flush=True)
'''

class CheckTests(unittest.TestCase):
    def test_paginated_catalog(self):
        r = module.verify([sys.executable, '-c', SERVER], timeout=2)
        self.assertEqual((r['tool_count'], r['pages'], r['target_executed']), (2, 2, False))

    def test_repeat_cursor(self):
        server = SERVER.replace("else:r={'tools':[{'name':'two'}]}", "else:r={'tools':[{'name':'two'}],'nextCursor':'page2'}")
        with self.assertRaisesRegex(RuntimeError, 'Repeated'):
            module.verify([sys.executable, '-c', server], timeout=2)

    def test_timeout(self):
        with self.assertRaises(TimeoutError):
            module.verify([sys.executable, '-c', 'import time;time.sleep(30)'], timeout=.1)

    def test_protocol_error_redacts_payload(self):
        server = "import sys,json\nm=json.loads(sys.stdin.readline());print(json.dumps({'id':m['id'],'error':{'message':'SECRET_FIXTURE'}}),flush=True)"
        with self.assertRaises(RuntimeError) as cm:
            module.verify([sys.executable, '-c', server], timeout=2)
        self.assertNotIn('SECRET_FIXTURE', str(cm.exception))

    def test_invalid_json(self):
        with self.assertRaisesRegex(RuntimeError, 'non-JSON'):
            module.verify([sys.executable, '-c', "print('bad',flush=True)"], timeout=2)

    def test_config_failure_is_redacted(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'config.toml';p.write_text('[mcp_servers.rea]\ncommand = "SECRET_NOT_A_COMMAND"\n')
            r = subprocess.run([sys.executable, str(CHECK), '--config', str(p)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertNotIn('SECRET_NOT_A_COMMAND', r.stdout + r.stderr)
            self.assertEqual(json.loads(r.stdout)['status'], 'FAIL')

if __name__ == '__main__':unittest.main()
