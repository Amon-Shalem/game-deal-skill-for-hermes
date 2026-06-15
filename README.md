# game-deals — Hermes Plugin

[繁體中文](README.zh-TW.md)

A [Hermes agent](https://hermes-agent.nousresearch.com) plugin that queries game deals across 40+ stores via the [IsThereAnyDeal API](https://isthereanydeal.com), with support for regional pricing (TWD, JPY, EUR, etc.).

---

## Tools

| Tool | Description |
|---|---|
| `search_game` | Search for a game by title, returns ITAD UUID |
| `get_game_prices` | Get current prices and all-time low for a specific game |
| `get_top_deals` | Browse top deals with filters (country, discount, score) |

> `search_game` must be called first to obtain the `game_id` before using `get_game_prices`.

---

## Prerequisites

- [Hermes agent](https://hermes-agent.nousresearch.com) installed
- An [IsThereAnyDeal API key](https://isthereanydeal.com/apps/new/) (free registration)

---

## Installation

1. Open the `/plugins` tab in Hermes
2. Search for `game-deal-skill-for-hermes` and install it
3. When prompted, paste your `ITAD_API_KEY` — Hermes saves it automatically

---

## Usage Examples

Once installed, talk to Hermes naturally:

```
Is Hades on sale right now?
What are the best Steam deals in Taiwan this week?
What's the all-time low price for Elden Ring in TWD?
Show me games with over 70% off and a Steam score above 80.
```

### Supported countries

Pass any [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code:

| Code | Country | Currency |
|---|---|---|
| `TW` | Taiwan | TWD |
| `US` | United States | USD |
| `JP` | Japan | JPY |
| `GB` | United Kingdom | GBP |
| `DE` | Germany | EUR |

---

## Tool Reference

### `search_game`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | Yes | — | Game title to search |
| `limit` | integer | No | 5 | Max results (1–10) |

### `get_game_prices`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `game_id` | string | Yes | — | ITAD UUID from `search_game` |
| `country` | string | No | `US` | ISO country code |

### `get_top_deals`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `country` | string | No | `US` | ISO country code |
| `limit` | integer | No | 10 | Results to return (1–30) |
| `min_discount_percent` | integer | No | 0 | Minimum discount % |
| `min_steam_score` | integer | No | 0 | Minimum Steam rating |
| `sort` | string | No | `trending` | `trending` / `cut:desc` / `price:asc` / `time:desc` |

---

## Project Structure

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

## Development

```bash
# Install test dependencies
pip install requests pytest

# Run tests
pytest tests/ -v
```

Tests use a `FakePluginContext` to simulate Hermes without requiring a live API connection or a real API key.

---

## License

MIT
