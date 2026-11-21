"""Executes pure-Python client recipes extracted from client_recipes.md.

Mirrors test_image_recipe.py: compiles the shipped markdown blocks directly
rather than copying helper code into the test file, so prose edits cannot
silently drift from verified behaviour.

Run: uv run pytest skills/heylook-provider/tests/ -q
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pytest

DOC = (
    Path(__file__).resolve().parents[1]
    / "skills" / "heylook-provider" / "references" / "client_recipes.md"
)


@lru_cache(maxsize=1)
def _python_blocks() -> list[str]:
    return re.findall(r"```python\n(.*?)```", DOC.read_text(), re.S)


def _block_with(needle: str) -> str:
    matches = [b for b in _python_blocks() if needle in b]
    assert len(matches) == 1, f"expected 1 block with {needle!r}, found {len(matches)}"
    return matches[0]


@lru_cache(maxsize=1)
def _preset_ns() -> dict:
    ns: dict = {}
    exec(compile(_block_with("def apply_preset_to_request"), "client_recipes.md:preset", "exec"), ns)
    return ns


@lru_cache(maxsize=1)
def _thinking_ns() -> dict:
    ns: dict = {}
    exec(compile(_block_with("def thinking_options"), "client_recipes.md:thinking", "exec"), ns)
    return ns


@lru_cache(maxsize=1)
def _embeddings_ns() -> dict:
    ns: dict = {}
    exec(compile(_block_with("def plan_embedding_batches"), "client_recipes.md:embeddings", "exec"), ns)
    return ns


@lru_cache(maxsize=1)
def _streaming_ns() -> dict:
    ns: dict = {}
    exec(compile(_block_with("def stream_message"), "client_recipes.md:streaming", "exec"), ns)
    return ns


class TestPresetExpansion:
    def test_override_box_leaves_existing_system_prompt_when_preset_prompt_empty(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        model_row = {"capabilities": ["chat"]}
        for blank in (None, ""):
            out = apply_preset(
                {"system_prompt": blank, "params": {"temperature": 0.4}},
                model_row,
                {"model": "m1", "system": "Keep me", "messages": [{"role": "user", "content": "hi"}]},
            )
            assert out["system"] == "Keep me"
            assert out["temperature"] == 0.4

    def test_empty_preset_prompt_omits_system_key_when_caller_omits_it(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        out = apply_preset(
            {"system_prompt": None, "params": {"top_p": 0.9}},
            {"capabilities": ["chat"]},
            {"model": "m1", "messages": []},
        )
        assert "system" not in out
        assert out["top_p"] == 0.9

    def test_renames_thinking_and_budget_and_merges_into_object(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        model_row = {"capabilities": ["chat", "thinking", "thinking_budget"]}
        out = apply_preset(
            {
                "system_prompt": "Be concise.",
                "params": {"enable_thinking": True, "thinking_budget_tokens": 256, "temperature": 0.7},
            },
            model_row,
            {"model": "m1", "messages": []},
        )
        assert out["system"] == "Be concise."
        assert out["thinking"] == {"type": "enabled", "budget_tokens": 256}
        assert "enable_thinking" not in out
        assert "thinking_budget_tokens" not in out

    def test_drops_thinking_keys_when_model_lacks_capabilities(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        out = apply_preset(
            {
                "system_prompt": None,
                "params": {"enable_thinking": False, "thinking_budget_tokens": 128, "seed": 42},
            },
            {"capabilities": ["chat"]},
            {"model": "m1", "messages": []},
        )
        assert "thinking" not in out
        assert out["seed"] == 42

    def test_filters_reasoning_effort_against_model_depth(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        model_row = {
            "capabilities": ["chat", "reasoning_effort"],
            "engine": {"thinking": {"depth": {
                "values": ["low", "high"],
                "aliases": {"med": "medium"},
                "unknown": "raises",
            }}},
        }
        dropped = apply_preset(
            {"params": {"reasoning_effort": "xhigh"}},
            model_row,
            {"model": "m1", "messages": []},
        )
        assert "reasoning_effort" not in dropped

        kept_alias = apply_preset(
            {"params": {"reasoning_effort": "med"}},
            model_row,
            {"model": "m1", "messages": []},
        )
        assert kept_alias["reasoning_effort"] == "med"

        verbatim_row = {
            "capabilities": ["chat", "reasoning_effort"],
            "engine": {"thinking": {"depth": {"values": ["low"], "unknown": "verbatim"}}},
        }
        kept_verbatim = apply_preset(
            {"params": {"reasoning_effort": "custom_word"}},
            verbatim_row,
            {"model": "m1", "messages": []},
        )
        assert kept_verbatim["reasoning_effort"] == "custom_word"

    def test_caller_fields_win_over_preset(self):
        apply_preset = _preset_ns()["apply_preset_to_request"]
        out = apply_preset(
            {"system_prompt": "Preset system", "params": {"temperature": 0.2}},
            {"capabilities": ["chat"]},
            {"model": "m1", "system": "Caller system", "temperature": 0.8, "messages": []},
        )
        assert out["system"] == "Caller system"
        assert out["temperature"] == 0.8


class TestThinkingOptions:
    def test_folds_off_values_and_omits_redundant_on_when_default_active(self):
        thinking_options = _thinking_ns()["thinking_options"]
        row = {
            "engine": {
                "thinking": {
                    "switch": "enable_thinking",
                    "depth": {
                        "values": ["none", "minimal", "high"],
                        "off": ["none"],
                        "default": "minimal",
                    },
                }
            }
        }
        opts = thinking_options(row)
        assert opts == [
            ("Default", {}),
            ("Off", {"thinking": False}),
            ("minimal", {"reasoning_effort": "minimal"}),
            ("high", {"reasoning_effort": "high"}),
        ]

    def test_offers_on_when_default_is_null_or_in_off(self):
        thinking_options = _thinking_ns()["thinking_options"]
        row = {
            "engine": {
                "thinking": {
                    "switch": "enable_thinking",
                    "depth": {"values": ["off", "low"], "off": ["off"], "default": "off"},
                }
            }
        }
        opts = thinking_options(row)
        assert opts == [
            ("Default", {}),
            ("Off", {"thinking": False}),
            ("On", {"thinking": True}),
            ("low", {"reasoning_effort": "low"}),
        ]


class TestEmbeddingBatchPlanner:
    def test_splits_by_item_limit_and_media_budget(self):
        plan = _embeddings_ns()["plan_embedding_batches"]
        limits = {"items": 2, "request_media_bytes": 1000}
        # base64 length 400 -> 300 decoded bytes; 75% of 1000 = 750
        item_300 = {"content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "A" * 400}}]}
        item_600 = {"content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "A" * 800}}]}
        text_only = {"content": [{"type": "text", "text": "hello"}]}

        batches = plan([text_only, text_only, text_only], limits)
        assert [len(b) for b in batches] == [2, 1]

        media_batches = plan([item_300, item_300, item_600], limits)
        assert [len(b) for b in media_batches] == [2, 1]

    def test_rejects_single_item_exceeding_media_cap(self):
        plan = _embeddings_ns()["plan_embedding_batches"]
        limits = {"items": 16, "request_media_bytes": 100}
        oversized = {"content": [{"type": "video", "source": {"type": "base64", "media_type": "video/mp4", "data": "A" * 200}}]}
        with pytest.raises(ValueError):
            plan([oversized], limits)


def test_url_recipes_percent_encode_model_id():
    image_plan_block = _block_with("def image_plan")
    load_block = _block_with("/load")
    assert "quote(model" in image_plan_block
    assert "quote(model" in load_block


class TestStreamingAuthAndErrorHandling:
    def test_auth_headers_resolves_explicit_then_env_then_empty(self, monkeypatch):
        auth_headers = _streaming_ns()["_auth_headers"]
        monkeypatch.delenv("HEYLOOK_API_KEY", raising=False)
        assert auth_headers() == {}

        monkeypatch.setenv("HEYLOOK_API_KEY", "env-key")
        assert auth_headers() == {"x-api-key": "env-key"}
        assert auth_headers("explicit-key") == {"x-api-key": "explicit-key"}

    def test_http_error_distinguishes_503_overloaded_from_auth_misconfigured(self):
        import httpx

        ns = _streaming_ns()
        http_error = ns["_http_error"]
        overloaded_cls = ns["Overloaded"]

        overloaded_res = httpx.Response(
            503,
            headers={"Retry-After": "4"},
            json={"error": {"code": "model_overloaded", "message": "busy"}},
        )
        err_busy = http_error(overloaded_res)
        assert isinstance(err_busy, overloaded_cls)
        assert err_busy.retry_after == 4.0

        misconf_res = httpx.Response(
            503,
            json={
                "detail": "Key file has mode 0644; run chmod 600",
                "error": {"code": "auth_misconfigured", "message": "Key file has mode 0644"},
            },
        )
        err_misconf = http_error(misconf_res)
        assert not isinstance(err_misconf, overloaded_cls)
        assert "0644" in str(err_misconf)
