import { Link } from 'react-router-dom';
import { ChevronDown, Github, Radio, Workflow, ShieldCheck } from 'lucide-react';
import Nav from '../components/Nav';
import Footer from '../components/Footer';

// ─── Data ─────────────────────────────────────────────────────────────────────

const marqueeItems = [
  'yfinance',
  'OpenRouter',
  'Perplexity Sonar',
  'Claude Haiku 4.5',
  'FastAPI',
  'WebSockets',
  'React 18',
  'LangGraph',
];

const agentCards = [
  {
    letter: 'M',
    name: 'Market Data',
    tagline: 'Live prices from Yahoo Finance.',
    description:
      'Live Yahoo prices, day range, 50/200-day moving averages, volume.',
    badges: ['yfinance', 'live quote', '52-week range', 'MA50/MA200'],
    example: 'AAPL · $189.42 · +1.2% · day range 187–191',
    accentSide: false,
    animDelay: '0.55s',
  },
  {
    letter: 'N',
    name: 'News Context',
    tagline: 'Recent headlines via Perplexity Sonar.',
    description:
      'Recent headlines for the same ticker via Perplexity Sonar with web search.',
    badges: ['Perplexity Sonar', 'web search', 'sentiment scoring', 'citations'],
    example: '5 headlines about Q3 earnings, 3 positive / 1 mixed / 1 negative',
    accentSide: true,
    animDelay: '0.70s',
  },
  {
    letter: 'A',
    name: 'Technical Analysis',
    tagline: 'Structured signal via Claude Haiku.',
    description: 'Structured trend signal, key catalysts, key risks.',
    badges: ['Claude Haiku 4.5', 'structured JSON', 'trend signal', 'catalysts and risks'],
    example: 'bullish bias on positive earnings beat; risk: macro slowdown',
    accentSide: false,
    animDelay: '0.85s',
  },
];

const howItWorks = [
  {
    num: '1',
    bold: 'Ask in plain English',
    detail: '"How is AAPL today?" or "NVDA vs AMD"',
  },
  {
    num: '2',
    bold: 'Three agents run in sequence',
    detail: 'They fetch data, news, and analysis independently',
  },
  {
    num: '3',
    bold: 'A supervisor composes the answer',
    detail: 'Using all three outputs into a single reply',
  },
];

const aboutPillars = [
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
];

// ─── Component ─────────────────────────────────────────────────────────────────

