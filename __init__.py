"""
Hermes Plugin：game-deals

向 Hermes agent 註冊三個工具：
  - search_game_deals     — 依遊戲名稱搜尋折扣
  - get_top_steam_deals   — 取得 Steam 熱門折扣排行
  - get_deal_link         — 產生折扣購買連結

安裝方式：
    將此目錄複製到 ~/.hermes/plugins/game-deals/
    hermes plugins enable game-deals
"""

import json
import logging

from api_client import search_games, get_steam_deals, build_deal_url
from schemas import (
    SEARCH_GAME_DEALS_SCHEMA,
    GET_TOP_STEAM_DEALS_SCHEMA,
    GET_DEAL_LINK_SCHEMA,
)

logger = logging.getLogger(__name__)


def register(ctx) -> None:
    """
    Hermes plugin 進入點，由 PluginManager 在載入時呼叫。

    Args:
        ctx: Hermes PluginContext，提供 register_tool / register_hook 等 API。
    """

    # ── Tool: search_game_deals ────────────────────────────────────────────

    def handle_search_game_deals(params: dict, **kwargs) -> str:
        """
        依名稱搜尋遊戲並回傳折扣資訊。

        Args:
            params: 含 title（必要）、limit（選用）。

        Returns:
            JSON 字串，含找到的遊戲清單及各遊戲最低售價。
        """
        title: str = params["title"]
        limit: int = min(int(params.get("limit", 5)), 10)

        try:
            games = search_games(title, limit=limit)
        except Exception as exc:
            logger.error("search_game_deals 呼叫 CheapShark API 失敗：%s", exc)
            return json.dumps({"error": str(exc)})

        if not games:
            return json.dumps({
                "found": 0,
                "games": [],
                "message": f"找不到名稱含有 '{title}' 的遊戲。",
            })

        results = []
        for game in games:
            steam_app_id = game.get("steamAppID")
            results.append({
                "name": game.get("external"),
                "cheapest_price_usd": game.get("cheapest"),
                "deal_id": game.get("cheapestDealID"),
                "steam_url": (
                    f"https://store.steampowered.com/app/{steam_app_id}"
                    if steam_app_id
                    else None
                ),
            })

        return json.dumps({"found": len(results), "games": results}, ensure_ascii=False)

    ctx.register_tool(
        name="search_game_deals",
        toolset="game_deals",
        schema=SEARCH_GAME_DEALS_SCHEMA,
        handler=handle_search_game_deals,
        description="依遊戲名稱搜尋 Steam 折扣資訊",
    )

    # ── Tool: get_top_steam_deals ──────────────────────────────────────────

    def handle_get_top_steam_deals(params: dict, **kwargs) -> str:
        """
        取得 Steam 熱門折扣排行，支援多種篩選條件。

        Args:
            params: 含 count、sort_by、min_discount_percent、max_price_usd、min_steam_rating（均選用）。

        Returns:
            JSON 字串，含折扣清單。
        """
        count: int = min(int(params.get("count", 10)), 30)
        sort_by: str = params.get("sort_by", "DealRating")
        min_discount: int = int(params.get("min_discount_percent", 0))
        max_price: float = float(params.get("max_price_usd", 50))
        min_rating: int = int(params.get("min_steam_rating", 0))

        try:
            raw_deals = get_steam_deals(
                page_size=count,
                sort_by=sort_by,
                min_discount=min_discount,
                max_price=max_price,
                min_steam_rating=min_rating,
            )
        except Exception as exc:
            logger.error("get_top_steam_deals 呼叫 CheapShark API 失敗：%s", exc)
            return json.dumps({"error": str(exc)})

        deals = [
            {
                "title": d.get("title"),
                "sale_price_usd": d.get("salePrice"),
                "original_price_usd": d.get("normalPrice"),
                "discount_percent": round(float(d.get("savings", 0)), 1),
                "steam_rating": d.get("steamRatingText"),
                "steam_rating_percent": d.get("steamRatingPercent"),
                "deal_id": d.get("dealID"),
                "metacritic_score": d.get("metacriticScore") or None,
            }
            for d in raw_deals
        ]

        return json.dumps(
            {"count": len(deals), "sorted_by": sort_by, "deals": deals},
            ensure_ascii=False,
        )

    ctx.register_tool(
        name="get_top_steam_deals",
        toolset="game_deals",
        schema=GET_TOP_STEAM_DEALS_SCHEMA,
        handler=handle_get_top_steam_deals,
        description="取得 Steam 目前熱門折扣排行，支援依折扣幅度、售價、評分篩選",
    )

    # ── Tool: get_deal_link ────────────────────────────────────────────────

    def handle_get_deal_link(params: dict, **kwargs) -> str:
        """
        根據 dealID 產生購買連結。

        Args:
            params: 含 deal_id（必要）。

        Returns:
            JSON 字串，含購買連結 URL。
        """
        deal_id: str = params["deal_id"]
        url = build_deal_url(deal_id)
        return json.dumps({"purchase_url": url}, ensure_ascii=False)

    ctx.register_tool(
        name="get_deal_link",
        toolset="game_deals",
        schema=GET_DEAL_LINK_SCHEMA,
        handler=handle_get_deal_link,
        description="根據 dealID 產生 CheapShark 購買導向連結",
    )

    # ── Hook: log every tool call in this toolset ──────────────────────────

    def _on_tool_call(tool_name: str, params: dict, result: str) -> None:
        """post_tool_call hook，記錄 game_deals toolset 的每次呼叫。"""
        if tool_name in {"search_game_deals", "get_top_steam_deals", "get_deal_link"}:
            logger.debug("[game-deals] tool=%s params=%s", tool_name, params)

    ctx.register_hook("post_tool_call", _on_tool_call)
