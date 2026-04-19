# OpenRouter Pricing & Model Reference
> Last Updated: April 19, 2026 — Scraped live from openrouter.ai

## How OpenRouter Works

OpenRouter is a **unified API gateway** for 200+ AI models. You deposit credits ($10 currently on file), get a single API key, and route requests to any supported model. Pricing is per-token, deducted from your balance at the selected model's rate.

- **API Base URL:** `https://openrouter.ai/api/v1/chat/completions`
- **Auth:** Bearer token via `OPENROUTER_API_KEY`
- **Key Location:** `execution/hermes-agent/.env`
- **Schema:** OpenAI-compatible (drop-in replacement)
- **Token Tracking:** `/api/v1/credits` (balance) + `/api/v1/auth/key` (burn rates)
- **Our Monitor Script:** `execution/monitor_usage.py` (Rich CLI dashboard)

---

## Current Account Status
| Metric | Value |
|--------|-------|
| Deposited | $10.00 |
| Spent (all time) | $0.045 |
| Available Balance | **$9.955** |
| Current Model | `openai/gpt-4o-mini` via OpenRouter |

---

## Google Gemini Models on OpenRouter (All have 1.05M context window)

### Budget Tier (< $0.50/M input)

| Model | OpenRouter ID | Input $/M | Output $/M | Tool Calling |
|-------|--------------|-----------|------------|:------------:|
| **Gemini 2.0 Flash Lite** | `google/gemini-2.0-flash-lite-001` | $0.075 | $0.30 | ✅ |
| **Gemini 2.0 Flash** | `google/gemini-2.0-flash` | $0.10 | $0.40 | ❌ |
| **Gemini 2.5 Flash Lite** | `google/gemini-2.5-flash-lite` | $0.10 | $0.40 | ✅ |
| **Gemini 2.5 Flash** | `google/gemini-2.5-flash` | $0.30 | $2.50 | ✅ |
| Gemini 3.1 Flash Lite Preview | `google/gemini-3.1-flash-lite-preview` | $0.25 | $1.50 | ✅ |

### Mid Tier ($0.50–$2/M input)

| Model | OpenRouter ID | Input $/M | Output $/M | Tool Calling |
|-------|--------------|-----------|------------|:------------:|
| Gemini 3 Flash Preview | `google/gemini-3-flash-preview` | $0.50 | $3.00 | ✅ |
| Gemini 2.5 Pro | `google/gemini-2.5-pro` | $1.25 | $10.00 | ✅ |

### Premium Tier ($2+/M input)

| Model | OpenRouter ID | Input $/M | Output $/M | Tool Calling |
|-------|--------------|-----------|------------|:------------:|
| Gemini 3.1 Pro Preview | `google/gemini-3.1-pro-preview` | $2.00 | $12.00 | ✅ |

---

## Non-Gemini Budget Models (Tool Calling Enabled)

| Model | OpenRouter ID | Input $/M | Output $/M | Context |
|-------|--------------|-----------|------------|---------|
| **Gemma 4 26B (FREE)** | `google/gemma-4-26b-a4b-it` | $0.00 | $0.00 | 262K |
| **Gemma 4 31B (FREE)** | `google/gemma-4-31b-it` | $0.00 | $0.00 | 262K |
| GPT-5 Nano | `openai/gpt-5-nano` | $0.20 | $1.25 | 262K |
| GPT-4o-mini (CURRENT) | `openai/gpt-4o-mini` | $0.15 | $0.60 | 128K |

---

## Premium Models (Reference Only)

| Model | OpenRouter ID | Input $/M | Output $/M | Context |
|-------|--------------|-----------|------------|---------|
| Claude Opus 4.7 | `anthropic/claude-opus-4.7` | $5.00 | $25.00 | 262K |
| GPT-4 | `openai/gpt-4` | $30.00 | $60.00 | 1M |

---

## Runway Projections (Based on $9.955 balance)

| Model | Cost/1M tokens (blended) | Runway (tokens) |
|-------|-------------------------|-----------------|
| Gemma 4 (free) | $0.00 | ∞ (unlimited) |
| Gemini 2.0 Flash Lite | ~$0.19 | ~52.4M |
| Gemini 2.5 Flash Lite | ~$0.25 | ~39.8M |
| GPT-4o-mini (current) | ~$0.375 | ~26.5M |
| Gemini 2.5 Flash | ~$1.40 | ~7.1M |
| Gemini 2.5 Pro | ~$5.63 | ~1.8M |

---

## Hermes Configuration

### Config File
`execution/hermes-agent/config.yaml`
```yaml
model:
  default: openai/gpt-4o-mini    # <-- Change this to switch models
  provider: openrouter
```

### Changing Models
- **Live (in session):** Type `/model google/gemini-2.0-flash-lite-001` in the Hermes terminal
- **Permanent (shell):** Run `hermes model` from the system shell
- **Manual:** Edit `config.yaml` directly and restart

### Environment Variables
`execution/hermes-agent/.env`
```
OPENROUTER_API_KEY="sk-or-v1-xxxxx..."
```

---

## Recommendation for Cost-Optimized Agent Use

For Hermes background automation (cron jobs, general chat, tool calling):

1. **Best value with tools:** `google/gemini-2.5-flash-lite` — $0.10/$0.40 per M, 1.05M context, tool calling ✅
2. **Absolute cheapest:** `google/gemini-2.0-flash-lite-001` — $0.075/$0.30 per M, tool calling ✅
3. **Free tier (experimental):** `google/gemma-4-31b-it` — $0 but may have quality/reliability tradeoffs

Current `gpt-4o-mini` is solid but ~2-4x more expensive than the Gemini Flash Lite options.
