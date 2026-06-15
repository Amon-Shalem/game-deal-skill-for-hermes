"""
三個遊戲折扣工具的 schema 定義（Hermes 格式，使用 "parameters" 欄位）。
"""

SEARCH_GAME_SCHEMA = {
    "name": "search_game",
    "description": (
        "依遊戲名稱在 IsThereAnyDeal 資料庫搜尋，回傳遊戲 ID 與基本資訊。"
        "查詢價格或折扣前必須先呼叫此工具取得遊戲 ID。"
        "適合「幫我找 Hades」或「Elden Ring 的 ID 是什麼」這類查詢。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "遊戲名稱，支援英文關鍵字模糊搜尋，例如 'hades' 或 'elden ring'。",
            },
            "limit": {
                "type": "integer",
                "description": "最多回傳幾筆結果，預設 5，最大 10。",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["title"],
    },
}

GET_GAME_PRICES_SCHEMA = {
    "name": "get_game_prices",
    "description": (
        "查詢特定遊戲在各商店的目前售價與歷史最低價。"
        "需先用 search_game 取得 game_id。"
        "支援指定國家代碼，可取得對應貨幣（例如 TW 回傳台幣、JP 回傳日圓）。"
        "適合「Hades 現在多少錢？」或「這款遊戲歷史最低是多少？」這類查詢。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "game_id": {
                "type": "string",
                "description": "ITAD 遊戲 UUID，由 search_game 回傳的 id 欄位取得。",
            },
            "country": {
                "type": "string",
                "description": (
                    "兩字母國家代碼（ISO 3166-1），決定回傳的貨幣與區域價格。"
                    "例如 TW（台幣）、US（美元）、JP（日圓）、GB（英鎊）。預設 US。"
                ),
                "default": "US",
                "minLength": 2,
                "maxLength": 2,
            },
        },
        "required": ["game_id"],
    },
}

GET_TOP_DEALS_SCHEMA = {
    "name": "get_top_deals",
    "description": (
        "瀏覽各商店目前的熱門折扣，可依國家、折扣幅度、Steam 評分、商店篩選。"
        "適合「台灣 Steam 上有什麼好折扣？」或「推薦幾款折扣超過 70% 的高評分遊戲」這類查詢。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": (
                    "兩字母國家代碼，決定回傳貨幣與區域價格。"
                    "例如 TW（台幣）、US（美元）、JP（日圓）。預設 US。"
                ),
                "default": "US",
                "minLength": 2,
                "maxLength": 2,
            },
            "limit": {
                "type": "integer",
                "description": "回傳幾筆折扣，預設 10，最大 30。",
                "default": 10,
                "minimum": 1,
                "maximum": 30,
            },
            "min_discount_percent": {
                "type": "integer",
                "description": "最低折扣百分比，例如 50 表示至少五折。預設 0（不限制）。",
                "default": 0,
                "minimum": 0,
                "maximum": 100,
            },
            "min_steam_score": {
                "type": "integer",
                "description": "Steam 玩家評分最低門檻（0–100），例如 70 表示好評以上。預設 0（不限制）。",
                "default": 0,
                "minimum": 0,
                "maximum": 100,
            },
            "sort": {
                "type": "string",
                "description": (
                    "排序方式。"
                    "trending（熱門趨勢，預設）、"
                    "cut:desc（折扣幅度最大）、"
                    "price:asc（售價最低）、"
                    "time:desc（最新折扣）。"
                ),
                "enum": ["trending", "cut:desc", "price:asc", "time:desc"],
                "default": "trending",
            },
        },
        "required": [],
    },
}
