import { useState } from 'react';
import { CheckCircle2, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { AgentState } from '../hooks/useWorkflowStream';

// ─── Step-data sub-types ──────────────────────────────────────────────────────

interface TickerResult {
  ticker: string;
  name: string;
  currency: string;
  price: number;
  previous_close: number;
  change_pct: number;
  day_low: number;
  day_high: number;
  fifty_two_week_low: number;
  fifty_two_week_high: number;
  ma_50: number;
  ma_200: number;
  market_cap: number;
  pe_ratio: number;
  volume: number;
}

interface MarketDataStep {
  tickers: string[];
  results: TickerResult[];
}

interface Headline {
  title: string;
  source: string;
  summary: string;
  sentiment: string;
}

interface NewsStep {
  headlines: Headline[];
  overall_sentiment: string;
  as_of: string;
  citations?: string[];
}

interface AnalysisStep {
  trend_signal: 'bullish' | 'neutral' | 'bearish';
  confidence: number;
  key_catalysts: string[];
  key_risks: string[];
  time_horizon_note: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmtMarketCap(val: number): string {
  if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
  if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
  if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
  return `$${val.toFixed(0)}`;
}

function fmtNum(val: number, decimals = 2): string {
  return val.toFixed(decimals);
}

// ─── Step-data renderers ──────────────────────────────────────────────────────

function MarketDataRenderer({ data }: { data: MarketDataStep }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', marginTop: '0.75rem' }}>
      {data.results.map((r) => {
        const isPositive = r.change_pct >= 0;
        return (
          <div
            key={r.ticker}
            style={{
              padding: '0.875rem 1rem',
              borderRadius: '6px',
              background: 'var(--col-surface2)',
              border: '1px solid var(--col-border)',
            }}
          >
            {/* Ticker + price row */}
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    color: 'var(--col-text)',
                    background: 'var(--col-amber-bg)',
                    border: '1px solid var(--col-amber-border)',
                    borderRadius: '3px',
                    padding: '0.1em 0.5em',
                    letterSpacing: '0.04em',
                  }}
                >
                  {r.ticker}
                </span>
                <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.8125rem', color: 'var(--col-muted)' }}>
                  {r.name}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                <span
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700,
                    fontSize: '1.25rem',
                    letterSpacing: '-0.02em',
                    color: 'var(--col-text)',
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {r.currency} {fmtNum(r.price)}
                </span>
                <span
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: isPositive ? '#4d8c6f' : '#c46060',
                    background: isPositive ? 'rgba(77,140,111,0.1)' : 'rgba(196,96,96,0.1)',
                    border: `1px solid ${isPositive ? 'rgba(77,140,111,0.3)' : 'rgba(196,96,96,0.3)'}`,
                    borderRadius: '3px',
                    padding: '0.1em 0.45em',
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {isPositive ? '+' : ''}{fmtNum(r.change_pct)}%
                </span>
              </div>
            </div>
            {/* Meta rows */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                gap: '0.25rem 1rem',
              }}
            >
              {[
                { label: 'Day range', value: `${fmtNum(r.day_low)} – ${fmtNum(r.day_high)}` },
                { label: '52W range', value: `${fmtNum(r.fifty_two_week_low)} – ${fmtNum(r.fifty_two_week_high)}` },
                { label: 'MA50', value: fmtNum(r.ma_50) },
                { label: 'MA200', value: fmtNum(r.ma_200) },
                { label: 'Mkt cap', value: fmtMarketCap(r.market_cap) },
                { label: 'P/E', value: r.pe_ratio ? fmtNum(r.pe_ratio, 1) : 'N/A' },
              ].map((m) => (
                <div key={m.label} style={{ display: 'flex', gap: '0.35rem' }}>
                  <span
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.6875rem',
                      color: 'var(--col-faint)',
                      letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                      fontWeight: 600,
                      flexShrink: 0,
                    }}
                  >
                    {m.label}
                  </span>
                  <span
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.6875rem',
                      color: 'var(--col-muted)',
                      fontVariantNumeric: 'tabular-nums',
                    }}
                  >
                    {m.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function sentimentColor(s: string): string {
  if (s === 'positive') return '#4d8c6f';
  if (s === 'negative') return '#c46060';
  if (s === 'mixed') return 'var(--col-amber-glow)';
  return 'var(--col-muted)';
}

function NewsRenderer({ data }: { data: NewsStep }) {
  return (
    <div style={{ marginTop: '0.75rem' }}>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          marginBottom: '0.75rem',
          padding: '0.2rem 0.6rem',
          borderRadius: '3px',
          fontSize: '0.6875rem',
          fontFamily: 'var(--font-body)',
          fontWeight: 600,
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          color: sentimentColor(data.overall_sentiment),
          border: `1px solid ${sentimentColor(data.overall_sentiment)}44`,
          background: `${sentimentColor(data.overall_sentiment)}12`,
        }}
      >
        Overall: {data.overall_sentiment}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
        {data.headlines.map((h, i) => (
          <div
            key={i}
            style={{
              padding: '0.75rem',
              borderRadius: '5px',
              background: 'var(--col-surface2)',
              border: '1px solid var(--col-border)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem', marginBottom: '0.3rem' }}>
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.8125rem',
                  color: 'var(--col-text)',
                  fontWeight: 600,
                  lineHeight: 1.4,
                  flex: 1,
                }}
              >
                {h.title}
              </p>
              <span
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.625rem',
                  fontWeight: 600,
                  color: sentimentColor(h.sentiment),
                  border: `1px solid ${sentimentColor(h.sentiment)}44`,
                  background: `${sentimentColor(h.sentiment)}12`,
                  borderRadius: '3px',
                  padding: '0.1em 0.4em',
                  letterSpacing: '0.04em',
                  textTransform: 'uppercase',
                  flexShrink: 0,
                  marginTop: '1px',
                }}
              >
                {h.sentiment}
              </span>
            </div>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.6875rem', color: 'var(--col-muted)', marginBottom: '0.2rem' }}>
              {h.source}
            </p>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.75rem', color: 'var(--col-muted)', lineHeight: 1.5 }}>
              {h.summary}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalysisRenderer({ data }: { data: AnalysisStep }) {
  const signalColor =
    data.trend_signal === 'bullish'
      ? '#4d8c6f'
      : data.trend_signal === 'bearish'
      ? '#c46060'
      : 'var(--col-muted)';

  const SignalIcon =
    data.trend_signal === 'bullish'
      ? TrendingUp
      : data.trend_signal === 'bearish'
      ? TrendingDown
      : Minus;

  return (
    <div style={{ marginTop: '0.75rem' }}>
      {/* Trend signal pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.4rem 0.875rem',
            borderRadius: '999px',
            background: `${signalColor}14`,
            border: `1px solid ${signalColor}44`,
            color: signalColor,
          }}
        >
          <SignalIcon size={14} strokeWidth={2} aria-hidden="true" />
          <span
            style={{
              fontFamily: 'var(--font-body)',
              fontWeight: 700,
              fontSize: '0.875rem',
              textTransform: 'capitalize',
              letterSpacing: '0.02em',
            }}
          >
            {data.trend_signal}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.75rem', color: 'var(--col-muted)' }}>
            Confidence:
          </span>
          <span
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--col-text)',
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {Math.round(data.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Catalysts vs risks two-column */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '0.75rem',
        }}
      >
        <div>
          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.6875rem',
              fontWeight: 600,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: '#4d8c6f',
              marginBottom: '0.5rem',
            }}
          >
            Catalysts
          </p>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {data.key_catalysts.map((c, i) => (
              <li
                key={i}
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.75rem',
                  color: 'var(--col-muted)',
                  lineHeight: 1.5,
                  paddingLeft: '0.75rem',
                  borderLeft: '2px solid rgba(77,140,111,0.3)',
                }}
              >
                {c}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.6875rem',
              fontWeight: 600,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: '#c46060',
              marginBottom: '0.5rem',
            }}
          >
            Risks
          </p>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {data.key_risks.map((r, i) => (
              <li
                key={i}
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.75rem',
                  color: 'var(--col-muted)',
                  lineHeight: 1.5,
                  paddingLeft: '0.75rem',
                  borderLeft: '2px solid rgba(196,96,96,0.3)',
                }}
              >
                {r}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {data.time_horizon_note && (
        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.75rem',
            color: 'var(--col-faint)',
            fontStyle: 'italic',
            marginTop: '0.75rem',
            lineHeight: 1.5,
          }}
        >
          {data.time_horizon_note}
        </p>
      )}
    </div>
  );
}

