from pathlib import Path
from app.config import load_devices

def test_demo_config():
    devices=load_devices(str(Path(__file__).parent.parent / 'config/machines.yaml'))
    assert len(devices)==1
    assert devices[0]['id']=='index_ms22_01'
