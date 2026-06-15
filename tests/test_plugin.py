"""
game-deals plugin 的單元測試。

因 Hermes PluginContext 在測試環境中不存在，
使用 FakePluginContext 模擬 ctx.register_tool / ctx.register_hook，
直接提取並呼叫 handler 函式進行驗證。
"""

import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Plugin 根目錄（tests/ 的上一層）
PLUGIN_ROOT = Path(__file__).parent.parent


def _load_plugin_register():
    """
    使用 importlib 載入 plugin 的 __init__.py，
    模擬 Hermes 將 plugin 目錄加進 sys.path 後的載入行為。

    Returns:
        plugin 的 register 函式。
    """
    # 讓 api_client / schemas 可以用絕對 import 找到
    if str(PLUGIN_ROOT) not in sys.path:
        sys.path.insert(0, str(PLUGIN_ROOT))

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
    """
    最小化的 Hermes PluginContext 模擬，
    只記錄 register_tool / register_hook 的呼叫。
    """

    def __init__(self):
        self.tools: dict[str, dict] = {}
        self.hooks: list[tuple] = []

    def register_tool(self, *, name, toolset, schema, handler, description):
        self.tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
            "description": description,
        }

    def register_hook(self, hook_name: str, callback):
        self.hooks.append((hook_name, callback))

    def call(self, tool_name: str, params: dict) -> dict:
        """
        呼叫已註冊的 handler，回傳解析後的 dict（方便斷言）。

        Args:
            tool_name: 工具名稱。
            params: 傳入 handler 的參數 dict。
        """
        handler = self.tools[tool_name]["handler"]
        return json.loads(handler(params))


@pytest.fixture(scope="module")
def ctx():
    """建立並完成 register() 的 FakePluginContext，整個 module 共用一份。"""
    register = _load_plugin_register()
    fake_ctx = FakePluginContext()
    register(fake_ctx)
    return fake_ctx


# ── 測試 register() 本身 ──────────────────────────────────────────────────────

def test_register_all_tools(ctx: FakePluginContext):
    """register() 應註冊三個工具。"""
    assert set(ctx.tools.keys()) == {
        "search_game_deals",
        "get_top_steam_deals",
        "get_deal_link",
    }


def test_register_post_tool_call_hook(ctx: FakePluginContext):
    """register() 應註冊 post_tool_call hook。"""
    hook_names = [name for name, _ in ctx.hooks]
    assert "post_tool_call" in hook_names


def test_all_schemas_use_parameters_key(ctx: FakePluginContext):
    """所有工具 schema 必須使用 'parameters' 欄位（Hermes 格式，非 Claude API 的 input_schema）。"""
    for name, info in ctx.tools.items():
        assert "parameters" in info["schema"], (
            f"{name} 的 schema 缺少 'parameters' 欄位"
        )
        assert "input_schema" not in info["schema"], (
            f"{name} 的 schema 不應含有 Claude API 的 'input_schema' 欄位"
        )


# ── 測試 search_game_deals ────────────────────────────────────────────────────

def test_search_game_deals_found(ctx: FakePluginContext):
    """找到遊戲時應回傳正確欄位。"""
    fake_games = [{
        "gameID": "196149",
        "steamAppID": "1145360",
        "cheapest": "24.99",
        "cheapestDealID": "abc123",
        "external": "Hades",
    }]
    with patch("game_deals_plugin.search_games", return_value=fake_games):
        result = ctx.call("search_game_deals", {"title": "hades"})

    assert result["found"] == 1
    game = result["games"][0]
    assert game["name"] == "Hades"
    assert game["cheapest_price_usd"] == "24.99"
    assert game["deal_id"] == "abc123"
    assert "1145360" in game["steam_url"]


def test_search_game_deals_not_found(ctx: FakePluginContext):
    """找不到遊戲時應回傳 found=0 與提示訊息。"""
    with patch("game_deals_plugin.search_games", return_value=[]):
        result = ctx.call("search_game_deals", {"title": "xxxxxxxxnotexist"})

    assert result["found"] == 0
    assert "找不到" in result["message"]


def test_search_game_deals_api_error(ctx: FakePluginContext):
    """API 失敗時應回傳含 error 欄位的 dict，而非拋出例外。"""
    with patch("game_deals_plugin.search_games", side_effect=Exception("timeout")):
        result = ctx.call("search_game_deals", {"title": "hades"})

    assert "error" in result


# ── 測試 get_top_steam_deals ──────────────────────────────────────────────────

def test_get_top_steam_deals_parses_fields(ctx: FakePluginContext):
    """應正確解析折扣欄位並計算 discount_percent。"""
    fake_deals = [{
        "title": "Hotline Miami",
        "salePrice": "0.99",
        "normalPrice": "9.99",
        "savings": "90.09",
        "steamRatingText": "Overwhelmingly Positive",
        "steamRatingPercent": "96",
        "dealID": "deal456",
        "metacriticScore": "85",
    }]
    with patch("game_deals_plugin.get_steam_deals", return_value=fake_deals):
        result = ctx.call("get_top_steam_deals", {"min_discount_percent": 50})

    assert result["count"] == 1
    deal = result["deals"][0]
    assert deal["title"] == "Hotline Miami"
    assert deal["discount_percent"] == 90.1
    assert deal["deal_id"] == "deal456"


def test_get_top_steam_deals_api_error(ctx: FakePluginContext):
    """API 失敗時應回傳含 error 欄位的 dict。"""
    with patch("game_deals_plugin.get_steam_deals", side_effect=Exception("connection refused")):
        result = ctx.call("get_top_steam_deals", {})

    assert "error" in result


# ── 測試 get_deal_link ────────────────────────────────────────────────────────

def test_get_deal_link_builds_correct_url(ctx: FakePluginContext):
    """應組合正確的 CheapShark 購買導向 URL。"""
    result = ctx.call("get_deal_link", {"deal_id": "abc%2B123"})
    assert result["purchase_url"] == "https://www.cheapshark.com/redirect?dealID=abc%2B123"