// ─── Agent row ────────────────────────────────────────────────────────────────

const AGENT_UI: Record<string, { label: string; step: string }> = {
  text_analyzer: { label: 'Market Data Agent', step: 'market_data' },
  data_processor: { label: 'News & Sentiment Agent', step: 'news' },
  api_client:    { label: 'Technical Analyst', step: 'analysis' },
};

interface AgentRowProps {
  agentId: string;
  agent: AgentState;
  stepData: unknown | undefined;
  stepCompleted: boolean;
}

function AgentRow({ agentId, agent, stepData, stepCompleted }: AgentRowProps) {
  void agentId;
  const ui = AGENT_UI[agentId] ?? { label: agentId, step: agentId };
  const isBusy = agent.status === 'busy';
  const [expanded, setExpanded] = useState(true);

  return (
    <div
      style={{
        borderBottom: '1px solid var(--col-border)',
        paddingBottom: '0.875rem',
        marginBottom: '0.875rem',
      }}
    >
      {/* Row header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '0.75rem',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          {stepCompleted ? (
            <CheckCircle2
              size={14}
              strokeWidth={2}
              style={{ color: '#4d8c6f', flexShrink: 0 }}
              aria-hidden="true"
            />
          ) : (
            <span
              className={`status-dot${isBusy ? ' busy' : ''}`}
              aria-hidden="true"
              style={{ flexShrink: 0 }}
            />
          )}
          <span
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: stepCompleted ? 'var(--col-text)' : isBusy ? 'var(--col-amber-glow)' : 'var(--col-muted)',
              transition: 'color 0.3s',
            }}
          >
            {ui.label}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {agent.currentTask && !stepCompleted && (
            <span
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.75rem',
                color: 'var(--col-muted)',
                fontStyle: 'italic',
                maxWidth: '24ch',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {agent.currentTask}
            </span>
          )}
          {stepCompleted && Boolean(stepData) && (
            <button
              onClick={() => setExpanded((v) => !v)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0.2rem 0.4rem',
                borderRadius: '3px',
                fontFamily: 'var(--font-body)',
                fontSize: '0.6875rem',
                color: 'var(--col-muted)',
                transition: 'color 0.2s',
              }}
              aria-expanded={expanded}
              aria-label={expanded ? 'Collapse output' : 'Expand output'}
            >
              {expanded ? <ChevronUp size={12} strokeWidth={2} /> : <ChevronDown size={12} strokeWidth={2} />}
              {expanded ? 'hide' : 'show'}
            </button>
          )}
        </div>
      </div>

      {/* Expanded step-data */}
      {stepCompleted && Boolean(stepData) && expanded && (
        <div style={{ overflow: 'hidden' }}>
          {ui.step === 'market_data' && (
            <MarketDataRenderer data={stepData as MarketDataStep} />
          )}
          {ui.step === 'news' && (
            <NewsRenderer data={stepData as NewsStep} />
          )}
          {ui.step === 'analysis' && (
            <AnalysisRenderer data={stepData as AnalysisStep} />
          )}
        </div>
      )}
    </div>
  );
}

