"""
IsThereAnyDeal (ITAD) API 的同步 HTTP 客戶端。

API 文件：https://docs.isthereanydeal.com/
認證方式：在 request header 加入 ITAD-API-Key，
         或設 key query param，兩者等效。
         本模組使用 header 方式，key 從環境變數 ITAD_API_KEY 讀取。
"""

import os
import requests

_BASE_URL = "https://api.isthereanydeal.com"


def _headers() -> dict:
    """
    建立含 API key 的 request headers。

    Returns:
        dict，含 ITAD-API-Key 與 User-Agent。

    Raises:
        RuntimeError: 當環境變數 ITAD_API_KEY 未設定時。
    """
    api_key = os.environ.get("ITAD_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "環境變數 ITAD_API_KEY 未設定。"
            "請先執行 hermes plugins install 或手動設定 ITAD_API_KEY。"
        )
    return {
        "ITAD-API-Key": api_key,
        "User-Agent": "HermesGameDealPlugin/2.0 (hermes-agent)",
    }


def search_games(title: str, results: int = 5) -> list[dict]:
    """
    依遊戲名稱搜尋，回傳 ITAD 遊戲清單。

    Args:
        title: 遊戲名稱（支援模糊搜尋）。
        results: 最多回傳筆數。

    Returns:
        遊戲清單，每筆含 id（UUID）、title、slug。
    """
    resp = requests.get(
        f"{_BASE_URL}/games/search/v1",
        params={"title": title, "results": results},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_game_overview(game_ids: list[str], country: str = "US", vouchers: bool = False) -> dict:
    """
    取得指定遊戲的價格總覽，包含目前最優惠與歷史最低。

    Args:
        game_ids: ITAD 遊戲 UUID 清單。
        country: 兩字母國家代碼（ISO 3166-1），例如 "TW"、"US"、"JP"。
        vouchers: 是否納入折扣碼優惠。

    Returns:
        dict，含 prices 清單（每筆含 id、current 最優惠、lowest 歷史最低）。
    """
    resp = requests.post(
        f"{_BASE_URL}/games/overview/v2",
        params={"country": country, "vouchers": str(vouchers).lower()},
        json=game_ids,
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_deals(
    country: str = "US",
    limit: int = 10,
    offset: int = 0,
    shops: list[int] | None = None,
    min_cut: int = 0,
    min_steam_score: int = 0,
    sort: str = "trending",
) -> dict:
    """
    取得折扣列表，支援地區、商店、折扣幅度、評分篩選。

    Args:
        country: 兩字母國家代碼，決定回傳價格的貨幣。
        limit: 每次回傳幾筆，最大 200。
        offset: 分頁起始位移。
        shops: 商店 ID 清單，None 表示不限商店。
        min_cut: 最低折扣百分比（0–100）。
        min_steam_score: Steam 評分最低門檻（0–100）。
        sort: 排序方式，例如 "trending"、"price:asc"、"cut:desc"、"time:desc"。

    Returns:
        dict，含 list（折扣清單）、hasMore、nextOffset。
    """
    body: dict = {
        "country": country,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "filter": {},
    }

    if shops:
        body["shops"] = shops

    if min_cut > 0:
        body["filter"]["cut"] = {"min": min_cut}

    if min_steam_score > 0:
        body["filter"]["steamPerc"] = {"min": min_steam_score}

    resp = requests.post(
        f"{_BASE_URL}/deals/v2",
        json=body,
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_shops() -> list[dict]:
    """
    取得 ITAD 目前支援的所有有效商店清單。

    Returns:
        商店清單，每筆含 id、title、deals（目前折扣數）。
    """
    resp = requests.get(
        f"{_BASE_URL}/service/shops/v1",
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
