import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from contextlib import nullcontext

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/chatgpt-codex-network/scripts/inspect_environment.py'
spec = importlib.util.spec_from_file_location('inspect_environment', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EnvironmentTests(unittest.TestCase):
    def test_cli_omits_credentials_paths_and_query(self):
        env = os.environ.copy()
        credential = 'fixture-' + 'credential'
        env.update(HTTPS_PROXY=f'http://fixture-user:{credential}@[::1]:9999/private-path?token=fixture-query',
                   NO_PROXY='internal-private-name,localhost,127.0.0.1,::1')
        result = subprocess.run([sys.executable, str(SCRIPT), '--no-processes'], env=env,
                                capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for secret in ('fixture-user', credential, 'private-path', 'fixture-query', 'internal-private-name'):
            self.assertNotIn(secret, result.stdout)
        proxy = data['current_process_proxy_environment']['HTTPS_PROXY']
        self.assertEqual((proxy['host'], proxy['port'], proxy['credentials_present']), ('::1', 9999, True))

    def test_bypass_requires_literal_ip_or_covering_cidr(self):
        self.assertFalse(module.bypass_summary('localhost,127.*')['ipv4_loopback_ip_match'])
        self.assertTrue(module.bypass_summary('127.0.0.0/8')['ipv4_loopback_ip_match'])
        self.assertTrue(module.bypass_summary('::1')['ipv6_loopback_ip_match'])
        self.assertFalse(module.bypass_summary('192.168.0.0/16')['ipv4_loopback_ip_match'])

    def test_invalid_proxy_is_not_echoed(self):
        for value in ('secret-bare-value', 'http://secret:bad-port/', 'file:///secret/path'):
            output = module.proxy_summary(value)
            self.assertEqual(output, {'configured': True, 'parseable': False})

    def test_selected_processes_and_missing_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for pid, name in ((10, 'ChatGPT'), (11, 'codex'), (12, 'unrelated')):
                process = root / str(pid)
                process.mkdir()
                (process / 'comm').write_text(name + '\n')
                (process / 'status').write_text('PPid:\t1\nTracerPid:\t0\n')
            credential = 'fixture-' + 'credential'
            value = f'HTTPS_PROXY=http://fixture-user:{credential}@localhost:9876\0UNRELATED_SECRET=hidden\0'
            (root / '10/environ').write_bytes(value.encode())
            data = module.linux_processes(root)
            self.assertEqual([p['pid'] for p in data['processes']], [10, 11])
            self.assertFalse(data['processes'][1]['proxy_environment_accessible'])
            self.assertNotIn(credential, json.dumps(data))
            self.assertNotIn('hidden', json.dumps(data))
            self.assertTrue(module.linux_processes(root, limit=1)['truncated'])

    def test_windows_servers_and_pac_are_sanitized(self):
        credential = 'fixture-' + 'credential'
        values = {'ProxyEnable': 1,
                  'ProxyServer': f'http=fixture-user:{credential}@proxy.test:8080;https=https://secure.test:8443;socks=[::1]:1080',
                  'ProxyOverride': 'localhost;127.0.0.1;private-bypass.test',
                  'AutoConfigURL': f'https://fixture-user:{credential}@pac.test/private-pac?access=fixture-query'}
        data = module.windows_proxy_summary(values)
        output = json.dumps(data)
        for secret in ('fixture-user', credential, 'private-pac', 'fixture-query', 'private-bypass.test'):
            self.assertNotIn(secret, output)
        self.assertTrue(data['manual_proxy_enabled'])
        self.assertEqual(data['stored_proxy_servers'][0]['endpoint']['host'], 'proxy.test')
        self.assertTrue(data['stored_proxy_servers'][0]['endpoint']['credentials_present'])
        self.assertEqual(data['stored_proxy_servers'][1]['endpoint']['scheme'], 'https')
        self.assertEqual(data['stored_proxy_servers'][2]['endpoint']['host'], '::1')
        self.assertEqual(data['winhttp_policy'], 'not_collected')

    def test_windows_missing_and_disabled_values_remain_distinct(self):
        empty = module.windows_proxy_summary({})
        self.assertIsNone(empty['manual_proxy_enabled'])
        self.assertIsNone(empty['bypass'])
        self.assertIsNone(empty['pac_url']['configured'])
        explicit_empty_pac = module.windows_proxy_summary({'AutoConfigURL': ''})
        self.assertFalse(explicit_empty_pac['pac_url']['configured'])
        disabled = module.windows_proxy_summary({'ProxyEnable': 0, 'ProxyServer': 'localhost:8080'})
        self.assertFalse(disabled['manual_proxy_enabled'])
        self.assertEqual(len(disabled['stored_proxy_servers']), 1)
        malformed = module.windows_proxy_summary({'ProxyServer': b'unknown', 'ProxyOverride': 123})
        self.assertEqual(malformed['stored_proxy_servers'], [])
        self.assertIsNone(malformed['bypass'])

    def test_windows_registry_uses_read_only_allowlist(self):
        queried = []
        def query(key, name):
            queried.append(name)
            if name == 'ProxyEnable':
                return 0, 4
            raise FileNotFoundError()
        fake = SimpleNamespace(HKEY_CURRENT_USER=object(), OpenKey=lambda *args: nullcontext(object()), QueryValueEx=query)
        with patch.dict(sys.modules, {'winreg': fake}):
            data = module.system_proxy_snapshot('Windows')
        self.assertTrue(data['available'])
        self.assertFalse(data['manual_proxy_enabled'])
        self.assertEqual(queried, ['ProxyEnable', 'ProxyServer', 'ProxyOverride', 'AutoConfigURL'])

    def test_windows_unreadable_registry_is_unknown(self):
        fake = SimpleNamespace(HKEY_CURRENT_USER=object(), OpenKey=lambda *args: (_ for _ in ()).throw(PermissionError()))
        with patch.dict(sys.modules, {'winreg': fake}):
            data = module.system_proxy_snapshot('Windows')
        self.assertFalse(data['available'])
        self.assertNotIn('manual_proxy_enabled', data)

    def test_macos_root_snapshot_preserves_pac_and_ignores_scoped_values(self):
        credential = 'fixture-' + 'credential'
        text = f'''<dictionary> {{
  HTTPEnable : 1
  HTTPProxy : proxy.test
  HTTPPort : 8080
  SOCKSEnable : 1
  SOCKSProxy : ::1
  SOCKSPort : 1080
  ProxyAutoConfigEnable : 1
  ProxyAutoConfigURLString : https://fixture-user:{credential}@pac.test/private-pac?access=fixture-query
  ExceptionsList : <array> {{
    0 : private-bypass.test
  }}
  __SCOPED__ : <dictionary> {{
    en0 : <dictionary> {{
      HTTPProxy : private-scoped.test
      HTTPPort : 9000
    }}
  }}
}}'''
        data = module.macos_proxy_summary(text)
        output = json.dumps(data)
        self.assertTrue(data['available'])
        self.assertTrue(data['pac_enabled'])
        self.assertEqual(data['proxies']['http']['endpoint']['host'], 'proxy.test')
        self.assertEqual(data['proxies']['socks']['endpoint']['host'], '::1')
        for secret in ('fixture-user', credential, 'private-pac', 'fixture-query', 'private-scoped.test', 'private-bypass.test'):
            self.assertNotIn(secret, output)
        self.assertEqual(data['scoped_settings'], 'not_collected')

    def test_macos_unrecognized_output_is_not_reported_as_disabled(self):
        for text in ('', 'command failed with private-info', '<dictionary> {\nHTTPEnable : 1'):
            data = module.macos_proxy_summary(text)
            self.assertFalse(data['available'])
            self.assertNotIn('proxies', data)
            self.assertNotIn('private-info', json.dumps(data))
        data = module.macos_proxy_summary('<dictionary> {\n}')
        self.assertIsNone(data['proxies']['http']['enabled'])
        self.assertIsNone(data['pac_url']['configured'])

    def test_macos_collection_invokes_only_read_only_command(self):
        with patch.object(module.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='<dictionary> {\n}')) as call:
            self.assertTrue(module.system_proxy_snapshot('Darwin')['available'])
        self.assertEqual(call.call_args.args[0], ['/usr/sbin/scutil', '--proxy'])
        with patch.object(module.subprocess, 'run', side_effect=subprocess.TimeoutExpired('scutil', 4)):
            self.assertFalse(module.system_proxy_snapshot('Darwin')['available'])


if __name__ == '__main__':
    unittest.main()
