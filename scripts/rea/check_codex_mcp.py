#!/usr/bin/env python3
"""Verify configured REA stdio handshake without executing target-analysis tools.
Python 3.11+. Reads only mcp_servers.rea; never prints config or server stderr.
"""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import tomllib


def verify(command, env=None, timeout=30):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, env=env)
    inbox = queue.Queue()

    def reader():
        for line in process.stdout:
            try:
                inbox.put(json.loads(line))
            except json.JSONDecodeError:
                inbox.put({'invalid_json': True})
        inbox.put(None)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    def send(message):
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()

    def receive(number):
        deadline = time.monotonic() + timeout
        while True:
            try:
                value = inbox.get(timeout=max(.001, deadline - time.monotonic()))
            except queue.Empty:
                raise TimeoutError('REA MCP response timeout') from None
            if value is None:
                raise RuntimeError('REA MCP exited before response')
            if value.get('invalid_json'):
                raise RuntimeError('REA stdout contains non-JSON protocol data')
            if value.get('id') == number:
                if 'error' in value:
                    raise RuntimeError('REA returned a JSON-RPC error; inspect client logs locally')
                return value['result']
            if time.monotonic() >= deadline:
                raise TimeoutError('REA MCP response timeout')

    try:
        send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
            'protocolVersion': '2024-11-05', 'capabilities': {},
            'clientInfo': {'name': 'toolkit-rea-check', 'version': '1.0'}}})
        initialized = receive(1)
        send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        names, seen, cursor = [], set(), None
        for number in range(2, 102):
            send({'jsonrpc': '2.0', 'id': number, 'method': 'tools/list',
                  'params': {'cursor': cursor} if cursor else {}})
            page = receive(number)
            names.extend(t['name'] for t in page['tools'])
            cursor = page.get('nextCursor')
            if not cursor:
                break
            if cursor in seen:
                raise RuntimeError('Repeated tools/list cursor')
            seen.add(cursor)
        else:
            raise RuntimeError('tools/list exceeded 100 pages')
        if not names or len(names) != len(set(names)):
            raise RuntimeError('Empty or duplicate tool catalog')
        return {'status': 'PASS', 'server_version': initialized['serverInfo'].get('version'),
                'tool_count': len(names), 'pages': number - 1,
                'target_executed': False, 'active_agent_discovery': 'NOT_TESTED',
                'providers': 'NOT_TESTED'}
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        for stream in [process.stdin, process.stdout]:
            stream.close()
        thread.join(timeout=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'config.toml'
    parser.add_argument('--config', type=Path, default=default)
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    if not 0 < args.timeout <= 120:
        parser.error('--timeout must be >0 and <=120 seconds per response')
    try:
        registration = tomllib.loads(args.config.read_text())['mcp_servers']['rea']
        command = registration['command']
        if not isinstance(command, str) or not command:
            raise ValueError('Expected an enabled stdio REA command')
        if registration.get('enabled') is False:
            raise ValueError('REA registration is disabled')
        argv = registration.get('args', [])
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            raise ValueError('REA args must be an array of strings')
        env = dict(os.environ)
        env.update(registration.get('env', {}))
        print(json.dumps(verify([command, *argv], env, args.timeout), indent=2))
        return 0
    except Exception as exc:
        # Do not expose config values, command arguments, or upstream error payloads.
        print(json.dumps({'status': 'FAIL', 'error_type': type(exc).__name__,
                          'next_step': 'Inspect REA command/PATH and client logs locally; no config was changed.'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
