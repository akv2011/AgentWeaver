"""Multi-agent stock analysis pipeline.

The user asks a natural-language stock question. Three specialist agents run in
sequence and a supervisor synthesizes the final chat reply, with each step
broadcast over the existing WebSocket integration so the frontend can render
visible reasoning.

External services:
    yfinance        - live Yahoo market data, no auth, free
    OpenRouter      - perplexity/sonar for web-grounded news, claude haiku 4.5
                      for ticker resolution / analysis / synthesis
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from typing import Any

import httpx
import yfinance as yf

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HAIKU_MODEL = "anthropic/claude-haiku-4.5"
SONAR_MODEL = "perplexity/sonar"

_TICKER_RE = re.compile(r"(?:\$)?\b([A-Z]{1,5}(?:\.[A-Z])?)\b")
_COMMON_WORDS = {
    "I", "A", "AN", "THE", "IS", "IT", "OR", "AND", "BUT", "ON", "AT", "TO",
    "WHAT", "HOW", "WHY", "WHEN", "WHERE", "WHO", "DO", "DOES", "DID", "AM",
    "BE", "BEEN", "ARE", "WAS", "WERE", "HAS", "HAVE", "HAD", "WILL", "WOULD",
    "SHOULD", "CAN", "COULD", "MAY", "MIGHT", "MUST", "OF", "FOR", "IN", "OUT",
    "UP", "DOWN", "OK", "OH", "NO", "YES", "NOW", "VS", "VS.",
}


# ---------------------------------------------------------------------------
# OpenRouter helper
# ---------------------------------------------------------------------------


async def _openrouter_chat(
    model: str,
    messages: list[dict],
    *,
    response_format_json: bool = False,
    max_tokens: int = 800,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Single shared OpenRouter call with structured error handling."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return {"error": "OPENROUTER_API_KEY not configured on the server."}

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if response_format_json:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agentweaver-frontend.vercel.app",
        "X-Title": "AgentWeaver Stock Analyst",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        if r.status_code != 200:
            return {
                "error": f"OpenRouter HTTP {r.status_code}",
                "detail": r.text[:300],
            }
        data = r.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        result = {"content": content}
        if "citations" in data:
            result["citations"] = data["citations"]
        return result
    except (httpx.RequestError, httpx.TimeoutException) as exc:
        return {"error": f"{exc.__class__.__name__}: {exc}"}


def _parse_json_loose(content: str) -> dict[str, Any] | None:
    """Try to parse JSON from a model response, tolerating code fences."""
    if not content:
        return None
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```\s*$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", stripped)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None


# ---------------------------------------------------------------------------
# Step 1: ticker resolution
# ---------------------------------------------------------------------------


async def resolve_tickers(query: str) -> list[str]:
    """Pull up to 2 tickers from a natural-language question.

    Strategy: take the LLM's interpretation first (handles company names like
    'Apple', 'Nvidia') and fall back to a regex scan if that fails.
    """
    system = (
        "You extract US stock ticker symbols from user questions. "
        "Return JSON of the form {\"tickers\": [\"AAPL\", \"NVDA\"]}. "
        "Maximum 2 tickers. If the user names a company (Apple, Nvidia, Tesla), "
        "resolve to the correct primary US ticker. If you cannot identify any, "
        "return {\"tickers\": []}. Output JSON only."
    )
    resp = await _openrouter_chat(
        HAIKU_MODEL,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        response_format_json=True,
        max_tokens=120,
        timeout=20,
    )
    parsed = _parse_json_loose(resp.get("content", "") or "")
    tickers: list[str] = []
    if parsed and isinstance(parsed.get("tickers"), list):
        for t in parsed["tickers"][:2]:
            if isinstance(t, str) and t.strip():
                tickers.append(t.strip().upper())

    if not tickers:
        for m in _TICKER_RE.findall(query):
            up = m.upper()
            if up in _COMMON_WORDS:
                continue
            if up not in tickers:
                tickers.append(up)
            if len(tickers) >= 2:
                break

    return tickers


# ---------------------------------------------------------------------------
# Step 2: market data via yfinance
# ---------------------------------------------------------------------------


def _fetch_market_data_sync(ticker: str) -> dict[str, Any]:
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
    except Exception as exc:  # noqa: BLE001
        return {"ticker": ticker, "error": f"yfinance failed: {exc.__class__.__name__}"}

    price = info.get("regularMarketPrice") or info.get("currentPrice")
    prev_close = info.get("previousClose")
    if price is None or prev_close is None:
        return {
            "ticker": ticker,
            "error": "Market data unavailable for this ticker right now.",
        }

    change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else None
    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName") or ticker,
        "currency": info.get("currency", "USD"),
        "price": round(float(price), 2),
        "previous_close": round(float(prev_close), 2),
        "change_pct": round(float(change_pct), 2) if change_pct is not None else None,
        "day_low": info.get("regularMarketDayLow"),
        "day_high": info.get("regularMarketDayHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "ma_50": round(float(info["fiftyDayAverage"]), 2) if info.get("fiftyDayAverage") else None,
        "ma_200": round(float(info["twoHundredDayAverage"]), 2) if info.get("twoHundredDayAverage") else None,
        "market_cap": info.get("marketCap"),
        "pe_ratio": round(float(info["trailingPE"]), 2) if info.get("trailingPE") else None,
        "volume": info.get("regularMarketVolume") or info.get("volume"),
    }


async def fetch_market_data(tickers: list[str]) -> dict[str, Any]:
    if not tickers:
        return {"error": "No tickers identified in the question.", "results": []}
    results = await asyncio.gather(
        *[asyncio.to_thread(_fetch_market_data_sync, t) for t in tickers]
    )
    return {"results": list(results)}


# ---------------------------------------------------------------------------
# Step 3: news context via Perplexity Sonar
# ---------------------------------------------------------------------------


async def fetch_news_context(tickers: list[str], query: str) -> dict[str, Any]:
    if not tickers:
        return {"error": "Cannot fetch news without a resolved ticker."}

    tickers_str = ", ".join(tickers)
    user_msg = (
        f"Find 3-5 of the most relevant recent news items about "
        f"{tickers_str} that would help answer this question: \"{query}\".\n\n"
        "Return a JSON object with this shape (no commentary, JSON only):\n"
        "{\n"
        '  "headlines": [\n'
        '    {"title": "...", "source": "...", "summary": "...", "sentiment": "positive|neutral|negative"}\n'
        "  ],\n"
        '  "overall_sentiment": "positive|neutral|negative|mixed",\n'
        '  "as_of": "today\'s date"\n'
        "}"
    )
    resp = await _openrouter_chat(
        SONAR_MODEL,
        [{"role": "user", "content": user_msg}],
        max_tokens=900,
        timeout=45,
    )
    content = resp.get("content", "")
    parsed = _parse_json_loose(content)
    if not parsed:
        return {
            "headlines": [],
            "overall_sentiment": "unknown",
            "note": "Could not parse news response.",
            "raw_excerpt": content[:300] if content else None,
        }
    if resp.get("citations"):
        parsed["citations"] = resp["citations"][:5]
    return parsed


# ---------------------------------------------------------------------------
# Step 4: structured analysis
# ---------------------------------------------------------------------------


async def analyze(
    market: dict[str, Any], news: dict[str, Any], query: str
) -> dict[str, Any]:
    system = (
        "You are a structured equity analyst. Given live market data and a news "
        "briefing, return JSON of the form:\n"
        "{\n"
        '  "trend_signal": "bullish|neutral|bearish",\n'
        '  "confidence": 0.0-1.0,\n'
        '  "key_catalysts": ["..."],\n'
        '  "key_risks": ["..."],\n'
        '  "time_horizon_note": "..."\n'
        "}\n"
        "Output JSON only. Be sober and evidence-based. Up to 4 catalysts and 4 risks."
    )
    user = json.dumps(
        {"original_question": query, "market_data": market, "news_context": news},
        default=str,
    )
    resp = await _openrouter_chat(
        HAIKU_MODEL,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format_json=True,
        max_tokens=700,
        timeout=30,
    )
    parsed = _parse_json_loose(resp.get("content", "") or "")
    if not parsed:
        return {
            "trend_signal": "neutral",
            "confidence": 0.0,
            "key_catalysts": [],
            "key_risks": [],
            "time_horizon_note": "Analysis unavailable.",
            "error": resp.get("error", "Could not parse analyst response."),
        }
    return parsed


# ---------------------------------------------------------------------------
# Step 5: final chat synthesis
# ---------------------------------------------------------------------------


async def synthesize_reply(
    query: str,
    market: dict[str, Any],
    news: dict[str, Any],
    analysis: dict[str, Any],
) -> str:
    system = (
        "You are a friendly equity analyst writing a chat reply. Use the "
        "live market data, news context, and structured analysis you are given "
        "to answer the user's question in 2-4 short paragraphs of markdown. "
        "Mention the actual price and day change. Cite at least one headline "
        "by source. End with one italicized disclaimer line: "
        "*This is analysis, not investment advice.*"
    )
    user = json.dumps(
        {
            "user_question": query,
            "market_data": market,
            "news_context": news,
            "analysis": analysis,
        },
        default=str,
    )
    resp = await _openrouter_chat(
        HAIKU_MODEL,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=900,
        timeout=30,
    )
    return resp.get("content") or (
        "I could not generate a final reply. The error was: "
        f"{resp.get('error', 'unknown')}"
    )


# ---------------------------------------------------------------------------
# Orchestrator (publishes WS events as it goes)
# ---------------------------------------------------------------------------


async def run_pipeline(workflow_id: str, query: str) -> None:
    """Drive the full pipeline, emitting WebSocket events at each step.

    Imports the integration service lazily so this module can be imported
    standalone (e.g. for unit tests) without booting the WS manager.
    """
    from src.services.websocket_integration import integration_service

    started = time.perf_counter()

    await integration_service.notify_workflow_started(
        workflow_id,
        {"estimated_steps": 4, "input_data": {"query": query[:300]}},
    )

    # ---- Step 1: text_analyzer → market data ------------------------------
    await integration_service.notify_agent_status_change(
        "text_analyzer", "idle", "busy",
        {"current_task": "Resolving ticker symbols..."},
    )
    tickers = await resolve_tickers(query)

    if tickers:
        await integration_service.notify_agent_status_change(
            "text_analyzer", "busy", "busy",
            {"current_task": f"Fetching live market data for {', '.join(tickers)}..."},
        )

    market = await fetch_market_data(tickers)
    market["tickers"] = tickers
    await integration_service.notify_workflow_step(
        workflow_id, "market_data", market
    )
    await integration_service.notify_agent_status_change(
        "text_analyzer", "busy", "idle", {"current_task": None}
    )

    # ---- Step 2: data_processor → news context ----------------------------
    await integration_service.notify_agent_status_change(
        "data_processor", "idle", "busy",
        {"current_task": "Searching latest news with web context..."},
    )
    news = await fetch_news_context(tickers, query)
    await integration_service.notify_workflow_step(workflow_id, "news", news)
    await integration_service.notify_agent_status_change(
        "data_processor", "busy", "idle", {"current_task": None}
    )

    # ---- Step 3: api_client → structured analysis -------------------------
    await integration_service.notify_agent_status_change(
        "api_client", "idle", "busy",
        {"current_task": "Computing trend signal and catalysts..."},
    )
    analysis = await analyze(market, news, query)
    await integration_service.notify_workflow_step(workflow_id, "analysis", analysis)
    await integration_service.notify_agent_status_change(
        "api_client", "busy", "idle", {"current_task": None}
    )

    # ---- Step 4: supervisor synthesis -------------------------------------
    reply = await synthesize_reply(query, market, news, analysis)
    await integration_service.notify_workflow_step(
        workflow_id,
        "synthesis",
        {"reply_markdown": reply},
    )

    elapsed = round(time.perf_counter() - started, 2)
    await integration_service.notify_workflow_completed(
        workflow_id,
        {
            "execution_time": elapsed,
            "tickers_analyzed": tickers,
            "result_summary": {"tickers": tickers, "elapsed_seconds": elapsed},
        },
    )
