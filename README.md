# game-deals — Hermes Plugin

A [Hermes agent](https://hermes-agent.nousresearch.com) plugin that queries game deals across 40+ stores via the [IsThereAnyDeal API](https://isthereanydeal.com), with support for regional pricing (TWD, JPY, EUR, etc.).

一個 [Hermes agent](https://hermes-agent.nousresearch.com) plugin，透過 [IsThereAnyDeal API](https://isthereanydeal.com) 查詢 40+ 個遊戲商店的折扣資訊，支援地區貨幣（台幣、日圓、歐元等）。

---

## Tools / 工具

| Tool | Description | 說明 |
|---|---|---|
| `search_game` | Search for a game by title, returns ITAD UUID | 依名稱搜尋遊戲，取得 ITAD UUID |
| `get_game_prices` | Get current prices and all-time low for a specific game | 查詢特定遊戲的現況售價與歷史最低 |
| `get_top_deals` | Browse top deals with filters (country, discount, score) | 瀏覽熱門折扣，支援地區、折扣幅度、評分篩選 |

> `search_game` must be called first to obtain the `game_id` before using `get_game_prices`.
>
> 查詢價格前必須先呼叫 `search_game` 取得 `game_id`。

---

## Prerequisites / 前置需求

- [Hermes agent](https://hermes-agent.nousresearch.com) installed
- An [IsThereAnyDeal API key](https://isthereanydeal.com/apps/new/) (free registration)

---

- 已安裝 [Hermes agent](https://hermes-agent.nousresearch.com)
- [IsThereAnyDeal API key](https://isthereanydeal.com/apps/new/)（免費註冊）

---

## Installation / 安裝

```bash
hermes plugins install Amon-Shalem/game-deal-skill-for-hermes --enable
```

During installation, Hermes will prompt you to set `ITAD_API_KEY`. Paste your API key at the prompt — it is stored as a local environment variable and **never written to any file or uploaded anywhere**.

安裝過程中，Hermes 會提示你設定 `ITAD_API_KEY`。將 API key 貼上即可。key 只存在本機環境變數，**不會寫入任何檔案或上傳至任何地方**。

### Manual setup / 手動設定

If you prefer to set the environment variable yourself:

如果你想手動設定環境變數：

```bash
# Linux / macOS
export ITAD_API_KEY="your_api_key_here"

# Windows PowerShell
$env:ITAD_API_KEY = "your_api_key_here"
```

---

## Usage Examples / 使用範例

Once installed, talk to Hermes naturally:

安裝後直接用自然語言詢問 Hermes：

```
Is Hades on sale right now?
Hades 現在有打折嗎？

What are the best Steam deals in Taiwan this week?
台灣 Steam 本週有什麼好折扣？

What's the all-time low price for Elden Ring in TWD?
Elden Ring 台幣歷史最低是多少？

Show me games with over 70% off and a Steam score above 80.
給我折扣超過 70% 且 Steam 評分 80 以上的遊戲。
```

### Supported countries / 支援地區

Pass any [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code:

傳入任何 [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) 國家代碼：

| Code | Country | Currency |
|---|---|---|
| `TW` | Taiwan | TWD |
| `US` | United States | USD |
| `JP` | Japan | JPY |
| `GB` | United Kingdom | GBP |
| `DE` | Germany | EUR |

---

## Tool Reference / 工具參數說明

### `search_game`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | Yes | — | Game title to search / 遊戲名稱 |
| `limit` | integer | No | 5 | Max results (1–10) / 最多回傳筆數 |

### `get_game_prices`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `game_id` | string | Yes | — | ITAD UUID from `search_game` |
| `country` | string | No | `US` | ISO country code / 國家代碼 |

### `get_top_deals`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `country` | string | No | `US` | ISO country code / 國家代碼 |
| `limit` | integer | No | 10 | Results to return (1–30) / 回傳筆數 |
| `min_discount_percent` | integer | No | 0 | Minimum discount % / 最低折扣百分比 |
| `min_steam_score` | integer | No | 0 | Minimum Steam rating / Steam 評分門檻 |
| `sort` | string | No | `trending` | `trending` / `cut:desc` / `price:asc` / `time:desc` |

---

## Project Structure / 專案結構

```
game-deal-skill-for-hermes/
├── plugin.yaml       # Hermes plugin manifest
├── __init__.py       # register(ctx) entry point
├── api_client.py     # IsThereAnyDeal HTTP client
├── schemas.py        # Tool schemas (Hermes format)
└── tests/
    └── test_plugin.py
```

---

## Development / 開發

```bash
# Install test dependencies / 安裝測試依賴
pip install requests pytest

# Run tests / 執行測試
pytest tests/ -v
```

Tests use a `FakePluginContext` to simulate Hermes without requiring a live API connection or a real API key.

測試使用 `FakePluginContext` 模擬 Hermes 環境，不需要真實 API key 或網路連線。

---

## License / 授權

MIT
