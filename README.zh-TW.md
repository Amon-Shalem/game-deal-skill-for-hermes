# game-deals — Hermes Plugin

[English](README.md)

一個 [Hermes agent](https://hermes-agent.nousresearch.com) plugin，透過 [IsThereAnyDeal API](https://isthereanydeal.com) 查詢 40+ 個遊戲商店的折扣資訊，支援地區貨幣（台幣、日圓、歐元等）。

---

## 工具

| 工具 | 說明 |
|---|---|
| `search_game` | 依名稱搜尋遊戲，取得 ITAD UUID |
| `get_game_prices` | 查詢特定遊戲的現況售價與歷史最低 |
| `get_top_deals` | 瀏覽熱門折扣，支援地區、折扣幅度、評分篩選 |

> 查詢價格前必須先呼叫 `search_game` 取得 `game_id`。

---

## 前置需求

- 已安裝 [Hermes agent](https://hermes-agent.nousresearch.com)
- [IsThereAnyDeal API key](https://isthereanydeal.com/apps/new/)（免費註冊）

---

## 安裝

```bash
hermes plugins install Amon-Shalem/game-deal-skill-for-hermes --enable
```

安裝過程中，Hermes 會提示你設定 `ITAD_API_KEY`。將 API key 貼上即可。key 只存在本機環境變數，**不會寫入任何檔案或上傳至任何地方**。

### 手動設定環境變數

```bash
# Linux / macOS
export ITAD_API_KEY="your_api_key_here"

# Windows PowerShell
$env:ITAD_API_KEY = "your_api_key_here"
```

---

## 使用範例

安裝後直接用自然語言詢問 Hermes：

```
Hades 現在有打折嗎？
台灣 Steam 本週有什麼好折扣？
Elden Ring 台幣歷史最低是多少？
給我折扣超過 70% 且 Steam 評分 80 以上的遊戲。
```

### 支援地區

傳入任何 [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) 國家代碼：

| 代碼 | 國家 | 貨幣 |
|---|---|---|
| `TW` | 台灣 | TWD |
| `US` | 美國 | USD |
| `JP` | 日本 | JPY |
| `GB` | 英國 | GBP |
| `DE` | 德國 | EUR |

---

## 工具參數說明

### `search_game`

| 參數 | 類型 | 必要 | 預設值 | 說明 |
|---|---|---|---|---|
| `title` | string | 是 | — | 遊戲名稱 |
| `limit` | integer | 否 | 5 | 最多回傳筆數（1–10） |

### `get_game_prices`

| 參數 | 類型 | 必要 | 預設值 | 說明 |
|---|---|---|---|---|
| `game_id` | string | 是 | — | 由 `search_game` 取得的 ITAD UUID |
| `country` | string | 否 | `US` | 國家代碼 |

### `get_top_deals`

| 參數 | 類型 | 必要 | 預設值 | 說明 |
|---|---|---|---|---|
| `country` | string | 否 | `US` | 國家代碼 |
| `limit` | integer | 否 | 10 | 回傳筆數（1–30） |
| `min_discount_percent` | integer | 否 | 0 | 最低折扣百分比 |
| `min_steam_score` | integer | 否 | 0 | Steam 評分門檻 |
| `sort` | string | 否 | `trending` | `trending` / `cut:desc` / `price:asc` / `time:desc` |

---

## 專案結構

```
game-deal-skill-for-hermes/
├── plugin.yaml       # Hermes plugin manifest
├── __init__.py       # register(ctx) 進入點
├── api_client.py     # IsThereAnyDeal HTTP 客戶端
├── schemas.py        # 工具 schema（Hermes 格式）
└── tests/
    └── test_plugin.py
```

---

## 開發

```bash
# 安裝測試依賴
pip install requests pytest

# 執行測試
pytest tests/ -v
```

測試使用 `FakePluginContext` 模擬 Hermes 環境，不需要真實 API key 或網路連線。

---

## 授權

MIT
