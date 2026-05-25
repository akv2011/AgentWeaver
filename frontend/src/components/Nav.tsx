import { Link, useLocation } from 'react-router-dom';

export default function Nav() {
  const { pathname } = useLocation();

  return (
    <nav
      aria-label="Site navigation"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        borderBottom: '1px solid var(--col-border)',
        background: 'rgba(13, 12, 10, 0.88)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 clamp(1.25rem, 5vw, 3.5rem)',
          height: '52px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem',
        }}
      >
        {/* Wordmark */}
        <Link
          to="/"
          style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            fontSize: '1rem',
            letterSpacing: '-0.02em',
            color: 'var(--col-text)',
            fontStyle: 'italic',
            textDecoration: 'none',
            flexShrink: 0,
          }}
        >
          AgentWeaver
        </Link>

        {/* Links */}
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <Link
            to="/"
            className={`nav-link${pathname === '/' ? ' active' : ''}`}
            aria-current={pathname === '/' ? 'page' : undefined}
          >
            Overview
          </Link>
          <Link
            to="/dashboard"
            className={`nav-link${pathname === '/dashboard' ? ' active' : ''}`}
            aria-current={pathname === '/dashboard' ? 'page' : undefined}
          >
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  );
}
