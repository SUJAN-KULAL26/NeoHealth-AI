import React from 'react';
import { HelpCircle, RefreshCw, Sun, Focus, Stethoscope, ArrowLeft, History } from 'lucide-react';
import type { ScreeningResult } from '../types/screening';
import { Disclaimer } from '../components/Disclaimer';

interface UncertainResultProps {
  result: ScreeningResult;
  onRetake: () => void;
  onNavigateHome: () => void;
  onViewHistory?: () => void;
  onBack?: () => void;
}

export const UncertainResult: React.FC<UncertainResultProps> = ({
  result,
  onRetake,
  onNavigateHome,
  onViewHistory,
  onBack,
}) => {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Warning Header */}
      <div className="glass-panel" style={{
        padding: '2.5rem 2rem',
        borderTop: '4px solid var(--accent-purple)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'rgba(168, 85, 247, 0.15)',
          color: '#c084fc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.25rem',
          border: '1px solid rgba(168, 85, 247, 0.3)',
        }}>
          <HelpCircle size={36} />
        </div>

        <span className="badge badge-uncertain" style={{ marginBottom: '0.75rem' }}>
          Low AI Confidence Threshold (Score: {Math.round(result.confidenceScore)}%)
        </span>

        <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.75rem' }}>
          Diagnostic Result Inconclusive
        </h2>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '600px', margin: '0 auto 1.5rem', lineHeight: 1.5 }}>
          {result.uncertaintyReason || 'The AI neural network could not reach the 75% confidence safety threshold required for clinical classification due to image quality limitations.'}
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button onClick={onRetake} className="btn-primary" style={{ padding: '0.85rem 1.75rem' }}>
            <RefreshCw size={18} /> Retake Photo with Better Quality
          </button>
          {onViewHistory && (
            <button onClick={onViewHistory} className="btn-secondary" style={{ padding: '0.85rem 1.5rem' }}>
              <History size={16} /> View Case History
            </button>
          )}
          <button onClick={onBack || onNavigateHome} className="btn-secondary">
            <ArrowLeft size={16} /> Back
          </button>
        </div>
      </div>

      {/* Troubleshooting Tips Grid */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>
          How to Improve Scan Quality for Re-analysis:
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
          }}>
            <Sun size={20} color="var(--accent-amber)" style={{ marginBottom: '0.5rem' }} />
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.2rem' }}>Natural Direct Lighting</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avoid harsh shadows, glares, or low ambient light.</p>
          </div>

          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
          }}>
            <Focus size={20} color="var(--accent-cyan)" style={{ marginBottom: '0.5rem' }} />
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.2rem' }}>Macro Focus & Clarity</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Tap screen to focus camera. Ensure lesion outline is crisp.</p>
          </div>

          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
          }}>
            <Stethoscope size={20} color="var(--accent-emerald)" style={{ marginBottom: '0.5rem' }} />
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.2rem' }}>Consult a Physician</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>If lesion causes pain or bleeding, see a doctor regardless of scan.</p>
          </div>
        </div>
      </div>

      <Disclaimer />
    </div>
  );
};
