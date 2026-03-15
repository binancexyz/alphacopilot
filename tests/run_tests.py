import os
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tests.test_extractors import (
    test_extract_audit_context_preserves_validity_flags,
    test_extract_audit_context_normalizes_snake_case_validity_flags,
    test_extract_signal_context,
    test_extract_signal_context_enriches_market_and_futures_fields,
    test_extract_signal_context_marks_fresh_when_signal_has_data_but_age_is_missing,
    test_extract_token_context,
    test_extract_wallet_context_from_address_list,
    test_extract_watch_today_context_from_skill_shapes,
)
from tests.test_live_service import (
    test_live_service_loads_token_payload_from_file_directory,
    test_live_service_marks_bridge_unavailable_runtime_state,
    test_live_service_marks_partial_watch_board,
    test_live_service_supports_nested_command_paths,
    test_live_service_unwraps_bridge_envelope_and_surfaces_partial_skill_warning,
    test_live_service_watchtoday_and_wallet_file_modes,
)
from tests.test_square_posts import (
    test_build_square_post_contains_key_fields,
    test_masked_square_key_masks_full_secret,
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
from tests.test_analyzer_return_types import test_analyzers_return_analysis_brief_instances
from tests.test_audit_analysis import (
    test_analyze_audit_adds_market_context_when_market_data_is_available,
    test_analyze_audit_adds_signal_lens_when_smart_money_is_active,
    test_analyze_audit_marks_limited_validity_when_payload_is_partial,
    test_analyze_audit_marks_valid_supported_payload,
    test_analyze_audit_pulls_bonding_curve_data_from_meme_lens,
    test_analyze_audit_respects_validity_flags_from_extracted_live_payload,
)
from tests.test_skill_bridge import (
    test_fetch_live_bundle_builds_wallet_payload_with_skill_refs,
    test_fetch_live_bundle_marks_partial_failure_without_dropping_other_skill_data,
)
from tests.test_skill_registry import test_skill_registry_resolves_query_token_info_reference
from tests.test_audit_judgment_states import (
    test_audit_does_not_imply_clean_when_result_is_unsupported,
    test_audit_marks_blocked_structural_risk,
    test_audit_marks_tax_heavy_as_tradable_but_flagged,
)
from tests.test_brief_analysis import (
    test_analyze_brief_packs_market_fields_and_boosts_active_smart_money_quality,
    test_analyze_brief_handles_unmatched_signal_with_binance_spot,
    test_analyze_brief_uses_binance_spot_context,
)
from tests.test_brief_posture_aware import test_analyze_brief_adds_portfolio_posture_note
from tests.test_careers_tracker import (
    test_build_summary_and_short_note,
    test_extract_jobs_from_jsonld_html,
    test_summarize_snapshot_contains_takeaway,
)
from tests.test_config_validation import test_config_warnings_reports_live_without_base_url
from tests.test_env_autoload import test_config_autoload_reads_local_env
from tests.test_exposure_groups import (
    test_classify_asset_supports_exchange_and_data_buckets,
    test_top_groups_ranks_exposure_buckets,
)
from tests.test_factory import test_factory_defaults_to_mock
from tests.test_formatter_thin_payloads import (
    test_format_audit_card_surfaces_limited_validity,
    test_format_signal_card_keeps_setup_structure_when_thin,
    test_format_token_card_keeps_ownership_structure_when_thin,
    test_format_watchtoday_card_keeps_sections_when_thin,
)
from tests.test_holdings_thin_states import (
    test_portfolio_unavailable_state_keeps_holdings_block,
    test_wallet_thin_state_keeps_premium_structure,
)
from tests.test_heuristics import (
    test_token_conviction_low_when_risks_high,
    test_token_signal_quality_high,
)
from tests.test_live_extractors_depth import (
    test_extract_meme_context_enriches_participation_fields,
    test_extract_watch_today_context_adds_exchange_board,
)
from tests.test_market_watch import test_watch_today_adds_exchange_board_from_binance_spot
from tests.test_meme_analysis import test_analyze_meme_includes_evidence_quality
from tests.test_portfolio_analysis import (
    test_analyze_portfolio_builds_balanced_snapshot,
    test_analyze_portfolio_includes_margin_exposure,
    test_analyze_portfolio_normalizes_ld_assets,
)
from tests.test_portfolio_history import (
    test_append_and_load_history,
    test_describe_delta_detects_material_changes,
    test_describe_trend_detects_short_local_direction,
)
from tests.test_premium_output_formatters import (
    test_format_audit_card_renders_market_context_section,
    test_format_compact_brief_card_renders_market_section_and_wallet_count,
    test_format_portfolio_card_renders_margin_trend_and_five_holdings,
    test_format_signal_card_renders_context_section,
    test_format_token_card_renders_market_and_momentum_sections,
    test_format_wallet_card_renders_value_holdings_and_narrative,
    test_format_watchtoday_card_caps_extra_sections_at_six_total,
)
from tests.test_portfolio_trend_tag import test_short_trend_tag_shape
from tests.test_posture_aware_analysis import (
    test_watchtoday_adds_portfolio_posture_note,
)
from tests.test_price_analysis import (
    test_analyze_price_uses_binance_spot_when_available,
    test_fetch_binance_spot_quote_prefers_usdt_pair,
)
from tests.test_rendered_examples_consistency import (
    test_compact_brief_thin_footer_does_not_duplicate_liquidity_warning,
    test_token_ownership_block_keeps_three_rows_when_partial,
)
from tests.test_runtime_bridge_live_stub import (
    test_signal_from_raw_returns_text,
    test_token_from_raw_returns_text,
    test_wallet_from_raw_returns_text,
    test_watchtoday_from_raw_returns_text,
)
from tests.test_runtime_demo import test_runtime_demo_signal, test_runtime_demo_token
from tests.test_runtime_footer_cleanup import (
    test_signal_footer_prefers_dependency_label_over_degraded_duplication,
    test_watchtoday_footer_prefers_clean_runtime_labels,
)
from tests.test_runtime_health import (
    test_runtime_status_reports_file_health,
    test_runtime_status_reports_unconfigured,
)
from tests.test_runtime_report import (
    test_apply_runtime_meta_adds_warning_to_brief,
    test_build_runtime_meta_mock_mode_shape,
)
from tests.test_signal_check import test_analyze_signal_adds_binance_spot_unmatched_note
from tests.test_signal_heuristics import (
    test_signal_quality_penalizes_thin_and_crowded_futures_setup,
    test_signal_quality_triggered_without_context_is_not_auto_high,
    test_signal_quality_watch_without_context_stays_low,
)
from tests.test_signal_judgment_states import (
    test_signal_brief_marks_early_setup_below_trigger,
    test_signal_brief_marks_late_setup_when_exit_pressure_is_high,
    test_signal_brief_marks_stale_setup_even_if_signal_exists,
    test_signal_quality_blocked_when_audit_gate_blocks,
    test_signal_quality_high_for_fresh_trigger_holding_setup,
)
from tests.test_signal_live_brief import test_build_signal_brief
from tests.test_signal_posture_aware import test_signal_adds_portfolio_posture_note
from tests.test_square_diary_context import (
    test_build_morning_diary_post_uses_market_snapshot_mode,
    test_build_night_diary_post_includes_market_wrap_and_futures,
    test_choose_morning_mode_prefers_signal_then_narrative,
    test_contextual_builder_line_can_use_posture_note,
    test_contextual_market_line_can_use_market_tone,
    test_fetch_morning_market_snapshot_returns_structured_lines,
)
from tests.test_thin_copy_polish import (
    test_compact_brief_thin_copy_uses_limited_read_language,
    test_token_thin_copy_uses_signal_not_confirmed,
    test_watchtoday_thin_copy_is_less_placeholder_like,
)
from tests.test_token_analysis import test_analyze_token_adds_binance_spot_tag
from tests.test_token_judgment_states import (
    test_token_brief_marks_active_but_ownership_risky,
    test_token_brief_marks_active_supportive_structure,
    test_token_brief_marks_blocked_setup_when_audit_blocks,
    test_token_brief_marks_late_setup_when_exit_pressure_is_high,
    test_token_brief_marks_stale_setup_when_timing_is_old,
)
from tests.test_token_liquidity_rendering import (
    test_token_render_uses_explicit_liquidity_tag_when_present,
)
from tests.test_token_live_brief import test_build_token_brief
from tests.test_token_posture_aware import test_token_adds_portfolio_posture_note
from tests.test_token_real_case_improvements import (
    test_analyze_token_propagates_quote_context_into_deep_brief,
    test_deep_brief_uses_market_active_setup_absent_when_price_exists_but_signal_does_not,
)
from tests.test_token_render_alignment import (
    test_token_render_aligns_active_verdict_with_snapshot_signal,
    test_token_render_aligns_late_verdict_with_snapshot_signal,
)
from tests.test_token_risk_cleanup import (
    test_analyze_token_removes_stale_low_liquidity_risk_when_quote_backfill_is_strong,
)
from tests.test_token_risk_compression import (
    test_token_footer_compresses_upgradeable_contract_risk,
    test_token_footer_compresses_user_reported_risk,
)
from tests.test_wallet_analysis import test_analyze_wallet_adds_lead_holding_tag
from tests.test_wallet_live_brief import test_build_wallet_brief
from tests.test_wallet_live_extractors import (
    test_extract_wallet_context_adds_audit_overlay_when_holdings_are_flagged,
    test_extract_wallet_context_builds_style_profile_and_exposures,
)
from tests.test_watchtoday_live_brief import (
    test_build_watchtoday_brief,
    test_build_watchtoday_brief_includes_lane_coverage_when_partial,
)
from tests.test_watchtoday_live_extractors import (
    test_extract_watchtoday_context_backfills_sparse_lanes_from_exchange_board_and_narratives,
)
from tests.test_alpha_extractors import (
    test_extract_alpha_context_alpha_listed,
    test_extract_alpha_context_not_alpha,
    test_extract_alpha_context_empty_raw,
)
from tests.test_depth_kline_extractors import (
    test_extract_token_context_spot_and_kline,
    test_extract_token_context_legacy_spot,
)
from tests.test_dynamic_data_extractors import (
    test_extract_token_context_dynamic_data,
    test_extract_token_context_incomplete_dynamic,
)
from tests.test_futures_data_extractors import (
    test_extract_futures_context,
    test_enrich_futures_sentiment,
)
from tests.test_futures_extractors import (
    test_extract_futures_context_basic,
    test_extract_futures_context_extreme_funding,
    test_extract_futures_context_empty,
    test_token_context_enriched_with_futures,
    test_token_context_with_spot_enrichment,
)
from tests.test_klines_extras_extractors import (
    test_extract_spot_alpha_klines_and_trades,
    test_extract_futures_klines_and_ticker,
)
from tests.test_pnl_rank_extractors import (
    test_extract_watch_today_context_pnl_rank,
)
from tests.test_skill_mapping_completeness import (
    test_all_commands_have_nonempty_skill_lists,
    test_optional_commands_are_valid,
    test_alpha_command_exists,
    test_futures_command_exists,
    test_token_has_optional_enrichments,
    test_signal_command_has_market_rank_and_futures_support,
    test_audit_command_has_signal_support,
)


def main() -> None:
    # --- normalizers & extractors ---
    test_normalize_token_context()
    test_normalize_wallet_context()
    test_normalize_watch_today_context()
    test_normalize_signal_context()
    test_extract_token_context()
    test_extract_signal_context()
    test_extract_signal_context_enriches_market_and_futures_fields()
    test_extract_signal_context_marks_fresh_when_signal_has_data_but_age_is_missing()
    test_extract_audit_context_preserves_validity_flags()
    test_extract_audit_context_normalizes_snake_case_validity_flags()
    test_extract_wallet_context_from_address_list()
    test_extract_wallet_context_adds_audit_overlay_when_holdings_are_flagged()
    test_extract_watch_today_context_from_skill_shapes()

    # --- runtime bridge templates ---
    test_run_token_flow()
    test_run_signal_flow()
    test_run_wallet_flow()
    test_run_watchtoday_flow()
    test_run_token_flow_uses_raw_payload_when_provided()
    test_run_watchtoday_flow_uses_raw_payload_when_provided()

    # --- live service (tmp_path adapted) ---
    test_live_service_loads_token_payload_from_file_directory(Path(tempfile.mkdtemp()))
    test_live_service_supports_nested_command_paths(Path(tempfile.mkdtemp()))
    test_live_service_watchtoday_and_wallet_file_modes(Path(tempfile.mkdtemp()))
    test_live_service_unwraps_bridge_envelope_and_surfaces_partial_skill_warning(Path(tempfile.mkdtemp()))
    test_live_service_marks_bridge_unavailable_runtime_state()
    test_live_service_marks_partial_watch_board()

    # --- square posts ---
    test_build_square_post_contains_key_fields()
    test_publish_square_post_dry_run()
    test_masked_square_key_masks_full_secret()

    # --- analyzer return types ---
    test_analyzers_return_analysis_brief_instances()

    # --- audit analysis ---
    test_analyze_audit_marks_limited_validity_when_payload_is_partial()
    test_analyze_audit_marks_valid_supported_payload()
    test_analyze_audit_respects_validity_flags_from_extracted_live_payload()
    test_analyze_audit_pulls_bonding_curve_data_from_meme_lens()
    test_analyze_audit_adds_signal_lens_when_smart_money_is_active()
    test_analyze_audit_adds_market_context_when_market_data_is_available()

    # --- skill registry + bridge ---
    test_skill_registry_resolves_query_token_info_reference()
    test_fetch_live_bundle_builds_wallet_payload_with_skill_refs()
    test_fetch_live_bundle_marks_partial_failure_without_dropping_other_skill_data()

    # --- audit judgment states ---
    test_audit_marks_blocked_structural_risk()
    test_audit_marks_tax_heavy_as_tradable_but_flagged()
    test_audit_does_not_imply_clean_when_result_is_unsupported()

    # --- brief analysis ---
    test_analyze_brief_uses_binance_spot_context()
    test_analyze_brief_handles_unmatched_signal_with_binance_spot()
    test_analyze_brief_packs_market_fields_and_boosts_active_smart_money_quality()

    # --- brief posture aware ---
    test_analyze_brief_adds_portfolio_posture_note()

    # --- careers tracker ---
    test_extract_jobs_from_jsonld_html()
    test_summarize_snapshot_contains_takeaway()
    test_build_summary_and_short_note()

    # --- config validation ---
    test_config_warnings_reports_live_without_base_url()

    # --- env autoload (tmp_path adapted) ---
    test_config_autoload_reads_local_env(Path(tempfile.mkdtemp()))

    # --- exposure groups ---
    test_top_groups_ranks_exposure_buckets()
    test_classify_asset_supports_exchange_and_data_buckets()

    # --- factory ---
    test_factory_defaults_to_mock()

    # --- formatter thin payloads ---
    test_format_signal_card_keeps_setup_structure_when_thin()
    test_format_token_card_keeps_ownership_structure_when_thin()
    test_format_watchtoday_card_keeps_sections_when_thin()
    test_format_audit_card_surfaces_limited_validity()
    test_format_compact_brief_card_renders_market_section_and_wallet_count()
    test_format_token_card_renders_market_and_momentum_sections()
    test_format_signal_card_renders_context_section()
    test_format_watchtoday_card_caps_extra_sections_at_six_total()
    test_format_audit_card_renders_market_context_section()
    test_format_portfolio_card_renders_margin_trend_and_five_holdings()
    test_format_wallet_card_renders_value_holdings_and_narrative()

    # --- holdings thin states ---
    test_wallet_thin_state_keeps_premium_structure()
    test_portfolio_unavailable_state_keeps_holdings_block()

    # --- heuristics ---
    test_token_signal_quality_high()
    test_token_conviction_low_when_risks_high()

    # --- live extractors depth ---
    test_extract_meme_context_enriches_participation_fields()
    test_extract_watch_today_context_adds_exchange_board()

    # --- market watch ---
    test_watch_today_adds_exchange_board_from_binance_spot()

    # --- meme analysis ---
    test_analyze_meme_includes_evidence_quality()

    # --- portfolio analysis ---
    test_analyze_portfolio_builds_balanced_snapshot()
    test_analyze_portfolio_normalizes_ld_assets()
    test_analyze_portfolio_includes_margin_exposure()

    # --- portfolio history (tmp_path adapted) ---
    test_describe_delta_detects_material_changes()
    test_append_and_load_history(Path(tempfile.mkdtemp()))
    test_describe_trend_detects_short_local_direction()

    # --- portfolio trend tag ---
    test_short_trend_tag_shape()

    # --- posture aware analysis ---
    test_watchtoday_adds_portfolio_posture_note()

    # --- price analysis ---
    test_fetch_binance_spot_quote_prefers_usdt_pair()
    test_analyze_price_uses_binance_spot_when_available()

    # --- rendered examples consistency ---
    test_compact_brief_thin_footer_does_not_duplicate_liquidity_warning()
    test_token_ownership_block_keeps_three_rows_when_partial()

    # --- runtime bridge live stub ---
    test_token_from_raw_returns_text()
    test_signal_from_raw_returns_text()
    test_wallet_from_raw_returns_text()
    test_watchtoday_from_raw_returns_text()

    # --- runtime demo ---
    test_runtime_demo_token()
    test_runtime_demo_signal()

    # --- runtime footer cleanup ---
    test_signal_footer_prefers_dependency_label_over_degraded_duplication()
    test_watchtoday_footer_prefers_clean_runtime_labels()

    # --- runtime health (tmp_path adapted) ---
    test_runtime_status_reports_unconfigured()
    test_runtime_status_reports_file_health(Path(tempfile.mkdtemp()))

    # --- runtime report ---
    test_build_runtime_meta_mock_mode_shape()
    test_apply_runtime_meta_adds_warning_to_brief()

    # --- signal check ---
    test_analyze_signal_adds_binance_spot_unmatched_note()

    # --- signal heuristics ---
    test_signal_quality_triggered_without_context_is_not_auto_high()
    test_signal_quality_watch_without_context_stays_low()
    test_signal_quality_penalizes_thin_and_crowded_futures_setup()

    # --- signal judgment states ---
    test_signal_quality_high_for_fresh_trigger_holding_setup()
    test_signal_brief_marks_late_setup_when_exit_pressure_is_high()
    test_signal_brief_marks_stale_setup_even_if_signal_exists()
    test_signal_brief_marks_early_setup_below_trigger()
    test_signal_quality_blocked_when_audit_gate_blocks()

    # --- signal live brief ---
    test_build_signal_brief()

    # --- signal posture aware ---
    test_signal_adds_portfolio_posture_note()

    # --- square diary context ---
    test_contextual_market_line_can_use_market_tone()
    test_contextual_builder_line_can_use_posture_note()
    test_choose_morning_mode_prefers_signal_then_narrative()
    test_fetch_morning_market_snapshot_returns_structured_lines()
    test_build_morning_diary_post_uses_market_snapshot_mode()
    test_build_night_diary_post_includes_market_wrap_and_futures()

    # --- thin copy polish ---
    test_compact_brief_thin_copy_uses_limited_read_language()
    test_watchtoday_thin_copy_is_less_placeholder_like()
    test_token_thin_copy_uses_signal_not_confirmed()

    # --- token analysis ---
    test_analyze_token_adds_binance_spot_tag()

    # --- token judgment states ---
    test_token_brief_marks_active_supportive_structure()
    test_token_brief_marks_active_but_ownership_risky()
    test_token_brief_marks_late_setup_when_exit_pressure_is_high()
    test_token_brief_marks_stale_setup_when_timing_is_old()
    test_token_brief_marks_blocked_setup_when_audit_blocks()

    # --- token liquidity rendering ---
    test_token_render_uses_explicit_liquidity_tag_when_present()

    # --- token live brief ---
    test_build_token_brief()

    # --- token posture aware ---
    test_token_adds_portfolio_posture_note()

    # --- token real case improvements ---
    test_analyze_token_propagates_quote_context_into_deep_brief()
    test_deep_brief_uses_market_active_setup_absent_when_price_exists_but_signal_does_not()

    # --- token render alignment ---
    test_token_render_aligns_active_verdict_with_snapshot_signal()
    test_token_render_aligns_late_verdict_with_snapshot_signal()

    # --- token risk cleanup ---
    test_analyze_token_removes_stale_low_liquidity_risk_when_quote_backfill_is_strong()

    # --- token risk compression ---
    test_token_footer_compresses_user_reported_risk()
    test_token_footer_compresses_upgradeable_contract_risk()

    # --- wallet analysis ---
    test_analyze_wallet_adds_lead_holding_tag()

    # --- wallet live brief ---
    test_build_wallet_brief()

    # --- wallet live extractors ---
    test_extract_wallet_context_builds_style_profile_and_exposures()

    # --- watchtoday live brief ---
    test_build_watchtoday_brief()
    test_build_watchtoday_brief_includes_lane_coverage_when_partial()

    # --- watchtoday live extractors ---
    test_extract_watchtoday_context_backfills_sparse_lanes_from_exchange_board_and_narratives()

    # --- alpha extractors ---
    test_extract_alpha_context_alpha_listed()
    test_extract_alpha_context_not_alpha()
    test_extract_alpha_context_empty_raw()

    # --- depth & kline extractors ---
    test_extract_token_context_spot_and_kline()
    test_extract_token_context_legacy_spot()

    # --- dynamic data extractors ---
    test_extract_token_context_dynamic_data()
    test_extract_token_context_incomplete_dynamic()

    # --- futures data extractors ---
    test_extract_futures_context()
    test_enrich_futures_sentiment()

    # --- futures extractors ---
    test_extract_futures_context_basic()
    test_extract_futures_context_extreme_funding()
    test_extract_futures_context_empty()
    test_token_context_enriched_with_futures()
    test_token_context_with_spot_enrichment()

    # --- klines extras extractors ---
    test_extract_spot_alpha_klines_and_trades()
    test_extract_futures_klines_and_ticker()

    # --- pnl rank extractors ---
    test_extract_watch_today_context_pnl_rank()

    # --- skill mapping completeness ---
    test_all_commands_have_nonempty_skill_lists()
    test_optional_commands_are_valid()
    test_alpha_command_exists()
    test_futures_command_exists()
    test_token_has_optional_enrichments()
    test_signal_command_has_market_rank_and_futures_support()
    test_audit_command_has_signal_support()

    # --- API tests (conditional — require FastAPI) ---
    try:
        from tests.test_api_guard import (
            test_auth_rejects_wrong_key,
            test_guard_status_shape,
            test_rate_limit_allows_first_request,
        )
        from tests.test_api import (
            test_brief_endpoint,
            test_brief_deep_endpoint,
            test_health,
            test_health_payload_shape,
            test_holdings_endpoint,
            test_runtime_report_endpoint,
            test_wallet_endpoint_rejects_bad_address,
            test_watchtoday_endpoint,
        )
        from tests.test_bridge_api import (
            test_bridge_health,
            test_bridge_runtime_requires_entity_for_token,
            test_bridge_runtime_token_contract,
            test_first_matching_token_prefers_exact_symbol,
        )
    except ModuleNotFoundError:
        print("Skipping API tests: FastAPI test dependencies are not installed on this host.")
    else:
        test_guard_status_shape()
        test_rate_limit_allows_first_request()
        test_auth_rejects_wrong_key()
        test_health()
        test_health_payload_shape()
        test_brief_endpoint()
        test_brief_deep_endpoint()
        test_holdings_endpoint()
        test_watchtoday_endpoint()
        test_wallet_endpoint_rejects_bad_address()
        test_runtime_report_endpoint()
        test_bridge_health()
        test_bridge_runtime_token_contract()
        test_bridge_runtime_requires_entity_for_token()
        test_first_matching_token_prefers_exact_symbol()

    # --- Live integration tests (conditional — require LIVE_TESTS=1) ---
    if os.environ.get("LIVE_TESTS") == "1":
        from tests.test_live_integration import (
            test_live_bridge_token_bnb,
            test_live_bridge_token_sol,
            test_live_bridge_token_eth,
            test_live_bridge_signal_bnb,
            test_live_bridge_signal_doge,
            test_live_bridge_watchtoday,
            test_live_bridge_audit_bnb,
            test_live_bridge_futures_bnb,
            test_live_bridge_futures_eth,
            test_live_bridge_alpha_bnb,
            test_live_bridge_meme_doge,
            test_live_bridge_meme_pepe,
            test_live_bridge_wallet,
            test_live_bridge_portfolio,
            test_live_pipeline_token_bnb,
            test_live_pipeline_token_sol,
            test_live_pipeline_signal_bnb,
            test_live_pipeline_signal_doge,
            test_live_pipeline_watchtoday,
            test_live_pipeline_wallet,
            test_live_pipeline_futures_bnb,
            test_live_pipeline_alpha_bnb,
            test_live_pipeline_audit_bnb,
            test_live_pipeline_meme_doge,
            test_live_bridge_meta_shape,
            test_live_bridge_response_time,
        )

        print("\n--- Live bridge tests ---")
        test_live_bridge_token_bnb()
        test_live_bridge_token_sol()
        test_live_bridge_token_eth()
        test_live_bridge_signal_bnb()
        test_live_bridge_signal_doge()
        test_live_bridge_watchtoday()
        test_live_bridge_audit_bnb()
        test_live_bridge_futures_bnb()
        test_live_bridge_futures_eth()
        test_live_bridge_alpha_bnb()
        test_live_bridge_meme_doge()
        test_live_bridge_meme_pepe()
        test_live_bridge_wallet()
        test_live_bridge_portfolio()

        print("\n--- Live pipeline tests ---")
        test_live_pipeline_token_bnb()
        test_live_pipeline_token_sol()
        test_live_pipeline_signal_bnb()
        test_live_pipeline_signal_doge()
        test_live_pipeline_watchtoday()
        test_live_pipeline_wallet()
        test_live_pipeline_futures_bnb()
        test_live_pipeline_alpha_bnb()
        test_live_pipeline_audit_bnb()
        test_live_pipeline_meme_doge()

        print("\n--- Live meta tests ---")
        test_live_bridge_meta_shape()
        test_live_bridge_response_time()

        try:
            from tests.test_live_api_endpoints import (
                test_live_api_health,
                test_live_api_brief_bnb,
                test_live_api_brief_sol,
                test_live_api_brief_deep_bnb,
                test_live_api_signal_bnb,
                test_live_api_signal_doge,
                test_live_api_watchtoday,
                test_live_api_audit_bnb,
                test_live_api_alpha_bnb,
                test_live_api_futures_bnb,
                test_live_api_futures_eth,
                test_live_api_holdings,
            )
        except ModuleNotFoundError:
            print("Skipping live API tests: FastAPI test dependencies are not installed on this host.")
        else:
            print("\n--- Live API endpoint tests ---")
            test_live_api_health()
            test_live_api_brief_bnb()
            test_live_api_brief_sol()
            test_live_api_brief_deep_bnb()
            test_live_api_signal_bnb()
            test_live_api_signal_doge()
            test_live_api_watchtoday()
            test_live_api_audit_bnb()
            test_live_api_alpha_bnb()
            test_live_api_futures_bnb()
            test_live_api_futures_eth()
            test_live_api_holdings()
    else:
        print("Skipping live integration tests: set LIVE_TESTS=1 to enable.")

    print("All tests passed.")


if __name__ == "__main__":
    main()
