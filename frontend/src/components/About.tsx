import { Radio, Workflow, ShieldCheck } from 'lucide-react';

export default function About() {
  return (
    <section
      aria-labelledby="about-heading"
      className="about-section"
      style={{ padding: 'clamp(4rem, 10vh, 7rem) 0' }}
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

            <div
              className="reveal delay-2"
              style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '2.5rem' }}
            >
              {[
                {
                  icon: <Radio size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'Real-time streaming',
                  sub: 'Every step appears as it happens',
                },
                {
                  icon: <Workflow size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'Visible orchestration',
                  sub: 'Agent states and outputs rendered inline',
                },
                {
                  icon: <ShieldCheck size={15} strokeWidth={1.5} aria-hidden="true" />,
                  label: 'Transparent reasoning',
                  sub: 'No closed-box demos — real JSON, real data',
                },
              ].map((item) => (
                <div key={item.label} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
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
                I built AgentWeaver to make agent collaboration visible. Every step the system
                takes — fetching live market data, searching for news, computing the trend signal
                — streams to the browser as it happens, with the actual JSON outputs rendered
                inline. It is the opposite of the closed-box agent demos that show you a final
                answer and ask you to trust them. Built by Arunkumar V.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
