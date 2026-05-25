import { Activity, Clock, CheckCircle2 } from 'lucide-react';
import type { TimelineEvent } from '../hooks/useWorkflowStream';

interface LiveTimelineProps {
  timeline: TimelineEvent[];
  progress: number;
  isRunning: boolean;
  completionTime: number | null;
}

const AGENT_LABELS: Record<string, string> = {
  text_analyzer: 'Text Analyzer',
  data_processor: 'Data Processor',
  api_client: 'API Client',
};

function eventIcon(type: TimelineEvent['type']) {
  if (type === 'workflow_completed') {
    return (
      <CheckCircle2
        size={13}
        strokeWidth={2}
        style={{ color: '#4d8c6f', flexShrink: 0 }}
        aria-hidden="true"
      />
    );
  }
  if (type === 'agent_update') {
    return (
      <Activity
        size={13}
        strokeWidth={2}
        style={{ color: 'var(--col-amber)', flexShrink: 0 }}
        aria-hidden="true"
      />
    );
  }
  return (
    <Clock
      size={13}
      strokeWidth={1.5}
      style={{ color: 'var(--col-muted)', flexShrink: 0 }}
      aria-hidden="true"
    />
  );
}

export default function LiveTimeline({
  timeline,
  progress,
  isRunning,
  completionTime,
}: LiveTimelineProps) {
  const hasEvents = timeline.length > 0;
  const isComplete = !isRunning && completionTime !== null;

  return (
    <section
      aria-labelledby="timeline-heading"
      style={{
        borderTop: '1px solid var(--col-border)',
        background: 'var(--col-surface)',
        padding: 'clamp(4rem, 10vh, 7rem) 0',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 clamp(1.25rem, 5vw, 3.5rem)',
        }}
      >
        {/* Section header */}
        <div style={{ marginBottom: '2.5rem' }}>
          <p className="section-label reveal delay-0" style={{ marginBottom: '0.75rem' }}>
            Live Timeline
          </p>
          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.75rem',
            }}
          >
            <h2
              id="timeline-heading"
              className="reveal delay-1"
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: 'clamp(2rem, 5vw, 3.25rem)',
                letterSpacing: '-0.03em',
                lineHeight: 1.05,
                color: 'var(--col-text)',
              }}
            >
              {isComplete ? (
                <>
                  Workflow complete{' '}
                  <span style={{ fontStyle: 'italic', color: 'var(--col-muted)' }}>
                    in {completionTime!.toFixed(1)}s
                  </span>
                </>
              ) : isRunning ? (
                <>
                  Running{' '}
                  <span style={{ fontStyle: 'italic', color: 'var(--col-amber-glow)' }}>
                    now
                  </span>
                </>
              ) : (
                'Event stream'
              )}
            </h2>

            {/* Running indicator */}
            {isRunning && (
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.75rem',
                  color: 'var(--col-amber-glow)',
                  fontWeight: 500,
                  letterSpacing: '0.04em',
                }}
              >
                <span className="status-dot busy" aria-hidden="true" />
                Receiving events
              </div>
            )}
            {isComplete && (
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.75rem',
                  color: '#4d8c6f',
                  fontWeight: 500,
                }}
              >
                <CheckCircle2 size={13} strokeWidth={2} aria-hidden="true" />
                {completionTime!.toFixed(1)}s total
              </div>
            )}
          </div>
        </div>

        {/* Progress bar — always reserve space */}
        <div
          style={{
            height: '3px',
            background: 'var(--col-border)',
            borderRadius: '2px',
            marginBottom: '2rem',
            overflow: 'hidden',
          }}
          role="progressbar"
          aria-valuenow={Math.round(progress * 100)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Workflow progress"
        >
          <div
            style={{
              height: '100%',
              width: `${Math.round(progress * 100)}%`,
              background: isComplete
                ? '#4d8c6f'
                : 'linear-gradient(90deg, var(--col-amber-dim), var(--col-amber-glow))',
              borderRadius: '2px',
              transition: 'width 0.6s var(--ease-out-expo), background 0.5s ease',
            }}
          />
        </div>

        {/* Timeline surface */}
        <div className="glass-surface reveal delay-2">
          {!hasEvents ? (
            /* Empty state */
            <div
              style={{
                padding: 'clamp(3rem, 8vw, 5rem) clamp(1.5rem, 4vw, 2.5rem)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.75rem',
                textAlign: 'center',
              }}
            >
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  border: '1px solid var(--col-border2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--col-faint)',
                }}
                aria-hidden="true"
              >
                <Activity size={18} strokeWidth={1.5} />
              </div>
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.9375rem',
                  color: 'var(--col-muted)',
                  lineHeight: 1.5,
                }}
              >
                No workflows yet
              </p>
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.8125rem',
                  color: 'var(--col-faint)',
                  fontStyle: 'italic',
                }}
              >
                Press "Run a demo workflow" above to start
              </p>
            </div>
          ) : (
            /* Event rows */
            <div
              style={{ padding: 'clamp(1.25rem, 3vw, 1.75rem)' }}
              role="log"
              aria-label="Workflow event log"
              aria-live="polite"
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                {timeline.map((ev, idx) => (
                  <div
                    key={ev.id}
                    className="timeline-row"
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.875rem',
                      padding: '0.875rem 0',
                      borderBottom:
                        idx < timeline.length - 1
                          ? '1px solid var(--col-border)'
                          : 'none',
                      animationDelay: '0s',
                    }}
                  >
                    {/* Timeline connector line */}
                    <div
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        paddingTop: '1px',
                        flexShrink: 0,
                      }}
                    >
                      {eventIcon(ev.type)}
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'baseline',
                          justifyContent: 'space-between',
                          gap: '1rem',
                          flexWrap: 'wrap',
                          marginBottom: ev.detail ? '0.25rem' : 0,
                        }}
                      >
                        <p
                          style={{
                            fontFamily: 'var(--font-body)',
                            fontSize: '0.875rem',
                            color: 'var(--col-text)',
                            fontWeight: 500,
                            lineHeight: 1.3,
                          }}
                        >
                          {ev.agentId ? (
                            <>
                              <span
                                style={{
                                  color: 'var(--col-amber-glow)',
                                  fontWeight: 600,
                                }}
                              >
                                {AGENT_LABELS[ev.agentId] ?? ev.agentId}
                              </span>
                              {' — '}
                              {ev.label}
                            </>
                          ) : (
                            ev.label
                          )}
                        </p>
                        <span
                          style={{
                            fontFamily: 'var(--font-body)',
                            fontSize: '0.6875rem',
                            color: 'var(--col-faint)',
                            fontVariantNumeric: 'tabular-nums',
                            fontFeatureSettings: '"tnum"',
                            flexShrink: 0,
                            letterSpacing: '0.03em',
                          }}
                        >
                          {ev.timestamp}
                        </span>
                      </div>

                      {ev.detail && (
                        <p
                          style={{
                            fontFamily: 'var(--font-body)',
                            fontSize: '0.75rem',
                            color: 'var(--col-muted)',
                            lineHeight: 1.5,
                            fontVariantNumeric: 'tabular-nums',
                          }}
                        >
                          {ev.detail}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
