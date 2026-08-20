import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle, Baby, CheckCircle2 } from 'lucide-react';
import type { ScreeningResult, RiskLevel } from '../types/screening';
import { formatPercentage, getRiskColor } from '../utils/validation';

interface ConfidenceCardProps {
  result: ScreeningResult;
}

export const ConfidenceCard: React.FC<ConfidenceCardProps> = ({ result }) => {
  const riskColor = getRiskColor(result.riskLevel);

  const getRiskIcon = (risk: RiskLevel) => {
    switch (risk) {
      case 'low':
        return <ShieldCheck size={20} color="#10b981" />;
      case 'moderate':
        return <AlertTriangle size={20} color="#f59e0b" />;
      case 'high':
        return <ShieldAlert size={20} color="#ef4444" />;
      case 'uncertain':
        return <HelpCircle size={20} color="#8b5cf6" />;
    }
  };

  const getBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'low':
        return 'badge-low';
      case 'moderate':
        return 'badge-moderate';
      case 'high':
        return 'badge-high';
      case 'uncertain':
        return 'badge-uncertain';
    }
  };

  return (
    <div className="glass-panel" style={{
      padding: '2.25rem',
      position: 'relative',
      overflow: 'hidden',
      borderTop: `4px solid ${riskColor}`,
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '2rem',
      }}>
        {/* Left: Prediction & Risk Badge */}
        <div style={{ flex: '1 1 340px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
            <span className={`badge ${getBadgeClass(result.riskLevel)}`}>
              {getRiskIcon(result.riskLevel)}
              {result.riskLevel} Risk
            </span>

            <span style={{
              background: 'rgba(6, 182, 212, 0.12)',
              color: '#38bdf8',
              padding: '0.3rem 0.75rem',
              borderRadius: '999px',
              fontSize: '0.78rem',
              fontWeight: 700,
              border: '1px solid rgba(6, 182, 212, 0.25)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}>
              <Baby size={13} /> {result.category || 'Pediatric Condition'}
            </span>

            <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>
              Scan ID: {result.id}
            </span>
          </div>

          <h2 style={{
            fontSize: '2.2rem',
            fontWeight: 900,
            color: 'var(--text-main)',
            marginBottom: '0.85rem',
            lineHeight: 1.15,
          }}>
            {result.primaryPrediction}
          </h2>

          <p style={{
            fontSize: '0.95rem',
            color: 'var(--text-muted)',
            lineHeight: 1.6,
            marginBottom: '1.25rem',
          }}>
            {result.diagnosticSummary}
          </p>

          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            padding: '0.9rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            fontSize: '0.88rem',
            color: 'var(--text-main)',
            lineHeight: 1.5,
          }}>
            <strong style={{ color: riskColor, marginRight: '6px' }}>Clinical Impression:</strong>
            {result.clinicalSignificance}
          </div>
        </div>

        {/* Right: AI Model Confidence Meter Gauge */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(13, 21, 39, 0.8)',
          padding: '1.75rem 2.25rem',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          minWidth: '220px',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
        }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>
            Model Confidence
          </span>

          <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="130" height="130" viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="10"
              />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke={riskColor}
                strokeWidth="10"
                strokeDasharray={`${(result.confidenceScore / 100) * 314} 314`}
                strokeLinecap="round"
                transform="rotate(-90 60 60)"
                style={{ transition: 'stroke-dasharray 1.2s ease', filter: `drop-shadow(0 0 8px ${riskColor})` }}
              />
            </svg>

            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <span style={{ fontSize: '1.8rem', fontWeight: 900, color: '#ffffff' }}>
                {formatPercentage(result.confidenceScore)}
              </span>
            </div>
          </div>

          <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={13} color="var(--accent-emerald)" /> 6-Class Neural Net
          </span>
        </div>
      </div>
    </div>
  );
};
