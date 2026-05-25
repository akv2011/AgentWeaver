import { useState } from 'react';
import { Play, Loader2, ChevronDown } from 'lucide-react';
import type { ConnectionState } from '../hooks/useWorkflowStream';
import { triggerDemoWorkflow } from '../lib/api';

interface HeroProps {
  connectionState: ConnectionState;
  onWorkflowStarted: () => void;
}

const marqueeItems = [
  'FastAPI',
  'LangGraph',
  'WebSockets',
  'Redis Upstash',
  'React 18',
  'Supervisor Pattern',
  'Real-time Streaming',
  'Multi-agent',
];

export default function Hero({ connectionState, onWorkflowStarted }: HeroProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);
    try {
      await triggerDemoWorkflow();
      onWorkflowStarted();
    } catch (e) {
      setError('Could not reach backend. It may be waking from cold start — try again in 30s.');
    } finally {
      setIsLoading(false);
    }
  }

  const connLabel =
    connectionState === 'connected'
      ? 'Connected'
      : connectionState === 'connecting'
      ? 'Connecting'
      : 'Disconnected';

  return (
    <section
      aria-label="Introduction"
      style={{ paddingTop: 'clamp(5rem, 14vh, 9rem)', paddingBottom: '5rem', position: 'relative' }}
    >
      {/* Background decorative number */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: '0',
          right: '-2%',
          userSelect: 'none',
          pointerEvents: 'none',
          lineHeight: '0.85',
          zIndex: 0,
        }}
      >
        <span className="hero-deco-num reveal-fade delay-0">03</span>
      </div>

      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 clamp(1.25rem, 5vw, 3.5rem)',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Section label + status pill row */}
        <div
          className="reveal delay-0"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
            marginBottom: '1.75rem',
          }}
        >
          <p className="section-label">
            Portfolio&nbsp;&nbsp;/&nbsp;&nbsp;Apple Developer Academy @ BINUS
          </p>

          {/* Status pill */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.3rem 0.75rem',
              borderRadius: '999px',
              border: '1px solid var(--col-border2)',
              background: 'var(--col-surface)',
              fontFamily: 'var(--font-body)',
              fontSize: '0.6875rem',
              fontWeight: 500,
              letterSpacing: '0.04em',
              color: 'var(--col-muted)',
            }}
          >
            <span className={`status-dot ${connectionState}`} aria-hidden="true" />
            <span>{connLabel}</span>
          </div>
        </div>

        {/* Main headline */}
        <h1
          className="hero-headline reveal delay-1"
          style={{ maxWidth: '17ch', marginBottom: '2rem' }}
        >
          Watch AI agents{' '}
          <em>collaborate</em>
          <br />
          in real time.
        </h1>

        {/* Sub-headline */}
        <p
          className="reveal delay-2"
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: 'clamp(1rem, 2.2vw, 1.1875rem)',
            color: 'var(--col-muted)',
            maxWidth: '50ch',
            lineHeight: '1.7',
            marginBottom: '2.75rem',
            fontWeight: 400,
          }}
        >
          Three specialist agents — text analysis, data processing, and API integration —
          coordinated by a supervisor and{' '}
          <span
            style={{
              color: 'var(--col-text)',
              fontStyle: 'italic',
              fontFamily: 'var(--font-display)',
              fontWeight: 500,
            }}
          >
            streaming every step live over WebSocket.
          </span>
        </p>

        {/* CTA */}
        <div className="reveal delay-3" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'flex-start' }}>
          <button
            className="btn-primary"
            onClick={handleRun}
            disabled={isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={15} strokeWidth={2} aria-hidden="true" style={{ animation: 'spin 0.8s linear infinite' }} />
                Starting workflow...
              </>
            ) : (
              <>
                <Play size={14} strokeWidth={2} aria-hidden="true" />
                Run a demo workflow
              </>
            )}
          </button>

          {error && (
            <p
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.8125rem',
                color: '#c9843a',
                maxWidth: '48ch',
                lineHeight: 1.5,
              }}
              role="alert"
            >
              {error}
            </p>
          )}
        </div>

        {/* Author + meta */}
        <div
          className="reveal delay-4"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            marginTop: '3.5rem',
            marginBottom: '4rem',
          }}
        >
          <div
            aria-hidden="true"
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--col-amber-dim) 0%, var(--col-amber) 100%)',
              border: '1px solid var(--col-amber-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: '1rem',
              color: '#fff',
              fontStyle: 'italic',
              flexShrink: 0,
            }}
          >
            A
          </div>
          <div>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.875rem', color: 'var(--col-text)', fontWeight: 500, lineHeight: 1.2 }}>
              Arunkumar V
            </p>
            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.75rem', color: 'var(--col-muted)', lineHeight: 1.2 }}>
              Full-stack · Multi-agent systems
            </p>
          </div>
          <div style={{ height: '24px', width: '1px', background: 'var(--col-border2)', marginLeft: '0.25rem' }} />
          <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.75rem', color: 'var(--col-muted)' }}>
            3 agents&nbsp;&nbsp;·&nbsp;&nbsp;Live WS stream
          </p>
        </div>

        {/* Scroll hint */}
        <div
          className="scroll-hint"
          style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '0.35rem' }}
        >
          <span
            style={{
              fontSize: '0.625rem',
              fontFamily: 'var(--font-body)',
              fontWeight: 600,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: 'var(--col-faint)',
            }}
          >
            Scroll
          </span>
          <ChevronDown size={16} strokeWidth={1.5} style={{ color: 'var(--col-muted)' }} aria-hidden="true" />
        </div>
      </div>

      {/* Marquee stripe */}
      <div className="marquee-track reveal-fade delay-5" style={{ marginTop: '4rem' }} aria-hidden="true">
        <div className="marquee-inner">
          {[...marqueeItems, ...marqueeItems].map((item, i) => (
            <span key={i} className="marquee-item">
              {item}
              <span className="marquee-dot" />
            </span>
          ))}
        </div>
      </div>

      {/* spin keyframe inline */}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </section>
  );
}
