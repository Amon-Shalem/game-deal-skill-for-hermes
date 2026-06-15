"""
CheapShark API 的同步 HTTP 客戶端。

使用 requests 進行同步呼叫，符合 Hermes plugin handler 的同步執行模型。
API 文件：https://apidocs.cheapshark.com/
"""

import requests

_BASE_URL = "https://www.cheapshark.com/api/1.0"
_DEAL_REDIRECT_URL = "https://www.cheapshark.com/redirect?dealID="
_STEAM_STORE_ID = "1"

# CheapShark 要求必須附帶描述性 User-Agent，否則回傳 400
_HEADERS = {"User-Agent": "HermesGameDealPlugin/1.0 (hermes-agent)"}


def search_games(title: str, limit: int = 5) -> list[dict]:
    """
    依遊戲名稱搜尋，回傳各商店最低價格清單。

    Args:
        title: 遊戲名稱（英文，支援模糊搜尋）。
        limit: 最多回傳筆數，最大 60。

    Returns:
        遊戲清單，每筆含 gameID、external（名稱）、cheapest、cheapestDealID、steamAppID。
    """
    resp = requests.get(
        f"{_BASE_URL}/games",
        params={"title": title, "limit": limit},
        headers=_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_steam_deals(
    page_size: int = 10,
    sort_by: str = "DealRating",
    min_discount: int = 0,
    max_price: float = 50.0,
    min_steam_rating: int = 0,
) -> list[dict]:
    """
    取得 Steam 折扣列表，可依多種條件篩選。

    Args:
        page_size: 每頁筆數，最大 60。
        sort_by: 排序方式（DealRating / Savings / Price / Reviews / Recent）。
        min_discount: 最低折扣百分比（0–100）。
        max_price: 最高售價（美元）。
        min_steam_rating: Steam 評分最低門檻（0–100）。

    Returns:
        折扣清單，每筆含 title、salePrice、normalPrice、savings、steamRatingText、dealID。
    """
    params: dict = {
        "storeID": _STEAM_STORE_ID,
        "pageSize": page_size,
        "sortBy": sort_by,
        "upperPrice": max_price,
        "steamRating": min_steam_rating,
        "onSale": 1,
    }
    if min_discount > 0:
        params["minDiscount"] = min_discount

    resp = requests.get(
        f"{_BASE_URL}/deals",
        params=params,
        headers=_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def build_deal_url(deal_id: str) -> str:
    """
    組合 CheapShark 折扣的購買導向連結。

    Args:
        deal_id: CheapShark 的 dealID（URL-encoded 字串）。

    Returns:
        可直接開啟的購買連結。
    """
    return f"{_DEAL_REDIRECT_URL}{deal_id}"
