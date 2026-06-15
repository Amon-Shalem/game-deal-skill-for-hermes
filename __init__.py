"""
Hermes Plugin：game-deals v2

向 Hermes agent 註冊三個工具：
  - search_game        — 依名稱搜尋遊戲，取得 ITAD UUID
  - get_game_prices    — 查特定遊戲在各商店的現況與歷史最低（支援地區貨幣）
  - get_top_deals      — 瀏覽熱門折扣排行（支援地區貨幣與多種篩選條件）

安裝：
    hermes plugins install Amon-Shalem/game-deal-skill-for-hermes --enable
    # 安裝時會提示設定 ITAD_API_KEY 環境變數
"""

import json
import logging

from api_client import search_games, get_game_overview, get_deals
from schemas import SEARCH_GAME_SCHEMA, GET_GAME_PRICES_SCHEMA, GET_TOP_DEALS_SCHEMA

logger = logging.getLogger(__name__)


def _fmt_price(price: dict | None) -> str | None:
    """
    將 ITAD price 物件格式化為易讀字串。

    Args:
        price: 含 amount 與 currency 欄位的 dict，或 None。

    Returns:
        格式化字串，例如 "TWD 299.00"，或 None。
    """
    if not price:
        return None
    return f"{price['currency']} {price['amount']:.2f}"


def register(ctx) -> None:
    """
    Hermes plugin 進入點，由 PluginManager 在載入時呼叫。

    Args:
        ctx: Hermes PluginContext。
    """

    # ── Tool: search_game ─────────────────────────────────────────────────

    def handle_search_game(params: dict, **kwargs) -> str:
        """
        依名稱搜尋遊戲。

        Args:
            params: 含 title（必要）、limit（選用）。

        Returns:
            JSON 字串，含找到的遊戲清單（id、title、slug）。
        """
        title: str = params["title"]
        limit: int = min(int(params.get("limit", 5)), 10)

        try:
            games = search_games(title, results=limit)
        except Exception as exc:
            logger.error("search_game 失敗：%s", exc)
            return json.dumps({"error": str(exc)})

        if not games:
            return json.dumps({
                "found": 0,
                "games": [],
                "message": f"找不到名稱含有 '{title}' 的遊戲。",
            })

        results = [
            {"id": g["id"], "title": g["title"], "slug": g["slug"]}
            for g in games
        ]
        return json.dumps({"found": len(results), "games": results}, ensure_ascii=False)

    ctx.register_tool(
        name="search_game",
        toolset="game_deals",
        schema=SEARCH_GAME_SCHEMA,
        handler=handle_search_game,
        description="依遊戲名稱搜尋，取得 ITAD UUID（查詢價格前的必要步驟）",
    )

    # ── Tool: get_game_prices ─────────────────────────────────────────────

    def handle_get_game_prices(params: dict, **kwargs) -> str:
        """
        查詢特定遊戲在各商店的目前售價與歷史最低。

        Args:
            params: 含 game_id（必要）、country（選用，預設 US）。

        Returns:
            JSON 字串，含目前最優惠與歷史最低的完整資訊。
        """
        game_id: str = params["game_id"]
        country: str = params.get("country", "US").upper()

        try:
            overview = get_game_overview([game_id], country=country)
        except Exception as exc:
            logger.error("get_game_prices 失敗：%s", exc)
            return json.dumps({"error": str(exc)})

        prices = overview.get("prices", [])
        if not prices:
            return json.dumps({"found": False, "message": "查無此遊戲的價格資料。"})

        record = prices[0]
        current = record.get("current")
        lowest = record.get("lowest")

        result = {
            "game_id": game_id,
            "country": country,
            "current_best": None,
            "history_low": None,
            "store_url": record.get("urls", {}).get("game"),
        }

        if current:
            result["current_best"] = {
                "shop": current["shop"]["title"],
                "price": _fmt_price(current.get("price")),
                "regular_price": _fmt_price(current.get("regular")),
                "discount_percent": current.get("cut"),
                "deal_url": current.get("url"),
                "expires": current.get("expiry"),
            }

        if lowest:
            result["history_low"] = {
                "shop": lowest["shop"]["title"],
                "price": _fmt_price(lowest.get("price")),
                "discount_percent": lowest.get("cut"),
                "date": lowest.get("timestamp"),
            }

        return json.dumps(result, ensure_ascii=False)

    ctx.register_tool(
        name="get_game_prices",
        toolset="game_deals",
        schema=GET_GAME_PRICES_SCHEMA,
        handler=handle_get_game_prices,
        description="查詢特定遊戲在各商店的現況與歷史最低（支援地區貨幣）",
    )

    # ── Tool: get_top_deals ───────────────────────────────────────────────

    def handle_get_top_deals(params: dict, **kwargs) -> str:
        """
        取得熱門折扣排行，支援國家、折扣幅度、Steam 評分篩選。

        Args:
            params: 含 country、limit、min_discount_percent、min_steam_score、sort（均選用）。

        Returns:
            JSON 字串，含折扣清單。
        """
        country: str = params.get("country", "US").upper()
        limit: int = min(int(params.get("limit", 10)), 30)
        min_cut: int = int(params.get("min_discount_percent", 0))
        min_score: int = int(params.get("min_steam_score", 0))
        sort: str = params.get("sort", "trending")

        try:
            data = get_deals(
                country=country,
                limit=limit,
                min_cut=min_cut,
                min_steam_score=min_score,
                sort=sort,
            )
        except Exception as exc:
            logger.error("get_top_deals 失敗：%s", exc)
            return json.dumps({"error": str(exc)})

        deals = []
        for item in data.get("list", []):
            deal = item.get("deal", {})
            deals.append({
                "title": item.get("title"),
                "shop": deal.get("shop", {}).get("title"),
                "price": _fmt_price(deal.get("price")),
                "regular_price": _fmt_price(deal.get("regular")),
                "discount_percent": deal.get("cut"),
                "is_history_low": deal.get("flag") in ("N", "H"),
                "deal_url": deal.get("url"),
                "expires": deal.get("expiry"),
            })

        return json.dumps(
            {"country": country, "count": len(deals), "deals": deals},
            ensure_ascii=False,
        )

    ctx.register_tool(
        name="get_top_deals",
        toolset="game_deals",
        schema=GET_TOP_DEALS_SCHEMA,
        handler=handle_get_top_deals,
        description="瀏覽熱門折扣排行（支援地區貨幣與折扣幅度、評分篩選）",
    )

    # ── Hook: debug logging ───────────────────────────────────────────────

    def _on_tool_call(tool_name: str, params: dict, result: str) -> None:
        """post_tool_call hook，記錄 game_deals toolset 的每次呼叫。"""
        if tool_name in {"search_game", "get_game_prices", "get_top_deals"}:
            logger.debug("[game-deals] tool=%s params=%s", tool_name, params)

    ctx.register_hook("post_tool_call", _on_tool_call)