export default function LandingPage() {
  return (
    <main>
      <Nav />

      {/* ── 1. Hero ─────────────────────────────────────────────────────── */}
      <section
        aria-label="Introduction"
        style={{
          paddingTop: 'clamp(5rem, 14vh, 9rem)',
          paddingBottom: '5rem',
          position: 'relative',
        }}
      >
        {/* Background deco numeral */}
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
          {/* Section label */}
          <p className="section-label reveal delay-0" style={{ marginBottom: '1.75rem' }}>
            Portfolio&nbsp;&nbsp;/&nbsp;&nbsp;Real-time multi-agent demo
          </p>

          {/* Headline */}
          <h1
            className="hero-headline reveal delay-1"
            style={{ maxWidth: '18ch', marginBottom: '2rem' }}
          >
            Ask any question about any stock.{' '}
            <em>Watch</em> three agents answer it.
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
            Real Yahoo market data, web-grounded news via Perplexity, structured
            analysis by Claude. Every step streams live.
          </p>

          {/* CTAs */}
          <div
            className="reveal delay-3"
            style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '3.5rem' }}
          >
            <Link to="/dashboard" className="btn-primary">
              Try the chat →
            </Link>
            <a
              href="https://github.com/akv2011/AgentWeaver"
              className="btn-secondary"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github size={14} strokeWidth={1.5} aria-hidden="true" />
              View source
            </a>
          </div>

          {/* Author */}
          <div
            className="reveal delay-4"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
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
      </section>

      {/* ── 2. What it does ─────────────────────────────────────────────── */}
      <section
        aria-labelledby="what-heading"
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: 'clamp(4rem, 10vh, 7rem) clamp(1.25rem, 5vw, 3.5rem)',
        }}
      >
        <div style={{ marginBottom: '3rem' }}>
          <p className="section-label reveal delay-0" style={{ marginBottom: '0.75rem' }}>
            The Work
          </p>
          <h2
            id="what-heading"
            className="reveal delay-1"
            style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: 'clamp(2rem, 5vw, 3.25rem)',
              letterSpacing: '-0.03em',
              lineHeight: 1.05,
              color: 'var(--col-text)',
              maxWidth: '22ch',
            }}
          >
            Three agents.{' '}
            <span style={{ fontStyle: 'italic', color: 'var(--col-muted)' }}>
              One answer.
            </span>
          </h2>
        </div>

        <div className="cards-grid-three">
          {agentCards.map((card) => (
            <article
              key={card.name}
              className="app-card reveal"
              style={{
                borderRadius: '8px',
                padding: 'clamp(1.5rem, 4vw, 2.25rem)',
                animationDelay: card.animDelay,
              }}
            >
              {/* Accent bar */}
              {card.accentSide ? (
                <div
                  aria-hidden="true"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    bottom: 0,
                    width: '2px',
                    background: 'linear-gradient(180deg, transparent 0%, var(--col-border2) 40%, transparent 100%)',
                  }}
                />
              ) : (
                <div
                  aria-hidden="true"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    background: 'linear-gradient(90deg, var(--col-amber) 0%, transparent 70%)',
                  }}
                />
              )}

              {/* Icon + name */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem', marginBottom: '1.25rem' }}>
                <div
                  style={{
                    width: '52px',
                    height: '52px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, rgba(201,132,58,0.18) 0%, rgba(201,132,58,0.08) 100%)',
                    border: '1px solid var(--col-amber-border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'var(--font-display)',
                    fontWeight: 700,
                    fontSize: '1.25rem',
                    fontStyle: 'italic',
                    color: 'var(--col-amber-glow)',
                    flexShrink: 0,
                  }}
                  aria-hidden="true"
                >
                  {card.letter}
                </div>
                <div style={{ paddingTop: '0.25rem' }}>
                  <h3
                    style={{
                      fontFamily: 'var(--font-display)',
                      fontWeight: 700,
                      fontSize: '1.375rem',
                      letterSpacing: '-0.025em',
                      lineHeight: 1,
                      color: 'var(--col-text)',
                      marginBottom: '0.3rem',
                    }}
                  >
                    {card.name}
                  </h3>
                  <p
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.8125rem',
                      color: 'var(--col-amber-glow)',
                      fontWeight: 500,
                      letterSpacing: '0.01em',
                    }}
                  >
                    {card.tagline}
                  </p>
                </div>
              </div>

              <hr className="hr-fine" style={{ marginBottom: '1.125rem' }} />

              {/* Description */}
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.9375rem',
                  color: 'var(--col-muted)',
                  lineHeight: '1.7',
                  marginBottom: '1.25rem',
                }}
              >
                {card.description}
              </p>

              {/* Badges */}
              <div
                style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '1.25rem' }}
                role="list"
                aria-label="Technologies"
              >
                {card.badges.map((b) => (
                  <span key={b} className="tech-badge tech-badge-accent" role="listitem">
                    {b}
                  </span>
                ))}
              </div>

              {/* Example one-liner */}
              <div
                style={{
                  padding: '0.625rem 0.875rem',
                  borderRadius: '4px',
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--col-border)',
                }}
              >
                <p
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: '0.75rem',
                    color: 'var(--col-faint)',
                    fontStyle: 'italic',
                    lineHeight: 1.5,
                  }}
                >
                  {card.example}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ── 3. How it works ─────────────────────────────────────────────── */}
      <section
        aria-labelledby="how-heading"
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 clamp(1.25rem, 5vw, 3.5rem) clamp(4rem, 10vh, 7rem)',
        }}
      >
        <div
          className="gatekeeper-card reveal delay-0"
          style={{
            borderRadius: '8px',
            padding: 'clamp(1.75rem, 5vw, 2.75rem)',
            maxWidth: '760px',
          }}
        >
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem', marginBottom: '1.75rem' }}>
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                background: 'var(--col-amber-bg)',
                border: '1px solid var(--col-amber-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                marginTop: '1px',
              }}
              aria-hidden="true"
            >
              <Workflow size={16} strokeWidth={1.5} style={{ color: 'var(--col-amber-glow)' }} />
            </div>
            <div>
              <h2
                id="how-heading"
                style={{
                  fontFamily: 'var(--font-display)',
                  fontWeight: 700,
                  fontSize: '1.25rem',
                  letterSpacing: '-0.02em',
                  lineHeight: 1.15,
                  color: 'var(--col-text)',
                  marginBottom: '0.35rem',
                }}
              >
                How it works
              </h2>
              <p
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.8125rem',
                  color: 'var(--col-muted)',
                  lineHeight: 1.5,
                }}
              >
                One question. Three agents. Five to ten seconds.
              </p>
            </div>
          </div>

          {/* Steps */}
          <ol
            style={{
              listStyle: 'none',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              marginBottom: '1.75rem',
            }}
            aria-label="How it works"
          >
            {howItWorks.map((step) => (
              <li key={step.num} className="gatekeeper-step">
                <span className="gatekeeper-num tabular-nums" aria-hidden="true">
                  {step.num}
                </span>
                <div>
                  <p
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '0.9375rem',
                      color: 'var(--col-muted)',
                      lineHeight: 1.6,
                    }}
                  >
                    <span className="gatekeeper-bold">{step.bold}</span>
                    {' — '}
                    {step.detail}
                  </p>
                </div>
              </li>
            ))}
          </ol>

          {/* Closing line */}
          <div
            style={{
              padding: '0.875rem 1.125rem',
              borderRadius: '4px',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--col-border)',
            }}
          >
            <p
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.8125rem',
                color: 'var(--col-muted)',
                lineHeight: 1.55,
              }}
            >
              Five to ten seconds end-to-end.{' '}
              <span style={{ color: 'var(--col-text)', fontWeight: 500 }}>
                No clicks beyond your one question.
              </span>
            </p>
          </div>
        </div>
      </section>

      {/* ── 4. About ────────────────────────────────────────────────────── */}
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
                {aboutPillars.map((item) => (
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

      {/* ── 5. Footer ───────────────────────────────────────────────────── */}
      <Footer />
    </main>
  );
}
