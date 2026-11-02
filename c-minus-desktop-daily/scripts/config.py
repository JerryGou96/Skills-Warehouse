"""Local JSON configuration; paths resolve beside the config, never the skill."""
import json, os, re
from pathlib import Path
from datetime import date
from zoneinfo import ZoneInfo

def valid_date(value):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Expected YYYY-MM-DD')
    date.fromisoformat(value)
    return value

def load_config():
    name = os.environ.get('C_MINUS_CONFIG')
    if not name:
        raise ValueError('Set C_MINUS_CONFIG to your local JSON config')
    file = Path(name).resolve()
    cfg = json.loads(file.read_text())
    for key in ('output_dir', 'runtime_dir', 'timezone', 'source_guild_id', 'source_channel_id', 'author_id', 'destination_account', 'destination_channel_id', 'cdp_endpoint'):
        if not isinstance(cfg.get(key), str) or not cfg[key].strip() or cfg[key].startswith('SET_'):
            raise ValueError(f'Configure {key}')
    for key in ('source_guild_id', 'source_channel_id', 'author_id', 'destination_channel_id'):
        if not re.fullmatch(r'\d+', cfg[key]):
            raise ValueError(f'{key} must be a numeric string')
    if cfg['source_channel_id'] == cfg['destination_channel_id']:
        raise ValueError('Source and destination channels must differ')
    ZoneInfo(cfg['timezone'])
    for key in ('output_dir', 'runtime_dir'):
        cfg[key] = str((file.parent / cfg[key]).resolve())
    return cfg
