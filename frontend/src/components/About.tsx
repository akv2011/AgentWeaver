import { Zap, Radio, Code2 } from 'lucide-react';

export default function About() {
  return (
    <section
      aria-labelledby="about-heading"
      style={{
        borderTop: '1px solid var(--col-border)',
        borderBottom: '1px solid var(--col-border)',
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
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 'clamp(2.5rem, 6vw, 5rem)',
            alignItems: 'start',
          }}
          className="about-grid"
        >
          {/* Left column */}
          <div style={{ maxWidth: '280px' }}>
            <p className="section-label reveal delay-0" style={{ marginBottom: '1rem' }}>
              About the Project
            </p>

            {/* Design pillars */}
            <div
              className="reveal delay-2"
              style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '2.5rem' }}
            >
              {[
                {
                  icon: <Radio size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'Real-time first',
                  sub: 'WebSocket, not polling',
                },
                {
                  icon: <Zap size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'On-trigger demos',
                  sub: 'No auto-play, no mocks',
                },
                {
                  icon: <Code2 size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'Production stack',
                  sub: 'FastAPI, LangGraph, Render',
                },
              ].map((item) => (
                <div
                  key={item.label}
                  style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}
                >
                  <div style={{ color: 'var(--col-amber)', marginTop: '1px', flexShrink: 0 }}>
                    {item.icon}
                  </div>
                  <div>
                    <p
                      style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.875rem',
                        color: 'var(--col-text)',
                        fontWeight: 600,
                        lineHeight: 1.2,
                        marginBottom: '0.15rem',
                      }}
                    >
                      {item.label}
                    </p>
                    <p
                      style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '0.75rem',
                        color: 'var(--col-muted)',
                        lineHeight: 1.4,
                      }}
                    >
                      {item.sub}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right column */}
          <div style={{ maxWidth: '640px' }}>
            <h2
              id="about-heading"
              className="reveal delay-1"
              style={{
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: 'clamp(1.875rem, 4vw, 2.75rem)',
                letterSpacing: '-0.03em',
                lineHeight: 1.1,
                color: 'var(--col-text)',
                marginBottom: '2rem',
              }}
            >
              Built to show what{' '}
              <em style={{ color: 'var(--col-amber-glow)' }}>real</em>{' '}
              agent coordination looks like.
            </h2>

            <div
              className="reveal delay-3"
              style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
            >
              <p
                className="drop-cap"
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '1rem',
                  color: 'var(--col-muted)',
                  lineHeight: '1.75',
                }}
              >
                I am{' '}
                <strong style={{ color: 'var(--col-text)', fontWeight: 600 }}>Arunkumar V</strong>,
                applying to the{' '}
                <strong style={{ color: 'var(--col-text)', fontWeight: 600 }}>
                  Apple Developer Academy @ BINUS
                </strong>
                . AgentWeaver is a portfolio project demonstrating multi-agent orchestration
                with a FastAPI backend, LangGraph for agent coordination, and Redis (Upstash) for
                state. Three specialist agents — text analyzer, data processor, and API client —
                are supervised by a coordinator that sequences their execution and streams every
                step to the browser over WebSocket.
              </p>

              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '1rem',
                  color: 'var(--col-muted)',
                  lineHeight: '1.75',
                }}
              >
                This page shows no mock data. When you press the run button, a real POST fires to
                a live backend on Render and the timeline below fills with actual WebSocket events.
                The design deliberately avoids auto-running demos:{' '}
                <span
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontStyle: 'italic',
                    fontWeight: 500,
                    color: 'var(--col-text)',
                  }}
                >
                  you initiate, the system responds.
                </span>{' '}
                That is the interaction model I find most honest for portfolio work.
              </p>
            </div>

            {/* Badge rows */}
            <div
              className="reveal delay-4"
              style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}
            >
              <div>
                <p
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase',
                    color: 'var(--col-faint)',
                    marginBottom: '0.5rem',
                  }}
                >
                  Stack
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {['FastAPI', 'LangGraph', 'Redis (Upstash)', 'WebSockets', 'React 18', 'TypeScript'].map((b) => (
                    <span key={b} className="tech-badge tech-badge-accent">{b}</span>
                  ))}
                </div>
              </div>
              <div>
                <p
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase',
                    color: 'var(--col-faint)',
                    marginBottom: '0.5rem',
                  }}
                >
                  Design principles
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {['Real-time first', 'On-trigger demos', 'No mock data', 'No console noise'].map((b) => (
                    <span key={b} className="tech-badge">{b}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* About grid responsive override */}
      <style>{`@media (min-width: 820px) { .about-grid { grid-template-columns: 240px 1fr !important; } }`}</style>
    </section>
  );
}
