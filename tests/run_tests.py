import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tests.test_extractors import test_extract_signal_context, test_extract_token_context
from tests.test_live_service import (
    test_live_service_loads_token_payload_from_file_directory,
    test_live_service_supports_nested_command_paths,
    test_live_service_watchtoday_and_wallet_file_modes,
)
from tests.test_square_posts import (
    test_build_square_post_contains_key_fields,
    test_publish_square_post_dry_run,
)
from tests.test_normalizers import (
    test_normalize_signal_context,
    test_normalize_token_context,
    test_normalize_wallet_context,
    test_normalize_watch_today_context,
)
from tests.test_runtime_bridge_templates import (
    test_run_signal_flow,
    test_run_token_flow,
    test_run_token_flow_uses_raw_payload_when_provided,
    test_run_wallet_flow,
    test_run_watchtoday_flow,
    test_run_watchtoday_flow_uses_raw_payload_when_provided,
)


def main() -> None:
    test_normalize_token_context()
    test_normalize_wallet_context()
    test_normalize_watch_today_context()
    test_normalize_signal_context()
    test_extract_token_context()
    test_extract_signal_context()
    test_run_token_flow()
    test_run_signal_flow()
    test_run_wallet_flow()
    test_run_watchtoday_flow()
    test_run_token_flow_uses_raw_payload_when_provided()
    test_run_watchtoday_flow_uses_raw_payload_when_provided()
    test_live_service_loads_token_payload_from_file_directory(Path("/tmp/ac_test_live1"))
    test_live_service_supports_nested_command_paths(Path("/tmp/ac_test_live2"))
    test_live_service_watchtoday_and_wallet_file_modes(Path("/tmp/ac_test_live3"))
    test_build_square_post_contains_key_fields()
    test_publish_square_post_dry_run()

    try:
        from tests.test_api import (
            test_health,
            test_token_endpoint,
            test_wallet_endpoint_rejects_bad_address,
            test_watchtoday_endpoint,
        )
        from tests.test_bridge_api import (
            test_bridge_health,
            test_bridge_runtime_requires_entity_for_token,
            test_bridge_runtime_token_contract,
        )
    except ModuleNotFoundError:
        print("Skipping API tests: FastAPI test dependencies are not installed on this host.")
    else:
        test_health()
        test_token_endpoint()
        test_watchtoday_endpoint()
        test_wallet_endpoint_rejects_bad_address()
        test_bridge_health()
        test_bridge_runtime_token_contract()
        test_bridge_runtime_requires_entity_for_token()

    print("All tests passed.")


if __name__ == "__main__":
    main()
