#!/usr/bin/env python3
"""Read proxy/process metadata without printing credentials or command lines."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import platform
import re
import subprocess
from urllib.parse import urlsplit

PROXY_NAMES = ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy')
PROCESS_PREFIXES = ('chatgpt', 'codex', 'magpie', 'clash', 'verge-mihomo', 'mihomo')


def proxy_summary(value):
    if not value:
        return {'configured': False}
    if '://' not in value:
        return {'configured': True, 'parseable': False}
    try:
        parsed = urlsplit(value)
        host, port = parsed.hostname, parsed.port
        valid = parsed.scheme in ('http', 'https', 'socks', 'socks4', 'socks4a', 'socks5', 'socks5h')
        if not host or any(c.isspace() for c in host) or not valid:
            return {'configured': True, 'parseable': False}
        return {'configured': True, 'scheme': parsed.scheme, 'host': host, 'port': port,
                'credentials_present': parsed.username is not None}
    except ValueError:
        return {'configured': True, 'parseable': False}


def bypass_summary(value):
    entries = [v.strip() for v in value.split(',') if v.strip()]
    networks = []
    for entry in entries:
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError:
            pass
    def covers(address):
        ip = ipaddress.ip_address(address)
        return '*' in entries or any(ip in network for network in networks)
    return {'configured': bool(entries), 'entry_count': len(entries),
            'localhost_entry': 'localhost' in entries,
            'ipv4_loopback_ip_match': covers('127.0.0.1'),
            'ipv6_loopback_ip_match': covers('::1')}


def environment_summary(env):
    result = {name: proxy_summary(env.get(name, '')) for name in PROXY_NAMES if name in env}
    result.update({name: bypass_summary(env[name]) for name in ('NO_PROXY', 'no_proxy') if name in env})
    return result


def flag(value):
    return {'0': False, '1': True}.get(str(value))


def url_setting_summary(values, name):
    if name not in values:
        return {'configured': None, 'reason': 'value_not_present'}
    if not isinstance(values[name], str):
        return {'configured': None, 'reason': 'unexpected_value_type'}
    return proxy_summary(values[name])


def native_proxy_endpoint(value, scheme='http'):
    if not value:
        return {'configured': False}
    return proxy_summary(value if '://' in value else scheme + '://' + value)


def windows_proxy_summary(values):
    servers = []
    raw_servers = values.get('ProxyServer')
    for part in (raw_servers if isinstance(raw_servers, str) else '').split(';'):
        if not part.strip():
            continue
        request_scheme, separator, endpoint = part.strip().partition('=')
        if separator and request_scheme.lower() in ('http', 'https', 'ftp', 'socks'):
            scheme = request_scheme.lower()
        else:
            scheme, endpoint = 'all', part.strip()
        servers.append({'request_scheme': scheme,
                        'endpoint': native_proxy_endpoint(endpoint, 'socks' if scheme == 'socks' else 'http')})
    bypass = values.get('ProxyOverride')
    return {'available': True, 'scope': 'Current-user Internet Settings; not WinHTTP/PAC decisions or effective app routing',
            'manual_proxy_enabled': flag(values.get('ProxyEnable')), 'stored_proxy_servers': servers,
            'pac_url': url_setting_summary(values, 'AutoConfigURL'),
            'bypass': bypass_summary(bypass.replace(';', ',')) if isinstance(bypass, str) else None,
            'auto_discovery': 'not_collected', 'winhttp_policy': 'not_collected'}


def windows_system_proxy():
    try:
        import winreg
        values = {}
        key_name = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_name) as key:
            for name in ('ProxyEnable', 'ProxyServer', 'ProxyOverride', 'AutoConfigURL'):
                try:
                    values[name] = winreg.QueryValueEx(key, name)[0]
                except FileNotFoundError:
                    pass
        return windows_proxy_summary(values)
    except (ImportError, OSError):
        return {'available': False, 'reason': 'current_user_registry_unavailable'}


def macos_proxy_summary(text):
    values, depth, opened = {}, 0, False
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r'^([A-Za-z][A-Za-z0-9]*)\s*:\s*(.*)$', stripped)
        if depth == 1 and match:
            values[match[1]] = match[2].strip()
        if stripped == '<dictionary> {' or re.search(r':\s*<(dictionary|array)>\s*\{$', stripped):
            depth += 1
            opened = True
        elif stripped == '}':
            depth -= 1
            if depth < 0:
                return {'available': False, 'reason': 'unrecognized_scutil_output'}
    if not opened or depth != 0:
        return {'available': False, 'reason': 'unrecognized_scutil_output'}
    proxies = {}
    for prefix, scheme in (('HTTP', 'http'), ('HTTPS', 'http'), ('SOCKS', 'socks')):
        host, port = values.get(prefix + 'Proxy'), values.get(prefix + 'Port')
        endpoint = {'configured': False}
        if host and port:
            if ':' in host and not host.startswith('[') and '@' not in host:
                host = '[' + host + ']'
            endpoint = native_proxy_endpoint(host + ':' + port, scheme)
        proxies[prefix.lower()] = {'enabled': flag(values.get(prefix + 'Enable')), 'endpoint': endpoint}
    return {'available': True, 'scope': 'scutil top-level snapshot; scoped/PAC decisions and effective app routing are not inspected',
            'proxies': proxies, 'pac_enabled': flag(values.get('ProxyAutoConfigEnable')),
            'pac_url': url_setting_summary(values, 'ProxyAutoConfigURLString'),
            'auto_discovery_enabled': flag(values.get('ProxyAutoDiscoveryEnable')),
            'scoped_settings': 'not_collected', 'bypass': 'not_collected'}


def system_proxy_snapshot(system):
    if system == 'Windows':
        return windows_system_proxy()
    if system == 'Darwin':
        try:
            result = subprocess.run(['/usr/sbin/scutil', '--proxy'], capture_output=True, text=True, timeout=4)
            if result.returncode:
                return {'available': False, 'reason': 'scutil_failed'}
            return macos_proxy_summary(result.stdout)
        except (OSError, subprocess.TimeoutExpired):
            return {'available': False, 'reason': 'scutil_unavailable'}
    return {'available': False, 'reason': 'native_snapshot_not_implemented_for_this_platform'}


def linux_processes(root=Path('/proc'), limit=64):
    processes, matched = [], 0
    for entry in sorted(root.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else -1):
        if not entry.name.isdigit():
            continue
        try:
            name = (entry / 'comm').read_text().strip()
            if not name.lower().startswith(PROCESS_PREFIXES):
                continue
            matched += 1
            if len(processes) >= limit:
                continue
            record = {'pid': int(entry.name), 'name': name}
            status = dict(line.split(':', 1) for line in (entry / 'status').read_text().splitlines() if ':' in line)
            record['parent_pid'] = status.get('PPid', '').strip()
            record['tracer_pid'] = status.get('TracerPid', '').strip()
            try:
                pairs = (entry / 'environ').read_bytes().split(b'\0')
                env = dict(pair.decode(errors='replace').split('=', 1) for pair in pairs if b'=' in pair)
                record['proxy_environment'] = environment_summary(env)
            except OSError:
                record['proxy_environment_accessible'] = False
            processes.append(record)
        except OSError:
            continue
    return {'processes': processes, 'matched_count': matched, 'truncated': matched > len(processes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-processes', action='store_true', help='Skip the Linux process inventory')
    parser.add_argument('--system-proxy', action='store_true', help='Read a sanitized native Windows/macOS proxy snapshot')
    args = parser.parse_args()
    result = {'execution_platform': platform.system(), 'current_process_proxy_environment': environment_summary(os.environ),
              'scope': 'Configuration metadata only; effective routes and target application behavior are not inspected.'}
    if platform.system() == 'Linux' and not args.no_processes:
        result['linux'] = linux_processes()
    if args.system_proxy:
        result['system_proxy_snapshot'] = system_proxy_snapshot(result['execution_platform'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
