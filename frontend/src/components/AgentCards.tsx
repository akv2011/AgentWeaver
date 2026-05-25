import { Brain, Database, Globe } from 'lucide-react';
import type { AgentState } from '../hooks/useWorkflowStream';

interface AgentCardProps {
  id: string;
  name: string;
  type: string;
  icon: React.ReactNode;
  capabilities: string[];
  state: AgentState;
  animDelay: string;
  /* Asymmetric sizing: 'tall' | 'mid' | 'short' */
  size: 'tall' | 'mid' | 'short';
}

function AgentCard({ id: _id, name, type, icon, capabilities, state, animDelay, size }: AgentCardProps) {
  const isBusy = state.status === 'busy';

  const paddingMap = {
    tall: 'clamp(2rem, 4vw, 2.75rem)',
    mid: 'clamp(1.75rem, 3.5vw, 2.25rem)',
    short: 'clamp(1.5rem, 3vw, 2rem)',
  };

  return (
    <article
      className={`agent-card reveal${isBusy ? ' is-busy' : ''}`}
      style={{
        padding: paddingMap[size],
        animationDelay: animDelay,
      }}
    >
      {/* Accent top bar */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: isBusy
            ? 'linear-gradient(90deg, var(--col-amber) 0%, var(--col-amber-glow) 50%, transparent 100%)'
            : 'linear-gradient(90deg, var(--col-border2) 0%, transparent 60%)',
          transition: 'background 0.5s ease',
        }}
      />

      {/* Icon + names */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem', marginBottom: '1.25rem' }}>
        <div
          aria-hidden="true"
          style={{
            width: '44px',
            height: '44px',
            borderRadius: '10px',
            background: isBusy
              ? 'linear-gradient(135deg, rgba(201,132,58,0.2) 0%, rgba(201,132,58,0.1) 100%)'
              : 'linear-gradient(135deg, var(--col-surface2) 0%, var(--col-border) 100%)',
            border: isBusy ? '1px solid var(--col-amber-border)' : '1px solid var(--col-border2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: isBusy ? 'var(--col-amber-glow)' : 'var(--col-muted)',
            flexShrink: 0,
            transition: 'all 0.4s ease',
          }}
        >
          {icon}
        </div>
        <div style={{ paddingTop: '0.2rem' }}>
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: '1.375rem',
              letterSpacing: '-0.025em',
              lineHeight: 1,
              color: 'var(--col-text)',
              marginBottom: '0.25rem',
            }}
          >
            {name}
          </h3>
          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '0.75rem',
              color: isBusy ? 'var(--col-amber-glow)' : 'var(--col-muted)',
              fontWeight: 500,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              transition: 'color 0.4s ease',
            }}
          >
            {type}
          </p>
        </div>
      </div>

      <hr className="hr-fine" style={{ marginBottom: '1.125rem' }} />

      {/* Capabilities */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.35rem',
          marginBottom: '1.5rem',
        }}
        role="list"
        aria-label="Capabilities"
      >
        {capabilities.map((cap) => (
          <span key={cap} className="tech-badge" role="listitem">
            {cap}
          </span>
        ))}
      </div>

      {/* Current task */}
      <div
        style={{
          minHeight: '2.75rem',
          padding: '0.625rem 0.875rem',
          borderRadius: '4px',
          background: isBusy ? 'var(--col-amber-bg)' : 'rgba(255,255,255,0.02)',
          border: isBusy ? '1px solid var(--col-amber-border)' : '1px solid var(--col-border)',
          transition: 'all 0.4s ease',
          display: 'flex',
          alignItems: 'center',
          gap: '0.625rem',
        }}
      >
        <span
          className={`status-dot${isBusy ? ' busy' : ''}`}
          aria-hidden="true"
          style={{ flexShrink: 0 }}
        />
        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.8125rem',
            color: isBusy ? 'var(--col-amber-glow)' : 'var(--col-faint)',
            lineHeight: 1.4,
            fontStyle: isBusy ? 'normal' : 'italic',
            transition: 'color 0.4s ease',
          }}
        >
          {isBusy && state.currentTask
            ? state.currentTask
            : 'Idle — awaiting workflow'}
        </p>
      </div>
    </article>
  );
}

interface AgentCardsProps {
  agents: Record<string, AgentState>;
}

const agentDefs = [
  {
    id: 'text_analyzer',
    name: 'Text Analyzer',
    type: 'Natural Language',
    icon: <Brain size={20} strokeWidth={1.5} />,
    capabilities: ['sentiment analysis', 'entity extraction', 'topic classification'],
    size: 'tall' as const,
    animDelay: '0.55s',
  },
  {
    id: 'data_processor',
    name: 'Data Processor',
    type: 'Data Processing',
    icon: <Database size={20} strokeWidth={1.5} />,
    capabilities: ['record processing', 'quality scoring', 'normalization'],
    size: 'mid' as const,
    animDelay: '0.70s',
  },
  {
    id: 'api_client',
    name: 'API Client',
    type: 'API Integration',
    icon: <Globe size={20} strokeWidth={1.5} />,
    capabilities: ['external data', 'request batching', 'response parsing'],
    size: 'short' as const,
    animDelay: '0.85s',
  },
];

const fallbackAgent: AgentState = { id: '', status: 'idle', currentTask: null };

export default function AgentCards({ agents }: AgentCardsProps) {
  return (
    <section
      aria-labelledby="agents-heading"
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: 'clamp(4rem, 10vh, 7rem) clamp(1.25rem, 5vw, 3.5rem)',
      }}
    >
      {/* Section header */}
      <div style={{ marginBottom: '3rem' }}>
        <p className="section-label reveal delay-0" style={{ marginBottom: '0.75rem' }}>
          The Agents
        </p>
        <h2
          id="agents-heading"
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
          Three specialists.{' '}
          <span style={{ fontStyle: 'italic', color: 'var(--col-muted)' }}>
            One supervisor.
          </span>
        </h2>
        <p
          className="reveal delay-2"
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.9375rem',
            color: 'var(--col-muted)',
            marginTop: '0.875rem',
            maxWidth: '52ch',
            lineHeight: 1.65,
          }}
        >
          Each agent has a narrow specialty. The supervisor orchestrates the sequence, passing outputs
          downstream. Watch their status update live as a workflow runs.
        </p>
      </div>

      {/* Asymmetric three-column grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '1.25rem',
          alignItems: 'start',
        }}
      >
        {agentDefs.map((def) => (
          <AgentCard
            key={def.id}
            {...def}
            state={agents[def.id] ?? fallbackAgent}
          />
        ))}
      </div>
    </section>
  );
}