// ─── Panel ────────────────────────────────────────────────────────────────────

export interface AgentActivityPanelProps {
  agents: Record<string, AgentState>;
  latestOutputs: Record<string, unknown>;
  isRunning: boolean;
  executionTime: number | null;
  onExpandPast?: () => void;
  collapsed?: boolean;
}

export default function AgentActivityPanel({
  agents,
  latestOutputs,
  isRunning,
  executionTime,
  collapsed = false,
}: AgentActivityPanelProps) {
  const [panelExpanded, setPanelExpanded] = useState(!collapsed);

  const completedSteps = new Set<string>(
    Object.entries(AGENT_UI)
      .filter(([, ui]) => latestOutputs[ui.step] !== undefined)
      .map(([id]) => id)
  );

  const isDone = !isRunning && executionTime !== null;

  return (
    <div
      style={{
        background: 'var(--col-surface)',
        border: '1px solid var(--col-border)',
        borderRadius: '8px',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top gradient accent */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, var(--col-amber-border), transparent)',
        }}
      />

      {/* Panel header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.75rem 1rem',
          borderBottom: panelExpanded ? '1px solid var(--col-border)' : 'none',
          cursor: isDone ? 'pointer' : 'default',
        }}
        onClick={() => isDone && setPanelExpanded((v) => !v)}
        role={isDone ? 'button' : undefined}
        aria-expanded={isDone ? panelExpanded : undefined}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {isRunning && <span className="status-dot busy" aria-hidden="true" />}
          {isDone && <CheckCircle2 size={13} strokeWidth={2} style={{ color: '#4d8c6f' }} aria-hidden="true" />}
          <span
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: isRunning ? 'var(--col-amber-glow)' : 'var(--col-muted)',
              letterSpacing: '0.04em',
            }}
          >
            {isRunning ? 'Agents working…' : `3 agents · ${executionTime?.toFixed(1) ?? '?'}s · click to ${panelExpanded ? 'collapse' : 'expand'}`}
          </span>
        </div>
        {isDone && (
          panelExpanded
            ? <ChevronUp size={14} strokeWidth={2} style={{ color: 'var(--col-muted)' }} aria-hidden="true" />
            : <ChevronDown size={14} strokeWidth={2} style={{ color: 'var(--col-muted)' }} aria-hidden="true" />
        )}
      </div>

      {/* Agent rows */}
      {panelExpanded && (
        <div style={{ padding: '0.875rem 1rem 0.125rem' }}>
          {['text_analyzer', 'data_processor', 'api_client'].map((agentId) => (
            <AgentRow
              key={agentId}
              agentId={agentId}
              agent={agents[agentId] ?? { id: agentId, status: 'idle', currentTask: null }}
              stepData={latestOutputs[AGENT_UI[agentId]?.step ?? agentId]}
              stepCompleted={completedSteps.has(agentId)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
