"""
game-deals plugin v2 的單元測試。

使用 FakePluginContext 模擬 Hermes PluginContext，
並以 unittest.mock.patch 攔截 ITAD API 呼叫。
"""

import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent


def _load_plugin_register():
    """
    使用 importlib 載入 plugin 的 __init__.py，
    模擬 Hermes 將 plugin 目錄加進 sys.path 後的載入行為。

    Returns:
        plugin 的 register 函式。
    """
    if str(PLUGIN_ROOT) not in sys.path:
        sys.path.insert(0, str(PLUGIN_ROOT))

    # 設定假 API key，避免 api_client._headers() 在 import 時失敗
    os.environ.setdefault("ITAD_API_KEY", "test-key-placeholder")

    spec = importlib.util.spec_from_file_location(
        "game_deals_plugin",
        PLUGIN_ROOT / "__init__.py",
        submodule_search_locations=[str(PLUGIN_ROOT)],
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["game_deals_plugin"] = mod
    spec.loader.exec_module(mod)
    return mod.register


class FakePluginContext:
    """最小化的 Hermes PluginContext 模擬。"""

    def __init__(self):
        self.tools: dict[str, dict] = {}
        self.hooks: list[tuple] = []

    def register_tool(self, *, name, toolset, schema, handler, description):
        self.tools[name] = {"schema": schema, "handler": handler}

    def register_hook(self, hook_name: str, callback):
        self.hooks.append((hook_name, callback))

    def call(self, tool_name: str, params: dict) -> dict:
        """呼叫已註冊的 handler，回傳解析後的 dict。"""
        return json.loads(self.tools[tool_name]["handler"](params))


@pytest.fixture(scope="module")
def ctx():
    """建立並完成 register() 的 FakePluginContext。"""
    register = _load_plugin_register()
    fake_ctx = FakePluginContext()
    register(fake_ctx)
    return fake_ctx


# ── 測試 register() 本身 ──────────────────────────────────────────────────────

def test_register_all_tools(ctx: FakePluginContext):
    """register() 應註冊三個工具。"""
    assert set(ctx.tools.keys()) == {"search_game", "get_game_prices", "get_top_deals"}


def test_register_post_tool_call_hook(ctx: FakePluginContext):
    """register() 應註冊 post_tool_call hook。"""
    assert "post_tool_call" in [name for name, _ in ctx.hooks]


def test_all_schemas_use_parameters_key(ctx: FakePluginContext):
    """所有工具 schema 必須使用 Hermes 格式的 'parameters' 欄位。"""
    for name, info in ctx.tools.items():
        assert "parameters" in info["schema"], f"{name} 缺少 'parameters' 欄位"
        assert "input_schema" not in info["schema"], f"{name} 不應有 'input_schema' 欄位"


# ── 測試 search_game ──────────────────────────────────────────────────────────

_FAKE_GAMES = [
    {"id": "uuid-hades-001", "title": "Hades", "slug": "hades", "type": "game", "mature": False, "assets": {}},
]

def test_search_game_found(ctx: FakePluginContext):
    """找到遊戲時應回傳 id、title、slug。"""
    with patch("game_deals_plugin.search_games", return_value=_FAKE_GAMES):
        result = ctx.call("search_game", {"title": "hades"})

    assert result["found"] == 1
    assert result["games"][0]["id"] == "uuid-hades-001"
    assert result["games"][0]["title"] == "Hades"


def test_search_game_not_found(ctx: FakePluginContext):
    """找不到遊戲時應回傳 found=0 與提示訊息。"""
    with patch("game_deals_plugin.search_games", return_value=[]):
        result = ctx.call("search_game", {"title": "xxxxxxxxnotexist"})

    assert result["found"] == 0
    assert "找不到" in result["message"]


def test_search_game_api_error(ctx: FakePluginContext):
    """API 失敗時應回傳含 error 欄位的 dict。"""
    with patch("game_deals_plugin.search_games", side_effect=Exception("timeout")):
        result = ctx.call("search_game", {"title": "hades"})

    assert "error" in result


# ── 測試 get_game_prices ──────────────────────────────────────────────────────

_FAKE_OVERVIEW = {
    "prices": [{
        "id": "uuid-hades-001",
        "current": {
            "shop": {"id": 61, "title": "Steam"},
            "price": {"amount": 299.0, "amountInt": 29900, "currency": "TWD"},
            "regular": {"amount": 597.0, "amountInt": 59700, "currency": "TWD"},
            "cut": 50,
            "voucher": None,
            "flag": None,
            "drm": [],
            "platforms": [],
            "timestamp": "2024-01-01T00:00:00Z",
            "expiry": None,
            "url": "https://store.steampowered.com/app/1145360",
        },
        "lowest": {
            "shop": {"id": 61, "title": "Steam"},
            "price": {"amount": 149.0, "amountInt": 14900, "currency": "TWD"},
            "regular": {"amount": 597.0, "amountInt": 59700, "currency": "TWD"},
            "cut": 75,
            "timestamp": "2023-06-15T00:00:00Z",
        },
        "bundled": 3,
        "urls": {"game": "https://isthereanydeal.com/game/hades/info/"},
    }],
    "bundles": [],
}

def test_get_game_prices_found(ctx: FakePluginContext):
    """找到價格時應正確解析 current_best 與 history_low。"""
    with patch("game_deals_plugin.get_game_overview", return_value=_FAKE_OVERVIEW):
        result = ctx.call("get_game_prices", {"game_id": "uuid-hades-001", "country": "TW"})

    assert result["country"] == "TW"
    assert result["current_best"]["shop"] == "Steam"
    assert result["current_best"]["price"] == "TWD 299.00"
    assert result["current_best"]["discount_percent"] == 50
    assert result["history_low"]["price"] == "TWD 149.00"
    assert result["history_low"]["discount_percent"] == 75


def test_get_game_prices_no_data(ctx: FakePluginContext):
    """查無資料時應回傳 found=False 與提示訊息。"""
    with patch("game_deals_plugin.get_game_overview", return_value={"prices": [], "bundles": []}):
        result = ctx.call("get_game_prices", {"game_id": "uuid-unknown"})

    assert result["found"] is False


def test_get_game_prices_api_error(ctx: FakePluginContext):
    """API 失敗時應回傳含 error 欄位的 dict。"""
    with patch("game_deals_plugin.get_game_overview", side_effect=Exception("403 Forbidden")):
        result = ctx.call("get_game_prices", {"game_id": "uuid-hades-001"})

    assert "error" in result


# ── 測試 get_top_deals ────────────────────────────────────────────────────────

_FAKE_DEALS = {
    "nextOffset": 10,
    "hasMore": True,
    "list": [{
        "id": "uuid-hades-001",
        "slug": "hades",
        "title": "Hades",
        "type": "game",
        "deal": {
            "shop": {"id": 61, "title": "Steam"},
            "price": {"amount": 299.0, "amountInt": 29900, "currency": "TWD"},
            "regular": {"amount": 597.0, "amountInt": 59700, "currency": "TWD"},
            "cut": 50,
            "voucher": None,
            "storeLow": None,
            "historyLow": None,
            "flag": "H",
            "drm": [],
            "platforms": [],
            "timestamp": "2024-01-01T00:00:00Z",
            "expiry": None,
            "url": "https://store.steampowered.com/app/1145360",
        },
    }],
}

def test_get_top_deals_parses_fields(ctx: FakePluginContext):
    """應正確解析折扣欄位，包含 is_history_low。"""
    with patch("game_deals_plugin.get_deals", return_value=_FAKE_DEALS):
        result = ctx.call("get_top_deals", {"country": "TW", "min_discount_percent": 30})

    assert result["country"] == "TW"
    assert result["count"] == 1
    deal = result["deals"][0]
    assert deal["title"] == "Hades"
    assert deal["price"] == "TWD 299.00"
    assert deal["discount_percent"] == 50
    assert deal["is_history_low"] is True


def test_get_top_deals_api_error(ctx: FakePluginContext):
    """API 失敗時應回傳含 error 欄位的 dict。"""
    with patch("game_deals_plugin.get_deals", side_effect=Exception("rate limited")):
        result = ctx.call("get_top_deals", {})

    assert "error" in result
