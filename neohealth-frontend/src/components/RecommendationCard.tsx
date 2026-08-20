import React from 'react';
import { Stethoscope, AlertOctagon, CheckCircle2, ChevronRight, AlertTriangle } from 'lucide-react';
import type { Recommendation } from '../types/screening';

interface RecommendationCardProps {
  recommendations: Recommendation[];
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendations }) => {
  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem' }}>
        <Stethoscope size={24} color="var(--accent-cyan)" />
        <div>
          <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Pediatric Care Protocol & Next Steps</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
            Actionable clinical guidance aligned with pediatric dermatology safety standards.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {recommendations.map((rec) => {
          const isUrgent = rec.urgency === 'urgent';
          const isWarning = rec.urgency === 'warning';

          return (
            <div
              key={rec.id}
              style={{
                background: isUrgent
                  ? 'rgba(244, 63, 94, 0.08)'
                  : isWarning
                  ? 'rgba(245, 158, 11, 0.08)'
                  : 'rgba(13, 21, 39, 0.65)',
                border: isUrgent
                  ? '1px solid rgba(244, 63, 94, 0.35)'
                  : isWarning
                  ? '1px solid rgba(245, 158, 11, 0.35)'
                  : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem 1.4rem',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem', flex: 1, minWidth: '260px' }}>
                {isUrgent ? (
                  <AlertOctagon size={22} color="#f43f5e" style={{ marginTop: '2px', flexShrink: 0 }} />
                ) : isWarning ? (
                  <AlertTriangle size={22} color="#f59e0b" style={{ marginTop: '2px', flexShrink: 0 }} />
                ) : (
                  <CheckCircle2 size={22} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
                )}

                <div>
                  <h4 style={{
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    color: isUrgent ? '#fda4af' : isWarning ? '#fde047' : '#ffffff',
                    marginBottom: '0.35rem',
                  }}>
                    {rec.title}
                  </h4>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {rec.detail}
                  </p>
                </div>
              </div>

              {rec.actionText && (
                <button
                  className={isUrgent ? 'btn-danger' : 'btn-secondary'}
                  style={{ fontSize: '0.85rem', padding: '0.55rem 1.1rem', whiteSpace: 'nowrap' }}
                  onClick={() => alert(`Triggered Protocol: ${rec.actionText}`)}
                >
                  {rec.actionText} <ChevronRight size={14} />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
