import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tests.test_extractors import test_extract_signal_context, test_extract_token_context
from tests.test_normalizers import (
    test_normalize_signal_context,
    test_normalize_token_context,
    test_normalize_wallet_context,
    test_normalize_watch_today_context,
)


def main() -> None:
    test_normalize_token_context()
    test_normalize_wallet_context()
    test_normalize_watch_today_context()
    test_normalize_signal_context()
    test_extract_token_context()
    test_extract_signal_context()
    print("All tests passed.")


if __name__ == "__main__":
    main()
