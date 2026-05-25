import { useEffect, useRef } from 'react';
import Nav from '../components/Nav';
import Composer from '../components/Composer';
import MarkdownMessage from '../components/MarkdownMessage';
import AgentActivityPanel from '../components/AgentActivityPanel';
import { useWorkflowStream } from '../hooks/useWorkflowStream';

// ─── Connection pill ──────────────────────────────────────────────────────────

function ConnectionPill({ state }: { state: string }) {
  const label =
    state === 'connected' ? 'Connected' : state === 'connecting' ? 'Connecting…' : 'Disconnected';
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.45rem',
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
      <span className={`status-dot ${state}`} aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const {
    connection,
    agents,
    messages,
    latestOutputs,
    isRunning,
    sendMessage,
  } = useWorkflowStream();

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    const el = scrollRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, latestOutputs]);

  const isDisabled = isRunning || connection === 'disconnected';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Nav />

      {/* Dashboard body */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          maxWidth: '820px',
          width: '100%',
          margin: '0 auto',
          padding: '1.5rem clamp(1rem, 4vw, 2rem) 0',
          gap: '0',
        }}
      >
        {/* Top status row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
          }}
        >
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: '1rem',
              letterSpacing: '-0.02em',
              color: 'var(--col-text)',
              fontStyle: 'italic',
            }}
          >
            AgentWeaver
          </span>
          <ConnectionPill state={connection} />
        </div>

        {/* Chat scroll area */}
        <div
          ref={scrollRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            minHeight: '0',
            paddingBottom: '1rem',
          }}
          aria-live="polite"
          aria-label="Conversation"
        >
          {messages.length === 0 ? (
            /* Empty state */
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '320px',
                gap: '1.5rem',
                textAlign: 'center',
              }}
            >
              <p
                style={{
                  fontFamily: 'var(--font-display)',
                  fontStyle: 'italic',
                  fontWeight: 500,
                  fontSize: 'clamp(1.25rem, 3vw, 1.75rem)',
                  color: 'var(--col-muted)',
                  letterSpacing: '-0.02em',
                }}
              >
                Ask about any ticker.
              </p>
            </div>
          ) : (
            /* Messages */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {messages.map((msg, idx) => {
                if (msg.role === 'user') {
                  return (
                    <div key={msg.id} style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <div className="chat-bubble-user">
                        {msg.content}
                      </div>
                    </div>
                  );
                }

                // Assistant message — includes agent panel
                const isLastAssistant = idx === messages.length - 1;
                return (
                  <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {/* Agent panel attached to this message */}
                    {msg.latestOutputs && (
                      <AgentActivityPanel
                        agents={agents}
                        latestOutputs={msg.latestOutputs}
                        isRunning={false}
                        executionTime={msg.executionTime ?? null}
                        collapsed={!isLastAssistant}
                      />
                    )}
                    <div className="chat-bubble-assistant">
                      <MarkdownMessage content={msg.content} />
                    </div>
                  </div>
                );
              })}

              {/* In-flight agent panel for active workflow */}
              {isRunning && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <AgentActivityPanel
                    agents={agents}
                    latestOutputs={latestOutputs}
                    isRunning={true}
                    executionTime={null}
                    collapsed={false}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Composer — sticky at bottom */}
        <div
          style={{
            position: 'sticky',
            bottom: 0,
            background: 'linear-gradient(to top, var(--col-ground) 80%, transparent)',
            paddingTop: '1.5rem',
            paddingBottom: '1.5rem',
          }}
        >
          <Composer
            onSend={sendMessage}
            disabled={isDisabled}
            placeholder='Ask about any ticker. Try "How is AAPL doing today?"'
          />
          {connection === 'disconnected' && (
            <p
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.75rem',
                color: 'var(--col-muted)',
                marginTop: '0.5rem',
                fontStyle: 'italic',
              }}
            >
              Connecting to server… backend may be waking from cold start (~30s on Render).
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
