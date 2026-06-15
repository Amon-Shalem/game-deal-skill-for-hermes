"""
三個遊戲折扣工具的 schema 定義（Hermes 格式，使用 "parameters" 欄位）。
"""

SEARCH_GAME_DEALS_SCHEMA = {
    "name": "search_game_deals",
    "description": (
        "依遊戲名稱搜尋折扣資訊，回傳各商店的最低售價與折扣連結。"
        "適合「Hades 現在多少錢？」或「黑神話有沒有特價？」這類查詢。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "遊戲名稱，支援英文關鍵字模糊搜尋，例如 'hades' 或 'hollow knight'。",
            },
            "limit": {
                "type": "integer",
                "description": "最多回傳幾筆遊戲結果，預設 5，最大 10。",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["title"],
    },
}

GET_TOP_STEAM_DEALS_SCHEMA = {
    "name": "get_top_steam_deals",
    "description": (
        "取得 Steam 目前熱門折扣排行，可設定最低折扣幅度、最高售價、最低 Steam 評分篩選。"
        "適合「有什麼便宜好玩的遊戲？」或「推薦幾款打五折以上的高評分遊戲」這類查詢。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "description": "回傳幾筆折扣，預設 10，最大 30。",
                "default": 10,
                "minimum": 1,
                "maximum": 30,
            },
            "sort_by": {
                "type": "string",
                "description": (
                    "排序方式："
                    "DealRating（折扣綜合評分，預設）、"
                    "Savings（折扣幅度最大）、"
                    "Price（售價最低）、"
                    "Reviews（Steam 評分最高）、"
                    "Recent（最新折扣）。"
                ),
                "enum": ["DealRating", "Savings", "Price", "Reviews", "Recent"],
                "default": "DealRating",
            },
            "min_discount_percent": {
                "type": "integer",
                "description": "最低折扣百分比，例如 50 表示至少五折。預設 0（不限制）。",
                "default": 0,
                "minimum": 0,
                "maximum": 100,
            },
            "max_price_usd": {
                "type": "number",
                "description": "最高售價（美元），預設 50。",
                "default": 50,
                "minimum": 0,
            },
            "min_steam_rating": {
                "type": "integer",
                "description": "Steam 玩家評分最低門檻（0–100），例如 70 表示好評以上。預設 0（不限制）。",
                "default": 0,
                "minimum": 0,
                "maximum": 100,
            },
        },
        "required": [],
    },
}

GET_DEAL_LINK_SCHEMA = {
    "name": "get_deal_link",
    "description": (
        "根據 dealID 產生可直接前往購買頁面的連結。"
        "search_game_deals 與 get_top_steam_deals 的結果中都含有 deal_id 欄位。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "deal_id": {
                "type": "string",
                "description": "CheapShark 回傳的 dealID 字串。",
            },
        },
        "required": ["deal_id"],
    },
}
