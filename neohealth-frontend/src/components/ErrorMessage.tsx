import React from 'react';
import { AlertTriangle, RefreshCw, XCircle } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, onDismiss }) => {
  return (
    <div style={{
      background: 'rgba(244, 63, 94, 0.12)',
      border: '1px solid rgba(244, 63, 94, 0.35)',
      borderRadius: 'var(--radius-md)',
      padding: '1.25rem 1.5rem',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      gap: '1rem',
      maxWidth: '750px',
      margin: '0 auto 1.5rem',
      boxShadow: '0 8px 20px rgba(244, 63, 94, 0.15)',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.8rem' }}>
        <AlertTriangle size={22} color="#f43f5e" style={{ marginTop: '2px', flexShrink: 0 }} />
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fda4af', marginBottom: '0.2rem' }}>
            Processing Error
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
            {message}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {onRetry && (
          <button
            onClick={onRetry}
            className="btn-danger"
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
          >
            <RefreshCw size={14} /> Retry
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.2rem',
            }}
          >
            <XCircle size={18} />
          </button>
        )}
      </div>
    </div>
  );
};
