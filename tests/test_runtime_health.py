from pathlib import Path
import json

from src.services.live_service import LiveMarketDataService


def test_runtime_status_reports_unconfigured():
    service = LiveMarketDataService(base_url='')
    status = service.healthcheck()
    assert status['bridge_mode'] == 'unconfigured'
    assert status['healthcheck'] == 'unconfigured'


def test_runtime_status_reports_file_health(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = {
        'crypto-market-rank': {
            'top_narratives': ['AI'],
            'summary': 'Opportunity exists.',
        }
    }
    path = tmp_path / 'watchtoday.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    service = LiveMarketDataService(base_url=f'file://{tmp_path}')
    status = service.healthcheck()
    assert status['bridge_mode'] == 'file'
    assert status['healthcheck'] == 'ok'
    assert status['last_event']['status'] == 'ok'
