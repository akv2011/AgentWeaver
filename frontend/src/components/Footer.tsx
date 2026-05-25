import { Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer
      role="contentinfo"
      style={{
        borderTop: '1px solid var(--col-border)',
        padding: 'clamp(2.5rem, 6vh, 4rem) 0',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 clamp(1.25rem, 5vw, 3.5rem)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
        }}
      >
        {/* Top row */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
          }}
        >
          {/* Wordmark */}
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: '1.125rem',
              letterSpacing: '-0.025em',
              color: 'var(--col-text)',
              fontStyle: 'italic',
            }}
          >
            AgentWeaver
          </span>

          {/* GitHub link */}
          <nav aria-label="Project links" style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
            <a
              href="https://github.com/akv2011/AgentWeaver"
              className="footer-link"
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <Github size={13} strokeWidth={1.5} aria-hidden="true" />
              akv2011/AgentWeaver
            </a>
          </nav>
        </div>

        <hr className="hr-fine" />

        {/* Bottom row */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.75rem',
          }}
        >
          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.75rem',
              color: 'var(--col-muted)',
            }}
          >
            &copy; 2026 Arunkumar V
          </p>

          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.75rem',
              color: 'var(--col-faint)',
              fontStyle: 'italic',
              textAlign: 'right',
              maxWidth: '52ch',
              lineHeight: 1.5,
            }}
          >
            Backend on Render (Singapore). First load may take ~30s if cold.
          </p>
        </div>
      </div>
    </footer>
  );
}
