import { useState, useRef, useCallback, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

interface ComposerProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const SUGGESTIONS = [
  'How is AAPL doing today?',
  'NVDA vs AMD this month',
  "What's driving TSLA right now?",
  'Should I worry about SPY?',
];

export default function Composer({ onSend, disabled = false, placeholder }: ComposerProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const lineHeight = parseFloat(getComputedStyle(el).lineHeight);
    const maxHeight = lineHeight * 6;
    el.style.height = `${Math.min(el.scrollHeight, maxHeight)}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }

  function handleSuggestion(text: string) {
    setValue(text);
    textareaRef.current?.focus();
  }

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div>
      {/* Suggestion chips — show when empty and not running */}
      {value === '' && !disabled && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            marginBottom: '0.875rem',
          }}
          aria-label="Suggested questions"
        >
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => handleSuggestion(s)}
              style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.75rem',
                color: 'var(--col-muted)',
                background: 'transparent',
                border: '1px solid var(--col-border2)',
                borderRadius: '999px',
                padding: '0.3rem 0.75rem',
                cursor: 'pointer',
                transition: 'border-color 0.2s, color 0.2s',
                lineHeight: 1.4,
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--col-amber-border)';
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--col-amber-glow)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--col-border2)';
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--col-muted)';
              }}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Composer box */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: '0.5rem',
          padding: '0.75rem',
          background: 'var(--col-surface)',
          border: '1px solid var(--col-border2)',
          borderRadius: '8px',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => {
          if (e.currentTarget.contains(e.target)) {
            e.currentTarget.style.borderColor = 'var(--col-amber-border)';
          }
        }}
        onBlur={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget as Node)) {
            e.currentTarget.style.borderColor = 'var(--col-border2)';
          }
        }}
      >
        <textarea
          ref={textareaRef}
          className="composer-textarea"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? 'Ask about any ticker. Try "How is AAPL doing today?"'}
          disabled={disabled}
          rows={1}
          aria-label="Message input"
          style={{ flex: 1 }}
        />

        <button
          type="button"
          onClick={handleSend}
          disabled={!canSend}
          aria-label="Send message"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            background: canSend ? 'var(--col-amber)' : 'var(--col-border2)',
            border: 'none',
            cursor: canSend ? 'pointer' : 'not-allowed',
            color: canSend ? '#fff' : 'var(--col-faint)',
            flexShrink: 0,
            transition: 'background 0.2s, color 0.2s',
          }}
        >
          <ArrowUp size={15} strokeWidth={2.5} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
