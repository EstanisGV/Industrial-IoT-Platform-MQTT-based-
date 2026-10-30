import os
import re
from pathlib import Path
import yaml

IDENT = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")

def load_devices(filename: str):
    path = Path(filename)
    root = path.parent
    config = yaml.safe_load(path.read_text())
    devices = config.get('machines', [])
    if not isinstance(devices, list) or not devices:
        raise ValueError('machines must be a non-empty list')
    names = set()
    for item in devices:
        ident = item.get('id', '')
        if not IDENT.fullmatch(ident) or ident in names:
            raise ValueError(f'invalid/duplicate machine id: {ident!r}')
        names.add(ident)
        if type(item.get('enabled')) is not bool:
            raise ValueError(f'{ident}: enabled must be boolean')
        if item.get('mode') not in ('mock','opcua'):
            raise ValueError(f'{ident}: mode must be mock or opcua')
        if not 1 <= float(item.get('interval_seconds', 0)) <= 3600:
            raise ValueError(f'{ident}: interval_seconds outside 1..3600')
        profile_path = (root / 'profiles' / item['profile']).resolve()
        if not profile_path.is_relative_to((root / 'profiles').resolve()):
            raise ValueError('profile path outside profiles')
        profile = yaml.safe_load(profile_path.read_text())
        variables = profile.get('variables', {})
        if not isinstance(variables, dict) or not variables:
            raise ValueError(f'{ident}: no variables')
        for key, v in variables.items():
            if not IDENT.fullmatch(key) or not isinstance(v, dict) or 'node_id' not in v:
                raise ValueError(f'{ident}: bad variable {key}')
        if item['mode'] == 'opcua' and item['enabled']:
            if not item.get('endpoint', '').startswith('opc.tcp://'):
                raise ValueError(f'{ident}: OPC UA endpoint required')
            if any('REPLACE_WITH_REAL' in v['node_id'] for v in variables.values()):
                raise ValueError(f'{ident}: replace placeholder NodeIds before real use')
            # Require explicitly configured secure channel, even for read-only access.
            if not item.get('security'):
                raise ValueError(f'{ident}: security required for real OPC UA mode')
            for envname in ('username_env', 'password_env'):
                if item.get(envname) and not os.getenv(item[envname]):
                    raise ValueError(f'{ident}: missing environment {item[envname]}')
        item['_variables'] = variables
    return [d for d in devices if d['enabled']]
