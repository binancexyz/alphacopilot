import importlib.util
import os
import sys
from pathlib import Path


def test_config_autoload_reads_local_env(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    env_path = tmp_path / '.env'
    env_path.write_text('BINANCE_SQUARE_API_KEY=demo_key\n', encoding='utf-8')

    config_path = Path(__file__).resolve().parents[1] / 'src' / 'config.py'
    temp_config_path = tmp_path / 'config.py'
    source = config_path.read_text(encoding='utf-8').replace(
        "ROOT = Path(__file__).resolve().parents[1]",
        f"ROOT = Path(r'{tmp_path}')",
    )
    temp_config_path.write_text(source, encoding='utf-8')

    module_name = 'temp_bibipilot_config'
    spec = importlib.util.spec_from_file_location(module_name, temp_config_path)
    module = importlib.util.module_from_spec(spec)
    old = os.environ.pop('BINANCE_SQUARE_API_KEY', None)
    old_module = sys.modules.get(module_name)
    try:
        sys.modules[module_name] = module
        assert spec and spec.loader
        spec.loader.exec_module(module)
        assert module.settings.square_api_key == 'demo_key'
    finally:
        if old is not None:
            os.environ['BINANCE_SQUARE_API_KEY'] = old
        else:
            os.environ.pop('BINANCE_SQUARE_API_KEY', None)
        if old_module is not None:
            sys.modules[module_name] = old_module
        else:
            sys.modules.pop(module_name, None)
